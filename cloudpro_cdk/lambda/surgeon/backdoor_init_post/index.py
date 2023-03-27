import json
import boto3
import os
import hashlib

from datetime import datetime
from decimal import Decimal

from json_encoder.json_encoder import JSONEncoder

dynamodb = boto3.resource('dynamodb')
table_name=os.environ["TABLE_SURGEONS"]


CORS_HEADERS = {
    'Access-Control-Allow-Headers': 'Content-Type',
    'Access-Control-Allow-Origin': os.environ["CORS_ALLOW_UI"],
    'Access-Control-Allow-Methods': 'OPTIONS,POST,GET'
}

def init_surgeon( field_values:json ):
    """
    Initialize a surgeon payload [accepts subs]

    Parameters
    ----------
    field_values : json
        Payload to write to surgeon table
    
    Returns
    -------
    json
        DynamoDB results
    """


    table = dynamodb.Table(table_name)

    return table.put_item ( Item=field_values  )

def handler(event,context):
    '''
        {
            "sub":"111-111",
            "name":"Dr. Bob Sinclair",
            "pts":["1111-1111","13311","3153151","3513135"]
        }
    '''
    init_payload=json.loads(event["body"])

    try: 
        result = init_surgeon( field_values=init_payload )

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

