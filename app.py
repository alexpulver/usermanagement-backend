import os

import aws_cdk as cdk
import aws_cdk.aws_servicecatalogappregistry_alpha as appregistry_alpha

import constants
from service.service_stack import ServiceStack
from toolchain.toolchain_stack import ToolchainStack


def main() -> None:
    app = cdk.App()

    application = appregistry_alpha.TargetApplication.create_application_stack(
        application_name=constants.APP_NAME,
        application_description=constants.APP_DESCRIPTION,
        stack_name=f"{constants.APP_NAME}-Application-Management",
        env=cdk.Environment(
            account=constants.APPLICATION_MANAGEMENT_ENVIRONMENT.account,
            region=constants.APPLICATION_MANAGEMENT_ENVIRONMENT.region,
        ),
    )
    application_associator = appregistry_alpha.ApplicationAssociator(
        app, "AppRegistryApplicationAssociator", applications=[application]
    )

    ServiceStack(
        app,
        f"{constants.APP_NAME}-Service-{constants.SERVICE_SANDBOX_ENVIRONMENT.name}",
        env=cdk.Environment(
            account=os.environ["CDK_DEFAULT_ACCOUNT"],
            region=os.environ["CDK_DEFAULT_REGION"],
        ),
        # pylint: disable=line-too-long
        compute_lambda_reserved_concurrency=constants.SERVICE_SANDBOX_ENVIRONMENT.compute_lambda_reserved_concurrency,
        # pylint: disable=line-too-long
        database_dynamodb_billing_mode=constants.SERVICE_SANDBOX_ENVIRONMENT.database_dynamodb_billing_mode,
    )

    ToolchainStack(
        app,
        f"{constants.APP_NAME}-Toolchain-Management",
        application_associator=application_associator,
        env=cdk.Environment(
            account=constants.TOOLCHAIN_MANAGEMENT_ENVIRONMENT.account,
            region=constants.TOOLCHAIN_MANAGEMENT_ENVIRONMENT.region,
        ),
    )

    app.synth()


if __name__ == "__main__":
    main()
