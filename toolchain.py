import json
import pathlib
from typing import Any

import aws_cdk as cdk
from aws_cdk import aws_codebuild as codebuild
from aws_cdk import pipelines
from constructs import Construct

import constants
from deployment import UserManagementBackend


class Toolchain(cdk.Stack):
    def __init__(self, scope: Construct, id_: str, **kwargs: Any):
        super().__init__(scope, id_, **kwargs)

        build_spec = codebuild.BuildSpec.from_object(
            {
                "phases": {
                    "install": {
                        "runtime-versions": {"python": constants.APP_PYTHON_VERSION},
                        "commands": ["env", "./scripts/install-deps.sh"],
                    },
                    "build": {"commands": ["./scripts/run-tests.sh", "npx cdk synth"]},
                },
                "version": "0.2",
            }
        )
        ContinuousDeployment(self, "ContinuousDeployment", build_spec=build_spec)
        PullRequestValidation(self, "PullRequestValidation", build_spec=build_spec)


class ContinuousDeployment(Construct):
    def __init__(self, scope: Construct, id_: str, *, build_spec: codebuild.BuildSpec):
        super().__init__(scope, id_)

        codepipeline_source_connection = pipelines.CodePipelineSource.connection(
            f"{constants.GITHUB_OWNER}/{constants.GITHUB_REPO}",
            constants.GITHUB_TRUNK_BRANCH,
            connection_arn=constants.GITHUB_CONNECTION_ARN,
        )
        codebuild_step = pipelines.CodeBuildStep(
            "CodeBuildStep",
            input=codepipeline_source_connection,
            partial_build_spec=build_spec,
            # The build_spec argument includes build commands.
            commands=[],
            primary_output_directory="cdk.out",
        )
        codepipeline = pipelines.CodePipeline(
            self,
            "CodePipeline",
            cli_version=ContinuousDeployment._get_cdk_cli_version(),
            cross_account_keys=True,
            docker_enabled_for_synth=True,
            publish_assets_in_parallel=False,
            synth=codebuild_step,
        )
        self._add_usermanagement_backend_prod_stage(codepipeline)

    def _add_usermanagement_backend_prod_stage(
        self, codepipeline: pipelines.CodePipeline
    ) -> None:
        usermanagement_backend_prod = UserManagementBackend(
            self,
            f"{constants.APP_NAME}-Prod",
            env=constants.PROD_ENV,
            api_lambda_reserved_concurrency=constants.PROD_API_LAMBDA_RESERVED_CONCURRENCY,
            database_dynamodb_billing_mode=constants.PROD_DATABASE_DYNAMODB_BILLING_MODE,
        )
        api_smoke_test = ApiSmokeTest(
            self, "ApiSmokeTest", api_endpoint=usermanagement_backend_prod.api_endpoint
        )
        codepipeline.add_stage(
            usermanagement_backend_prod, post=[api_smoke_test.shell_step]
        )

    @staticmethod
    def _get_cdk_cli_version() -> str:
        package_json_path = (
            pathlib.Path(__file__).parent.joinpath("package.json").resolve()
        )
        with open(package_json_path, encoding="utf_8") as package_json_file:
            package_json = json.load(package_json_file)
        cdk_cli_version = str(package_json["devDependencies"]["aws-cdk"])
        return cdk_cli_version


class ApiSmokeTest(Construct):
    def __init__(self, scope: Construct, id_: str, *, api_endpoint: cdk.CfnOutput):
        super().__init__(scope, id_)

        api_endpoint_env_var_name = f"{constants.APP_NAME.upper()}_API_ENDPOINT"
        smoke_test_commands = [f"curl ${api_endpoint_env_var_name}"]
        self.shell_step = pipelines.ShellStep(
            "ShellStep",
            env_from_cfn_outputs={api_endpoint_env_var_name: api_endpoint},
            commands=smoke_test_commands,
        )


class PullRequestValidation(Construct):
    def __init__(self, scope: Construct, id_: str, *, build_spec: codebuild.BuildSpec):
        super().__init__(scope, id_)

        webhook_filters = [
            codebuild.FilterGroup.in_event_of(
                codebuild.EventAction.PULL_REQUEST_CREATED
            ).and_base_branch_is(constants.GITHUB_TRUNK_BRANCH),
            codebuild.FilterGroup.in_event_of(
                codebuild.EventAction.PULL_REQUEST_UPDATED
            ).and_base_branch_is(constants.GITHUB_TRUNK_BRANCH),
        ]
        source = codebuild.Source.git_hub(
            owner=constants.GITHUB_OWNER,
            repo=constants.GITHUB_REPO,
            webhook_filters=webhook_filters,
        )
        codebuild.Project(
            self,
            "CodeBuildProject",
            source=source,
            build_spec=build_spec,
            environment=codebuild.BuildEnvironment(privileged=True),
        )
