#!/usr/bin/env python3
import os

import aws_cdk as cdk

from cloudpro_cdk.layers import LayersStack
from cloudpro_cdk.propack import ProPack
from cloudpro_cdk.ebus import EventBus
from cloudpro_cdk.dynamodb import DynamodbStack
from cloudpro_cdk.apig import ApigStack
from cloudpro_cdk.core_events import CoreEvents
from cloudpro_cdk.userportal import UserPortal
from cloudpro_cdk.cfront_apig import CfrontApig
from cloudpro_cdk.cfront_userportal import CfrontUserPortal
from cloudpro_cdk.cognito import CognitoStack


app = cdk.App()

LayersStack(app, "cdk-layers-stack-dev-dev")
dynamodb_stack = DynamodbStack(app, "cdk-dynamodb-stack-dev")



event_bus_stack=EventBus(app, "cdk-event-bus-stack-dev")
propack_loader=ProPack(app, "cdk-propack-stack-dev",ebus_pro=event_bus_stack.ebus,dynamodb_tables=dynamodb_stack.tables)

user_portal=UserPortal(app, "cdk-userportal-stack-dev")
cfront_userportal_stack=CfrontUserPortal(app, "cdk-cfront-userportal-stack-dev", 
    bucket_userportal=user_portal.bucket_userportal
)

core_events=CoreEvents(app, "cdk-core-events-stack-dev",ebus_pro=event_bus_stack.ebus,dynamodb_tables=dynamodb_stack.tables)

cognito_stack=CognitoStack(app, "cdk-cognito-stack-dev", dynamodb_user_table=dynamodb_stack.tables["user"],dynamodb_user_staged_table=dynamodb_stack.tables["user_staged"])

apig_stack=ApigStack(app,"cdk-apig-stack-dev",dynamodb_tables=dynamodb_stack.tables,cfront_user_portal_domain_name=cfront_userportal_stack.cfront_user_portal_domain_name,ebus_pro=event_bus_stack.ebus,bucket_propack=propack_loader.bucket_propack, cognito_userpool=cognito_stack.cognito_userpool)
cfront_apig_stack=CfrontApig(app, "cdk-cfront-apig-stack-dev",
    core_api=apig_stack.core_api
)

app.synth()


'''
LoremStack(app, "cdk-lorem-ipsum",
    # If you don't specify 'env', this stack will be environment-agnostic.
    # Account/Region-dependent features and context lookups will not work,
    # but a single synthesized template can be deployed anywhere.

    # Uncomment the next line to specialize this stack for the AWS Account
    # and Region that are implied by the current CLI configuration.

    #env=cdk.Environment(account=os.getenv('CDK_DEFAULT_ACCOUNT'), region=os.getenv('CDK_DEFAULT_REGION')),

    # Uncomment the next line if you know exactly what Account and Region you
    # want to deploy the stack to. */

    #env=cdk.Environment(account='123456789012', region='us-east-1'),

    # For more information, see https://docs.aws.amazon.com/cdk/latest/guide/environments.html
    )
'''