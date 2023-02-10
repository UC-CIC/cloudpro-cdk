import os

from constructs import Construct
from aws_cdk import(
    Stack,
    RemovalPolicy,
    aws_s3 as s3
)

class CfrontStack(Stack):
    def __init__(self,scope: Construct,  bucket_userportal, core_api, construct_id: str,  **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)


        