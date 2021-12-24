from typing import Any, cast

import aws_cdk as cdk
from aws_cdk import aws_dynamodb as dynamodb
from aws_cdk import aws_iam as iam
from constructs import Construct

from api.infrastructure import Api
from database.infrastructure import Database
from monitoring.infrastructure import Monitoring


class UserManagementBackend(cdk.Stage):
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

        stateful = cdk.Stack(self, "Stateful")
        database = Database(
            stateful, "Database", dynamodb_billing_mode=database_dynamodb_billing_mode
        )
        stateless = cdk.Stack(self, "Stateless")
        api = Api(
            stateless,
            "Api",
            database_dynamodb_table_name=database.dynamodb_table.table_name,
            lambda_reserved_concurrency=api_lambda_reserved_concurrency,
        )
        database.dynamodb_table.grant_read_write_data(
            cast(iam.IGrantable, api.lambda_function.role)
        )
        self.api_endpoint = cdk.CfnOutput(
            stateless,
            "ApiEndpoint",
            # Api doesn't disable create_default_stage, hence URL will be defined
            value=api.api_gateway_http_api.url,  # type: ignore
        )
        Monitoring(stateless, "Monitoring", database=database, api=api)
