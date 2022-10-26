from typing import Any

import aws_cdk as cdk
import aws_cdk.aws_dynamodb as dynamodb
from constructs import Construct

from backend.api.infrastructure import API
from backend.database.infrastructure import Database


class Backend(cdk.Stack):
    def __init__(
        self,
        scope: Construct,
        id_: str,
        *,
        database_dynamodb_billing_mode: dynamodb.BillingMode,
        api_lambda_reserved_concurrency: int,
        **kwargs: Any,
    ):
        super().__init__(scope, id_, **kwargs)

        self.database = Database(
            self,
            "Database",
            dynamodb_billing_mode=database_dynamodb_billing_mode,
        )
        self.api = API(
            self,
            "API",
            dynamodb_table_name=self.database.dynamodb_table.table_name,
            lambda_reserved_concurrency=api_lambda_reserved_concurrency,
        )

        self.database.dynamodb_table.grant_read_write_data(self.api.lambda_function)

        self.api_endpoint_cfn_output = cdk.CfnOutput(
            self,
            "APIEndpoint",
            # API doesn't disable create_default_stage, hence URL will be defined
            value=self.api.api_gateway_http_api.url,  # type: ignore
        )