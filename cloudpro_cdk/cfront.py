import os

from constructs import Construct
from aws_cdk import(
    Stack,
    aws_cloudfront as cloudfront,
    aws_cloudfront_origins as origins,
    Duration,
    aws_s3 as s3
)

class CfrontStack(Stack):
    def __init__(self,scope: Construct,  construct_id: str, bucket_userportal:s3.IBucket, core_api,   **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        XKEY = self.node.try_get_context("XKEY")


        error_response = cloudfront.ErrorResponse(
            http_status=403,

            # the properties below are optional
            response_http_status=200,
            response_page_path="/index.html",
            ttl=Duration.minutes(0)
        )           
        main_cdn = cloudfront.Distribution(
            self,
            "cfront-cloudpro",
            default_behavior=cloudfront.BehaviorOptions(
                origin=origins.S3Origin(bucket_userportal),
                viewer_protocol_policy=cloudfront.ViewerProtocolPolicy.HTTPS_ONLY,
                cache_policy=cloudfront.CachePolicy.CACHING_DISABLED,
            ),
            price_class=cloudfront.PriceClass.PRICE_CLASS_100,
            default_root_object="index.html",
            error_responses=[error_response],
            additional_behaviors={
                "/api/*": cloudfront.BehaviorOptions(
                    origin=origins.RestApiOrigin(
                        core_api,
                        custom_headers={
                            "x-api-key": XKEY
                        }
                    ),
                    cache_policy=cloudfront.CachePolicy.CACHING_DISABLED,
                    allowed_methods=cloudfront.AllowedMethods.ALLOW_ALL,
                    viewer_protocol_policy=cloudfront.ViewerProtocolPolicy.HTTPS_ONLY
                )
            }
        )


        