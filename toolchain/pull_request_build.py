from aws_cdk import aws_codebuild as codebuild
from constructs import Construct

import constants


class PullRequestBuild(Construct):
    def __init__(self, scope: Construct, id_: str, *, build_spec: codebuild.BuildSpec):
        super().__init__(scope, id_)

        webhook_filters = [
            codebuild.FilterGroup.in_event_of(
                codebuild.EventAction.PULL_REQUEST_CREATED
            ).and_base_branch_is(constants.GITHUB_TRUNK_BRANCH),
            codebuild.FilterGroup.in_event_of(
                codebuild.EventAction.PULL_REQUEST_UPDATED
            ).and_base_branch_is(constants.GITHUB_TRUNK_BRANCH),
        ]
        source = codebuild.Source.git_hub(
            owner=constants.GITHUB_OWNER,
            repo=constants.GITHUB_REPO,
            webhook_filters=webhook_filters,
        )
        codebuild.Project(
            self,
            "CodeBuildProject",
            source=source,
            build_spec=build_spec,
            environment=constants.CODEBUILD_BUILD_ENVIRONMENT,
        )
