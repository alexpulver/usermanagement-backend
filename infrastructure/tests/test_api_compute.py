import unittest

import aws_cdk as cdk
import aws_cdk.aws_dynamodb as dynamodb
from aws_cdk import assertions

import api.compute
import api.database


class LambdaTestCase(unittest.TestCase):
    def test_bundling(self) -> None:
        stack = cdk.Stack()
        database = api.database.Database(
            stack,
            "Database",
            dynamodb_billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
        )
        api.compute.Compute(
            stack,
            "Compute",
            dynamodb_table_name=database.dynamodb_table.table_name,
            lambda_reserved_concurrency=1,
        )
        template = assertions.Template.from_stack(stack).to_json()
        resources = template["Resources"]
        lambda_function_logical_id = "ComputeLambdaFunctionB5F83B01"
        self.assertIn(lambda_function_logical_id, resources)
        lambda_function_resource = resources[lambda_function_logical_id]
        lambda_function_code = lambda_function_resource["Properties"]["Code"]
        self.assertIn("S3Bucket", lambda_function_code)
        self.assertIn("S3Key", lambda_function_code)


if __name__ == "__main__":
    unittest.main()
