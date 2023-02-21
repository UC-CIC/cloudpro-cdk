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
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
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
                #pre_sign_up=fn_pre_sign_up,
                define_auth_challenge=fn_cognito_define_auth_challenge,
                create_auth_challenge=fn_cognito_create_auth_challenge,
                verify_auth_challenge_response=fn_cognito_verify_auth_challenge
            )
        )
        client = user_pool.add_client(
            "customer-app-client",
            auth_flows=cognito.AuthFlow(
                custom=True
            )
        )

        # workaround to get past circular dependency
        fn_cognito_verify_auth_challenge.role.attach_inline_policy(iam.Policy(self, "userpool-policy",
            statements=[iam.PolicyStatement(
                actions=["cognito-idp:AdminUpdateUserAttributes"],
                resources=[user_pool.user_pool_arn]
            )]
        ))