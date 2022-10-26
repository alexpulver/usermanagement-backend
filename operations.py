from typing import cast

import aws_cdk as cdk
import aws_cdk.aws_cloudwatch as cloudwatch
import aws_cdk.aws_servicecatalogappregistry_alpha as appregistry_alpha
import jsii
from constructs import Construct
from constructs import IConstruct

from backend.component import Backend

# pylint: disable=line-too-long
APPREGISTRY_APPLICATION_ARN = "arn:aws:servicecatalog:eu-west-1:807650736403:/applications/088rctd1yghw2b738o03p1e08w"  # noqa


# pylint: disable=too-few-public-methods
@jsii.implements(cdk.IAspect)
class Metadata:
    def visit(self, node: IConstruct) -> None:  # noqa
        if not cdk.Stack.is_stack(node) and not isinstance(node, Backend):
            return
        backend = cast(Backend, node)
        metadata = Construct(backend, "Metadata")
        attributes = {
            "api_endpoint": backend.api.api_gateway_http_api.url,
            "api_runtime_asset": backend.api.lambda_function_asset,
        }
        attribute_group = appregistry_alpha.AttributeGroup(
            metadata,
            "AppRegistryAttributeGroup",
            attribute_group_name=cdk.Names.unique_resource_name(metadata),
            attributes=attributes,
        )
        appregistry_app = appregistry_alpha.Application.from_application_arn(
            metadata, "AppRegistryApplication", APPREGISTRY_APPLICATION_ARN
        )
        appregistry_app.associate_attribute_group(attribute_group)


# pylint: disable=too-few-public-methods
@jsii.implements(cdk.IAspect)
class Monitoring:
    def visit(self, node: IConstruct) -> None:  # noqa
        if not cdk.Stack.is_stack(node) and not isinstance(node, Backend):
            return
        backend = cast(Backend, node)
        monitoring = Construct(backend, "Monitoring")
        widgets = [
            cloudwatch.SingleValueWidget(
                metrics=[backend.api.api_gateway_http_api.metric_count()]
            ),
            cloudwatch.SingleValueWidget(
                metrics=[
                    backend.database.dynamodb_table.metric_consumed_read_capacity_units()
                ]
            ),
        ]
        cloudwatch.Dashboard(monitoring, "CloudWatchDashboard", widgets=[widgets])