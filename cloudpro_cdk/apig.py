import os

from constructs import Construct
from aws_cdk import(
    Stack,
    aws_apigateway as apigateway,
    aws_lambda as lambda_,
    aws_iam as iam,
    Duration
)

class ApigStack(Stack):
    def __init__(self,scope: Construct, construct_id: str,  dynamodb_tables:dict, cfront_user_portal_domain_name, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)


        IDENTIFIER_PRO_QUESTION="custom.lambda.pro.question"
        IDENTIFIER_PRO_SCORING="custom.lambda.pro.scoring"
        IDENTIFIER_PRO_STATE="custom.lambda.pro.state"
        IDENTIFIER_USER="custom.lambda.user.profile"
        IDENTIFIER_SURVEY="custom.lambda.survey"
        IDENTIFIER_AUTHORIZER="custom.lambda.authorizer.core"
        IDENTIFIER_AUTHORIZER_DEBUG="custom.lambda.authorizer.debug"
        FULL_CFRONT_URL="https://"+cfront_user_portal_domain_name


        layer_cloudpro_lib = lambda_.LayerVersion.from_layer_version_arn(self,id="layer_cloudpro_lib",layer_version_arn=self.node.try_get_context("layer_arn"))
        layer_boto_lib = lambda_.LayerVersion.from_layer_version_arn(self,id="layer_boto_lib",layer_version_arn=self.node.try_get_context("layer_boto_arn"))


        
        fn_authorizer_core = lambda_.Function(
            self,"fn-authorizer-core",
            description="authorizer-core", #microservice tag
            runtime=lambda_.Runtime.PYTHON_3_9,
            handler="index.handler",
            code=lambda_.Code.from_asset(os.path.join("cloudpro_cdk/lambda/apig","authorizer_core")),
            environment={
                "IDENTIFIER":IDENTIFIER_AUTHORIZER,
                "CORS_ALLOW_UI":FULL_CFRONT_URL
            },
            layers=[ layer_cloudpro_lib ]
        )
        fn_authorizer_debug = lambda_.Function(
            self,"fn-authorizer-debug",
            description="authorizer-debug", #microservice tag
            runtime=lambda_.Runtime.PYTHON_3_9,
            handler="index.handler",
            code=lambda_.Code.from_asset(os.path.join("cloudpro_cdk/lambda/apig","authorizer_debug")),
            environment={
                "IDENTIFIER":IDENTIFIER_AUTHORIZER_DEBUG,
                "CORS_ALLOW_UI":FULL_CFRONT_URL,
                "DEBUG_TOKEN":self.node.try_get_context("debug_token")
            },
            layers=[ layer_cloudpro_lib ]
        )

        # we are disabling cahing on this authorizer due to an issue when calling
        # GET /user/{id}  
        # followed by 
        # PUT /user
        # initial GET call caches the policy for /user , however when we do a PUT, we have a hit but mismatch
        # ultimately failing the call
        auth = apigateway.TokenAuthorizer(self, "coreAuth",
            handler=fn_authorizer_core,
            results_cache_ttl=Duration.seconds(0)
        )

        '''
        auth_debug = apigateway.TokenAuthorizer(self, "debugAuth",
            handler=fn_authorizer_debug,
            results_cache_ttl=Duration.seconds(0)
        )
        '''




        core_api = apigateway.RestApi(
            self,"core-api",
            endpoint_configuration=apigateway.EndpointConfiguration(
                types=[apigateway.EndpointType.REGIONAL]
            ),
            default_cors_preflight_options=apigateway.CorsOptions(
                allow_methods=['GET', 'OPTIONS','PUT','PATCH','POST'],
                allow_origins=[FULL_CFRONT_URL])
        )
 
    
        










        ###### Route Base = /api [match for cloud front purposes]
        api_route = core_api.root.add_resource("api")
        







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
                "IDENTIFIER":IDENTIFIER_PRO_QUESTION,
                "CORS_ALLOW_UI":FULL_CFRONT_URL
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
                "IDENTIFIER":IDENTIFIER_PRO_QUESTION,
                "CORS_ALLOW_UI":FULL_CFRONT_URL
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
                "IDENTIFIER":IDENTIFIER_PRO_QUESTION,
                "CORS_ALLOW_UI":FULL_CFRONT_URL
            },
            layers=[ layer_cloudpro_lib ]
        )
        dynamodb_tables["questionnaire"].grant_read_data(fn_pro_question_all_get)

        
        

        ###### Route Base = /questionnaire
        public_route_questionnaire=api_route.add_resource("questionnaire")
        # /questionnaire/all
        public_route_questionnaire_all=public_route_questionnaire.add_resource("all")
        # GET: /questionnaire/all
        question_all_get_integration=apigateway.LambdaIntegration(fn_pro_question_all_get)
        method_questionnaire_prohash=public_route_questionnaire_all.add_method(
            "GET",question_all_get_integration,
            authorizer=auth,
            api_key_required=True
        )
        # /questionnaire/{pro_hash}
        public_route_questionnaire_prohash=public_route_questionnaire.add_resource("{pro_hash}")
         # GET: /questionnaire/{pro_hash}
        question_prohash_get_integration=apigateway.LambdaIntegration(fn_pro_question_prohash_get)
        method_questionnaire_prohash=public_route_questionnaire_prohash.add_method(
            "GET",question_prohash_get_integration,
            authorizer=auth,
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
            authorizer=auth,
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
                "IDENTIFIER":IDENTIFIER_PRO_SCORING,
                "CORS_ALLOW_UI":FULL_CFRONT_URL
            },
            layers=[ layer_cloudpro_lib ]
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
                "IDENTIFIER":IDENTIFIER_PRO_SCORING,
                "CORS_ALLOW_UI":FULL_CFRONT_URL
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
                "IDENTIFIER":IDENTIFIER_PRO_SCORING,
                "CORS_ALLOW_UI":FULL_CFRONT_URL
            },
            layers=[ layer_cloudpro_lib ]
        )
        dynamodb_tables["scoring"].grant_read_data(fn_pro_scoring_all_get)

        
        
        ###### Route Base = /scoring
        public_route_scoring=api_route.add_resource("scoring")
        # /scoring/all
        public_route_scoring_all=public_route_scoring.add_resource("all")
        # GET: /scoring/all
        scoring_all_get_integration=apigateway.LambdaIntegration(fn_pro_scoring_all_get)
        method_scoring_prohash=public_route_scoring_all.add_method(
            "GET",scoring_all_get_integration,
            authorizer=auth,
            api_key_required=True
        )
        # /scoring/{pro_hash}
        public_route_scoring_prohash=public_route_scoring.add_resource("{pro_hash}")
         # GET: /scoring/{pro_hash}
        scoring_prohash_get_integration=apigateway.LambdaIntegration(fn_pro_scoring_prohash_get)
        method_scoring_prohash=public_route_scoring_prohash.add_method(
            "GET",scoring_prohash_get_integration,
            authorizer=auth,
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
            authorizer=auth,
            api_key_required=True
        )

        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#

        #################################################################################
        # /state/{state_hash}
        #################################################################################
        fn_pro_state_statehash_get = lambda_.Function(
            self,"fn-pro-state-statehash-get",
            description="pro-state-statehash-get", #microservice tag
            runtime=lambda_.Runtime.PYTHON_3_9,
            handler="index.handler",
            code=lambda_.Code.from_asset(os.path.join("cloudpro_cdk/lambda/pro_state","pro_state_statehash_get")),
            environment={
                "TABLE_STATE":dynamodb_tables["state"].table_name,
                "IDENTIFIER":IDENTIFIER_PRO_STATE,
                "CORS_ALLOW_UI":FULL_CFRONT_URL
            },
            layers=[ layer_cloudpro_lib ]
        )
        dynamodb_tables["state"].grant_read_data(fn_pro_state_statehash_get)

        #################################################################################
        # /state/{state_hash}  [patch]
        #################################################################################
        fn_pro_state_statehash_patch = lambda_.Function(
            self,"fn-pro-state-statehash-patch",
            description="pro-state-statehash-patch", #microservice tag
            runtime=lambda_.Runtime.PYTHON_3_9,
            handler="index.handler",
            code=lambda_.Code.from_asset(os.path.join("cloudpro_cdk/lambda/pro_state","pro_state_statehash_patch")),
            environment={
                "TABLE_STATE":dynamodb_tables["state"].table_name,
                "IDENTIFIER":IDENTIFIER_PRO_STATE,
                "CORS_ALLOW_UI":FULL_CFRONT_URL
            },
            layers=[ layer_cloudpro_lib ]
        )
        dynamodb_tables["state"].grant_read_write_data(fn_pro_state_statehash_patch)


        #################################################################################
        # /state/update [put]
        #################################################################################
        fn_pro_state_update_put = lambda_.Function(
            self,"fn-pro-state-update-put",
            description="pro-state-update-put", #microservice tag
            runtime=lambda_.Runtime.PYTHON_3_9,
            handler="index.handler",
            code=lambda_.Code.from_asset(os.path.join("cloudpro_cdk/lambda/pro_state","pro_state_update_put")),
            environment={
                "TABLE_STATE":dynamodb_tables["state"].table_name,
                "IDENTIFIER":IDENTIFIER_PRO_STATE,
                "CORS_ALLOW_UI":FULL_CFRONT_URL
            },
            layers=[ layer_cloudpro_lib ]
        )
        dynamodb_tables["state"].grant_read_write_data(fn_pro_state_update_put)
        

        #################################################################################
        # /state/init/{state_hash}/{propack}
        #################################################################################
        fn_pro_state_init_post = lambda_.Function(
            self,"fn-pro-state-init-post",
            description="pro-state-init-post", #microservice tag
            runtime=lambda_.Runtime.PYTHON_3_9,
            handler="index.handler",
            code=lambda_.Code.from_asset(os.path.join("cloudpro_cdk/lambda/pro_state","pro_state_init")),
            environment={
                "TABLE_STATE":dynamodb_tables["state"].table_name,
                "TABLE_QUESTIONNAIRE":dynamodb_tables["questionnaire"].table_name,
                "IDENTIFIER":IDENTIFIER_PRO_STATE,
                "CORS_ALLOW_UI":FULL_CFRONT_URL
            },
            layers=[ layer_cloudpro_lib ]
        )
        dynamodb_tables["state"].grant_read_write_data(fn_pro_state_init_post)
        dynamodb_tables["questionnaire"].grant_read_data(fn_pro_state_init_post)

        ###### Route Base = /state
        public_route_state=api_route.add_resource("state")
        # /state/{state_hash}
        public_route_state_statehash=public_route_state.add_resource("{state_hash}")
        # GET: /state/{state_hash}
        state_statehash_get_integration=apigateway.LambdaIntegration(fn_pro_state_statehash_get)
        method_state_prohash=public_route_state_statehash.add_method(
            "GET",state_statehash_get_integration,
            authorizer=auth,
            api_key_required=True
        )


        # POST: /state/init/{state_hash}/{propack}
        public_init_route_state=public_route_state.add_resource("init")
        public_init_route_state_hash=public_init_route_state.add_resource("{state_hash}")
        public_init_route_pro_pack=public_init_route_state_hash.add_resource("{pro_pack}")
        # POST:
        state_statehash_get_integration=apigateway.LambdaIntegration(fn_pro_state_init_post)
        method_state_init=public_init_route_pro_pack.add_method(
            "POST",state_statehash_get_integration,
            authorizer=auth,
            api_key_required=True
        )



        # PATCH: /state/{state_hash}
        state_statehash_patch_integration=apigateway.LambdaIntegration(fn_pro_state_statehash_patch)
        method_state_prohash_patch=public_route_state_statehash.add_method(
            "PATCH",state_statehash_patch_integration,
            authorizer=auth,
            api_key_required=True,
            request_parameters={
                'method.request.querystring.profile': True,
                'method.request.querystring.username': True,
            }
        )

        # /state/update
        public_route_state_update=public_route_state.add_resource("update")
        # PUT: /state/update
        state_update_put_integration=apigateway.LambdaIntegration(fn_pro_state_update_put)
        method_state_prohash=public_route_state_update.add_method(
            "PUT",state_update_put_integration,
            authorizer=auth,
            api_key_required=True
        )

        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#

        fn_scheduler_processing = lambda_.Function(
            self,"fn-scheduler-processing",
            description="scheduler-processing", #microservice tag
            runtime=lambda_.Runtime.PYTHON_3_9,
            handler="index.handler",
            code=lambda_.Code.from_asset(os.path.join("cloudpro_cdk/lambda/survey","scheduler_processing")),
            environment={
                "IDENTIFIER":"SCHEDULER.PROCESSING"
            },
            layers=[layer_boto_lib]
        )
        #"SCHEDULER_PROCESSING_ARN": fn_scheduler_processing.function_arn
        #################################################################################
        # /user/{sub}
        #################################################################################
        fn_user_profile_get = lambda_.Function(
            self,"fn-user_profile-get",
            description="user_profile-get", #microservice tag
            runtime=lambda_.Runtime.PYTHON_3_9,
            handler="index.handler",
            code=lambda_.Code.from_asset(os.path.join("cloudpro_cdk/lambda/user","user_profile_get")),
            environment={
                "TABLE_USER":dynamodb_tables["user"].table_name,
                "IDENTIFIER":IDENTIFIER_USER,
                "CORS_ALLOW_UI":FULL_CFRONT_URL
            },
            layers=[ layer_cloudpro_lib ]
        )
        dynamodb_tables["user"].grant_read_data(fn_user_profile_get)



        profrole = iam.Role(self, "Role",
          assumed_by=iam.CompositePrincipal(
            iam.ServicePrincipal("scheduler.amazonaws.com"),
            iam.ServicePrincipal("lambda.amazonaws.com"),
            iam.ServicePrincipal("events.amazonaws.com")
            )
        )

        fn_user_profile_put = lambda_.Function(
            self,"fn-user_profile-put",
            description="user_profile-put", #microservice tag
            runtime=lambda_.Runtime.PYTHON_3_9,
            handler="index.handler",
            code=lambda_.Code.from_asset(os.path.join("cloudpro_cdk/lambda/user","user_profile_put")),
            role=profrole,
            environment={
                "TABLE_USER":dynamodb_tables["user"].table_name,
                "IDENTIFIER":IDENTIFIER_USER,
                "CORS_ALLOW_UI":FULL_CFRONT_URL,
                "SCHEDULER_PROCESSING_ARN": fn_scheduler_processing.function_arn,
                "SCHEDULER_PROCESSING_ROLE": fn_scheduler_processing.role.role_arn
            },
            layers=[ layer_cloudpro_lib,layer_boto_lib ]
        )

        # in production you'd likely want to pair this down (IE dynamically generate the policy on event scheduling)
        # technically should probably seperate on user profile creation to actually create an event and then trigger
        # the scheduling mechanics so we can separate duties
        fn_user_profile_put.role.attach_inline_policy(iam.Policy(self, "scheduler-policy",
            statements=[iam.PolicyStatement(
                actions=["scheduler:CreateSchedule"],
                resources=["*"]
            )             
            ]
        ))
        fn_user_profile_put.role.attach_inline_policy(iam.Policy(self, "scheduler-pass-policy",
            statements=[iam.PolicyStatement(
                actions=["iam:PassRole"],
                resources=[fn_scheduler_processing.role.role_arn]
            )]
        ))
        


        dynamodb_tables["user"].grant_read_write_data(fn_user_profile_put)

        ###### Route Base = /user
        public_route_user=api_route.add_resource("user")
        # PUT: /user/
        user_sub_put_integration=apigateway.LambdaIntegration(fn_user_profile_put)
        method_user_profile_put=public_route_user.add_method(
            "PUT",user_sub_put_integration,
            authorizer=auth,
            api_key_required=True
        )
        
        # /user/{sub}
        public_route_user_sub=public_route_user.add_resource("{sub}")
        # GET: /user/{sub}
        user_sub_get_integration=apigateway.LambdaIntegration(fn_user_profile_get)
        method_user_profile=public_route_user_sub.add_method(
            "GET",user_sub_get_integration,
            authorizer=auth,
            api_key_required=True
        )
        
        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#

        #################################################################################
        # /survey/{sub}
        #################################################################################
        fn_survey_get = lambda_.Function(
            self,"fn-survey-get",
            description="survey-get", #microservice tag
            runtime=lambda_.Runtime.PYTHON_3_9,
            handler="index.handler",
            code=lambda_.Code.from_asset(os.path.join("cloudpro_cdk/lambda/survey","survey_get")),
            environment={
                "TABLE_SURVEY":dynamodb_tables["survey"].table_name,
                "IDENTIFIER":IDENTIFIER_SURVEY,
                "CORS_ALLOW_UI":FULL_CFRONT_URL
            },
            layers=[ layer_cloudpro_lib ]
        )
        dynamodb_tables["survey"].grant_read_data(fn_survey_get)

         ###### Route Base = /survey
        public_route_survey=api_route.add_resource("survey")
        
        # /user/{sub}
        public_route_survey_sub=public_route_survey.add_resource("{sub}")
        # GET: /user/{sub}
        survey_sub_get_integration=apigateway.LambdaIntegration(fn_survey_get)
        method_survey=public_route_survey_sub.add_method(
            "GET",survey_sub_get_integration,
            authorizer=auth,
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
