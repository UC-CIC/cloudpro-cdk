import json
import boto3
import os
from decimal import Decimal

from json_encoder.json_encoder import JSONEncoder

dynamodb = boto3.resource('dynamodb')
table_name=os.environ["TABLE_STATE"]



def update_state( field_values:json ):
    """
    Update entire state payload given a state hash

    Parameters
    ----------
    state_hash : str
        Unique ID of the state to retrieve
    
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
            "body": json.dumps({},cls=JSONEncoder)
        }
    except Exception as e:
        return {
            "statusCode":500,
            "body": json.dumps({"msg":str(e)})
        }


