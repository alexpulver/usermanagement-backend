import os
from dataclasses import dataclass
from typing import Any, Dict

import aws_cdk as cdk
import aws_cdk.aws_dynamodb as dynamodb

APP_NAME = "UserManagementBackend"
APP_PYTHON_VERSION = "3.7"

# pylint: disable=line-too-long
GITHUB_CONNECTION_ARN = "arn:aws:codestar-connections:eu-west-1:807650736403:connection/1f244295-871f-411f-afb1-e6ca987858b6"
GITHUB_OWNER = "alexpulver"
GITHUB_REPO = "usermanagement-backend"
GITHUB_TRUNK_BRANCH = "main"


@dataclass
class ConstructParameters:
    # pylint: disable=invalid-name
    id: str
    props: Dict[str, Any]


TOOLCHAIN_STACK_PARAMETERS = ConstructParameters(
    id=f"{APP_NAME}Toolchain",
    props={
        "env": cdk.Environment(account="807650736403", region="eu-west-1"),
    },
)

USERMANAGEMENT_BACKEND_DEV_STAGE_PARAMETERS = ConstructParameters(
    id=f"{APP_NAME}Dev",
    props={
        "env": cdk.Environment(
            account=os.environ["CDK_DEFAULT_ACCOUNT"],
            region=os.environ["CDK_DEFAULT_REGION"],
        ),
        "api_lambda_reserved_concurrency": 1,
        "database_dynamodb_billing_mode": dynamodb.BillingMode.PAY_PER_REQUEST,
    },
)

USERMANAGEMENT_BACKEND_PIPELINE_STAGES_PARAMETERS = [
    ConstructParameters(
        id=f"{APP_NAME}Prod",
        props={
            "env": cdk.Environment(account="807650736403", region="eu-west-1"),
            "api_lambda_reserved_concurrency": 10,
            "database_dynamodb_billing_mode": dynamodb.BillingMode.PROVISIONED,
        },
    )
]
