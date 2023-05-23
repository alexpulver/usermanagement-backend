from typing import Any

import aws_cdk as cdk
import aws_cdk.aws_servicecatalogappregistry_alpha as appregistry_alpha

import constants


# pylint: disable=too-few-public-methods
class Metadata:
    def __init__(self, *, app: cdk.App, **kwargs: Any):
        application = appregistry_alpha.TargetApplication.create_application_stack(
            application_name=constants.APP_NAME,
            application_description=constants.APP_DESCRIPTION,
            **kwargs,
        )
        self.appregistry_application_associator = (
            appregistry_alpha.ApplicationAssociator(
                app, "AppRegistryApplicationAssociator", applications=[application]
            )
        )
