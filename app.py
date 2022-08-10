import aws_cdk as cdk

import constants
from deployment import UserManagementBackend
from toolchain import Toolchain

app = cdk.App()

# Development stage
UserManagementBackend(
    app,
    constants.USERMANAGEMENT_BACKEND_DEV_STAGE_PARAMETERS.id,
    **constants.USERMANAGEMENT_BACKEND_DEV_STAGE_PARAMETERS.props,
)

# Continuous deployment and pull request validation
Toolchain(
    app,
    constants.TOOLCHAIN_STACK_PARAMETERS.id,
    **constants.TOOLCHAIN_STACK_PARAMETERS.props,
)

app.synth()
