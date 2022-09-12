from typing import Any

import aws_cdk as cdk
import aws_cdk.aws_dynamodb as dynamodb
from constructs import Construct

import constants
from api.infrastructure import API
from database.infrastructure import Database
from monitoring.infrastructure import Monitoring


class UserManagementBackend(cdk.Stage):
    def __init__(
        self,
        scope: Construct,
        id_: str,
        *,
        env_name: str,
        database_dynamodb_billing_mode: dynamodb.BillingMode,
        api_lambda_reserved_concurrency: int,
        **kwargs: Any,
    ):
        super().__init__(scope, id_, **kwargs)

        usermanagement_backend = cdk.Stack(
            self,
            constants.APP_NAME,
            stack_name=constants.APP_NAME + env_name,
        )
        database = Database(
            usermanagement_backend,
            "Database",
            dynamodb_billing_mode=database_dynamodb_billing_mode,
        )
        api = API(
            usermanagement_backend,
            "API",
            database_dynamodb_table_name=database.dynamodb_table.table_name,
            lambda_reserved_concurrency=api_lambda_reserved_concurrency,
        )
        database.dynamodb_table.grant_read_write_data(api.lambda_function)
        self.api_endpoint = cdk.CfnOutput(
            usermanagement_backend,
            "APIEndpoint",
            # API doesn't disable create_default_stage, hence URL will be defined
            value=api.api_gateway_http_api.url,  # type: ignore
        )
        Monitoring(usermanagement_backend, "Monitoring", database=database, api=api)
