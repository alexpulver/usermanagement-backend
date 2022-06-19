import aws_cdk as cdk
import aws_cdk.aws_dynamodb as dynamodb
from constructs import Construct


class Database(Construct):
    def __init__(
        self, scope: Construct, id_: str, *, dynamodb_billing_mode: dynamodb.BillingMode
    ):
        super().__init__(scope, id_)

        partition_key = dynamodb.Attribute(
            name="username", type=dynamodb.AttributeType.STRING
        )
        self.dynamodb_table = dynamodb.Table(
            self,
            "DynamoDBTable",
            billing_mode=dynamodb_billing_mode,
            partition_key=partition_key,
            removal_policy=cdk.RemovalPolicy.DESTROY,
        )
