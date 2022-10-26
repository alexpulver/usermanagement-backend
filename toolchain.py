import json
import pathlib
from collections import namedtuple
from typing import Any

import aws_cdk as cdk
import aws_cdk.aws_codebuild as codebuild
import aws_cdk.aws_dynamodb as dynamodb
import aws_cdk.aws_servicecatalogappregistry_alpha as appregistry_alpha
from aws_cdk import pipelines
from constructs import Construct

import constants
import operations
from backend.component import Backend

Environment = namedtuple("Environment", ["name", "account", "region"])

# pylint: disable=line-too-long
GITHUB_CONNECTION_ARN = "arn:aws:codestar-connections:eu-west-1:807650736403:connection/1f244295-871f-411f-afb1-e6ca987858b6"
GITHUB_OWNER = "alexpulver"
GITHUB_REPO = "usermanagement-backend"
GITHUB_TRUNK_BRANCH = "main"
ENVIRONMENTS = [
    Environment(name="Production", account="807650736403", region="eu-west-1"),
]


class Toolchain(cdk.Stack):
    def __init__(
        self,
        scope: Construct,
        id_: str,
        *,
        appregistry_application_associator: appregistry_alpha.ApplicationAssociator,
        **kwargs: Any,
    ):
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
        ContinuousDeployment(
            self,
            "ContinuousDeployment",
            appregistry_application_associator=appregistry_application_associator,
            build_spec=build_spec,
        )
        PullRequestValidation(self, "PullRequestValidation", build_spec=build_spec)


class ContinuousDeployment(Construct):
    def __init__(
        self,
        scope: Construct,
        id_: str,
        *,
        appregistry_application_associator: appregistry_alpha.ApplicationAssociator,
        build_spec: codebuild.BuildSpec,
    ):
        super().__init__(scope, id_)

        source = pipelines.CodePipelineSource.connection(
            GITHUB_OWNER + "/" + GITHUB_REPO,
            GITHUB_TRUNK_BRANCH,
            connection_arn=GITHUB_CONNECTION_ARN,
        )
        synth = pipelines.CodeBuildStep(
            "Synth",
            input=source,
            partial_build_spec=build_spec,
            # The build_spec argument includes build and synth commands.
            commands=[],
            primary_output_directory="cdk.out",
        )
        pipeline = pipelines.CodePipeline(
            self,
            "Pipeline",
            cli_version=ContinuousDeployment._get_cdk_cli_version(),
            cross_account_keys=True,
            docker_enabled_for_synth=True,
            publish_assets_in_parallel=False,
            synth=synth,
        )
        ContinuousDeployment._add_stages(pipeline, appregistry_application_associator)

    @staticmethod
    def _get_cdk_cli_version() -> str:
        package_json_path = (
            pathlib.Path(__file__).parent.joinpath("package.json").resolve()
        )
        with open(package_json_path, encoding="utf_8") as package_json_file:
            package_json = json.load(package_json_file)
        cdk_cli_version = str(package_json["devDependencies"]["aws-cdk"])
        return cdk_cli_version

    @staticmethod
    def _add_stages(
        pipeline: pipelines.CodePipeline,
        appregistry_application_associator: appregistry_alpha.ApplicationAssociator,
    ) -> None:
        for environment in ENVIRONMENTS:
            stage = cdk.Stage(
                pipeline,
                environment.name,
                env=cdk.Environment(
                    account=environment.account, region=environment.region
                ),
            )
            appregistry_application_associator.associate_stage(stage)

            # Backend production stack
            backend = ContinuousDeployment._create_backend(stage)
            # Operations aspects for backend production stack
            cdk.Aspects.of(backend).add(operations.Metadata())
            cdk.Aspects.of(backend).add(operations.Monitoring())

            # Backend production smoke test
            smoke_test = ContinuousDeployment._create_smoke_test(backend)

            pipeline.add_stage(stage, post=[smoke_test])

    @staticmethod
    def _create_backend(stage: cdk.Stage) -> Backend:
        backend = Backend(
            stage,
            constants.APP_NAME + stage.stage_name,
            stack_name=constants.APP_NAME + stage.stage_name,
            api_lambda_reserved_concurrency=10,
            database_dynamodb_billing_mode=dynamodb.BillingMode.PROVISIONED,
        )
        return backend

    @staticmethod
    def _create_smoke_test(backend: Backend) -> pipelines.ShellStep:
        api_endpoint_env_var_name = constants.APP_NAME.upper() + "_API_ENDPOINT"
        smoke_test_commands = [f"curl ${api_endpoint_env_var_name}"]
        smoke_test = pipelines.ShellStep(
            "SmokeTest",
            env_from_cfn_outputs={
                api_endpoint_env_var_name: backend.api_endpoint_cfn_output
            },
            commands=smoke_test_commands,
        )
        return smoke_test


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
