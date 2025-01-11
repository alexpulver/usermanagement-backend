import os

import repository


def init_users_repository() -> repository.UsersRepository:
    dynamodb_repository = repository.DynamoDBDatabase(os.environ["DYNAMODB_TABLE_NAME"])
    users_repository = repository.UsersRepository(database=dynamodb_repository)
    return users_repository
