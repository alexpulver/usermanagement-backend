from typing import Any

import aws_cdk as cdk
import aws_cdk.aws_codebuild as codebuild
from constructs import Construct

import constants
from toolchain.deployment_pipeline import DeploymentPipeline
from toolchain.pull_request_build import PullRequestBuild


class ToolchainStack(cdk.Stack):
    def __init__(
        self,
        scope: Construct,
        id_: str,
        **kwargs: Any,
    ):
        super().__init__(scope, id_, **kwargs)

        build_spec = codebuild.BuildSpec.from_object(
            {
                "phases": {
                    "install": {
                        "runtime-versions": {"python": constants.PYTHON_VERSION},
                        "commands": ["env", "toolchain/scripts/install-deps.sh"],
                    },
                    "build": {
                        "commands": ["toolchain/scripts/run-tests.sh", "npx cdk synth"]
                    },
                },
                "version": "0.2",
            }
        )
        DeploymentPipeline(
            self,
            "DeploymentPipeline",
            build_spec=build_spec,
        )
        PullRequestBuild(self, "PullRequestBuild", build_spec=build_spec)
