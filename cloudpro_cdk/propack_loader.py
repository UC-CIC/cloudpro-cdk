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
    aws_events_targets as targets,
    aws_dynamodb as dynamodb
)

class ProPackLoaderStack(Stack):
    def __init__(self,scope: Construct,  construct_id: str, pro_bus:events.EventBus, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)


        
        dynamo_propack_questionnaire = dynamodb.Table(self,"cdk-dynamo-propack-questionnaire",
            partition_key=dynamodb.Attribute(name="pro_pack", type=dynamodb.AttributeType.STRING),
            #sort_key=dynamodb.Attribute(name="lorem", type=dynamodb.AttributeType.STRING),
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST
        )
        dynamo_propack_scoring = dynamodb.Table(self,"cdk-dynamo-propack-scoring",
            partition_key=dynamodb.Attribute(name="pro_pack", type=dynamodb.AttributeType.STRING),
            #sort_key=dynamodb.Attribute(name="lorem", type=dynamodb.AttributeType.STRING),
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST
        )
        

        bucket_propack=s3.Bucket(self, "cdk-bucket-propack",
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
            code=lambda_.Code.from_asset(os.path.join("cloudpro_cdk/lambda/","pro_loader")),
            environment={
                "TABLE_QUESTIONNAIRE":dynamo_propack_questionnaire.table_name,
                "TABLE_SCORING":dynamo_propack_scoring.table_name
            }
        )

        bucket_propack.grant_read_write(fn_propack_loader)

        # s3.EventType.OBJECT_CREATED
        rule_propack_new = events.Rule(self, "cdk-rule-propack-new",
            description="Rule for when new PRO packs are uploaded to S3.",
            event_pattern=events.EventPattern(
                source=["aws.s3"],
                detail_type=["Object Created"],
                detail={"bucket":{"name":[ bucket_propack.bucket_name ]}}
            ),
            event_bus=pro_bus
        )

        sqs_dflt_propack_dlq = sqs.Queue(self, "cdk-sqs-dflt-propack-dlq")
        # fwd to app bus
        rule_dflt_fwd_propack_newe = events.Rule(self, "cdk-rule-dflt-fwd-propack-new",
            description="Rule to forward from default bus.",
            event_pattern=events.EventPattern(
                source=["aws.s3"],
                detail_type=["Object Created"],
                detail={
                    "bucket": {
                        "name":[ bucket_propack.bucket_name ]
                    },
                    "object": {
                        "key": [ { "prefix": "raw/" }]    
                    }
                }
            )
        )


        rule_dflt_fwd_propack_newe.add_target(
            targets.EventBus(
                pro_bus,
                dead_letter_queue=sqs_dflt_propack_dlq
            )
        )

        sqs_propack_dlq = sqs.Queue(self, "cdk-sqs-propack-dlq")
        rule_propack_new.add_target(
            targets.LambdaFunction(
                fn_propack_loader,
                dead_letter_queue=sqs_propack_dlq,
                max_event_age=Duration.hours(2), 
                retry_attempts=2
            )
        )