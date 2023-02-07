import os

from constructs import Construct
from aws_cdk import(
    Stack,
    Duration,
    aws_events as events
)

class EventBus(Stack):
    def __init__(self,scope: Construct,  construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)


        ebus = events.EventBus(self, "cdk-ebus-cloudpro",
            event_bus_name="cdk-ebus-cloudpro"
        )

        ebus.archive("cdk-ebus-cloudpro-arch",
            archive_name="cdk-ebus-cloudpro-arch",
            description="Archive for CloudPro events",
            event_pattern=events.EventPattern(
                account=[Stack.of(self).account]
            ),
            retention=Duration.days(3)
        )

        self.ebus = ebus