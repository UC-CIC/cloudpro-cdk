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

        # Creating a custom cache policy for a Distribution -- all parameters optional
        # bucket_origin: origins.S3Origin

        api_cache_policy = cloudfront.CachePolicy(self, "cpol-apig",
            cache_policy_name="apig",
            comment="Default cache policy for API Gateway",
            default_ttl=Duration.seconds(0),
            min_ttl=Duration.seconds(0),
            max_ttl=Duration.seconds(1),
            cookie_behavior=cloudfront.CacheCookieBehavior.none(),
            header_behavior=cloudfront.CacheHeaderBehavior.allow_list("Authorization","Access-Control-Request-Method","Access-Control-Request-Headers","Origin"),
            query_string_behavior=cloudfront.CacheQueryStringBehavior.all(),
            enable_accept_encoding_gzip=True,
            enable_accept_encoding_brotli=True
        )
        

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
                #cache_policy=cloudfront.CachePolicy.CACHING_DISABLED,
                cache_policy=api_cache_policy,
                allowed_methods=cloudfront.AllowedMethods.ALLOW_ALL,
                viewer_protocol_policy=cloudfront.ViewerProtocolPolicy.HTTPS_ONLY
            ),
            price_class=cloudfront.PriceClass.PRICE_CLASS_100
        )  



        