import pathlib
from typing import cast

import aws_cdk.aws_iam as iam
import aws_cdk.aws_lambda as lambda_
import aws_cdk.aws_lambda_python_alpha as lambda_python_alpha
from constructs import Construct

import constants


class Compute(Construct):
    def __init__(
        self,
        scope: Construct,
        id_: str,
        *,
        lambda_reserved_concurrency: int,
        dynamodb_table_name: str,
    ):
        super().__init__(scope, id_)

        self.lambda_function = lambda_python_alpha.PythonFunction(
            self,
            "LambdaFunction",
            entry=str(pathlib.Path(__file__).parent.joinpath("app").resolve()),
            environment={"DYNAMODB_TABLE_NAME": dynamodb_table_name},
            handler="lambda_handler",
            index="main.py",
            reserved_concurrent_executions=lambda_reserved_concurrency,
            runtime=lambda_.Runtime(
                f"python{constants.PYTHON_VERSION}", family=lambda_.RuntimeFamily.PYTHON
            ),
            tracing=lambda_.Tracing.ACTIVE,
        )
        # PythonFunction creates the IAM role automatically.
        lambda_function_role = cast(iam.Role, self.lambda_function.role)
        lambda_function_role.add_managed_policy(
            iam.ManagedPolicy.from_aws_managed_policy_name("AWSXRayDaemonWriteAccess")
        )
