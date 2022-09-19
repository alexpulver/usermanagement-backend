import os

import users


def init_users_repository() -> users.UsersRepository:
    dynamodb_database = users.DynamoDBDatabase(os.environ["DYNAMODB_TABLE_NAME"])
    users_repository = users.UsersRepository(database=dynamodb_database)
    return users_repository
