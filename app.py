import os

import aws_cdk as cdk
import aws_cdk.aws_dynamodb as dynamodb

import constants
from component import Component
from toolchain import Toolchain

app = cdk.App()

# Component sandbox
Component(
    app,
    f"{constants.APP_NAME}Sandbox",
    env=cdk.Environment(
        account=os.environ["CDK_DEFAULT_ACCOUNT"],
        region=os.environ["CDK_DEFAULT_REGION"],
    ),
    api_lambda_reserved_concurrency=1,
    database_dynamodb_billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
)

# Continuous deployment and pull request validation
Toolchain(
    app,
    f"{constants.APP_NAME}Toolchain",
    env=cdk.Environment(account="807650736403", region="eu-west-1"),
)

app.synth()
