import os

from constructs import Construct
from aws_cdk import(
    Stack,
    aws_lambda as lambda_
)

class LayersStack(Stack):
    def __init__(self,scope: Construct, construct_id: str,  **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        layer_cloudpro_lib = lambda_.LayerVersion(
            self, "layer_cloudpro_lib",
            code=lambda_.Code.from_asset(os.path.join("cloudpro_cdk/lambda/custom_packages/layers","cloudpro_lib.zip")),
            compatible_runtimes=[lambda_.Runtime.PYTHON_3_9],
            description="Various shared modules such as pro parsers.",
            layer_version_name="layer_cloudpro_lib"
        )


        # No longer required as version is no longer expiremental
        '''
        layer_boto_1_26_86 = lambda_.LayerVersion(
            self, "layer_boto_lib",
            code=lambda_.Code.from_asset(os.path.join("cloudpro_cdk/lambda/custom_packages/layers","boto_1_26_86.zip")),
            compatible_runtimes=[lambda_.Runtime.PYTHON_3_9],
            description="Bumped boto version for event scheduler support",
            layer_version_name="layer_boto_lib"
        )
        '''