from typing import Any

from aws_lambda_powertools.event_handler import api_gateway

import users

app = api_gateway.ApiGatewayResolver(
    proxy_type=api_gateway.ProxyEventType.APIGatewayProxyEventV2
)


def lambda_handler(event: dict[str, Any], context: object) -> dict[str, Any]:
    return app.resolve(event, context)


@app.post("/users")  # type: ignore
def create_user() -> dict[str, Any]:
    user_attributes = app.current_event.json_body
    return users.create_user(user_attributes)


@app.put("/users")  # type: ignore
def update_user() -> dict[str, Any]:
    user_attributes = app.current_event.json_body
    return users.update_user(user_attributes)


@app.get("/users/<username>")  # type: ignore
def get_user(username: str) -> dict[str, Any]:
    return users.get_user(username)


@app.delete("/users/<username>")  # type: ignore
def delete_user(username: str) -> dict[str, Any]:
    return users.delete_user(username)
