import os

from constructs import Construct
from aws_cdk import(
    Stack,
    aws_apigateway as apigateway,
    aws_lambda as lambda_
)

class ApigStack(Stack):
    def __init__(self,scope: Construct, construct_id: str,  dynamodb_tables:dict, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)


        SOURCE_PRO_QUESTION_PROHASH_GET="custom.lambda.pro.question.loader"

        fn_pro_question_prohash_get = lambda_.Function(
            self,"fn-pro-question-prohash-get",
            description="pro-question-prohash-get", #microservice tag
            runtime=lambda_.Runtime.PYTHON_3_9,
            handler="index.handler",
            code=lambda_.Code.from_asset(os.path.join("cloudpro_cdk/lambda/pro_question","pro_question_prohash_get")),
            environment={
                "TABLE_QUESTIONNAIRE":dynamodb_tables["questionnaire"].table_name,
                "IDENTIFIER":SOURCE_PRO_QUESTION_PROHASH_GET
            }
        )

        dynamodb_tables["questionnaire"].grant_read_data(fn_pro_question_prohash_get)


        question_prohash_get_integration=apigateway.LambdaIntegration(fn_pro_question_prohash_get)

        core_api = apigateway.RestApi(
            self,"core-api",
            endpoint_configuration=apigateway.EndpointConfiguration(
                types=[apigateway.EndpointType.REGIONAL]
            )
        )

        public_route_questionnaire=core_api.root.add_resource("questionnaire")
        public_route_questionnaire_prohash=public_route_questionnaire.add_resource("{pro_hash}")
        method_questionnaire_prohash=public_route_questionnaire_prohash.add_method(
            "GET",question_prohash_get_integration,
            api_key_required=True
        )

        plan = core_api.add_usage_plan(
            "UsagePlan",name="public plan",
            throttle=apigateway.ThrottleSettings(
                rate_limit=10,
                burst_limit=2
            )
        )

        core_key=core_api.add_api_key("core-api-key")
        plan.add_api_key(core_key)
        plan.add_api_stage(api=core_api,stage=core_api.deployment_stage)

        self.core_api = core_api
