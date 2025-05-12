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
    'Access-Control-Allow-Methods': 'OPTIONS,POST,GET'
}

def update_state_item( state_hash:str, link_id:str, status:str ):
    """
    Update a specific question state within a state payload.

    Parameters
    ----------
    state_hash : str
        Unique ID of the state to retrieve
    
    link_id : str
        Identifier of the question to update state for
    
    status : str
        What to update the state to

    Returns
    -------
    json
        DynamoDB results
    """

    table = dynamodb.Table(table_name)
    try:
        response = table.update_item(
            Key={
                "state_hash": state_hash
            },
            UpdateExpression="set states.#link_id.entry_state=:state",
            ExpressionAttributeNames={
                '#link_id':link_id
            },
            ExpressionAttributeValues={
                ':state':status
            },
            ReturnValues="UPDATED_NEW"
        )
    except Exception as e:
        raise( e )
    else:
        return response['Attributes']


def handler(event,context):
    state_hash = event["pathParameters"]["state_hash"]
    link_id = event["queryStringParameters"]["link_id"]
    status = event["queryStringParameters"]["status"]

    try:
        result = update_state_item( state_hash, link_id, status )       
        return {
            "statusCode":200,
            "headers": CORS_HEADERS,
            "body": json.dumps(result["states"][link_id],cls=JSONEncoder)
        }
    except Exception as e:
        return {
            "statusCode":500,
            "headers": CORS_HEADERS,
            "body": json.dumps({"msg":str(e)})
        }


