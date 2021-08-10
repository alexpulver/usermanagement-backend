import json
import pathlib
import tempfile
import unittest

from aws_cdk import aws_dynamodb as dynamodb
from aws_cdk import core as cdk

from api.infrastructure import API
from database.infrastructure import Database


class APITestCase(unittest.TestCase):
    def test_endpoint_url_output_exists(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            app = cdk.App(outdir=temp_dir)
            stack = cdk.Stack(app, "Stack")
            database = Database(
                stack,
                "Database",
                dynamodb_billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
            )
            API(
                stack,
                "API",
                dynamodb_table=database.table,
                lambda_reserved_concurrency=1,
            )
            cloud_assembly = app.synth()
            template = cloud_assembly.get_stack_by_name(stack.stack_name).template
        self.assertEqual(
            template["Outputs"]["EndpointURL"]["Value"]["Fn::Sub"],
            "https://${RestAPI}.execute-api.${AWS::Region}.${AWS::URLSuffix}/v1/",
        )
        self.cleanup_chalice_config_file(f"{stack.stack_name}/API")

    @staticmethod
    def cleanup_chalice_config_file(stage_name: str) -> None:
        chalice_config_path = (
            pathlib.Path(__file__)
            .resolve()
            .parent.parent.joinpath("api/runtime/.chalice/config.json")
        )
        with pathlib.Path.open(chalice_config_path, "r+") as chalice_config_file:
            chalice_config = json.load(chalice_config_file)
            try:
                del chalice_config["stages"][stage_name]
            except KeyError:
                return
            else:
                chalice_config_file.seek(0)
                chalice_config_file.truncate()
                json.dump(chalice_config, chalice_config_file, indent=2)


if __name__ == "__main__":
    unittest.main()
