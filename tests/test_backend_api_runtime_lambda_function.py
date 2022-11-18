import json
import unittest
from unittest import mock

import lambda_function


class AppTestCase(unittest.TestCase):
    @mock.patch.dict("helpers.os.environ", {"DYNAMODB_TABLE_NAME": "AppTestCase"})
    @mock.patch("users.DynamoDBDatabase.get_user")
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
        response = lambda_function.lambda_handler(apigatewayv2_proxy_event, None)
        self.assertEqual(json.loads(response["body"]), user)


if __name__ == "__main__":
    unittest.main()
