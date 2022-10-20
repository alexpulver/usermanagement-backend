from typing import Dict, cast

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
class Metadata:
    def visit(self, node: IConstruct) -> None:
        if not cdk.Stack.is_stack(node):
            return
        stack = cast(cdk.Stack, node)
        metadata = Construct(stack, "Metadata")
        attributes = Metadata._get_outputs(stack)
        if not attributes:
            return
        attribute_group = appregistry_alpha.AttributeGroup(
            metadata,
            "AppRegistryAttributeGroup",
            attribute_group_name=cdk.Names.unique_resource_name(metadata),
            attributes=attributes,
        )
        appregistry_app = appregistry_alpha.Application.from_application_arn(
            metadata, "AppRegistryApplication", APPREGISTRY_APP_ARN
        )
        appregistry_app.associate_attribute_group(attribute_group)

    @staticmethod
    def _get_outputs(stack: cdk.Stack) -> Dict[str, str]:
        outputs = {}
        for child in stack.node.children:
            if isinstance(child, cdk.CfnOutput):
                cfn_output = child
                outputs[cfn_output.logical_id] = cfn_output.value
        return outputs


# pylint: disable=too-few-public-methods
@jsii.implements(cdk.IAspect)
class Monitoring:
    def visit(self, node: IConstruct) -> None:
        if not cdk.Stack.is_stack(node) and not isinstance(node, Backend):
            return
        backend = cast(Backend, node)
        monitoring = Construct(backend, "Monitoring")
        widgets = [
            cloudwatch.SingleValueWidget(
                metrics=[backend.api_gateway_http_api.metric_count()]
            ),
            cloudwatch.SingleValueWidget(
                metrics=[backend.dynamodb_table.metric_consumed_read_capacity_units()]
            ),
        ]
        cloudwatch.Dashboard(monitoring, "CloudWatchDashboard", widgets=[widgets])
