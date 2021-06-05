from aws_cdk import (
    aws_dynamodb as dynamodb,
    core as cdk
)


class Database(cdk.Construct):

    def __init__(
            self, scope: cdk.Construct, id: str, dynamodb_billing_mode: dynamodb.BillingMode, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        partition_key = dynamodb.Attribute(name='username', type=dynamodb.AttributeType.STRING)
        self.table = dynamodb.Table(
            self, 'Table', billing_mode=dynamodb_billing_mode, partition_key=partition_key,
            removal_policy=cdk.RemovalPolicy.DESTROY)
