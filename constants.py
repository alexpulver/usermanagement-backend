import os

import aws_cdk as cdk
import aws_cdk.aws_dynamodb as dynamodb

APP_NAME = "UserManagementBackend"
APP_PYTHON_VERSION = "3.7"

# pylint: disable=line-too-long
GITHUB_CONNECTION_ARN = "arn:aws:codestar-connections:eu-west-1:807650736403:connection/1f244295-871f-411f-afb1-e6ca987858b6"
GITHUB_OWNER = "alexpulver"
GITHUB_REPO = "usermanagement-backend"
GITHUB_TRUNK_BRANCH = "main"

TOOLCHAIN_ENV = cdk.Environment(account="807650736403", region="eu-west-1")

DEV_ENV = cdk.Environment(
    account=os.environ["CDK_DEFAULT_ACCOUNT"], region=os.environ["CDK_DEFAULT_REGION"]
)
DEV_API_LAMBDA_RESERVED_CONCURRENCY = 1
DEV_DATABASE_DYNAMODB_BILLING_MODE = dynamodb.BillingMode.PAY_PER_REQUEST

PROD_ENV = cdk.Environment(account="807650736403", region="eu-west-1")
PROD_API_LAMBDA_RESERVED_CONCURRENCY = 10
PROD_DATABASE_DYNAMODB_BILLING_MODE = dynamodb.BillingMode.PROVISIONED
