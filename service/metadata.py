import aws_cdk as cdk
import aws_cdk.aws_servicecatalogappregistry as appregistry
from constructs import Construct

import constants
from service.api.compute import Compute
from service.ingress import Ingress


class Metadata(Construct):
    def __init__(
        self,
        scope: Construct,
        id_: str,
        *,
        compute: Compute,
        network: Ingress,
    ) -> None:
        super().__init__(scope, id_)
        appregistry_attribute_group = appregistry.CfnAttributeGroup(
            self,
            "AppRegistryAttributeGroup",
            name=cdk.Stack.of(self).stack_name,
            attributes={
                "api_code": compute.lambda_function_code,
                "api_endpoint": network.api_gateway_http_api.url,
            },
        )
        appregistry_attribute_group_association = (
            appregistry.CfnAttributeGroupAssociation(
                self,
                "AppRegistryAttributeGroupAssociation",
                application=constants.APP_NAME,
                attribute_group=appregistry_attribute_group.name,
            )
        )
        appregistry_attribute_group_association.add_dependency(
            appregistry_attribute_group
        )
