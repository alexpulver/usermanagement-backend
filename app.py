import os

import aws_cdk as cdk
import aws_cdk.aws_dynamodb as dynamodb
import aws_cdk.aws_servicecatalogappregistry_alpha as appregistry_alpha

import constants
from backend.component import Backend
from toolchain import Toolchain

APPREGISTRY_APPLICATION_ENVIRONMENT = cdk.Environment(
    account="807650736403", region="eu-west-1"
)
TOOLCHAIN_ENVIRONMENT = cdk.Environment(account="807650736403", region="eu-west-1")


def main() -> None:
    app = cdk.App()

    # AppRegistry application stack and application associator aspect
    appregistry_application_associator = create_appregistry_application_associator(app)
    # Backend sandbox stack
    create_backend_sandbox(app)
    # Toolchain stack (continuous deployment pipeline)
    create_toolchain(app, appregistry_application_associator)

    app.synth()


def create_appregistry_application_associator(
    app: cdk.App,
) -> appregistry_alpha.ApplicationAssociator:
    application = appregistry_alpha.TargetApplication.create_application_stack(
        application_name=constants.APP_NAME,
        application_description=constants.APP_DESCRIPTION,
        stack_id=constants.APP_NAME + "Application",
        stack_name=constants.APP_NAME + "Application",
        env=APPREGISTRY_APPLICATION_ENVIRONMENT,
    )
    appregistry_application_associator = appregistry_alpha.ApplicationAssociator(
        app, "AppRegistryApplicationAssociator", applications=[application]
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
        env=TOOLCHAIN_ENVIRONMENT,
    )


if __name__ == "__main__":
    main()
