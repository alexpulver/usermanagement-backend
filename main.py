import os

import aws_cdk as cdk

import constants
from service.service_stack import ServiceStack
from toolchain.toolchain_stack import ToolchainStack


def main() -> None:
    app = cdk.App()

    ServiceStack(
        app,
        f"{constants.SERVICE_STACK_BASE_NAME}-{constants.SERVICE_SANDBOX_ENVIRONMENT.name}",
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
        f"{constants.TOOLCHAIN_STACK_BASE_NAME}-{constants.TOOLCHAIN_PRODUCTION_ENVIRONMENT.name}",
        env=cdk.Environment(
            account=constants.TOOLCHAIN_PRODUCTION_ENVIRONMENT.account,
            region=constants.TOOLCHAIN_PRODUCTION_ENVIRONMENT.region,
        ),
    )

    app.synth()


if __name__ == "__main__":
    main()
