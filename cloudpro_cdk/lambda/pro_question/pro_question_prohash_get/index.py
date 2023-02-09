import json
import boto3
import os
from decimal import Decimal


dynamodb = boto3.resource('dynamodb')
table_name=os.environ["TABLE_QUESTIONNAIRE"]


#Does quasi the same things as json.loads from here: https://pypi.org/project/dynamodb-json/
class JSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        return json.JSONEncoder.default(self, obj)


def read_questionnaire( pro_hash:str ):
    """
    Retrieve full payload for a specific questionnaire

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
        'pro_pack': pro_hash
    }
    

    return table.get_item(Key=search_key)


def handler(event,context):
    pro_hash = event["pathParameters"]["pro_hash"]

    try:
        result = read_questionnaire(pro_hash)
        if result['ResponseMetadata']['HTTPStatusCode'] != 200:
                raise Exception(f"DynamoDB issue")
        
        return {
            "statusCode":200,
            "body": json.dumps(result["Item"],cls=JSONEncoder)
        }
    except Exception as e:
        return {
            "statusCode":500,
            "body": json.dumps({"msg":str(e)})
        }


