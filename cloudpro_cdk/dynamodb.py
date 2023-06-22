from constructs import Construct
from aws_cdk import(
    Stack,
    aws_dynamodb as dynamodb
)

class DynamodbStack(Stack):
    def __init__(self,scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        dynamo_questionnaire = dynamodb.Table(self,"dynamo-questionnaire",
            partition_key=dynamodb.Attribute(name="pro_pack", type=dynamodb.AttributeType.STRING),
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST
        )
        dynamo_scoring = dynamodb.Table(self,"dynamo-scoring",
            partition_key=dynamodb.Attribute(name="pro_pack", type=dynamodb.AttributeType.STRING),
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST
        )
        dynamo_state = dynamodb.Table(self,"dynamo-state",
            partition_key=dynamodb.Attribute(name="state_hash", type=dynamodb.AttributeType.STRING),
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST
        )
        dynamo_user = dynamodb.Table(self,"dynamo-user",
            partition_key=dynamodb.Attribute(name="sub", type=dynamodb.AttributeType.STRING),
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST
        )
        dynamo_user_staged = dynamodb.Table(self,"dynamo-staged",
            partition_key=dynamodb.Attribute(name="email", type=dynamodb.AttributeType.STRING),
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST
        )
        
        dynamo_survey= dynamodb.Table(self,"dynamo-survey",
            partition_key=dynamodb.Attribute(name="sub", type=dynamodb.AttributeType.STRING),
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST
        )
        dynamo_survey_audit= dynamodb.Table(self,"dynamo-survey-audit",
            partition_key=dynamodb.Attribute(name="sid", type=dynamodb.AttributeType.STRING),
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST
        )
        dynamo_pt_reporting = dynamodb.Table(self,"dynamo-pt-reporting",
            partition_key=dynamodb.Attribute(name="sub", type=dynamodb.AttributeType.STRING),
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST
        )
        dynamo_aggs = dynamodb.Table(self,"dynamo-aggs",
            partition_key=dynamodb.Attribute(name="agg", type=dynamodb.AttributeType.STRING),
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST
        )

        dynamo_notifications = dynamodb.Table(self,"dynamo-notifications",
            partition_key=dynamodb.Attribute(name="sub", type=dynamodb.AttributeType.STRING),
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST
        )

        dynamo_surgeons = dynamodb.Table(self,"dynamo-surgeons",
            partition_key=dynamodb.Attribute(name="sub", type=dynamodb.AttributeType.STRING),
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST
        )

        dynamo_hospitals = dynamodb.Table(self,"dynamo-hospitals",
            partition_key=dynamodb.Attribute(name="hid", type=dynamodb.AttributeType.STRING),
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST
        )

        self.tables = {
            "questionnaire" : dynamo_questionnaire,
            "scoring" : dynamo_scoring,
            "state" : dynamo_state,
            "user" : dynamo_user,
            "user_staged": dynamo_user_staged,
            "survey":dynamo_survey,
            "survey_audit":dynamo_survey_audit,
            "pt_reporting":dynamo_pt_reporting,
            "aggregates":dynamo_aggs,
            "notifications":dynamo_notifications,
            "surgeons":dynamo_surgeons,
            "hospitals":dynamo_hospitals
        }
        
