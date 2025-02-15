import json
import pathlib

import aws_cdk as cdk
import aws_cdk.aws_codebuild as codebuild
from aws_cdk import pipelines
from constructs import Construct

import constants
from service.service_stack import ServiceStack


class DeploymentPipeline(Construct):
    def __init__(
        self,
        scope: Construct,
        id_: str,
        *,
        build_spec: codebuild.BuildSpec,
    ):
        super().__init__(scope, id_)

        source = pipelines.CodePipelineSource.connection(
            constants.GITHUB_OWNER + "/" + constants.GITHUB_REPO,
            constants.GITHUB_TRUNK_BRANCH,
            connection_arn=constants.GITHUB_CONNECTION_ARN,
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
            code_build_defaults=pipelines.CodeBuildOptions(
                build_environment=constants.CODEBUILD_BUILD_ENVIRONMENT,
            ),
            cli_version=DeploymentPipeline._get_cdk_cli_version(),
            cross_account_keys=True,
            publish_assets_in_parallel=False,
            synth=synth,
        )
        DeploymentPipeline._add_production_stage(pipeline)

    @staticmethod
    def _get_cdk_cli_version() -> str:
        package_json_path = (
            pathlib.Path(__file__).parent.parent.joinpath("package.json").resolve()
        )
        with open(package_json_path, encoding="utf_8") as package_json_file:
            package_json = json.load(package_json_file)
        cdk_cli_version = str(package_json["devDependencies"]["aws-cdk"])
        return cdk_cli_version

    @staticmethod
    def _add_production_stage(pipeline: pipelines.CodePipeline) -> None:
        production_environment = constants.SERVICE_PRODUCTION_ENVIRONMENT
        stage = cdk.Stage(
            pipeline,
            production_environment.name,
            env=cdk.Environment(
                account=production_environment.account,
                region=production_environment.region,
            ),
        )
        service_stack = DeploymentPipeline._create_service_stack(
            stage, production_environment
        )
        smoke_test = DeploymentPipeline._create_smoke_test(service_stack)
        pipeline.add_stage(stage, post=[smoke_test])

    @staticmethod
    def _create_service_stack(
        stage: cdk.Stage, service_environment: constants.ServiceEnvironment
    ) -> ServiceStack:
        service_stack = ServiceStack(
            stage,
            f"{constants.SERVICE_STACK_BASE_NAME}-{service_environment.name}",
            stack_name=f"{constants.SERVICE_STACK_BASE_NAME}-{service_environment.name}",
            # pylint: disable=line-too-long
            compute_lambda_reserved_concurrency=service_environment.compute_lambda_reserved_concurrency,
            database_dynamodb_billing_mode=service_environment.database_dynamodb_billing_mode,
        )
        return service_stack

    @staticmethod
    def _create_smoke_test(service_stack: ServiceStack) -> pipelines.ShellStep:
        api_endpoint_env_var_name = constants.APP_NAME.upper() + "_API_ENDPOINT"
        smoke_test_commands = [f"curl ${api_endpoint_env_var_name}"]
        smoke_test = pipelines.ShellStep(
            "SmokeTest",
            env_from_cfn_outputs={
                api_endpoint_env_var_name: service_stack.api_endpoint
            },
            commands=smoke_test_commands,
        )
        return smoke_test
