import json
import boto3
import os
from decimal import Decimal

from json_encoder.json_encoder import JSONEncoder

dynamodb = boto3.resource('dynamodb')
table_name=os.environ["TABLE_AUDIT"]

CORS_HEADERS = {
    'Access-Control-Allow-Headers': 'Content-Type',
    'Access-Control-Allow-Origin': os.environ["CORS_ALLOW_UI"],
    'Access-Control-Allow-Methods': 'OPTIONS,POST,GET'
}


def read_audit( state_hash:str ):
    """
    Retrieve full payload for a specific audit table

    Parameters
    ----------
    pro_hash : str
        Unique ID of the questionnaire
    
    Returns
    -------
    json
        DynamoDB results
    """
    table = dynamodb.Table(table_name)

    
    search_key = {
        'sid': state_hash
    }
    

    return table.get_item(Key=search_key)


def handler(event,context):
    sid = event["pathParameters"]["sid"]
    print("Check for:", sid)

    try:
        result = read_audit(sid)
        print(result)
        if result['ResponseMetadata']['HTTPStatusCode'] != 200:
                raise Exception(f"DynamoDB issue")
        if( "Item" in result ):
             rpayload=result["Item"]
        else:
             rpayload={}
        
        return {
            "statusCode":200,
            "headers": CORS_HEADERS,
            "body": json.dumps(rpayload,cls=JSONEncoder)
        }
    except Exception as e:
        return {
            "statusCode":500,
            "headers": CORS_HEADERS,
            "body": json.dumps({"msg":str(e)})
        }


