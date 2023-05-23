from collections import namedtuple

import aws_cdk.aws_codebuild as codebuild

APP_NAME = "UserManagement"
APP_DESCRIPTION = (
    "Ongoing project to build a realistic end-to-end application "
    "software development life cycle using the AWS CDK"
)
PYTHON_VERSION = "3.9"

# pylint: disable=line-too-long
GITHUB_CONNECTION_ARN = "arn:aws:codestar-connections:eu-west-1:807650736403:connection/1f244295-871f-411f-afb1-e6ca987858b6"
GITHUB_OWNER = "alexpulver"
GITHUB_REPO = "usermanagement"
GITHUB_TRUNK_BRANCH = "main"

CODEBUILD_BUILD_ENVIRONMENT = codebuild.BuildEnvironment(
    build_image=codebuild.LinuxBuildImage.STANDARD_5_0,
    privileged=True,
)

Environment = namedtuple("Environment", ["name", "account", "region"])
MANAGEMENT_ENVIRONMENT = Environment(
    name="Management", account="807650736403", region="eu-west-1"
)
COMPONENTS_ENVIRONMENTS = [
    Environment(name="Production", account="807650736403", region="eu-west-1"),
]
