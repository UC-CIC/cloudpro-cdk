import json
import boto3
import os
from decimal import Decimal

from json_encoder.json_encoder import JSONEncoder

dynamodb = boto3.resource('dynamodb')
table_name=os.environ["TABLE_QUESTIONNAIRE"]

CORS_HEADERS = {
    'Access-Control-Allow-Headers': 'Content-Type',
    'Access-Control-Allow-Origin': os.environ["CORS_ALLOWED_ORIGIN"],
    'Access-Control-Allow-Methods': 'OPTIONS,POST,GET'
}


def read_questionnaire_all( ):
    """
    Warning: Costly

    Retrieve all questionnaires stored in DB.

    Parameters
    ----------
    
    Returns
    -------
    json
        DynamoD
    """
    table = dynamodb.Table(table_name)

    return table.scan()


def handler(event,context):
    try:
        result = read_questionnaire_all()
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


