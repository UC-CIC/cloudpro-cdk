import json
import boto3
import os
from decimal import Decimal

from json_encoder.json_encoder import JSONEncoder

dynamodb = boto3.resource('dynamodb')
table_name=os.environ["TABLE_SURVEY"]


CORS_HEADERS = {
    'Access-Control-Allow-Headers': 'Content-Type',
    'Access-Control-Allow-Origin': os.environ["CORS_ALLOW_UI"] if os.environ["LOCALHOST_ORIGIN"] == "" else os.environ["LOCALHOST_ORIGIN"],
    'Access-Control-Allow-Methods': 'OPTIONS,POST,GET'
}



def write_survey( payload:json ):
    table = dynamodb.Table(table_name)

    return table.put_item ( Item=payload  )    

def read_survey( sub:str ):
    """
    Retrieve full payload for a users surveys

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
        'sub': sub
    }
    

    return table.get_item(Key=search_key)

def sweep_to_complete( sub, db_payload, fields ):
    sid = fields["sid"]
    due_date = fields["due_date"]

    #print("SID:",sid)
    #print("AD:",assigned_date)
    #print("DBP:",db_payload)

    survey_payload = {
        "sub":sub,
        "completed_surveys":[],
        "open_surveys":[]
    }
    additional_payload = {}

    if( 'Item' in db_payload ):
        survey_payload["completed_surveys"] = db_payload["Item"]["completed_surveys"]
        survey_payload["open_surveys"] = db_payload['Item']["open_surveys"]

        closed_payload={}
        store_key =""
        store_idx = -1
        for idx,group in enumerate(survey_payload["open_surveys"]):
            for key in group.keys():
                for sdx,survey in enumerate(survey_payload["open_surveys"][idx][key]):
                    if survey_payload["open_surveys"][idx][key][sdx]["sid"] == sid and survey_payload["open_surveys"][idx][key][sdx]["due"] == due_date:
                        closed_payload = survey_payload["open_surveys"][idx][key][sdx]
                        closed_payload["completed"] = True
                        store_key=key
                        survey_payload["open_surveys"][idx][key].pop(sdx)
                        #print("IDX=",idx)
                        #print("KEY=",key)
                        #print("SDX=",sdx)
                        #pass
                        break
        for idx,survey_set in enumerate(survey_payload["completed_surveys"]):
            for key in survey_set:
                if key == store_key:
                    store_idx = idx
                    break
                    
        if store_idx > -1:
            survey_payload["completed_surveys"][store_idx][store_key].append(closed_payload)
        else:
            survey_payload["completed_surveys"].append( { store_key: [closed_payload] } )


    return survey_payload

def handler(event,context):
    sub = event["pathParameters"]["sub"]
    field_values=json.loads(event["body"])

    #print("SUB:",sub)
    #print("FIELD_VALUES:",field_values)

    try:
        result = read_survey(sub)
        if result['ResponseMetadata']['HTTPStatusCode'] != 200:
                raise Exception(f"DynamoDB issue")
        
        survey_payload=sweep_to_complete(sub=sub,db_payload=result,fields=field_values)
        result = write_survey(survey_payload)
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


