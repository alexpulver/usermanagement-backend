from typing import Any, cast

from aws_cdk import aws_codebuild as codebuild
from aws_cdk import aws_dynamodb as dynamodb
from aws_cdk import aws_iam as iam
from aws_cdk import core as cdk

import constants
from api.infrastructure import API
from database.infrastructure import Database
from monitoring.infrastructure import Monitoring


class UserManagementBackend(cdk.Stage):
    def __init__(
        self,
        scope: cdk.Construct,
        id_: str,
        *,
        database_dynamodb_billing_mode: dynamodb.BillingMode,
        api_lambda_reserved_concurrency: int,
        **kwargs: Any,
    ):
        super().__init__(scope, id_, **kwargs)

        stateful = cdk.Stack(self, "Stateful")
        database = Database(
            stateful, "Database", dynamodb_billing_mode=database_dynamodb_billing_mode
        )
        stateless = cdk.Stack(self, "Stateless")
        api = API(
            stateless,
            "API",
            database_dynamodb_table_name=database.dynamodb_table.table_name,
            lambda_reserved_concurrency=api_lambda_reserved_concurrency,
        )
        database.dynamodb_table.grant_read_write_data(
            cast(iam.IGrantable, api.lambda_function.role)
        )
        self.api_endpoint_url_cfn_output = cdk.CfnOutput(
            stateless,
            "APIEndpointURL",
            # API doesn't disable create_default_stage, hence URL will be defined
            value=api.http_api.url,  # type: ignore
        )
        Monitoring(stateless, "Monitoring", database=database, api=api)


class ContinuousBuild(cdk.Stage):
    def __init__(
        self,
        scope: cdk.Construct,
        id_: str,
        **kwargs: Any,
    ):
        super().__init__(scope, id_, **kwargs)

        pull_request = cdk.Stack(self, "PullRequest")

        webhook_filters = [
            codebuild.FilterGroup.in_event_of(
                codebuild.EventAction.PULL_REQUEST_CREATED
            ).and_base_branch_is(constants.GITHUB_TRUNK_BRANCH),
            codebuild.FilterGroup.in_event_of(
                codebuild.EventAction.PULL_REQUEST_UPDATED
            ).and_base_branch_is(constants.GITHUB_TRUNK_BRANCH),
        ]
        git_hub_source = codebuild.Source.git_hub(
            owner=constants.GITHUB_OWNER,
            repo=constants.GITHUB_REPO,
            webhook_filters=webhook_filters,
        )
        build_environment = codebuild.BuildEnvironment(
            build_image=codebuild.LinuxBuildImage.STANDARD_5_0,
            compute_type=codebuild.ComputeType.SMALL,
            privileged=True,
        )
        build_spec = codebuild.BuildSpec.from_object(
            {
                "phases": {
                    "install": {
                        "runtime-versions": {
                            "python": constants.CDK_APP_PYTHON_VERSION
                        },
                        "commands": constants.CODEBUILD_INSTALL_COMMANDS,
                    },
                    "build": {"commands": constants.CODEBUILD_BUILD_COMMANDS},
                },
                "version": "0.2",
            }
        )
        codebuild.Project(
            pull_request,
            "Project",
            source=git_hub_source,
            build_spec=build_spec,
            environment=build_environment,
        )
