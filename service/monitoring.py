import aws_cdk.aws_cloudwatch as cloudwatch
from constructs import Construct

from service.database import Database
from service.ingress import Ingress


class Monitoring(Construct):
    def __init__(
        self,
        scope: Construct,
        id_: str,
        *,
        database: Database,
        network: Ingress,
    ) -> None:
        super().__init__(scope, id_)
        widgets = [
            cloudwatch.SingleValueWidget(
                metrics=[network.api_gateway_http_api.metric_count()]
            ),
            cloudwatch.SingleValueWidget(
                metrics=[database.dynamodb_table.metric_consumed_read_capacity_units()]
            ),
        ]
        cloudwatch.Dashboard(self, "CloudWatchDashboard", widgets=[widgets])
