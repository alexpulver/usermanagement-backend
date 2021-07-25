from pathlib import Path
from typing import Any, Dict

from aws_cdk import aws_dynamodb as dynamodb
from aws_cdk import aws_iam as iam
from aws_cdk import aws_sam as sam
from aws_cdk import core as cdk
from cdk_chalice import Chalice


class API(cdk.Construct):
    def __init__(
        self,
        scope: cdk.Construct,
        id_: str,
        *,
        dynamodb_table: dynamodb.Table,
        lambda_reserved_concurrency: int,
    ):
        super().__init__(scope, id_)

        service_principal = iam.ServicePrincipal("lambda.amazonaws.com")
        # The policy is needed for writing to Amazon CloudWatch Logs
        policy = iam.ManagedPolicy.from_aws_managed_policy_name(
            "service-role/AWSLambdaBasicExecutionRole"
        )
        handler_role = iam.Role(
            self,
            "HandlerRole",
            assumed_by=service_principal,
            managed_policies=[policy],
        )

        dynamodb_table.grant_read_write_data(handler_role)

        chalice_stage_config = API._create_chalice_stage_config(
            handler_role, dynamodb_table
        )
        self.chalice = Chalice(
            self,
            "Chalice",
            source_dir=str(Path(__file__).resolve().parent.joinpath("runtime")),
            stage_config=chalice_stage_config,
        )
        rest_api: sam.CfnApi = self.chalice.sam_template.get_resource("RestAPI")
        rest_api.tracing_enabled = True
        handler_function: sam.CfnFunction = self.chalice.sam_template.get_resource(
            "APIHandler"
        )
        handler_function.reserved_concurrent_executions = lambda_reserved_concurrency

        self.endpoint_url: cdk.CfnOutput = self.chalice.sam_template.get_output(
            "EndpointURL"
        )

    @staticmethod
    def _create_chalice_stage_config(
        handler_role: iam.Role, dynamodb_table: dynamodb.Table
    ) -> Dict[str, Any]:
        chalice_stage_config = {
            "api_gateway_stage": "v1",
            "lambda_functions": {
                "api_handler": {
                    "manage_iam_role": False,
                    "iam_role_arn": handler_role.role_arn,
                    "environment_variables": {"TABLE_NAME": dynamodb_table.table_name},
                    "lambda_memory_size": 128,
                    "lambda_timeout": 10,
                }
            },
        }
        return chalice_stage_config
