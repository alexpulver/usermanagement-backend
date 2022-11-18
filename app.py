import os

import aws_cdk as cdk
import aws_cdk.aws_dynamodb as dynamodb
import aws_cdk.aws_servicecatalogappregistry_alpha as appregistry_alpha

import constants
from backend.component import Backend
from operations import Operations
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
    create_backend_sandbox(app)
    # Toolchain stack (continuous deployment pipeline)
    create_toolchain(app, appregistry_application_associator)

    app.synth()


def create_appregistry_application_associator(
    app: cdk.App,
) -> appregistry_alpha.ApplicationAssociator:
    application = appregistry_alpha.TargetApplication.create_application_stack(
        application_name=constants.APP_NAME,
        stack_id=constants.APP_NAME + "AppRegistryApplication",
        stack_name=constants.APP_NAME + "AppRegistryApplication",
        env=cdk.Environment(
            account=APPREGISTRY_APPLICATION_ACCOUNT,
            region=APPREGISTRY_APPLICATION_REGION,
        ),
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
    cdk.Aspects.of(backend).add(Operations())
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
