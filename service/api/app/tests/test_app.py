import json
import unittest
from typing import cast
from unittest import mock

from aws_lambda_powertools.utilities.typing.lambda_context import LambdaContext

import main


class CRUDTestCase(unittest.TestCase):
    @mock.patch.dict("helpers.os.environ", {"DYNAMODB_TABLE_NAME": "Table"})
    @mock.patch("repository.DynamoDBDatabase.get_user")
    def test_get_user_exists(self, mock_get_user: mock.Mock) -> None:
        username = "john"
        user = {"username": username, "email": f"{username}@example.com"}
        mock_get_user.return_value = user
        apigatewayv2_proxy_event = {
            "rawPath": f"/users/{username}",
            "requestContext": {
                "http": {
                    "method": "GET",
                    "path": f"/users/{username}",
                },
                "stage": "$default",
            },
        }
        response = main.lambda_handler(
            apigatewayv2_proxy_event, cast(LambdaContext, {})
        )
        self.assertEqual(json.loads(response["body"]), user)


if __name__ == "__main__":
    unittest.main()
