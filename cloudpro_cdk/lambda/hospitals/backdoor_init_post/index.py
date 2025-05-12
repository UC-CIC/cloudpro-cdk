import json
import boto3
import os
import hashlib

from datetime import datetime
from decimal import Decimal

from json_encoder.json_encoder import JSONEncoder

dynamodb = boto3.resource('dynamodb')
table_name=os.environ["TABLE_HOSPITALS"]


CORS_HEADERS = {
    'Access-Control-Allow-Headers': 'Content-Type',
    'Access-Control-Allow-Origin': os.environ["CORS_ALLOWED_ORIGIN"],
    'Access-Control-Allow-Methods': 'OPTIONS,POST,GET'
}

def init_hospital( field_values:json ):
    """
    Initialize a hospital payload [accepts subs]

    Parameters
    ----------
    field_values : json
        Payload to write to hospital table
    
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
            "hid":"1",
            "hospital_name":"Most General Named Hospital",
            "surgeons":[
                {
                    "sub":"1111-111-111-111-111",
                    "name":"Dr. James Sinclair"
                }
            ]
        }
    '''
    init_payload=json.loads(event["body"])

    try: 
        result = init_hospital( field_values=init_payload )

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

