import os

import aws_cdk as cdk
import aws_cdk.aws_dynamodb as dynamodb
import aws_cdk.aws_servicecatalogappregistry_alpha as appregistry_alpha

import constants
from components import Components
from metadata import Metadata
from toolchain import Toolchain


def main() -> None:
    app = cdk.App()

    # Metadata management environment stack
    appregistry_application_associator = create_metadata_management(app)

    # Components sandbox environment stack
    create_components_sandbox(app)

    # Toolchain management environment stack (continuous deployment pipeline)
    create_toolchain_management(app, appregistry_application_associator)

    app.synth()


def create_metadata_management(
    app: cdk.App,
) -> appregistry_alpha.ApplicationAssociator:
    metadata = Metadata(
        app=app,
        stack_name=constants.APP_NAME + "-Metadata-Management",
        env=cdk.Environment(
            account=constants.MANAGEMENT_ENVIRONMENT.account,
            region=constants.MANAGEMENT_ENVIRONMENT.region,
        ),
    )
    return metadata.appregistry_application_associator


def create_components_sandbox(app: cdk.App) -> Components:
    components = Components(
        app,
        constants.APP_NAME + "-Components-Sandbox",
        env=cdk.Environment(
            account=os.environ["CDK_DEFAULT_ACCOUNT"],
            region=os.environ["CDK_DEFAULT_REGION"],
        ),
        api_compute_lambda_reserved_concurrency=1,
        api_database_dynamodb_billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
    )
    return components


def create_toolchain_management(
    app: cdk.App,
    appregistry_application_associator: appregistry_alpha.ApplicationAssociator,
) -> None:
    Toolchain(
        app,
        constants.APP_NAME + "-Toolchain-Management",
        appregistry_application_associator=appregistry_application_associator,
        env=cdk.Environment(
            account=constants.MANAGEMENT_ENVIRONMENT.account,
            region=constants.MANAGEMENT_ENVIRONMENT.region,
        ),
    )


if __name__ == "__main__":
    main()
