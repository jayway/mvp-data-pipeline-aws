#!/usr/bin/env python3

from aws_cdk import core

from src.stacks.pipeline_stack import PipelineStack


app = core.App()
# Production stack
PipelineStack(app, 'mvp-data-pipeline-aws', env={'region': 'eu-west-1'}, is_qa_stack=False)

# QA/Staging Stack
PipelineStack(app, 'mvp-data-pipeline-aws-qa', env={'region': 'eu-central-1'}, is_qa_stack=True)

app.synth()
