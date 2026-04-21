#!/usr/bin/env python3
import aws_cdk as cdk

from dda_pipeline_stack import DdaPipelineStack

app = cdk.App()

DdaPipelineStack(
    app,
    "DdaPipelineStack",
    env=cdk.Environment(
        account=app.node.try_get_context("account"),
        region=app.node.try_get_context("region"),
    ),
)

app.synth()
