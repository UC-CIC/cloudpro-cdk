import os

from constructs import Construct
from aws_cdk import(
    Stack,
    Duration,
    RemovalPolicy,
    aws_s3 as s3,
    aws_lambda as lambda_,
    aws_events as events,
    aws_sqs as sqs,
    aws_events_targets as targets
)

class ProPackLoaderStack(Stack):
    def __init__(self,scope: Construct,  construct_id: str, pro_bus:events.EventBus, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        propacks_bucket=s3.Bucket(self, "cdk-bucket-propack",
            versioned=True,
            removal_policy=RemovalPolicy.DESTROY,
            auto_delete_objects=True,
            block_public_access=s3.BlockPublicAccess.BLOCK_ALL,
            event_bridge_enabled=True
        )

        fn_propack_loader = lambda_.Function(
            self,"cdk-fn-propack-loader",
            runtime=lambda_.Runtime.PYTHON_3_9,
            handler="index.handler",
            code=lambda_.Code.from_asset(os.path.join("cloudpro_cdk/lambda/","pro_loader"))
        )


        # s3.EventType.OBJECT_CREATED
        propack_rule = events.Rule(self, "cdk-rule-propack-new",
            description="Rule for when new PRO packs are uploaded to S3.",
            event_pattern=events.EventPattern(
                source=["aws.s3"],
                detail_type=["Object Created"],
                detail={"bucket":{"name":[ propacks_bucket.bucket_name ]}}
            ),
            event_bus=pro_bus
        )

        dflt_propack_dlq = sqs.Queue(self, "cdk-sqs-dflt-propack-dlq")
        # fwd to app bus
        dflt_fwd_propack_new_rule = events.Rule(self, "cdk-fwd-propack-new",
            description="Rule to forward from default bus.",
            event_pattern=events.EventPattern(
                source=["aws.s3"],
                detail_type=["Object Created"],
                detail={"bucket":{"name":[ propacks_bucket.bucket_name ]}}
            )
        )
        dflt_fwd_propack_new_rule.add_target(
            targets.EventBus(
                pro_bus,
                dead_letter_queue=dflt_propack_dlq
            )
        )

        propack_dlq = sqs.Queue(self, "cdk-sqs-propack-dlq")
        propack_rule.add_target(
            targets.LambdaFunction(
                fn_propack_loader,
                dead_letter_queue=propack_dlq,
                max_event_age=Duration.hours(2), 
                retry_attempts=2
            )
        )