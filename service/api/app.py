from typing import Any, Optional

from aws_lambda_powertools.event_handler import api_gateway

from helpers import init_users_repository

app = api_gateway.ApiGatewayResolver(
    proxy_type=api_gateway.ProxyEventType.APIGatewayProxyEventV2
)


def lambda_handler(event: dict[str, Any], context: object) -> dict[str, Any]:
    return app.resolve(event, context)


@app.post("/users")  # type: ignore
def create_user() -> dict[str, Any]:
    user_attributes = app.current_event.json_body
    users_repository = init_users_repository()
    return users_repository.create_user(user_attributes["username"], user_attributes)


@app.put("/users")  # type: ignore
def update_user() -> dict[str, Any]:
    user_attributes = app.current_event.json_body
    username = user_attributes["username"]
    del user_attributes["username"]
    users_repository = init_users_repository()
    return users_repository.update_user(username, user_attributes)


@app.get("/users/<username>")  # type: ignore
def get_user(username: str) -> Optional[dict[str, Any]]:
    users_repository = init_users_repository()
    return users_repository.get_user(username)


@app.delete("/users/<username>")  # type: ignore
def delete_user(username: str) -> dict[str, Any]:
    users_repository = init_users_repository()
    users_repository.delete_user(username)
    return {"username": username}
