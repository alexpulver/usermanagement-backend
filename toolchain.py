import json
import pathlib
from typing import Any

from aws_cdk import aws_codebuild as codebuild
from aws_cdk import core as cdk
from aws_cdk import pipelines

import constants
from deployment import UserManagementBackend


class Toolchain(cdk.Stack):
    def __init__(
        self, scope: cdk.Construct, id_: str, app_scope: cdk.Construct, **kwargs: Any
    ):
        super().__init__(scope, id_, **kwargs)

        build_spec = codebuild.BuildSpec.from_object(
            {
                "phases": {
                    "install": {
                        "runtime-versions": {
                            "python": constants.CDK_APP_PYTHON_VERSION
                        },
                        "commands": ["./scripts/install-deps.sh"],
                    },
                    "build": {"commands": ["./scripts/run-tests.sh", "npx cdk synth"]},
                },
                "version": "0.2",
            }
        )
        self._add_pipeline(build_spec, app_scope)
        self._add_pull_request_build(build_spec)

    def _add_pipeline(
        self,
        build_spec: codebuild.BuildSpec,
        app_scope: cdk.Construct,
    ) -> None:
        source = pipelines.CodePipelineSource.connection(
            f"{constants.GITHUB_OWNER}/{constants.GITHUB_REPO}",
            constants.GITHUB_TRUNK_BRANCH,
            connection_arn=constants.GITHUB_CONNECTION_ARN,
        )
        synth = pipelines.CodeBuildStep(
            "Synth",
            input=source,
            partial_build_spec=build_spec,
            # The build_spec argument includes build commands.
            commands=[],
            primary_output_directory="cdk.out",
        )
        pipeline = pipelines.CodePipeline(
            self,
            "Pipeline",
            cli_version=Toolchain._get_cdk_cli_version(),
            docker_enabled_for_synth=True,
            synth=synth,
        )
        self._add_prod_stage(pipeline, app_scope)

    def _add_pull_request_build(self, build_spec: codebuild.BuildSpec) -> None:
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
            "PullRequestBuild",
            source=source,
            build_spec=build_spec,
            environment=codebuild.BuildEnvironment(privileged=True),
        )

    @staticmethod
    def _get_cdk_cli_version() -> str:
        package_json_path = (
            pathlib.Path(__file__).parent.joinpath("package.json").resolve()
        )
        with open(package_json_path) as package_json_file:
            package_json = json.load(package_json_file)
        cdk_cli_version = str(package_json["devDependencies"]["aws-cdk"])
        return cdk_cli_version

    @staticmethod
    def _add_prod_stage(
        pipeline: pipelines.CodePipeline, app_scope: cdk.Construct
    ) -> None:
        prod_stage = UserManagementBackend(
            app_scope,
            f"{constants.CDK_APP_NAME}-Prod",
            env=constants.PROD_ENV,
            api_lambda_reserved_concurrency=constants.PROD_API_LAMBDA_RESERVED_CONCURRENCY,
            database_dynamodb_billing_mode=constants.PROD_DATABASE_DYNAMODB_BILLING_MODE,
        )
        api_endpoint_url_env_var = f"{constants.CDK_APP_NAME.upper()}_API_ENDPOINT_URL"
        smoke_test_commands = [f"curl ${api_endpoint_url_env_var}"]
        smoke_test_shell_step = pipelines.ShellStep(
            "SmokeTest",
            env_from_cfn_outputs={
                api_endpoint_url_env_var: prod_stage.api_endpoint_url_cfn_output
            },
            commands=smoke_test_commands,
        )
        pipeline.add_stage(prod_stage, post=[smoke_test_shell_step])
