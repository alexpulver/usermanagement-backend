import aws_cdk as cdk
import aws_cdk.aws_cloudwatch as cloudwatch
import aws_cdk.aws_servicecatalogappregistry as appregistry
import jsii
from constructs import Construct
from constructs import IConstruct

import constants
from backend.component import Backend


# pylint: disable=too-few-public-methods
@jsii.implements(cdk.IAspect)
class Operations:
    def visit(self, node: IConstruct) -> None:  # noqa
        if not isinstance(node, Backend):
            return
        Metadata(node, "Metadata", backend=node)
        Monitoring(node, "Monitoring", backend=node)


class Metadata(Construct):
    def __init__(self, scope: Construct, id_: str, *, backend: Backend) -> None:
        super().__init__(scope, id_)
        attributes = {
            "api_endpoint": backend.api.api_gateway_http_api.url,
            "api_runtime_asset": backend.api.lambda_function_asset,
        }
        appregistry_attribute_group = appregistry.CfnAttributeGroup(
            self,
            "AppRegistryAttributeGroup",
            attributes=attributes,
            name=backend.stack_name,
        )
        appregistry_attribute_group_association = (
            appregistry.CfnAttributeGroupAssociation(
                self,
                "AppRegistryAttributeGroupAssociation",
                application=constants.APP_NAME,
                attribute_group=appregistry_attribute_group.name,
            )
        )
        # Need explicit dependency because attribute group name is known
        # at synth time. CloudFormation would deploy the attribute group and the
        # attribute group association in parallel, and fail. Using attribute group ID
        # would work, but would not be explicit.
        appregistry_attribute_group_association.add_depends_on(
            appregistry_attribute_group
        )


class Monitoring(Construct):
    def __init__(self, scope: Construct, id_: str, *, backend: Backend) -> None:
        super().__init__(scope, id_)
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
        cloudwatch.Dashboard(self, "CloudWatchDashboard", widgets=[widgets])
