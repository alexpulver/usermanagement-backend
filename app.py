import os

import aws_cdk as cdk
import aws_cdk.aws_dynamodb as dynamodb
import aws_cdk.aws_servicecatalogappregistry_alpha as appregistry_alpha

import constants
import operations
from backend.component import Backend
from toolchain import Toolchain

APPREGISTRY_APPLICATION_ACCOUNT = "807650736403"
APPREGISTRY_APPLICATION_REGION = "eu-west-1"
TOOLCHAIN_ACCOUNT = "807650736403"
TOOLCHAIN_REGION = "eu-west-1"


def main() -> None:
    app = cdk.App()

    # AppRegistry application stack and application associator aspect
    appregistry_application_associator = create_appregistry_application_associator(app)

    # Backend sandbox stack
    backend_sandbox = create_backend_sandbox(app)
    # Operations aspects for backend sandbox stack
    cdk.Aspects.of(backend_sandbox).add(operations.Metadata())
    cdk.Aspects.of(backend_sandbox).add(operations.Monitoring())

    # Toolchain stack (continuous deployment pipeline)
    create_toolchain(app, appregistry_application_associator)

    app.synth()


def create_appregistry_application_associator(
    app: cdk.App,
) -> appregistry_alpha.ApplicationAssociator:
    appregistry_application_associator = appregistry_alpha.ApplicationAssociator(
        app,
        "AppRegistryApplicationAssociator",
        application_name=constants.APP_NAME,
        stack_props=cdk.StackProps(
            stack_name=constants.APP_NAME + "Application",
            env=cdk.Environment(
                account=APPREGISTRY_APPLICATION_ACCOUNT,
                region=APPREGISTRY_APPLICATION_REGION,
            ),
        ),
    )
    appregistry_app_stack = (
        appregistry_application_associator.app_registry_application.stack
    )
    cdk.CfnOutput(
        appregistry_app_stack,
        "AppRegistryApplicationArn",
        export_name=constants.APPREGISTRY_APPLICATION_ARN_EXPORT_NAME,
        value=appregistry_application_associator.app_registry_application.application_arn,
    )
    return appregistry_application_associator


def create_backend_sandbox(app: cdk.App) -> Backend:
    backend = Backend(
        app,
        constants.APP_NAME + "Sandbox",
        env=cdk.Environment(
            account=os.environ["CDK_DEFAULT_ACCOUNT"],
            region=os.environ["CDK_DEFAULT_REGION"],
        ),
        api_lambda_reserved_concurrency=1,
        database_dynamodb_billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
    )
    return backend


def create_toolchain(
    app: cdk.App,
    appregistry_application_associator: appregistry_alpha.ApplicationAssociator,
) -> None:
    Toolchain(
        app,
        constants.APP_NAME + "Toolchain",
        appregistry_application_associator=appregistry_application_associator,
        env=cdk.Environment(account=TOOLCHAIN_ACCOUNT, region=TOOLCHAIN_REGION),
    )


if __name__ == "__main__":
    main()
