from aws_cdk import (
    aws_dynamodb as dynamodb,
    core as cdk
)

from api.infrastructure import Api
from database.infrastructure import Database
from monitoring.infrastructure import Monitoring


class Deployment(cdk.Stage):

    def __init__(self, scope: cdk.Construct, id: str, billing_mode: dynamodb.BillingMode, **kwargs):
        super().__init__(scope, id, **kwargs)

        application = cdk.Stack(self, 'Application')
        database = Database(application, 'Database', billing_mode)
        api = Api(application, 'Api', database)
        Monitoring(application, 'Monitoring', database, api)
