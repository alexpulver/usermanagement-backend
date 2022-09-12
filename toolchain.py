import json
import pathlib
from typing import Any

import aws_cdk as cdk
import aws_cdk.aws_codebuild as codebuild
import aws_cdk.aws_dynamodb as dynamodb
from aws_cdk import pipelines
from constructs import Construct

import constants
from component import UserManagementBackend

# pylint: disable=line-too-long
GITHUB_CONNECTION_ARN = "arn:aws:codestar-connections:eu-west-1:807650736403:connection/1f244295-871f-411f-afb1-e6ca987858b6"
GITHUB_OWNER = "alexpulver"
GITHUB_REPO = "usermanagement-backend"
GITHUB_TRUNK_BRANCH = "main"
PRODUCTION_ENV_NAME = "Production"
PRODUCTION_ENV_ACCOUNT = "807650736403"
PRODUCTION_ENV_REGION = "eu-west-1"


class UserManagementBackendToolchain(cdk.Stack):
    def __init__(self, scope: Construct, id_: str, **kwargs: Any):
        super().__init__(scope, id_, **kwargs)

        build_spec = codebuild.BuildSpec.from_object(
            {
                "phases": {
                    "install": {
                        "runtime-versions": {"python": "3.7"},
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
            f"{GITHUB_OWNER}/{GITHUB_REPO}",
            GITHUB_TRUNK_BRANCH,
            connection_arn=GITHUB_CONNECTION_ARN,
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
        self._add_production_stage(codepipeline)

    def _add_production_stage(self, codepipeline: pipelines.CodePipeline) -> None:
        usermanagement_backend = UserManagementBackend(
            self,
            constants.APP_NAME + PRODUCTION_ENV_NAME,
            env=cdk.Environment(
                account=PRODUCTION_ENV_ACCOUNT, region=PRODUCTION_ENV_REGION
            ),
            env_name=PRODUCTION_ENV_NAME,
            api_lambda_reserved_concurrency=10,
            database_dynamodb_billing_mode=dynamodb.BillingMode.PROVISIONED,
        )
        api_smoke_test = APISmokeTest(
            self,
            "APISmokeTest" + PRODUCTION_ENV_NAME,
            api_endpoint=usermanagement_backend.api_endpoint,
        )
        codepipeline.add_stage(usermanagement_backend, post=[api_smoke_test.shell_step])

    @staticmethod
    def _get_cdk_cli_version() -> str:
        package_json_path = (
            pathlib.Path(__file__).parent.joinpath("package.json").resolve()
        )
        with open(package_json_path, encoding="utf_8") as package_json_file:
            package_json = json.load(package_json_file)
        cdk_cli_version = str(package_json["devDependencies"]["aws-cdk"])
        return cdk_cli_version


class APISmokeTest(Construct):
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
            ).and_base_branch_is(GITHUB_TRUNK_BRANCH),
            codebuild.FilterGroup.in_event_of(
                codebuild.EventAction.PULL_REQUEST_UPDATED
            ).and_base_branch_is(GITHUB_TRUNK_BRANCH),
        ]
        source = codebuild.Source.git_hub(
            owner=GITHUB_OWNER,
            repo=GITHUB_REPO,
            webhook_filters=webhook_filters,
        )
        codebuild.Project(
            self,
            "CodeBuildProject",
            source=source,
            build_spec=build_spec,
            environment=codebuild.BuildEnvironment(privileged=True),
        )
