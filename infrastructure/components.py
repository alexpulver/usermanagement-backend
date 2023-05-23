from typing import Any

import aws_cdk as cdk
import aws_cdk.aws_dynamodb as dynamodb
from constructs import Construct

import api.compute as api_compute
import api.database as api_database
import api.metadata as api_metadata
import api.monitoring as api_monitoring
import api.network as api_network


class Components(cdk.Stack):
    def __init__(
        self,
        scope: Construct,
        id_: str,
        *,
        api_compute_lambda_reserved_concurrency: int,
        api_database_dynamodb_billing_mode: dynamodb.BillingMode,
        **kwargs: Any
    ):
        super().__init__(scope, id_, **kwargs)

        api = API(
            self,
            "API",
            api_compute_lambda_reserved_concurrency,
            api_database_dynamodb_billing_mode,
        )

        self.api_endpoint = cdk.CfnOutput(
            self,
            "APIEndpoint",
            # API Gateway doesn't disable create_default_stage, hence URL is defined
            value=api.endpoint,  # type: ignore
        )


class API(Construct):
    def __init__(
        self,
        scope: Construct,
        id_: str,
        compute_lambda_reserved_concurrency: int,
        database_dynamodb_billing_mode: dynamodb.BillingMode,
    ):
        super().__init__(scope, id_)

        database = api_database.Database(
            self,
            "Database",
            dynamodb_billing_mode=database_dynamodb_billing_mode,
        )
        compute = api_compute.Compute(
            self,
            "Compute",
            lambda_reserved_concurrency=compute_lambda_reserved_concurrency,
            dynamodb_table_name=database.dynamodb_table.table_name,
        )
        network = api_network.Network(
            self, "Network", lambda_function=compute.lambda_function
        )
        api_metadata.Metadata(self, "Metadata", compute=compute, network=network)
        api_monitoring.Monitoring(
            self, "Monitoring", database=database, network=network
        )

        database.dynamodb_table.grant_read_write_data(compute.lambda_function)

        self.endpoint = network.api_gateway_http_api.url
