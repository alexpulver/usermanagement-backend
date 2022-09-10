from typing import Any

import aws_cdk as cdk
import aws_cdk.aws_dynamodb as dynamodb
from constructs import Construct

from api.infrastructure import API
from database.infrastructure import Database
from monitoring.infrastructure import Monitoring


class Component(cdk.Stage):
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

        component = cdk.Stack(self, "Component")
        database = Database(
            component, "Database", dynamodb_billing_mode=database_dynamodb_billing_mode
        )
        api = API(
            component,
            "API",
            database_dynamodb_table_name=database.dynamodb_table.table_name,
            lambda_reserved_concurrency=api_lambda_reserved_concurrency,
        )
        database.dynamodb_table.grant_read_write_data(api.lambda_function)
        self.api_endpoint = cdk.CfnOutput(
            component,
            "APIEndpoint",
            # Api doesn't disable create_default_stage, hence URL will be defined
            value=api.api_gateway_http_api.url,  # type: ignore
        )
        Monitoring(component, "Monitoring", database=database, api=api)
