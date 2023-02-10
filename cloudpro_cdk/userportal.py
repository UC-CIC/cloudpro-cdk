import os

from constructs import Construct
from aws_cdk import(
    Stack,
    Duration,
    RemovalPolicy,
    aws_s3 as s3
)

class UserPortal(Stack):
    def __init__(self,scope: Construct,  construct_id: str,  **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        bucket_userportal=s3.Bucket(self, "bucket-userportal",
            versioned=True,
            removal_policy=RemovalPolicy.DESTROY,
            auto_delete_objects=True,
            block_public_access=s3.BlockPublicAccess.BLOCK_ALL
        )

        self.bucket_userportal = bucket_userportal