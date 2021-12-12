import pathlib

from aws_cdk import aws_apigatewayv2_alpha as apigatewayv2_alpha
from aws_cdk import (
    aws_apigatewayv2_integrations_alpha as apigatewayv2_integrations_alpha,
)
from aws_cdk import aws_lambda as lambda_
from aws_cdk import aws_lambda_python_alpha as lambda_python_alpha
from constructs import Construct


class Api(Construct):
    def __init__(
        self,
        scope: Construct,
        id_: str,
        *,
        database_dynamodb_table_name: str,
        lambda_reserved_concurrency: int,
    ):
        super().__init__(scope, id_)

        self.lambda_function = lambda_python_alpha.PythonFunction(
            self,
            "LambdaFunction",
            runtime=lambda_.Runtime.PYTHON_3_7,
            environment={"DATABASE_DYNAMODB_TABLE_NAME": database_dynamodb_table_name},
            reserved_concurrent_executions=lambda_reserved_concurrency,
            entry=str(pathlib.Path(__file__).parent.joinpath("runtime").resolve()),
            index="lambda_function.py",
            handler="lambda_handler",
            profiling=True,
        )

        lambda_integration = apigatewayv2_integrations_alpha.HttpLambdaIntegration(
            "ApiGatewayHttpLambdaIntegration", handler=self.lambda_function
        )
        self.api_gateway_http_api = apigatewayv2_alpha.HttpApi(
            self, "ApiGatewayHttpApi", default_integration=lambda_integration
        )
