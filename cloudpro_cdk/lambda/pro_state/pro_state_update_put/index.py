import json
import boto3
import os
from decimal import Decimal

from json_encoder.json_encoder import JSONEncoder

dynamodb = boto3.resource('dynamodb')
table_name=os.environ["TABLE_STATE"]

CORS_HEADERS = {
    'Access-Control-Allow-Headers': 'Content-Type',
    'Access-Control-Allow-Origin': os.environ["CORS_ALLOWED_ORIGIN"],
    'Access-Control-Allow-Methods': 'OPTIONS,POST,GET,PUT'
}

def update_state( field_values:json ):
    """
    Update entire state payload given a state hash

    Parameters
    ----------
    field_values : json
        Payload to write to state table
    
    Returns
    -------
    json
        DynamoDB results
    """


    table = dynamodb.Table(table_name)

    return table.put_item ( Item=field_values  )


def handler(event,context):
    field_values=json.loads(event["body"])
    try:
        result = update_state( field_values=field_values )   
        if result['ResponseMetadata']['HTTPStatusCode'] != 200:
            raise Exception(f"DynamoDB issue")
    
        return {
            "statusCode":200,
            "headers": CORS_HEADERS,
            "body": json.dumps({},cls=JSONEncoder)
        }
    except Exception as e:
        return {
            "statusCode":500,
            "headers": CORS_HEADERS,
            "body": json.dumps({"msg":str(e)})
        }


