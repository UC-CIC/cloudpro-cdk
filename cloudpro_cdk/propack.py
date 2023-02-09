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

class ProPack(Stack):
    def __init__(self,scope: Construct,  construct_id: str, ebus_pro:events.EventBus, dynamodb_tables:dict, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        SOURCE_PROPACK_EXTRACTOR="custom.lambda.proload.pro_extractor"
        DETAIL_TYPE_PROPACK_EXTRACTOR="PRO Extraction"

        SOURCE_PRO_QUESTION_LOADER="custom.lambda.pro.question.loader"
        SOURCE_PRO_SCORING_LOADER="custom.lambda.pro.scoring.loader"

        

        
        bucket_propack=s3.Bucket(self, "bucket-propack",
            versioned=True,
            removal_policy=RemovalPolicy.DESTROY,
            auto_delete_objects=True,
            block_public_access=s3.BlockPublicAccess.BLOCK_ALL,
            event_bridge_enabled=True
        )
 
        fn_propack_extractor = lambda_.Function(
            self,"fn-propack-extractor",
            description="propack-extractor", #microservice tag
            runtime=lambda_.Runtime.PYTHON_3_9,
            handler="index.handler",
            code=lambda_.Code.from_asset(os.path.join("cloudpro_cdk/lambda/","pro_extractor")),
            environment={
                "IDENTIFIER": SOURCE_PROPACK_EXTRACTOR,
                "EBUS_PROPACK":ebus_pro.event_bus_name,
                "DETAIL_TYPE":DETAIL_TYPE_PROPACK_EXTRACTOR
            }
        )
        ebus_pro.grant_put_events_to(fn_propack_extractor)
        bucket_propack.grant_read_write(fn_propack_extractor)

        ##########################################################################################################
        ##############################################################################
        # Default Bus: New S3 Object with prefix raw/ for PRO Pack
        ##############################################################################
        # DLQ for DFLT FWD Rule
        sqs_dflt_propack_dlq = sqs.Queue(self, "sqs-dflt-propack-dlq")
        # Rule filter to match object created in PRO Pack S3
        rule_dflt_fwd_propack_newe = events.Rule(self, "rule-dflt-fwd-propack-new",
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
        # Rule match: Set target to our core application event bus
        rule_dflt_fwd_propack_newe.add_target(
            targets.EventBus(
                ebus_pro,
                dead_letter_queue=sqs_dflt_propack_dlq
            )
        )


        ##############################################################################
        # Core Bus: Object has been created for PRO Pack
        ##############################################################################
        # DLQ for PRO Creation
        sqs_propack_dlq = sqs.Queue(self, "sqs-propack-dlq")
        # s3.EventType.OBJECT_CREATED
        rule_propack_new = events.Rule(self, "rule-propack-new",
            description="Rule for when new PRO packs are uploaded to S3.",
            event_pattern=events.EventPattern(
                source=["aws.s3"],
                detail_type=["Object Created"],
                detail={"bucket":{"name":[ bucket_propack.bucket_name ]}}
            ),
            event_bus=ebus_pro
        )
        # Rule match: Set target to lambda processor to extract files
        rule_propack_new.add_target(
            targets.LambdaFunction(
                fn_propack_extractor,
                dead_letter_queue=sqs_propack_dlq,
                max_event_age=Duration.hours(2), 
                retry_attempts=2
            )
        )
        ##########################################################################################################

        fn_pro_question_loader = lambda_.Function(
            self,"fn-pro-question-loader",
            description="pro-question-loader", #microservice tag
            runtime=lambda_.Runtime.PYTHON_3_9,
            handler="index.handler",
            code=lambda_.Code.from_asset(os.path.join("cloudpro_cdk/lambda/pro_question","pro_question_loader")),
            environment={
                "PROPACK_BUCKET":bucket_propack.bucket_name,
                "TABLE_QUESTIONNAIRE":dynamodb_tables["questionnaire"].table_name,
                "EBUS_PROPACK":ebus_pro.event_bus_name,
                "IDENTIFIER":SOURCE_PRO_QUESTION_LOADER
            }
        )
        fn_pro_scoring_loader = lambda_.Function(
            self,"fn-pro-scoring-loader",
            description="pro-scoring-loader", #microservice tag
            runtime=lambda_.Runtime.PYTHON_3_9,
            handler="index.handler",
            code=lambda_.Code.from_asset(os.path.join("cloudpro_cdk/lambda/pro_scoring","pro_scoring_loader")),
            environment={
                "PROPACK_BUCKET":bucket_propack.bucket_name,
                "TABLE_SCORING":dynamodb_tables["scoring"].table_name,
                "EBUS_PROPACK":ebus_pro.event_bus_name,
                "IDENTIFIER":SOURCE_PRO_SCORING_LOADER
            }
        )

        bucket_propack.grant_read(fn_pro_question_loader)
        dynamodb_tables["questionnaire"].grant_write_data(fn_pro_question_loader)

        bucket_propack.grant_read(fn_pro_scoring_loader)
        dynamodb_tables["scoring"].grant_write_data(fn_pro_scoring_loader)

        ##########################################################################################################
        ##############################################################################
        #  Core Bus: Extraction event
        ##############################################################################
        # DLQ for PRO Loading
        sqs_propack_load_dlq = sqs.Queue(self, "sqs-propack-load-dlq")
        # s3.EventType.OBJECT_CREATED
        rule_propack_load = events.Rule(self, "cdk-rule-propack-load",
            description="Rule for when new PRO packs complete extraction.",
            event_pattern=events.EventPattern(
                source=[SOURCE_PROPACK_EXTRACTOR],
                detail_type=[DETAIL_TYPE_PROPACK_EXTRACTOR],
                detail={"status":["extracted"]}
            ),
            event_bus=ebus_pro
        )
        # Rule match: Set target to lambda processor to extract files
        rule_propack_load.add_target(
            targets.LambdaFunction(
                fn_pro_question_loader,
                dead_letter_queue=sqs_propack_load_dlq,
                max_event_age=Duration.hours(2), 
                retry_attempts=2
            )
        )
        # Rule match: Set target to lambda processor to extract files
        rule_propack_load.add_target(
            targets.LambdaFunction(
                fn_pro_scoring_loader,
                dead_letter_queue=sqs_propack_load_dlq,
                max_event_age=Duration.hours(2), 
                retry_attempts=2
            )
        )
        ##########################################################################################################
