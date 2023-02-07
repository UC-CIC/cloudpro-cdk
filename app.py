#!/usr/bin/env python3
import os

import aws_cdk as cdk

from cloudpro_cdk.scoring_safety import ScoringSafety
from cloudpro_cdk.propack import ProPack
from cloudpro_cdk.ebus import EventBus

app = cdk.App()
event_bus_stack=EventBus(app, "cdk-event-bus-stack")
scoring_safety=ScoringSafety(app, "cdk-scoring-safety-stack")
propack_loader=ProPack(app, "cdk-propack-stack",ebus_pro=event_bus_stack.ebus)

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