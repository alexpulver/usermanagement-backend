from dataclasses import dataclass

import aws_cdk.aws_codebuild as codebuild
import aws_cdk.aws_dynamodb as dynamodb


# Use `kw_only=True` to support inheritance with default values.
# See https://stackoverflow.com/a/69822584/1658138 for details.
@dataclass(kw_only=True)
class Environment:
    name: str
    account: str | None = None
    region: str | None = None


@dataclass(kw_only=True)
class ServiceEnvironment(Environment):
    compute_lambda_reserved_concurrency: int
    database_dynamodb_billing_mode: dynamodb.BillingMode


APP_NAME = "UserManagementBackend"
APP_DESCRIPTION = "Ongoing project to build realistic application SDLC using AWS CDK"
PYTHON_VERSION = "3.11"

# pylint: disable=line-too-long
GITHUB_CONNECTION_ARN = "arn:aws:codestar-connections:eu-west-1:807650736403:connection/1f244295-871f-411f-afb1-e6ca987858b6"
GITHUB_OWNER = "alexpulver"
GITHUB_REPO = "usermanagement-backend"
GITHUB_TRUNK_BRANCH = "main"

CODEBUILD_BUILD_ENVIRONMENT = codebuild.BuildEnvironment(
    build_image=codebuild.LinuxBuildImage.AMAZON_LINUX_2_5,
    privileged=True,
)

TOOLCHAIN_STACK_BASE_NAME = f"{APP_NAME}-Toolchain"
TOOLCHAIN_PRODUCTION_ENVIRONMENT = Environment(
    name="Production", account="807650736403", region="eu-west-1"
)
SERVICE_STACK_BASE_NAME = f"{APP_NAME}-Service"
# The application uses caller's account and Region for the sandbox environment.
SERVICE_SANDBOX_ENVIRONMENT = ServiceEnvironment(
    name="Sandbox",
    compute_lambda_reserved_concurrency=1,
    database_dynamodb_billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
)
SERVICE_PRODUCTION_ENVIRONMENT = ServiceEnvironment(
    name="Production",
    account="807650736403",
    region="eu-west-1",
    compute_lambda_reserved_concurrency=10,
    database_dynamodb_billing_mode=dynamodb.BillingMode.PROVISIONED,
)
