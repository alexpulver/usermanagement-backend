from typing import Any

import aws_cdk as cdk
import aws_cdk.aws_dynamodb as dynamodb
from constructs import Construct

from service.compute import Compute
from service.database import Database
from service.ingress import Ingress
from service.metadata import Metadata
from service.monitoring import Monitoring


class ServiceStack(cdk.Stack):
    def __init__(
        self,
        scope: Construct,
        id_: str,
        *,
        compute_lambda_reserved_concurrency: int,
        database_dynamodb_billing_mode: dynamodb.BillingMode,
        **kwargs: Any
    ):
        super().__init__(scope, id_, **kwargs)

        database = Database(
            self,
            "Database",
            dynamodb_billing_mode=database_dynamodb_billing_mode,
        )
        compute = Compute(
            self,
            "Compute",
            lambda_reserved_concurrency=compute_lambda_reserved_concurrency,
            dynamodb_table_name=database.dynamodb_table.table_name,
        )
        ingress = Ingress(self, "Ingress", lambda_function=compute.lambda_function)
        Metadata(self, "Metadata", compute=compute, network=ingress)
        Monitoring(self, "Monitoring", database=database, network=ingress)

        database.dynamodb_table.grant_read_write_data(compute.lambda_function)

        self.api_endpoint = cdk.CfnOutput(
            self,
            "APIEndpoint",
            # API Gateway doesn't disable create_default_stage, hence URL is defined
            value=ingress.api_gateway_http_api.url,  # type: ignore
        )
