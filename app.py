import os

import aws_cdk as cdk
import aws_cdk.aws_dynamodb as dynamodb

import constants
from component import UserManagementBackend
from toolchain import UserManagementBackendToolchain

SANDBOX_ENV_NAME = "Sandbox"

app = cdk.App()

UserManagementBackend(
    app,
    constants.APP_NAME + SANDBOX_ENV_NAME,
    env=cdk.Environment(
        account=os.environ["CDK_DEFAULT_ACCOUNT"],
        region=os.environ["CDK_DEFAULT_REGION"],
    ),
    env_name=SANDBOX_ENV_NAME,
    api_lambda_reserved_concurrency=1,
    database_dynamodb_billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
)

UserManagementBackendToolchain(
    app,
    constants.APP_NAME + "Toolchain",
    env=cdk.Environment(account="807650736403", region="eu-west-1"),
)

app.synth()
