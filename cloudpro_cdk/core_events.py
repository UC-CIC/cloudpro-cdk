import os

from constructs import Construct
from aws_cdk import(
    Stack,
    Duration,
    aws_lambda as lambda_,
    aws_events as events,
    aws_events_targets as targets,
    aws_sqs as sqs
)

class CoreEvents(Stack):
    def __init__(self,scope: Construct,  construct_id: str, ebus_pro:events.EventBus, dynamodb_tables:dict,  **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        IDENT_PRO_STATE_INIT="custom.lambda.pro.state"
        SOURCE_PRO_STATE_INIT="custom.cloudpro.core"
        SOURCE_PT_COMPLETE_SURVEY="custom.cloudpro.core.survey.complete"
        DETAIL_TYPE_PROPACK_STATE_INIT="State Init"
        DETAIL_TYPE_PT_SURVEY_COMPLETE="Survey Completed"

        layer_cloudpro_lib = lambda_.LayerVersion.from_layer_version_arn(self,id="layer_cloudpro_lib",layer_version_arn=self.node.try_get_context("layer_arn"))



        fn_pro_state_init = lambda_.Function(
            self,"fn-pro-state-init",
            description="pro-state-init", #microservice tag
            runtime=lambda_.Runtime.PYTHON_3_9,
            handler="index.handler",
            code=lambda_.Code.from_asset(os.path.join("cloudpro_cdk/lambda/pro_state","pro_state_init")),
            environment={
                "IDENTIFIER": IDENT_PRO_STATE_INIT,
                "TABLE_QUESTIONNAIRE":dynamodb_tables["questionnaire"].table_name,
                "TABLE_STATE":dynamodb_tables["state"].table_name,
            },
            layers=[layer_cloudpro_lib]
        )
        # ebus_pro.grant_put_events_to(fn_pro_state_init)
        dynamodb_tables["questionnaire"].grant_read_data(fn_pro_state_init)
        dynamodb_tables["state"].grant_write_data(fn_pro_state_init)

        sqs_propack_state_init_dlq = sqs.Queue(self,"sqs-propack-state-init-dlq")
        rule_propack_init = events.Rule(self, "cdk-rule-propack-state-init",
            description="Rule to initialize a state for a user.",
            event_pattern=events.EventPattern(
                source=[SOURCE_PRO_STATE_INIT],
                detail_type=[DETAIL_TYPE_PROPACK_STATE_INIT]
            ),
            event_bus=ebus_pro
        ) 
        # Rule match: Set target to lambda processor to extract files
        rule_propack_init.add_target(
            targets.LambdaFunction(
                fn_pro_state_init,
                dead_letter_queue=sqs_propack_state_init_dlq,
                max_event_age=Duration.hours(2), 
                retry_attempts=2
            )
        )


        fn_survey_completed = lambda_.Function(
            self,"fn-reporting-survey-completed",
            description="reporting-survey-completed", #microservice tag
            runtime=lambda_.Runtime.PYTHON_3_9,
            handler="index.handler",
            code=lambda_.Code.from_asset(os.path.join("cloudpro_cdk/lambda/ptreporting","reporting_survey_completed")),
            environment={
                "IDENTIFIER": SOURCE_PT_COMPLETE_SURVEY,
                "TABLE_PT_REPORTING":dynamodb_tables["pt_reporting"].table_name,
                "TABLE_AGGREGATES":dynamodb_tables["aggregates"].table_name
            },
            layers=[layer_cloudpro_lib]
        )

        dynamodb_tables["pt_reporting"].grant_read_write_data(fn_survey_completed)
        dynamodb_tables["aggregates"].grant_read_write_data(fn_survey_completed)

        sqs_ptreport_dlq = sqs.Queue(self,"sqs-reporting-survey-complete-dlq")
        rule_ptreport_complete = events.Rule(self, "cdk-rule-reporting-survey-complete",
            description="Survey completed event.",
            event_pattern=events.EventPattern(
                source=[SOURCE_PT_COMPLETE_SURVEY],
                detail_type=[DETAIL_TYPE_PT_SURVEY_COMPLETE]
            ),
            event_bus=ebus_pro
        ) 
        # Rule match: Set target to lambda processor to extract files
        rule_ptreport_complete.add_target(
            targets.LambdaFunction(
                fn_survey_completed,
                dead_letter_queue=sqs_ptreport_dlq,
                max_event_age=Duration.hours(2), 
                retry_attempts=2
            )
        )