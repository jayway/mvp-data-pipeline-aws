from aws_cdk import (
    core,
    aws_lambda,
    aws_apigateway,
    aws_kinesisfirehose,
    aws_s3,
    aws_iam
)


class PipelineStack(core.Stack):

    def __init__(self, scope: core.Construct, id: str, is_qa_stack=False, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        def qa_maybe(id_str: str) -> str:
            return id_str if not is_qa_stack else id_str + '-qa'

        # Bucket used to deliver events
        delivery_bucket = aws_s3.Bucket(
            self, id=qa_maybe('my-event-storage-bucket'), bucket_name=qa_maybe('my-event-storage-bucket'),
            block_public_access=aws_s3.BlockPublicAccess.BLOCK_ALL
        )

        # ---- Below is firehose related code ----
        # Since firehose is not yet cdk ready we need to do everything the old way with defining roles
        role = aws_iam.Role(
            self, id=qa_maybe('my-firehose-delivery-role'),
            assumed_by=aws_iam.ServicePrincipal('firehose.amazonaws.com')
        )
        delivery_bucket.grant_write(role)

        # Everything that is not CDK ready still exists like Cfn (Cloudformation?) objects
        firehose = aws_kinesisfirehose.CfnDeliveryStream(
            self, id=qa_maybe('my-pipeline-firehose'), delivery_stream_name=qa_maybe('my-pipeline-firehose'),
            delivery_stream_type='DirectPut',
            s3_destination_configuration={
                'bucketArn': delivery_bucket.bucket_arn,
                'bufferingHints': {
                    'intervalInSeconds': 900,  # The recommended setting is 900 (maximum for firehose)
                    'sizeInMBs': 5
                },
                'compressionFormat': 'UNCOMPRESSED',
                'prefix': 'events/',  # This is the folder the events will end up in
                'errorOutputPrefix': 'delivery_error/',  # Folder in case of delivery error
                'roleArn': role.role_arn
            }
        )

        # Policy statement required for lambda to be able to put records on the firehose stream
        firehose_policy = aws_iam.PolicyStatement(
            actions=['firehose:DescribeDeliveryStream', 'firehose:PutRecord'],
            effect=aws_iam.Effect.ALLOW,
            resources=[firehose.attr_arn])

        # ---- API GW + Lambda code ----
        api_lambda = aws_lambda.Function(
            self,
            id=qa_maybe('my-api-gw-lambda'),
            runtime=aws_lambda.Runtime.PYTHON_3_8,
            code=aws_lambda.Code.asset('src/lambda_code/api_gw_lambda'),
            handler='main.handler',
            memory_size=128,
            timeout=core.Duration.seconds(5),
            environment={
                'region': self.region,
                'stream_name': firehose.delivery_stream_name
            }
        )
        # Important to add the firehose postRecord policy to lambda otherwise there will be access errors
        api_lambda.add_to_role_policy(firehose_policy)

        # Create the lambda that will receive the data messages
        api_gw = aws_apigateway.LambdaRestApi(
            self, id=qa_maybe('my-api-gw'), handler=api_lambda, proxy=False,
            deploy_options=aws_apigateway.StageOptions(stage_name='qa' if is_qa_stack else 'prod')
        )

        # Add API query method
        api_gw.root.add_resource('send_data').add_method('GET', api_key_required=True)

        # Generate an API key and add it to a usage plan
        api_key = api_gw.add_api_key(qa_maybe('MyPipelinePublicKey'))
        usage_plan = api_gw.add_usage_plan(
            id=qa_maybe('my-pipeline-usage-plan'),
            name='standard',
            api_key=api_key,
            throttle=aws_apigateway.ThrottleSettings(
                rate_limit=10, burst_limit=2
            )
        )

        # Add the usage plan to the API GW
        usage_plan.add_api_stage(
            stage=api_gw.deployment_stage
        )
