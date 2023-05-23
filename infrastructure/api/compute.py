import pathlib
from typing import cast

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
            runtime=lambda_.Runtime(
                f"python{constants.PYTHON_VERSION}", family=lambda_.RuntimeFamily.PYTHON
            ),
            environment={"DYNAMODB_TABLE_NAME": dynamodb_table_name},
            reserved_concurrent_executions=lambda_reserved_concurrency,
            entry=str(
                pathlib.Path(__file__)
                .parent.parent.parent.joinpath("runtime/api")
                .resolve()
            ),
            index="app.py",
            handler="lambda_handler",
        )
        cfn_lambda_function = cast(
            lambda_.CfnFunction, self.lambda_function.node.default_child
        )
        code = cast(lambda_.CfnFunction.CodeProperty, cfn_lambda_function.code)
        self.lambda_function_code = f"s3://{code.s3_bucket}/{code.s3_key}"
