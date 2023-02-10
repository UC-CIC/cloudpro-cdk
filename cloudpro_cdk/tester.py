import os

from constructs import Construct
from aws_cdk import(
    Stack,
    aws_lambda as lambda_,
    Fn as CoreFn
)

# test class for concept of pulling layer verison in from deploy process

class TesterStack(Stack):
    def __init__(self,scope: Construct, construct_id: str,  **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        SOURCE_PRO_QUESTION_PROHASH_GET="custom.lambda.pro.question"

        #layer_arn = CoreFn.sub("${Val}",{"Val":latest_version_arn})
        '''
        layer_arn =  CoreFn.sub("arn:aws:lambda:${AWS::Region}:${AWS::AccountId}:layer:${LayerName}:${Version}",
                                   AWS=CoreFn.import_value("AWS::AccountId"),
                                   LayerName=layers["layer_cloudpro_lib"].layer_version_arn.split(":")[-2],
                                   Version=layers["layer_cloudpro_lib"].layer_version_arn.split(":")[-1])
                                           
        '''

        fn_pro_question_prohash_get = lambda_.Function(
            self,"fn-pro-question-prohash-get",
            description="pro-question-prohash-get", #microservice tag
            runtime=lambda_.Runtime.PYTHON_3_9,
            handler="index.handler",
            code=lambda_.Code.from_asset(os.path.join("cloudpro_cdk/lambda/pro_question","pro_question_prohash_get")),
            environment={
                "TABLE_QUESTIONNAIRE":"questionnaire",
                "IDENTIFIER":SOURCE_PRO_QUESTION_PROHASH_GET
            },
            layers=[ lambda_.LayerVersion.from_layer_version_arn(self,id="layer_cloudpro_lib",layer_version_arn=self.node.try_get_context("layer_arn"))]
        )
        

