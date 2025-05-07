import os

from constructs import Construct
from aws_cdk import(
    Stack,
    aws_s3 as s3,
    aws_apigateway as apigateway,
    aws_lambda as lambda_,
    aws_events as events,
    aws_iam as iam,
    Duration
)
import json

class ApigStack(Stack):
    def __init__(self,scope: Construct, construct_id: str,  dynamodb_tables:dict, cfront_user_portal_domain_name, ebus_pro:events.EventBus, cognito_userpool, bucket_propack,**kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)


        IDENTIFIER_PRO_QUESTION="custom.lambda.pro.question"
        IDENTIFIER_PRO_SCORING="custom.lambda.pro.scoring"
        IDENTIFIER_PRO_STATE="custom.lambda.pro.state"
        IDENTIFIER_USER="custom.lambda.user.profile"
        IDENTIFIER_SURVEY="custom.lambda.survey"
        IDENTIFIER_AGGREGATES="custom.lambda.aggregates"
        IDENTIFIER_PTREPORTING="custom.lambda.ptreporting"
        IDENTIFIER_AUTHORIZER="custom.lambda.authorizer.core"
        IDENTIFIER_AUTHORIZER_DEBUG="custom.lambda.authorizer.debug"
        IDENTIFIER_NOTIFICATIONS="custom.lambda.notifications"
        IDENTIFIER_QOL="custom.lambda.qol"
        DETAIL_TYPE_REPORTING="Survey Completed"
        
        FULL_CFRONT_URL="https://"+cfront_user_portal_domain_name
        LOCALHOST_ORIGIN="http://localhost:3000"

        # Allow all origins if env=dev
        env = self.node.try_get_context("env")
        if env == "dev":
            CORS_ALLOWED_ORIGIN = "*"
        else: 
            CORS_ALLOWED_ORIGIN = FULL_CFRONT_URL

        layer_cloudpro_lib = lambda_.LayerVersion.from_layer_version_arn(self,id="layer_cloudpro_lib",layer_version_arn=self.node.try_get_context("layer_arn"))
        #layer_boto_lib = lambda_.LayerVersion.from_layer_version_arn(self,id="layer_boto_lib",layer_version_arn=self.node.try_get_context("layer_boto_arn"))


        
        fn_authorizer_core = lambda_.Function(
            self,"fn-authorizer-core-dev",
            description="authorizer-core-dev", #microservice tag
            runtime=lambda_.Runtime.PYTHON_3_9,
            handler="index.handler",
            code=lambda_.Code.from_asset(os.path.join("cloudpro_cdk/lambda/apig","authorizer_core")),
            environment={
                "IDENTIFIER":IDENTIFIER_AUTHORIZER,
                "CORS_ALLOWED_ORIGIN":CORS_ALLOWED_ORIGIN
            },
            layers=[ layer_cloudpro_lib ]
        )
        fn_authorizer_debug = lambda_.Function(
            self,"fn-authorizer-debug-dev",
            description="authorizer-debug-dev", #microservice tag
            runtime=lambda_.Runtime.PYTHON_3_9,
            handler="index.handler",
            code=lambda_.Code.from_asset(os.path.join("cloudpro_cdk/lambda/apig","authorizer_debug")),
            environment={
                "IDENTIFIER":IDENTIFIER_AUTHORIZER_DEBUG,
                "CORS_ALLOWED_ORIGIN":CORS_ALLOWED_ORIGIN,
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
                allow_origins=[FULL_CFRONT_URL, LOCALHOST_ORIGIN if env=="dev" else ""])
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
                "CORS_ALLOWED_ORIGIN":CORS_ALLOWED_ORIGIN,
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
                "CORS_ALLOWED_ORIGIN":CORS_ALLOWED_ORIGIN,
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
                "CORS_ALLOWED_ORIGIN":CORS_ALLOWED_ORIGIN,
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
                "CORS_ALLOWED_ORIGIN":CORS_ALLOWED_ORIGIN,
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
                "CORS_ALLOWED_ORIGIN":CORS_ALLOWED_ORIGIN,
            },
            layers=[ layer_cloudpro_lib ]
        )
        dynamodb_tables["scoring"].grant_read_data(fn_pro_scoring_linkid_get)

        #################################################################################
        # /scoring/evaluate/{link_id}
        #################################################################################
        fn_pro_scoring_evaluate_post = lambda_.Function(
            self,"fn-pro-scoring-evaluate-post",
            description="pro-scoring-evaluate-post", #microservice tag
            runtime=lambda_.Runtime.PYTHON_3_9,
            handler="index.handler",
            code=lambda_.Code.from_asset(os.path.join("cloudpro_cdk/lambda/pro_scoring","pro_scoring_evaluate_post")),
            environment={
                "TABLE_SCORING":dynamodb_tables["scoring"].table_name,
                "IDENTIFIER":IDENTIFIER_PRO_SCORING,
                "CORS_ALLOWED_ORIGIN":CORS_ALLOWED_ORIGIN,
            },
            layers=[ layer_cloudpro_lib ]
        )
        dynamodb_tables["scoring"].grant_read_data(fn_pro_scoring_evaluate_post)


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
                "CORS_ALLOWED_ORIGIN":CORS_ALLOWED_ORIGIN,
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


        # POST: /scoring/evaluate/{link_id}
        public_route_scoring_evaluate=public_route_scoring.add_resource("evaluate")
        public_route_scoring_evaluate_link_id=public_route_scoring_evaluate.add_resource("{link_id}")
        scoring_prohash_evaluate_post_integration=apigateway.LambdaIntegration(fn_pro_scoring_evaluate_post)
        method_scoring_evaluate_link_id=public_route_scoring_evaluate_link_id.add_method(
            "POST",scoring_prohash_evaluate_post_integration,
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
                "CORS_ALLOWED_ORIGIN":CORS_ALLOWED_ORIGIN,
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
                "CORS_ALLOWED_ORIGIN":CORS_ALLOWED_ORIGIN,
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
                "CORS_ALLOWED_ORIGIN":CORS_ALLOWED_ORIGIN,
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
                "CORS_ALLOWED_ORIGIN":CORS_ALLOWED_ORIGIN,
            },
            layers=[ layer_cloudpro_lib ]
        )
        dynamodb_tables["state"].grant_read_write_data(fn_pro_state_init_post)
        dynamodb_tables["questionnaire"].grant_read_data(fn_pro_state_init_post)

        ###### Route Base = /state
        public_route_state=api_route.add_resource("state")

        # PUT: /state
        state_update_put_integration=apigateway.LambdaIntegration(fn_pro_state_update_put)
        method_state_prohash=public_route_state.add_method(
            "PUT",state_update_put_integration,
            authorizer=auth,
            api_key_required=True
        )


        # /state/{state_hash}
        public_route_state_statehash=public_route_state.add_resource("{state_hash}")
        # GET: /state/{state_hash}
        state_statehash_get_integration=apigateway.LambdaIntegration(fn_pro_state_statehash_get)
        method_state_prohash=public_route_state_statehash.add_method(
            "GET",state_statehash_get_integration,
            authorizer=auth,
            api_key_required=True
        )


        '''
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
        '''
        # POST: /state/init/{propack}/{state_hash}
        
        public_init_route_state=public_route_state.add_resource("init")
        public_init_route_pro_pack=public_init_route_state.add_resource("{pro_pack}")
        public_init_route_state_hash=public_init_route_pro_pack.add_resource("{state_hash}")
        
        # POST:
        state_statehash_get_integration=apigateway.LambdaIntegration(fn_pro_state_init_post)
        method_state_init=public_init_route_state_hash.add_method(
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

        '''
        # /state/update
        public_route_state_update=public_route_state.add_resource("update")
        # PUT: /state/update
        state_update_put_integration=apigateway.LambdaIntegration(fn_pro_state_update_put)
        method_state_prohash=public_route_state_update.add_method(
            "PUT",state_update_put_integration,
            authorizer=auth,
            api_key_required=True
        )
        '''

        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#


        profrole = iam.Role(self, "scheduler-role",
          assumed_by=iam.CompositePrincipal(
            iam.ServicePrincipal("scheduler.amazonaws.com"),
            iam.ServicePrincipal("lambda.amazonaws.com"),
            iam.ServicePrincipal("events.amazonaws.com")
            )
        )
        fn_scheduler_processing = lambda_.Function(
            self,"fn-scheduler-processing",
            description="scheduler-processing", #microservice tag
            runtime=lambda_.Runtime.PYTHON_3_9,
            handler="index.handler",
            role=profrole,
            code=lambda_.Code.from_asset(os.path.join("cloudpro_cdk/lambda/survey","scheduler_processing")),
            environment={
                "IDENTIFIER":"SCHEDULER.PROCESSING",
                "TABLE_SURVEY": dynamodb_tables["survey"].table_name,
                "TABLE_SURVEY_AUDIT": dynamodb_tables["survey_audit"].table_name,
                "TABLE_STATE": dynamodb_tables["state"].table_name
            },
            #layers=[layer_boto_lib]
            layers=[]
        )
        dynamodb_tables["survey"].grant_read_write_data(fn_scheduler_processing)
        dynamodb_tables["survey_audit"].grant_read_write_data(fn_scheduler_processing)
        dynamodb_tables["state"].grant_read_data(fn_scheduler_processing)

        # in production you'd likely want to pair this down (IE dynamically generate the policy on event scheduling)
        # technically should probably seperate on user profile creation to actually create an event and then trigger
        # the scheduling mechanics so we can separate duties
        profrole.attach_inline_policy(iam.Policy(self, "scheduler-policy",
            statements=[iam.PolicyStatement(
                actions=["scheduler:CreateSchedule","scheduler:GetSchedule","scheduler:UpdateSchedule"],
                resources=["*"]
            )             
            ]
        ))
        profrole.attach_inline_policy(iam.Policy(self, "scheduler-pass-policy",
            statements=[iam.PolicyStatement(
                actions=["iam:PassRole"],
                resources=[fn_scheduler_processing.role.role_arn]
            )]
        ))
        profrole.attach_inline_policy(iam.Policy(self, "scheduler-basic-execution-logging",
            statements=[iam.PolicyStatement(
                actions=["logs:CreateLogGroup","logs:CreateLogStream","logs:PutLogEvents"],
                resources=["*"]
            )             
            ]
        ))
        profrole.attach_inline_policy(iam.Policy(self, "scheduler-basic-explicit-invoke",
            statements=[iam.PolicyStatement(
                actions=["lambda:InvokeFunction"],
                resources=[fn_scheduler_processing.function_arn]
            )             
            ]
        ))
        profrole.attach_inline_policy(iam.Policy(self, "s3-functionality-list",
            statements=[iam.PolicyStatement(
                actions=["s3:ListObjectsInBucket"],
                resources=[bucket_propack.bucket_arn]
            )             
            ]
        ))
        profrole.attach_inline_policy(iam.Policy(self, "s3-functionality-put",
            statements=[iam.PolicyStatement(
                actions=["s3:PutObject"],
                resources=[bucket_propack.bucket_arn+"/*"]
            )             
            ]
        ))

        # create a role for mfa lambdas
        lambdarole = iam.Role(self, "lambda-role",
          assumed_by=iam.CompositePrincipal(
            iam.ServicePrincipal("lambda.amazonaws.com"),
            )
        )

        lambdarole.attach_inline_policy(iam.Policy(self, "dynamodb",
            statements=[iam.PolicyStatement(
                actions=["dynamodb:*", "cognito-idp:*", "sns:*"],
                resources=["*"]
            )             
            ]
        ))

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
                "CORS_ALLOWED_ORIGIN":CORS_ALLOWED_ORIGIN,
            },
            layers=[ layer_cloudpro_lib ]
        )
        dynamodb_tables["user"].grant_read_data(fn_user_profile_get)




        fn_user_profile_put = lambda_.Function(
            self,"fn-user_profile-put",
            description="user_profile-put", #microservice tag
            runtime=lambda_.Runtime.PYTHON_3_9,
            handler="index.handler",
            code=lambda_.Code.from_asset(os.path.join("cloudpro_cdk/lambda/user","user_profile_put")),
            role=profrole,
            environment={
                "TABLE_USER":dynamodb_tables["user"].table_name,
                "TABLE_SURGEON":dynamodb_tables["surgeons"].table_name,
                "IDENTIFIER":IDENTIFIER_USER,
                "CORS_ALLOWED_ORIGIN":CORS_ALLOWED_ORIGIN,
                "SCHEDULER_PROCESSING_ARN": fn_scheduler_processing.function_arn,
                "SCHEDULER_PROCESSING_ROLE": fn_scheduler_processing.role.role_arn
            },
            #layers=[ layer_cloudpro_lib,layer_boto_lib ]
            layers=[layer_cloudpro_lib]
        )

        #this access flows to our scheduler too
        dynamodb_tables["user"].grant_read_write_data(fn_user_profile_put)
        dynamodb_tables["surgeons"].grant_read_write_data(fn_user_profile_put)

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
                "CORS_ALLOWED_ORIGIN":CORS_ALLOWED_ORIGIN,
            },
            layers=[ layer_cloudpro_lib ]
        )
        dynamodb_tables["survey"].grant_read_data(fn_survey_get)

        fn_survey_patch = lambda_.Function(
            self,"fn-survey-patch",
            description="survey-patch", #microservice tag
            runtime=lambda_.Runtime.PYTHON_3_9,
            handler="index.handler",
            code=lambda_.Code.from_asset(os.path.join("cloudpro_cdk/lambda/survey","survey_patch")),
            environment={
                "TABLE_SURVEY":dynamodb_tables["survey"].table_name,
                "TABLE_AUDIT":dynamodb_tables["survey_audit"].table_name,
                "TABLE_STATE":dynamodb_tables["state"].table_name,
                "IDENTIFIER":IDENTIFIER_SURVEY,
                "CORS_ALLOWED_ORIGIN":CORS_ALLOWED_ORIGIN,
                "EBUS_PROPACK":ebus_pro.event_bus_name,
                "DETAIL_TYPE":DETAIL_TYPE_REPORTING
            },
            layers=[ layer_cloudpro_lib ]
        )
        dynamodb_tables["survey"].grant_read_write_data(fn_survey_patch)
        dynamodb_tables["state"].grant_read_data(fn_survey_patch)
        dynamodb_tables["survey_audit"].grant_read_write_data(fn_survey_patch)
        ebus_pro.grant_put_events_to(fn_survey_patch)

         ###### Route Base = /survey
        public_route_survey=api_route.add_resource("survey")
        
        # /survey/{sub}
        public_route_survey_sub=public_route_survey.add_resource("{sub}")
        # GET: /survey/{sub}
        survey_sub_get_integration=apigateway.LambdaIntegration(fn_survey_get)
        method_survey=public_route_survey_sub.add_method(
            "GET",survey_sub_get_integration,
            authorizer=auth,
            api_key_required=True
        )
        # PATCH: /survey/{sub}
        survey_sub_patch_integration=apigateway.LambdaIntegration(fn_survey_patch)
        method_survey=public_route_survey_sub.add_method(
            "PATCH",survey_sub_patch_integration,
            authorizer=auth,
            api_key_required=True
        )

        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#

        #################################################################################
        # /audit/{sid}
        #################################################################################
        fn_audit_get = lambda_.Function(
            self,"fn-audit-get",
            description="audit-get", #microservice tag
            runtime=lambda_.Runtime.PYTHON_3_9,
            handler="index.handler",
            code=lambda_.Code.from_asset(os.path.join("cloudpro_cdk/lambda/audit","audit_sid_get")),
            environment={
                "TABLE_AUDIT":dynamodb_tables["survey_audit"].table_name,
                "IDENTIFIER":IDENTIFIER_SURVEY,
                "CORS_ALLOWED_ORIGIN":CORS_ALLOWED_ORIGIN,
            },
            layers=[ layer_cloudpro_lib ]
        )
        dynamodb_tables["survey_audit"].grant_read_data(fn_audit_get)

         ###### Route Base = /audit
        public_route_survey=api_route.add_resource("audit")
        
        # /audit/{sid}
        public_route_audit_sid=public_route_survey.add_resource("{sid}")
        # GET: /audit/{sid}
        audit_sid_get_integration=apigateway.LambdaIntegration(fn_audit_get)
        method_survey=public_route_audit_sid.add_method(
            "GET",audit_sid_get_integration,
            authorizer=auth,
            api_key_required=True
        )

        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#




        #################################################################################
        # /aggregates/{agg}
        #################################################################################
        
        fn_aggs_get = lambda_.Function(
            self,"fn-aggs-get",
            description="aggs-get", #microservice tag
            runtime=lambda_.Runtime.PYTHON_3_9,
            handler="index.handler",
            code=lambda_.Code.from_asset(os.path.join("cloudpro_cdk/lambda/aggregates","agg_get")),
            environment={
                "TABLE_AGGREGATES":dynamodb_tables["aggregates"].table_name,
                "IDENTIFIER":IDENTIFIER_AGGREGATES,
                "CORS_ALLOWED_ORIGIN":CORS_ALLOWED_ORIGIN,
            },
            layers=[ layer_cloudpro_lib ]
        )
        dynamodb_tables["aggregates"].grant_read_data(fn_aggs_get)

         ###### Route Base = /aggregates
        public_route_aggregates=api_route.add_resource("aggregates")
        
        # /aggregates/{agg}
        public_route_aggregates_agg=public_route_aggregates.add_resource("{agg}")
        # GET:/aggregates/{agg}
        aggregate_agg_get_integration=apigateway.LambdaIntegration(fn_aggs_get)
        method_agg=public_route_aggregates_agg.add_method(
            "GET",aggregate_agg_get_integration,
            authorizer=auth,
            api_key_required=True
        )

        #################################################################################
        # /ptreporting/{sub}
        #################################################################################
        
        fn_ptreport_get = lambda_.Function(
            self,"fn-ptreport-get",
            description="ptreport-get", #microservice tag
            runtime=lambda_.Runtime.PYTHON_3_9,
            handler="index.handler",
            code=lambda_.Code.from_asset(os.path.join("cloudpro_cdk/lambda/ptreporting","ptreport_sub_get")),
            environment={
                "TABLE_PTREPORTING":dynamodb_tables["pt_reporting"].table_name,
                "IDENTIFIER":IDENTIFIER_PTREPORTING,
                "CORS_ALLOWED_ORIGIN":CORS_ALLOWED_ORIGIN,
            },
            layers=[ layer_cloudpro_lib ]
        )
        dynamodb_tables["pt_reporting"].grant_read_data(fn_ptreport_get)

         ###### Route Base = /ptreporting
        public_route_ptreporting=api_route.add_resource("ptreporting")
        
        # /ptreporting/{sub}
        public_route_ptreporting_sub=public_route_ptreporting.add_resource("{sub}")
        # GET:/ptreporting/{sub}
        ptreporting_ptreport_get_integration=apigateway.LambdaIntegration(fn_ptreport_get)
        method_ptreport_sub_get=public_route_ptreporting_sub.add_method(
            "GET",ptreporting_ptreport_get_integration,
            authorizer=auth,
            api_key_required=True
        )


        #################################################################################
        # /notifications/{sub}
        #################################################################################
        
        fn_notifications_get = lambda_.Function(
            self,"fn-notifications-get",
            description="notifications-get", #microservice tag
            runtime=lambda_.Runtime.PYTHON_3_9,
            handler="index.handler",
            code=lambda_.Code.from_asset(os.path.join("cloudpro_cdk/lambda/notifications","notification_get_sub")),
            environment={
                "TABLE_NOTIFICATIONS":dynamodb_tables["notifications"].table_name,
                "IDENTIFIER":IDENTIFIER_NOTIFICATIONS,
                "CORS_ALLOWED_ORIGIN":CORS_ALLOWED_ORIGIN,
            },
            layers=[ layer_cloudpro_lib ]
        )
        dynamodb_tables["notifications"].grant_read_data(fn_notifications_get)

        ###### Route Base = /notifications
        public_route_notifications=api_route.add_resource("notifications")
        
        # /notifications/{sub}
        public_route_notifications_sub=public_route_notifications.add_resource("{sub}")
        # GET:/ptreporting/{sub}
        ptreporting_notifications_get_integration=apigateway.LambdaIntegration(fn_notifications_get)
        method_notifications_sub_get=public_route_notifications_sub.add_method(
            "GET",ptreporting_notifications_get_integration,
            authorizer=auth,
            api_key_required=True
        )

        #################################################################################
        # /surgeon/
        #################################################################################
        
        fn_surgeon_init_post = lambda_.Function(
            self,"fn-surgeons-bd-init-post",
            description="surgeons-bd-init-post", #microservice tag
            runtime=lambda_.Runtime.PYTHON_3_9,
            handler="index.handler",
            code=lambda_.Code.from_asset(os.path.join("cloudpro_cdk/lambda/surgeon","backdoor_init_post")),
            environment={
                "TABLE_SURGEONS":dynamodb_tables["surgeons"].table_name,
                "IDENTIFIER":"BD_SURGEONS_INIT",
                "CORS_ALLOWED_ORIGIN":CORS_ALLOWED_ORIGIN,
            },
            layers=[ layer_cloudpro_lib ]
        )
        dynamodb_tables["surgeons"].grant_read_write_data(fn_surgeon_init_post)

        fn_surgeon_list = lambda_.Function(
            self,"fn-surgeons-list",
            description="surgeons-list", #microservice tag
            runtime=lambda_.Runtime.PYTHON_3_9,
            handler="index.handler",
            code=lambda_.Code.from_asset(os.path.join("cloudpro_cdk/lambda/surgeon","all_surgeons_get")),
            environment={
                "TABLE_SURGEONS":dynamodb_tables["surgeons"].table_name,
                "IDENTIFIER":"SURGEONS_LIST",
                "CORS_ALLOWED_ORIGIN":CORS_ALLOWED_ORIGIN,
            },
            layers=[ layer_cloudpro_lib ]
        )
        dynamodb_tables["surgeons"].grant_read_data(fn_surgeon_list)

        ###### Route Base = /surgeon
        public_route_surgeon=api_route.add_resource("surgeon")
        
        # /surgeon/init
        public_route_surgeon_init=public_route_surgeon.add_resource("init")
        # POST:/surgeon/init
        surgeon_init_post_integration=apigateway.LambdaIntegration(fn_surgeon_init_post)
        method_surgeon_init=public_route_surgeon_init.add_method(
            "POST",surgeon_init_post_integration,
            authorizer=auth,
            api_key_required=True
        )


        # /surgeon/list
        public_route_surgeon_list=public_route_surgeon.add_resource("list")
        # GET:/surgeon/init
        surgeon_list_get_integration=apigateway.LambdaIntegration(fn_surgeon_list)
        method_surgeon_list=public_route_surgeon_list.add_method(
            "GET",surgeon_list_get_integration,
            authorizer=auth,
            api_key_required=True
        )

        fn_surgeon_get = lambda_.Function(
            self,"fn-surgeon-get",
            description="surgeon-get", #microservice tag
            runtime=lambda_.Runtime.PYTHON_3_9,
            handler="index.handler",
            code=lambda_.Code.from_asset(os.path.join("cloudpro_cdk/lambda/surgeon","surgeon_get")),
            environment={
                "TABLE_SURGEONS":dynamodb_tables["surgeons"].table_name,
                "TABLE_USER":dynamodb_tables["user"].table_name,
                "TABLE_SURVEY":dynamodb_tables["survey"].table_name,
                "CORS_ALLOWED_ORIGIN":CORS_ALLOWED_ORIGIN,
            },
            layers=[ layer_cloudpro_lib ]
        )
        dynamodb_tables["surgeons"].grant_read_data(fn_surgeon_get)
        dynamodb_tables["user"].grant_read_data(fn_surgeon_get)
        dynamodb_tables["survey"].grant_read_data(fn_surgeon_get)

        fn_patient_details_get = lambda_.Function(
            self,"fn-patient-details-get",
            description="patient-details-get", #microservice tag
            runtime=lambda_.Runtime.PYTHON_3_9,
            handler="index.handler",
            code=lambda_.Code.from_asset(os.path.join("cloudpro_cdk/lambda/surgeon","patient_details_get")),
            environment={
                "TABLE_USER":dynamodb_tables["user"].table_name,
                "TABLE_SURVEY":dynamodb_tables["survey"].table_name,
                "TABLE_REPORTING":dynamodb_tables["pt_reporting"].table_name,
                "CORS_ALLOWED_ORIGIN":CORS_ALLOWED_ORIGIN,
            },
            layers=[ layer_cloudpro_lib ]
        )
        dynamodb_tables["user"].grant_read_data(fn_patient_details_get)
        dynamodb_tables["survey"].grant_read_data(fn_patient_details_get)
        dynamodb_tables["pt_reporting"].grant_read_data(fn_patient_details_get)

        fn_all_patient_details_get = lambda_.Function(
            self,"fn-all-patient-details-get",
            description="all-patient-details-get", #microservice tag
            runtime=lambda_.Runtime.PYTHON_3_9,
            handler="index.handler",
            code=lambda_.Code.from_asset(os.path.join("cloudpro_cdk/lambda/surgeon","all_patient_details_get")),
            environment={
                "TABLE_USER":dynamodb_tables["user"].table_name,
                "TABLE_SURVEY":dynamodb_tables["survey"].table_name,
                "TABLE_REPORTING":dynamodb_tables["pt_reporting"].table_name,
                "TABLE_SURGEONS":dynamodb_tables["surgeons"].table_name,
                "CORS_ALLOWED_ORIGIN":CORS_ALLOWED_ORIGIN,
            },
            layers=[ layer_cloudpro_lib ]
        )
        dynamodb_tables["user"].grant_read_data(fn_all_patient_details_get)
        dynamodb_tables["survey"].grant_read_data(fn_all_patient_details_get)
        dynamodb_tables["pt_reporting"].grant_read_data(fn_all_patient_details_get)
        dynamodb_tables["surgeons"].grant_read_data(fn_all_patient_details_get)
        
        # /surgeon/{sub}
        public_route_surgeon_init=public_route_surgeon.add_resource("{sub}")
        # GET:/surgeon/{sub}
        surgeon_init_get_integration=apigateway.LambdaIntegration(fn_surgeon_get)
        method_patient_list=public_route_surgeon_init.add_method(
            "GET",surgeon_init_get_integration,
            authorizer=auth,
            api_key_required=True
        )

        # /surgeon/patient-details/{sub}
        public_route_surgeon_init=public_route_surgeon.add_resource("patient-details")
        public_route_patient_details_init=public_route_surgeon_init.add_resource("{sub}")
        # GET:/surgeon/patient-details/{sub}
        surgeon_init_get_integration=apigateway.LambdaIntegration(fn_patient_details_get)
        method_patient_details=public_route_patient_details_init.add_method(
            "GET",surgeon_init_get_integration,
            authorizer=auth,
            api_key_required=True
        )

        # /surgeon/all-patient-details/{sub}
        public_route_surgeon_init=public_route_surgeon.add_resource("all-patient-details")
        public_route_all_patient_details_init=public_route_surgeon_init.add_resource("{sub}")
        # GET:/surgeon/patient-details/{sub}
        surgeon_init_get_integration=apigateway.LambdaIntegration(fn_all_patient_details_get)
        method_all_patient_details=public_route_all_patient_details_init.add_method(
            "GET",surgeon_init_get_integration,
            authorizer=auth,
            api_key_required=True
        )

        #################################################################################
        # /mfa/
        #################################################################################

        fn_set_mfa_preference = lambda_.Function(
            self,"fn-mfa-set-preference",
            description="mfa-set-preference", #microservice tag
            runtime=lambda_.Runtime.PYTHON_3_9,
            handler="index.handler",
            code=lambda_.Code.from_asset(os.path.join("cloudpro_cdk/lambda/mfa","set_mfa_preference")),
            role=lambdarole,
            environment={
                "USERPOOL_ID":cognito_userpool.user_pool_id,
                "CORS_ALLOWED_ORIGIN":CORS_ALLOWED_ORIGIN,
            },
            layers=[ layer_cloudpro_lib ]
        )

        fn_verify_otp = lambda_.Function(
            self,"fn-mfa-verify-otp",
            description="mfa-verify-otp", #microservice tag
            runtime=lambda_.Runtime.PYTHON_3_9,
            handler="index.handler",
            code=lambda_.Code.from_asset(os.path.join("cloudpro_cdk/lambda/mfa","verify_otp")),
            role=lambdarole,
            environment={
                "TABLE_OTP":dynamodb_tables["otp_staged"].table_name,
                "USERPOOL_ID":cognito_userpool.user_pool_id,
                "CORS_ALLOWED_ORIGIN":CORS_ALLOWED_ORIGIN,
            },
            layers=[ layer_cloudpro_lib ]
        )
        dynamodb_tables["otp_staged"].grant_read_write_data(fn_verify_otp)

        fn_send_otp = lambda_.Function(
            self,"fn-mfa-send-otp",
            description="mfa-send-otp", #microservice tag
            runtime=lambda_.Runtime.PYTHON_3_9,
            handler="index.handler",
            code=lambda_.Code.from_asset(os.path.join("cloudpro_cdk/lambda/mfa","send_otp")),
            role=lambdarole,
            environment={
                "TABLE_OTP":dynamodb_tables["otp_staged"].table_name,
                "ENV":env,
                "CORS_ALLOWED_ORIGIN":CORS_ALLOWED_ORIGIN,
            },
            layers=[ layer_cloudpro_lib ]
        )
        dynamodb_tables["otp_staged"].grant_read_write_data(fn_send_otp)

        ###### Route Base = /mfa
        public_route_mfa=api_route.add_resource("mfa")
        
        # /mfa/set-preference
        public_mfa_set_preference=public_route_mfa.add_resource("set-preference")
        # POST:/mfa/set-preference
        mfa_set_preference_post_integration=apigateway.LambdaIntegration(fn_set_mfa_preference)
        method_mfa_set_preference=public_mfa_set_preference.add_method(
            "POST",mfa_set_preference_post_integration,
            api_key_required=True
        )

        # /mfa/{phone}
        public_mfa_send_otp=public_route_mfa.add_resource("{phone}")
        # GET:/mfa/{phone}
        mfa_send_otp_post_integration=apigateway.LambdaIntegration(fn_send_otp)
        method_mfa_set_preference=public_mfa_send_otp.add_method(
            "GET",mfa_send_otp_post_integration,
            authorizer=auth,
            api_key_required=True
        )

        # /mfa/verify
        public_mfa_verify_otp=public_route_mfa.add_resource("verify")
        # POST:/mfa/verify
        mfa_set_preference_post_integration=apigateway.LambdaIntegration(fn_verify_otp)
        method_mfa_verify_otp=public_mfa_verify_otp.add_method(
            "POST",mfa_set_preference_post_integration,
            authorizer=auth,
            api_key_required=True
        )

        #################################################################################
        # /hospital/
        #################################################################################
        fn_hospital_init_post = lambda_.Function(
            self,"fn-hospitals-bd-init-post",
            description="hospitals-bd-init-post", #microservice tag
            runtime=lambda_.Runtime.PYTHON_3_9,
            handler="index.handler",
            code=lambda_.Code.from_asset(os.path.join("cloudpro_cdk/lambda/hospitals","backdoor_init_post")),
            environment={
                "TABLE_HOSPITALS":dynamodb_tables["hospitals"].table_name,
                "IDENTIFIER":"BD_HOSPITALS_INIT",
                "CORS_ALLOWED_ORIGIN":CORS_ALLOWED_ORIGIN,
            },
            layers=[ layer_cloudpro_lib ]
        )
        dynamodb_tables["hospitals"].grant_read_write_data(fn_hospital_init_post)

        fn_hospital_list = lambda_.Function(
            self,"fn-hospital-list",
            description="hospital-list", #microservice tag
            runtime=lambda_.Runtime.PYTHON_3_9,
            handler="index.handler",
            code=lambda_.Code.from_asset(os.path.join("cloudpro_cdk/lambda/hospitals","all_hospitals_get")),
            environment={
                "TABLE_HOSPITALS":dynamodb_tables["hospitals"].table_name,
                "IDENTIFIER":"HOSPITALS_LIST",
                "CORS_ALLOWED_ORIGIN":CORS_ALLOWED_ORIGIN,
            },
            layers=[ layer_cloudpro_lib ]
        )
        dynamodb_tables["hospitals"].grant_read_data(fn_hospital_list)

        fn_hospital_hid_get = lambda_.Function(
            self,"fn-hospital-hid-get",
            description="hospital-hid-get", #microservice tag
            runtime=lambda_.Runtime.PYTHON_3_9,
            handler="index.handler",
            code=lambda_.Code.from_asset(os.path.join("cloudpro_cdk/lambda/hospitals","hospital_hid_get")),
            environment={
                "TABLE_HOSPITALS":dynamodb_tables["hospitals"].table_name,
                "IDENTIFIER":"HOSPITALS_LIST",
                "CORS_ALLOWED_ORIGIN":CORS_ALLOWED_ORIGIN,
            },
            layers=[ layer_cloudpro_lib ]
        )
        dynamodb_tables["hospitals"].grant_read_data(fn_hospital_hid_get)

        ###### Route Base = /hospitals
        public_route_hospital=api_route.add_resource("hospital")
        
        # /hospital/init
        public_route_hospital_init=public_route_hospital.add_resource("init")
        # POST:/surgeon/init
        hospital_init_post_integration=apigateway.LambdaIntegration(fn_hospital_init_post)
        method_hospital_init=public_route_hospital_init.add_method(
            "POST",hospital_init_post_integration,
            authorizer=auth,
            api_key_required=True
        )


        # /hospital/list
        public_route_hospital_list=public_route_hospital.add_resource("list")
        # GET:/hospital/init
        hospital_list_get_integration=apigateway.LambdaIntegration(fn_hospital_list)
        method_hospital_list=public_route_hospital_list.add_method(
            "GET",hospital_list_get_integration,
            authorizer=auth,
            api_key_required=True
        )

        # GET:/hospital/by_hid/
        public_route_hospital_by_hid=public_route_hospital.add_resource("hid")
        # GET:/hospital/by_hid/{hid}
        public_route_hospital_by_hid_hidid=public_route_hospital_by_hid.add_resource("{hid}")
        public_route_hospital_by_hid_hidid_integration=apigateway.LambdaIntegration(fn_hospital_hid_get)
        method_notifications_sub_get=public_route_hospital_by_hid_hidid.add_method(
            "GET",public_route_hospital_by_hid_hidid_integration,
            authorizer=auth,
            api_key_required=True
        )

        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#

        fn_qol_simulate_proupload = lambda_.Function(
            self,"fn-qol-simulate-proupload-get",
            description="qol_simulate_prupload-get", #microservice tag
            runtime=lambda_.Runtime.PYTHON_3_9,
            handler="index.handler",
            code=lambda_.Code.from_asset(os.path.join("cloudpro_cdk/lambda/qol","uploader")),
            role=profrole,
            environment={
                "IDENTIFIER":IDENTIFIER_QOL,
                "CORS_ALLOWED_ORIGIN":CORS_ALLOWED_ORIGIN,
                "BUCKET_PROPACK_NAME":bucket_propack.bucket_name
            },
            #layers=[ layer_cloudpro_lib,layer_boto_lib ]
            layers=[layer_cloudpro_lib]
        )


        fn_qol_simulate_schedule = lambda_.Function(
            self,"fn-qol-simulate-schedule-post",
            description="qol_simulate_schedule-post", #microservice tag
            runtime=lambda_.Runtime.PYTHON_3_9,
            handler="index.handler",
            code=lambda_.Code.from_asset(os.path.join("cloudpro_cdk/lambda/qol","simulate_schedule")),
            role=profrole,
            environment={
                "IDENTIFIER":IDENTIFIER_QOL,
                "CORS_ALLOWED_ORIGIN":CORS_ALLOWED_ORIGIN,
                "SCHEDULER_PROCESSING_ARN": fn_scheduler_processing.function_arn,
                "SCHEDULER_PROCESSING_ROLE": fn_scheduler_processing.role.role_arn
            },
            #layers=[ layer_cloudpro_lib,layer_boto_lib ]
            layers=[layer_cloudpro_lib]
        )
         ###### Route Base = /qol
        public_route_qol=api_route.add_resource("qol")
        
        # /qol/simulate/
        public_route_simulate=public_route_qol.add_resource("simulatesched")
        # /qol/simulate/rollover
        public_route_simulate_rollover=public_route_simulate.add_resource("rollover")
        # POST:# /qol/simulate/rollover
        simulate_rollover_post_integration=apigateway.LambdaIntegration(fn_qol_simulate_schedule)
        method_simulate_rollover_post=public_route_simulate_rollover.add_method(
            "POST",simulate_rollover_post_integration,
            authorizer=auth,
            api_key_required=True
        )
        # /qol/uploader/
        public_route_uploader=public_route_qol.add_resource("uploader")
        # GET:# /qol/uploader
        uploader_post_integration=apigateway.LambdaIntegration(fn_qol_simulate_proupload)
        method_uploader_post=public_route_uploader.add_method(
            "POST",uploader_post_integration,
            authorizer=auth,
            api_key_required=True
        )

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
