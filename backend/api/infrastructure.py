import pathlib
from typing import cast

import aws_cdk.aws_apigatewayv2_alpha as apigatewayv2_alpha
import aws_cdk.aws_apigatewayv2_integrations_alpha as apigatewayv2_integrations_alpha
import aws_cdk.aws_lambda as lambda_
import aws_cdk.aws_lambda_python_alpha as lambda_python_alpha
from constructs import Construct


class API(Construct):
    def __init__(
        self,
        scope: Construct,
        id_: str,
        *,
        dynamodb_table_name: str,
        lambda_reserved_concurrency: int,
    ):
        super().__init__(scope, id_)

        self.lambda_function = lambda_python_alpha.PythonFunction(
            self,
            "LambdaFunction",
            runtime=lambda_.Runtime.PYTHON_3_7,
            environment={"DYNAMODB_TABLE_NAME": dynamodb_table_name},
            reserved_concurrent_executions=lambda_reserved_concurrency,
            entry=str(pathlib.Path(__file__).parent.joinpath("runtime").resolve()),
            index="lambda_function.py",
            handler="lambda_handler",
            profiling=True,
        )
        cfn_lambda_function = cast(
            lambda_.CfnFunction, self.lambda_function.node.default_child
        )
        code = cast(lambda_.CfnFunction.CodeProperty, cfn_lambda_function.code)
        self.lambda_function_asset = f"s3://{code.s3_bucket}/{code.s3_key}"

        api_gateway_http_lambda_integration = (
            apigatewayv2_integrations_alpha.HttpLambdaIntegration(
                "APIGatewayHTTPLambdaIntegration", handler=self.lambda_function
            )
        )
        self.api_gateway_http_api = apigatewayv2_alpha.HttpApi(
            self,
            "APIGatewayHTTPAPI",
            default_integration=api_gateway_http_lambda_integration,
        )
