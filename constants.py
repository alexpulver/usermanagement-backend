from collections import namedtuple

import aws_cdk.aws_codebuild as codebuild
import aws_cdk.aws_dynamodb as dynamodb

APP_NAME = "UserManagementBackend"
APP_DESCRIPTION = "Ongoing project to build realistic application SDLC using AWS CDK"
PYTHON_VERSION = "3.9"

# pylint: disable=line-too-long
GITHUB_CONNECTION_ARN = "arn:aws:codestar-connections:eu-west-1:807650736403:connection/1f244295-871f-411f-afb1-e6ca987858b6"
GITHUB_OWNER = "alexpulver"
GITHUB_REPO = "usermanagement-backend"
GITHUB_TRUNK_BRANCH = "main"

CODEBUILD_BUILD_ENVIRONMENT = codebuild.BuildEnvironment(
    build_image=codebuild.LinuxBuildImage.STANDARD_5_0,
    privileged=True,
)

ApplicationEnvironment = namedtuple(
    "ApplicationEnvironment", ["name", "account", "region"]
)
APPLICATION_MANAGEMENT_ENVIRONMENT = ApplicationEnvironment(
    name="Management", account="807650736403", region="eu-west-1"
)
ToolchainEnvironment = namedtuple("ToolchainEnvironment", ["name", "account", "region"])
TOOLCHAIN_MANAGEMENT_ENVIRONMENT = ToolchainEnvironment(
    name="Management", account="807650736403", region="eu-west-1"
)
ServiceEnvironment = namedtuple(
    "ServiceEnvironment",
    [
        "name",
        "account",
        "region",
        "compute_lambda_reserved_concurrency",
        "database_dynamodb_billing_mode",
    ],
    defaults=["111111111111", "eu-west-1", 1, dynamodb.BillingMode.PAY_PER_REQUEST],
)
# The application uses caller's account and Region.
SERVICE_SANDBOX_ENVIRONMENT = ServiceEnvironment(
    name="Sandbox",
    compute_lambda_reserved_concurrency=1,
    database_dynamodb_billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
)
SERVICE_SHARED_ENVIRONMENTS = [
    ServiceEnvironment(
        name="Production",
        account="807650736403",
        region="eu-west-1",
        compute_lambda_reserved_concurrency=10,
        database_dynamodb_billing_mode=dynamodb.BillingMode.PROVISIONED,
    ),
]
