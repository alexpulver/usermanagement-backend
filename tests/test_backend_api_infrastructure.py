import unittest

import aws_cdk as cdk
import aws_cdk.aws_dynamodb as dynamodb
from aws_cdk import assertions

from backend.api.infrastructure import API
from backend.database.infrastructure import Database


class APITestCase(unittest.TestCase):
    def test_lambda_function_bundling(self) -> None:
        stack = cdk.Stack()
        database = Database(
            stack,
            "Database",
            dynamodb_billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
        )
        API(
            stack,
            "API",
            dynamodb_table_name=database.dynamodb_table.table_name,
            lambda_reserved_concurrency=1,
        )
        template = assertions.Template.from_stack(stack).to_json()
        lambda_function_code_property = template["Resources"][
            "APILambdaFunction0BD6F5C6"
        ]["Properties"]["Code"]
        self.assertIn("S3Bucket", lambda_function_code_property)
        self.assertIn("S3Key", lambda_function_code_property)


if __name__ == "__main__":
    unittest.main()
