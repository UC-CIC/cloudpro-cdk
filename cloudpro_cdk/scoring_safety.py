import os

from constructs import Construct
from aws_cdk import(
    Stack,
    aws_lambda as lambda_
)

class ScoringSafety(Stack):
    def __init__(self,scope: Construct,  construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        fn_scoring_safety = lambda_.Function(
            self,"cdk-fn-scoring-safety",
            runtime=lambda_.Runtime.PYTHON_3_9,
            handler="index.handler",
            code=lambda_.Code.from_asset(os.path.join("cloudpro_cdk/lambda/","scoring_safety"))
        )


        self.fn_scoring_safety = fn_scoring_safety