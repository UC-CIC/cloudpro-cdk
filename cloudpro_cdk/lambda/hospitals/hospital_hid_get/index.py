import json
import boto3
import os

from json_encoder.json_encoder import JSONEncoder


dynamodb = boto3.resource('dynamodb')
table_name=os.environ["TABLE_HOSPITALS"]

CORS_HEADERS = {
    'Access-Control-Allow-Headers': 'Content-Type',
    'Access-Control-Allow-Origin': os.environ["CORS_ALLOW_UI"] if os.environ["LOCALHOST_ORIGIN"] == "" else os.environ["LOCALHOST_ORIGIN"],
    'Access-Control-Allow-Methods': 'OPTIONS,POST,GET'
}


def read_hospital( hid:str ):
    """
    Retrieve full payload for a specific hospital

    Parameters
    ----------
    hid : str
        Unique ID of the hospital
    
    Returns
    -------
    json
        DynamoDB results
    """
    table = dynamodb.Table(table_name)

    search_key = {
        'hid': hid
    }
    

    return table.get_item(Key=search_key)


def handler(event,context):
    hid = event["pathParameters"]["hid"]

    try:
        result = read_hospital(hid)
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


