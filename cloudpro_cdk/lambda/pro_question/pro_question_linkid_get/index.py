import json
import boto3
import os

from json_encoder.json_encoder import JSONEncoder

import pro_parsers.cpro_r1
import pro_parsers.cpro_fhir

parsers = {
    "CPRO_R1":pro_parsers.cpro_r1,
    "FHIR_R4":pro_parsers.cpro_fhir
}


dynamodb = boto3.resource('dynamodb')
table_name=os.environ["TABLE_QUESTIONNAIRE"]

CORS_HEADERS = {
    'Access-Control-Allow-Headers': 'Content-Type',
    'Access-Control-Allow-Origin': os.environ["CORS_ALLOW_UI"] if os.environ["LOCALHOST_ORIGIN"] == "" else os.environ["LOCALHOST_ORIGIN"],
    'Access-Control-Allow-Methods': 'OPTIONS,POST,GET'
}


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
    link_id = event["pathParameters"]["link_id"]

    try:
        result = read_questionnaire(pro_hash)
        if result['ResponseMetadata']['HTTPStatusCode'] != 200:
                raise Exception(f"DynamoDB issue")
        
        pro_format=result["Item"]["pro_pack_format"]
        questionnaire_data=result["Item"]["data"]

        question_result=parsers[pro_format].read_question( questionnaire=questionnaire_data, link_id=link_id )
        print(question_result)
        
        return {
            "statusCode":200,
            "headers": CORS_HEADERS,
            "body": json.dumps(question_result,cls=JSONEncoder)
        }
    except Exception as e:
        return {
            "statusCode":500,
            "headers": CORS_HEADERS,
            "body": json.dumps({"msg":str(e)})
        }


