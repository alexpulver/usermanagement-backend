import aws_cdk.aws_apigatewayv2_alpha as apigatewayv2_alpha
import aws_cdk.aws_apigatewayv2_integrations_alpha as apigatewayv2_integrations_alpha
import aws_cdk.aws_lambda_python_alpha as lambda_python_alpha
from constructs import Construct


class Ingress(Construct):
    def __init__(
        self,
        scope: Construct,
        id_: str,
        *,
        lambda_function: lambda_python_alpha.PythonFunction,
    ):
        super().__init__(scope, id_)

        api_gateway_http_lambda_integration = (
            apigatewayv2_integrations_alpha.HttpLambdaIntegration(
                "APIGatewayIntegration", handler=lambda_function
            )
        )
        self.api_gateway_http_api = apigatewayv2_alpha.HttpApi(
            self,
            "APIGatewayHTTPAPI",
            default_integration=api_gateway_http_lambda_integration,
        )
