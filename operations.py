import aws_cdk as cdk
import aws_cdk.aws_cloudwatch as cloudwatch
import aws_cdk.aws_servicecatalogappregistry_alpha as appregistry_alpha
import jsii
from constructs import Construct
from constructs import IConstruct

from backend.component import Backend

# pylint: disable=line-too-long
APPREGISTRY_APP_ARN = "arn:aws:servicecatalog:eu-west-1:807650736403:/applications/088rctd1yghw2b738o03p1e08w"


# pylint: disable=too-few-public-methods
@jsii.implements(cdk.IAspect)
class Operations:
    def visit(self, node: IConstruct) -> None:
        if not isinstance(node, Backend):
            return
        backend = node
        Metadata(backend, "Metadata", backend=backend)
        Monitoring(backend, "Monitoring", backend=backend)


class Metadata(Construct):
    def __init__(self, scope: Construct, id_: str, *, backend: Backend):
        super().__init__(scope, id_)

        attribute_group = appregistry_alpha.AttributeGroup(
            self,
            "AppRegistryAttributeGroup",
            attribute_group_name=cdk.Names.unique_resource_name(self),
            attributes={
                "account": backend.account,
                "region": backend.region,
                "api_endpoint": backend.api_gateway_http_api.url,
                "api_lambda_function_asset": backend.lambda_function_asset,
            },
        )
        appregistry_app = appregistry_alpha.Application.from_application_arn(
            self, "AppRegistryApplication", APPREGISTRY_APP_ARN
        )
        appregistry_app.associate_attribute_group(attribute_group)


class Monitoring(Construct):
    def __init__(self, scope: Construct, id_: str, *, backend: Backend):
        super().__init__(scope, id_)

        widgets = [
            cloudwatch.SingleValueWidget(
                metrics=[backend.api_gateway_http_api.metric_count()]
            ),
            cloudwatch.SingleValueWidget(
                metrics=[backend.dynamodb_table.metric_consumed_read_capacity_units()]
            ),
        ]
        cloudwatch.Dashboard(self, "CloudWatchDashboard", widgets=[widgets])
