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


        SOURCE_PRO_QUESTION="custom.lambda.pro.question"
        SOURCE_PRO_SCORING="custom.lambda.pro.scoring"

        core_api = apigateway.RestApi(
            self,"core-api",
            endpoint_configuration=apigateway.EndpointConfiguration(
                types=[apigateway.EndpointType.REGIONAL]
            )
        )

        layer_cloudpro_lib = lambda_.LayerVersion.from_layer_version_arn(self,id="layer_cloudpro_lib",layer_version_arn=self.node.try_get_context("layer_arn"))
        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
        
               
        #################################################################################
        # /questionnaire/{pro_hash}
        #################################################################################
        fn_pro_question_prohash_get = lambda_.Function(
            self,"fn-pro-question-prohash-get",
            description="pro-question-prohash-get", #microservice tag
            runtime=lambda_.Runtime.PYTHON_3_9,
            handler="index.handler",
            code=lambda_.Code.from_asset(os.path.join("cloudpro_cdk/lambda/pro_question","pro_question_prohash_get")),
            environment={
                "TABLE_QUESTIONNAIRE":dynamodb_tables["questionnaire"].table_name,
                "IDENTIFIER":SOURCE_PRO_QUESTION
            },
            layers=[ layer_cloudpro_lib ]
        )
        dynamodb_tables["questionnaire"].grant_read_data(fn_pro_question_prohash_get)


        #################################################################################
        # /questionnaire/{pro_hash}/question/{link_id}
        #################################################################################
        fn_pro_question_linkid_get = lambda_.Function(
            self,"fn-pro-question-linkid-get",
            description="pro-question-linkid-get", #microservice tag
            runtime=lambda_.Runtime.PYTHON_3_9,
            handler="index.handler",
            code=lambda_.Code.from_asset(os.path.join("cloudpro_cdk/lambda/pro_question","pro_question_linkid_get")),
            environment={
                "TABLE_QUESTIONNAIRE":dynamodb_tables["questionnaire"].table_name,
                "IDENTIFIER":SOURCE_PRO_QUESTION
            },
            layers=[ layer_cloudpro_lib ]
        )
        dynamodb_tables["questionnaire"].grant_read_data(fn_pro_question_linkid_get)


        #################################################################################
        # *WARNING* For development purposes only. Pulls entire dynamo table. Costly call
        #################################################################################
        # /questionnaire/all
        #################################################################################
        fn_pro_question_all_get = lambda_.Function(
            self,"fn-pro-question-all-get",
            description="pro-question-all-get", #microservice tag
            runtime=lambda_.Runtime.PYTHON_3_9,
            handler="index.handler",
            code=lambda_.Code.from_asset(os.path.join("cloudpro_cdk/lambda/pro_question","pro_question_all_get")),
            environment={
                "TABLE_QUESTIONNAIRE":dynamodb_tables["questionnaire"].table_name,
                "IDENTIFIER":SOURCE_PRO_QUESTION
            },
            layers=[ layer_cloudpro_lib ]
        )
        dynamodb_tables["questionnaire"].grant_read_data(fn_pro_question_all_get)

        
        

        ###### Route Base = /questionnaire
        public_route_questionnaire=core_api.root.add_resource("questionnaire")
        # /questionnaire/all
        public_route_questionnaire_all=public_route_questionnaire.add_resource("all")
        # GET: /questionnaire/all
        question_all_get_integration=apigateway.LambdaIntegration(fn_pro_question_all_get)
        method_questionnaire_prohash=public_route_questionnaire_all.add_method(
            "GET",question_all_get_integration,
            api_key_required=True
        )
        # /questionnaire/{pro_hash}
        public_route_questionnaire_prohash=public_route_questionnaire.add_resource("{pro_hash}")
         # GET: /questionnaire/{pro_hash}
        question_prohash_get_integration=apigateway.LambdaIntegration(fn_pro_question_prohash_get)
        method_questionnaire_prohash=public_route_questionnaire_prohash.add_method(
            "GET",question_prohash_get_integration,
            api_key_required=True
        )
        # /questionnaire/{pro_hash}/question
        public_route_questionnaire_prohash_question=public_route_questionnaire_prohash.add_resource("question")
        # /questionnaire/{pro_hash}/question/{link_id}
        public_route_questionnaire_prohash_question_linkid=public_route_questionnaire_prohash_question.add_resource("{link_id}")
        # GET: /questionnaire/{pro_hash}/question/{link_id}
        question_linkid_get_integration=apigateway.LambdaIntegration(fn_pro_question_linkid_get)
        method_questionnaire_prohash=public_route_questionnaire_prohash_question_linkid.add_method(
            "GET",question_linkid_get_integration,
            api_key_required=True
        )


        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#

        #################################################################################
        # /scoring/{pro_hash}
        #################################################################################
        fn_pro_scoring_prohash_get = lambda_.Function(
            self,"fn-pro-scoring-prohash-get",
            description="pro-scoring-prohash-get", #microservice tag
            runtime=lambda_.Runtime.PYTHON_3_9,
            handler="index.handler",
            code=lambda_.Code.from_asset(os.path.join("cloudpro_cdk/lambda/pro_scoring","pro_scoring_prohash_get")),
            environment={
                "TABLE_SCORING":dynamodb_tables["scoring"].table_name,
                "IDENTIFIER":SOURCE_PRO_SCORING
            },
            layers=[ lambda_.LayerVersion.from_layer_version_arn(self,id="layer_cloudpro_lib_s0",layer_version_arn=self.node.try_get_context("layer_arn")) ]
        )
        dynamodb_tables["scoring"].grant_read_data(fn_pro_scoring_prohash_get)


        #################################################################################
        # /scoring/{pro_hash}/scoring/{link_id}
        #################################################################################
        fn_pro_scoring_linkid_get = lambda_.Function(
            self,"fn-pro-scoring-linkid-get",
            description="pro-scoring-linkid-get", #microservice tag
            runtime=lambda_.Runtime.PYTHON_3_9,
            handler="index.handler",
            code=lambda_.Code.from_asset(os.path.join("cloudpro_cdk/lambda/pro_scoring","pro_scoring_linkid_get")),
            environment={
                "TABLE_SCORING":dynamodb_tables["scoring"].table_name,
                "IDENTIFIER":SOURCE_PRO_SCORING
            },
            layers=[ layer_cloudpro_lib ]
        )
        dynamodb_tables["scoring"].grant_read_data(fn_pro_scoring_linkid_get)


        #################################################################################
        # *WARNING* For development purposes only. Pulls entire dynamo table. Costly call
        #################################################################################
        # /scoring/all
        #################################################################################
        fn_pro_scoring_all_get = lambda_.Function(
            self,"fn-pro-scoring-all-get",
            description="pro-scoring-all-get", #microservice tag
            runtime=lambda_.Runtime.PYTHON_3_9,
            handler="index.handler",
            code=lambda_.Code.from_asset(os.path.join("cloudpro_cdk/lambda/pro_scoring","pro_scoring_all_get")),
            environment={
                "TABLE_SCORING":dynamodb_tables["scoring"].table_name,
                "IDENTIFIER":SOURCE_PRO_SCORING
            },
            layers=[ layer_cloudpro_lib ]
        )
        dynamodb_tables["scoring"].grant_read_data(fn_pro_scoring_all_get)

        
        

        ###### Route Base = /scoring
        public_route_scoring=core_api.root.add_resource("scoring")
        # /scoring/all
        public_route_scoring_all=public_route_scoring.add_resource("all")
        # GET: /scoring/all
        scoring_all_get_integration=apigateway.LambdaIntegration(fn_pro_scoring_all_get)
        method_scoring_prohash=public_route_scoring_all.add_method(
            "GET",scoring_all_get_integration,
            api_key_required=True
        )
        # /scoring/{pro_hash}
        public_route_scoring_prohash=public_route_scoring.add_resource("{pro_hash}")
         # GET: /scoring/{pro_hash}
        scoring_prohash_get_integration=apigateway.LambdaIntegration(fn_pro_scoring_prohash_get)
        method_scoring_prohash=public_route_scoring_prohash.add_method(
            "GET",scoring_prohash_get_integration,
            api_key_required=True
        )
        # /scoring/{pro_hash}/scoring
        public_route_scoring_prohash_scoring=public_route_scoring_prohash.add_resource("scoring")
        # /scoring/{pro_hash}/scoring/{link_id}
        public_route_scoring_prohash_scoring_linkid=public_route_scoring_prohash_scoring.add_resource("{link_id}")
        # GET: /scoring/{pro_hash}/scoring/{link_id}
        scoring_linkid_get_integration=apigateway.LambdaIntegration(fn_pro_scoring_linkid_get)
        method_scoring_prohash=public_route_scoring_prohash_scoring_linkid.add_method(
            "GET",scoring_linkid_get_integration,
            api_key_required=True
        )

        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#



        #################################################################################
        # Usage plan and api key to "lock" API to only CFRONT calls
        #################################################################################
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
