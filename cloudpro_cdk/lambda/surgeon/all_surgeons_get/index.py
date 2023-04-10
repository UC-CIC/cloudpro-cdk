import json
import boto3
import os
from decimal import Decimal

from json_encoder.json_encoder import JSONEncoder

dynamodb = boto3.resource('dynamodb')
table_name=os.environ["TABLE_SURGEONS"]

CORS_HEADERS = {
    'Access-Control-Allow-Headers': 'Content-Type',
    'Access-Control-Allow-Origin': os.environ["CORS_ALLOW_UI"] if os.environ["LOCALHOST_ORIGIN"] == "" else os.environ["LOCALHOST_ORIGIN"],
    'Access-Control-Allow-Methods': 'OPTIONS,POST,GET'
}

# costly; we rarely would want to call this; needs refactored for production
def read_surgeons_all( ):
    """
    Warning: Costly

    Retrieve all surgoens stored in DB.

    Parameters
    ----------
    
    Returns
    -------
    json
        DynamoD
    """
    table = dynamodb.Table(table_name)

    return table.scan(
         ProjectionExpression = '#sub, #name',
         ExpressionAttributeNames = {'#sub': 'sub','#name':'name'}
    )


def handler(event,context):
    try:
        result = read_surgeons_all()
        if result['ResponseMetadata']['HTTPStatusCode'] != 200:
                raise Exception(f"DynamoDB issue")
        
        return {
            "statusCode":200,
            "headers": CORS_HEADERS,
            "body": json.dumps(result["Items"],cls=JSONEncoder)
        }
    except Exception as e:
        return {
            "statusCode":500,
            "headers": CORS_HEADERS,
            "body": json.dumps({"msg":str(e)})
        }


