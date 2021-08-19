import pathlib

from aws_cdk import aws_apigatewayv2 as apigatewayv2
from aws_cdk import aws_apigatewayv2_integrations as apigatewayv2_integrations
from aws_cdk import aws_lambda as lambda_
from aws_cdk import aws_lambda_python as lambda_python
from aws_cdk import core as cdk


class API(cdk.Construct):
    def __init__(
        self,
        scope: cdk.Construct,
        id_: str,
        *,
        database_dynamodb_table_name: str,
        lambda_reserved_concurrency: int,
    ):
        super().__init__(scope, id_)

        self.lambda_function = lambda_python.PythonFunction(
            self,
            "LambdaFunction",
            runtime=lambda_.Runtime.PYTHON_3_7,
            environment={"DATABASE_DYNAMODB_TABLE_NAME": database_dynamodb_table_name},
            reserved_concurrent_executions=lambda_reserved_concurrency,
            entry=str(pathlib.Path(__file__).resolve().parent.joinpath("runtime")),
            index="lambda_function.py",
            handler="lambda_handler",
            profiling=True,
        )

        lambda_integration = apigatewayv2_integrations.LambdaProxyIntegration(
            handler=self.lambda_function
        )
        self.http_api = apigatewayv2.HttpApi(
            self, "HttpApi", default_integration=lambda_integration
        )
