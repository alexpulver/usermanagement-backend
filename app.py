import os

import aws_cdk as cdk
import aws_cdk.aws_dynamodb as dynamodb
import aws_cdk.aws_servicecatalogappregistry_alpha as appregistry_alpha

import constants
from backend.component import Backend
from toolchain import Toolchain

app = cdk.App()

appregistry_app_associator = appregistry_alpha.ApplicationAssociator(
    app,
    "AppRegistryApplicationAssociator",
    application_name=constants.APP_NAME,
    stack_props=cdk.StackProps(
        stack_name=constants.APP_NAME + "Application",
        env=cdk.Environment(account="807650736403", region="eu-west-1"),
    ),
)

# Component sandbox stack
Backend(
    app,
    constants.APP_NAME + "Sandbox",
    env=cdk.Environment(
        account=os.environ["CDK_DEFAULT_ACCOUNT"],
        region=os.environ["CDK_DEFAULT_REGION"],
    ),
    api_lambda_reserved_concurrency=1,
    database_dynamodb_billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
)

# Toolchain stack (defines the continuous deployment pipeline)
Toolchain(
    app,
    constants.APP_NAME + "Toolchain",
    appregistry_app_associator=appregistry_app_associator,
    env=cdk.Environment(account="807650736403", region="eu-west-1"),
)

app.synth()
