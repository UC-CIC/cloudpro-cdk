import json
import boto3
import os
from decimal import Decimal
import pro_parsers.cpro_r1
import pro_parsers.cpro_fhir

parsers = {
    "CPRO_R1":pro_parsers.cpro_r1,
    "FHIR_R4":pro_parsers.cpro_fhir
}

from json_encoder.json_encoder import JSONEncoder

dynamodb = boto3.resource('dynamodb')
table_scoring=os.environ["TABLE_SCORING"]

CORS_HEADERS = {
    'Access-Control-Allow-Headers': 'Content-Type',
    'Access-Control-Allow-Origin': os.environ["CORS_ALLOWED_ORIGIN"],
    'Access-Control-Allow-Methods': 'OPTIONS,POST,GET'
}


def read_scoring( pro_hash:str ):
    """
    Retrieve full payload for a specific scoring algorithm

    Parameters
    ----------
    pro_hash : str
        Unique ID of the questionnaire
    
    Returns
    -------
    json
        DynamoDB results
    """
    table = dynamodb.Table(table_scoring)

    search_key = {
        'pro_pack': pro_hash
    }
    

    return table.get_item(Key=search_key)


def handler(event,context):
    print("<Scoring Evaluation:Hello>")
    link_id =  event["pathParameters"]["link_id"]

    post_payload=json.loads(event["body"])
    pro_pack_format=post_payload["pro_pack_format"]
    pro_pack=post_payload["pro_pack"]
    survey_values=post_payload["data"]


    try:
        pass
    except Exception as e:
        print("<exception>", e)

    try:
        result = read_scoring(pro_pack)
        if result['ResponseMetadata']['HTTPStatusCode'] != 200:
            raise Exception(f"DynamoDB issue")

        scoring_formula=parsers[pro_pack_format].read_formula( scoring=result["Item"]["formulas"], link_id=link_id)
        print("SCORING_FORMULA: ",scoring_formula)
        score=parsers[pro_pack_format].evaluate_formula(field_values=survey_values, formula=scoring_formula["formula"])

        return {
            "statusCode":200,
            "headers": CORS_HEADERS,
            "body": json.dumps(score)
        }
    except Exception as e:
        return {
            "statusCode":500,
            "headers": CORS_HEADERS,
            "body": json.dumps({"msg":str(e)})
        }
