from aws_cdk import (
    Stack,
    aws_cognito as cognito,
    aws_lambda as lambda_,
    aws_iam as iam
)
import json
import os
from constructs import Construct

class CognitoStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, dynamodb_user_table,dynamodb_user_staged_table,**kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        COGNITO_POOL="cognito-up-cloudpro"
        ######################################################################################################
        # Custom Cognito Lambda's
        ######################################################################################################
        fn_cognito_define_auth_challenge = lambda_.Function(
            self,"fn-cognito-define-auth-challenge",
            description="cognito-define-auth-challenge", #microservice tag
            runtime=lambda_.Runtime.PYTHON_3_9,
            handler="index.handler",
            code=lambda_.Code.from_asset(os.path.join("cloudpro_cdk/lambda/cognito","cognito_define_auth_challenge")),
            environment={
                "IDENTIFIER":"COGNITO.DEFINE_AUTH_CHALLENGE",
                "COGNITO_POOL":COGNITO_POOL
            },
            layers=[]
        ) 
        fn_cognito_create_auth_challenge = lambda_.Function(
            self,"fn-cognito-create-auth-challenge",
            description="cognito-create-auth-challenge", #microservice tag
            runtime=lambda_.Runtime.PYTHON_3_9,
            handler="index.handler",
            code=lambda_.Code.from_asset(os.path.join("cloudpro_cdk/lambda/cognito","cognito_create_auth_challenge")),
            environment={
                "IDENTIFIER":"COGNITO.CREATE_AUTH_CHALLENGE",
                "COGNITO_POOL":COGNITO_POOL
            },
            layers=[]
        )   
        fn_cognito_verify_auth_challenge = lambda_.Function(
            self,"fn-cognito-verify-auth-challenge",
            description="cognito-verify-auth-challenge-response", #microservice tag
            runtime=lambda_.Runtime.PYTHON_3_9,
            handler="index.handler",
            code=lambda_.Code.from_asset(os.path.join("cloudpro_cdk/lambda/cognito","cognito_verify_auth_challenge")),
            environment={
                "IDENTIFIER":"COGNITO.VERIFY_AUTH_CHALLENGE",
                "COGNITO_POOL":COGNITO_POOL
            },
            layers=[]
        )




        fn_cognito_post_confirmation = lambda_.Function(
            self,"fn-cognito-post-confirmation",
            description="cognito-post-confirmation", #microservice tag
            runtime=lambda_.Runtime.PYTHON_3_9,
            handler="index.handler",
            code=lambda_.Code.from_asset(os.path.join("cloudpro_cdk/lambda/cognito","cognito_post_confirmation")),
            environment={
                "IDENTIFIER":"COGNITO.POST_CONFIRMATION",
                "COGNITO_POOL":COGNITO_POOL,
                "TABLE_USER": dynamodb_user_table.table_name,
                "TABLE_USER_STAGED": dynamodb_user_staged_table.table_name
            },
            layers=[]
        ) 
        dynamodb_user_table.grant_read_write_data(fn_cognito_post_confirmation)
        dynamodb_user_staged_table.grant_read_data(fn_cognito_post_confirmation)


        fn_pre_sign_up = lambda_.Function(
            self,"fn-pre-sign-up",
            description="cognito-pre-signup", #microservice tag
            runtime=lambda_.Runtime.PYTHON_3_9,
            handler="index.handler",
            code=lambda_.Code.from_asset(os.path.join("cloudpro_cdk/lambda/cognito","cognito_pre_signup")),
            environment={
                "IDENTIFIER":"COGNITO.PRE_SIGN_UP",
                "COGNITO_POOL":COGNITO_POOL
            },
            layers=[]
        )

        ######################################################################################################
        # Cognito Configs
        ######################################################################################################
        user_pool = cognito.UserPool(self, "cognito-up-cloudpro",
            user_pool_name=COGNITO_POOL,
            sign_in_aliases=cognito.SignInAliases(username=False, email=True, phone=False),
            #auto_verify=cognito.AutoVerifiedAttrs(email=True, phone=True)
            sign_in_case_sensitive=False,
            self_sign_up_enabled=True,
            user_verification=cognito.UserVerificationConfig(
                email_subject="Verify your email for our CloudPRO app!",
                email_body="Thanks for signing up to our CloudPRO app! Your verification code is {####}",
                email_style=cognito.VerificationEmailStyle.CODE,
                sms_message="Thanks for signing up to our CloudPRO app! Your verification code is {####}"
            ),
            lambda_triggers=cognito.UserPoolTriggers(
                pre_sign_up=fn_pre_sign_up,
                define_auth_challenge=fn_cognito_define_auth_challenge,
                create_auth_challenge=fn_cognito_create_auth_challenge,
                verify_auth_challenge_response=fn_cognito_verify_auth_challenge,
                post_confirmation=fn_cognito_post_confirmation
            ),
            custom_attributes={
                "isEmployee": cognito.StringAttribute(mutable=True)
            }
        )
        
        client_write_attributes = (cognito.ClientAttributes()).with_standard_attributes(
            address=True,
            birthdate=True,
            email=True,
            email_verified=False,
            fullname=True,
            family_name=True,
            locale=True,
            gender=True,
            given_name=True,
            last_update_time=True,
            middle_name=True,
            nickname=True,
            phone_number=True,
            phone_number_verified=False,
            preferred_username=True,
            profile_page=True,
            profile_picture=True,
            timezone=True,
            website=True
        )
        client = user_pool.add_client(
            "customer-app-client",
            auth_flows=cognito.AuthFlow(
                custom=True
            ),
            write_attributes=client_write_attributes
        )


        cfn_user_pool_group = cognito.CfnUserPoolGroup(self, "users-up-group",
            user_pool_id=user_pool.user_pool_id,
            description="Patients",
            group_name="patients",
            precedence=123
        )
        cfn_surgeon_pool_group = cognito.CfnUserPoolGroup(self, "surgeon-up-group",
            user_pool_id=user_pool.user_pool_id,
            description="Surgeons",
            group_name="surgeons",
            precedence=10
        )


        # workaround to get past circular dependency
        fn_cognito_verify_auth_challenge.role.attach_inline_policy(iam.Policy(self, "userpool-policy",
            statements=[iam.PolicyStatement(
                actions=["cognito-idp:AdminUpdateUserAttributes","cognito-idp:AdminListGroupsForUser","cognito-idp:AdminAddUserToGroup"],
                resources=[user_pool.user_pool_arn]
            )]
        ))
        fn_cognito_create_auth_challenge.role.attach_inline_policy(iam.Policy(self, "ses-policy",
            statements=[iam.PolicyStatement(
                actions=["ses:SendEmail"],
                resources=["*"]
            )]
        ))