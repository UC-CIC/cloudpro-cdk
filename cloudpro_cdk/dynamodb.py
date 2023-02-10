from constructs import Construct
from aws_cdk import(
    Stack,
    aws_apigateway as apigateway,
    aws_dynamodb as dynamodb
)

class DynamodbStack(Stack):
    def __init__(self,scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        dynamo_questionnaire = dynamodb.Table(self,"dynamo-questionnaire",
            partition_key=dynamodb.Attribute(name="pro_pack", type=dynamodb.AttributeType.STRING),
            #sort_key=dynamodb.Attribute(name="lorem", type=dynamodb.AttributeType.STRING),
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST
        )
        dynamo_scoring = dynamodb.Table(self,"dynamo-scoring",
            partition_key=dynamodb.Attribute(name="pro_pack", type=dynamodb.AttributeType.STRING),
            #sort_key=dynamodb.Attribute(name="lorem", type=dynamodb.AttributeType.STRING),
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST
        )
        dynamo_state = dynamodb.Table(self,"dynamo-state",
            partition_key=dynamodb.Attribute(name="pro_pack", type=dynamodb.AttributeType.STRING),
            sort_key=dynamodb.Attribute(name="state_hash", type=dynamodb.AttributeType.STRING),
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST
        )


        self.tables = {
            "questionnaire" : dynamo_questionnaire,
            "scoring" : dynamo_scoring,
            "state" : dynamo_state
        }