import aws_cdk as cdk

import constants
from deployment import UserManagementBackend
from toolchain import Toolchain

app = cdk.App()

# Development stage
UserManagementBackend(
    app,
    f"{constants.APP_NAME}-Dev",
    env=constants.DEV_ENV,
    api_lambda_reserved_concurrency=constants.DEV_API_LAMBDA_RESERVED_CONCURRENCY,
    database_dynamodb_billing_mode=constants.DEV_DATABASE_DYNAMODB_BILLING_MODE,
)

# Continuous deployment and pull request validation
Toolchain(
    app,
    f"{constants.APP_NAME}-Toolchain",
    env=constants.TOOLCHAIN_ENV,
)

app.synth()
