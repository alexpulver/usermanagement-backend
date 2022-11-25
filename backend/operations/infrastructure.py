import aws_cdk as cdk
import aws_cdk.aws_cloudwatch as cloudwatch
import aws_cdk.aws_servicecatalogappregistry as appregistry
from constructs import Construct

import constants
from backend.api.infrastructure import API
from backend.database.infrastructure import Database


class Operations(Construct):
    def __init__(
        self, scope: Construct, id_: str, *, api: API, database: Database
    ) -> None:
        super().__init__(scope, id_)
        Metadata(self, "Metadata", api=api)
        Monitoring(self, "Monitoring", api=api, database=database)


class Metadata(Construct):
    def __init__(self, scope: Construct, id_: str, *, api: API) -> None:
        super().__init__(scope, id_)
        attributes = {
            "api_endpoint": api.api_gateway_http_api.url,
            "api_runtime_asset": api.lambda_function_asset,
        }
        # Setting attribute group name to a value that doesn't depend on construct path
        # will prevent refactoring the construct path down to the attribute group
        # definition, including its own construct ID. AWS CloudFormation will try
        # to create a new attribute group with the same name, which will fail.
        #
        # To enable the refactoring, I set the attribute group name to a "PLACEHOLDER"
        # value to instantiate the attribute group construct. I later replace the
        # placeholder value with the attribute group construct unique resource name.
        #
        # Now when refactoring the construct path down to the attribute group, the
        # attribute group name will change. This will allow CloudFormation to perform
        # the update.
        #
        # The trade-off is longer attribute group name, but no risk of failing
        # CloudFormation deployment due to attribute group name collision.
        #
        # Example of attribute group name that would lead to failure:
        # "UserManagementBackendSandbox"
        #
        # Example of attribute group name based on construct path that would succeed:
        # "UserManagementBackendSandboxOperationsMetadataAppRegistryAttributeGroup5C997743"
        appregistry_attribute_group = appregistry.CfnAttributeGroup(
            self,
            "AppRegistryAttributeGroup",
            attributes=attributes,
            name="PLACEHOLDER",
        )
        appregistry_attribute_group.name = cdk.Names.unique_resource_name(
            appregistry_attribute_group
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
    def __init__(
        self, scope: Construct, id_: str, *, api: API, database: Database
    ) -> None:
        super().__init__(scope, id_)
        widgets = [
            cloudwatch.SingleValueWidget(
                metrics=[api.api_gateway_http_api.metric_count()]
            ),
            cloudwatch.SingleValueWidget(
                metrics=[database.dynamodb_table.metric_consumed_read_capacity_units()]
            ),
        ]
        cloudwatch.Dashboard(self, "CloudWatchDashboard", widgets=[widgets])
