import os

from constructs import Construct
from aws_cdk import(
    Stack,
    aws_cloudfront as cloudfront,
    aws_cloudfront_origins as origins,
    Duration,
    aws_s3 as s3
)

class CfrontApig(Stack):
    def __init__(self,scope: Construct,  construct_id: str, core_api,   **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        XKEY = self.node.try_get_context("XKEY")


        api_cdn = cloudfront.Distribution(
            self,
            "cfront-cloudpro-api",
            default_behavior=cloudfront.BehaviorOptions(
                origin=origins.RestApiOrigin(
                    core_api,
                    custom_headers={
                        "x-api-key": XKEY
                    },
                ),
                cache_policy=cloudfront.CachePolicy.CACHING_DISABLED,
                allowed_methods=cloudfront.AllowedMethods.ALLOW_ALL,
                viewer_protocol_policy=cloudfront.ViewerProtocolPolicy.HTTPS_ONLY
            ),
            price_class=cloudfront.PriceClass.PRICE_CLASS_100
        )  



        