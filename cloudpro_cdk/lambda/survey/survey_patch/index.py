import json
import boto3
import os
from decimal import Decimal
import datetime

from json_encoder.json_encoder import JSONEncoder


event_client = boto3.client('events')
ebus_propack = os.environ['EBUS_PROPACK']
SOURCE=os.environ['IDENTIFIER']
DETAIL_TYPE=os.environ['DETAIL_TYPE']



dynamodb = boto3.resource('dynamodb')
table_name=os.environ["TABLE_SURVEY"]
TABLE_AUDIT_NAME=os.environ["TABLE_AUDIT"]
TABLE_STATE_NAME=os.environ["TABLE_STATE"]

CORS_HEADERS = {
    'Access-Control-Allow-Headers': 'Content-Type',
    'Access-Control-Allow-Origin': os.environ["CORS_ALLOWED_ORIGIN"],
    'Access-Control-Allow-Methods': 'OPTIONS,POST,GET,PATCH'
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
    table_survey_audit = dynamodb.Table(TABLE_AUDIT_NAME)
    table_survey_state = dynamodb.Table(TABLE_STATE_NAME)

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
                        closed_payload["completed_date"] = datetime.datetime.strftime(datetime.datetime.today().date(), "%Y-%m-%dT%H:%M:%S")
                        store_key=key
                        survey_payload["open_surveys"][idx][key].pop(sdx)
                        #print("IDX=",idx)
                        #print("KEY=",key)
                        #print("SDX=",sdx)
                        #pass
                        
                        search_key = {
                            'state_hash': sid + closed_payload["due"]
                        }
                        print("state-search:",search_key)
                        result = table_survey_state.get_item(Key=search_key)
                        state_payload={}
                        try:
                            state_payload=result["Item"]
                        except:
                            pass

                        t_score = "-1"
                        try:
                            t_score=state_payload["states"]["t_score"]["entry_response"]
                            if( t_score.isdecimal() == False ):
                                t_score=-1
                        except:
                            pass
                        report_dt_str="1/1/1111"

                        try:
                            date_str=closed_payload["due"]
                            date_format="%Y-%m-%dT%H:%M:%S"
                            date_obj=datetime.datetime.strptime(date_str,date_format)
                            report_dt_str = date_obj.strftime("%m/%d/%Y")
                        except:
                            pass

                        completed_dt_str="1/1/1111"

                        try:
                            date_str=closed_payload["completed_date"]
                            date_format="%Y-%m-%dT%H:%M:%S"
                            date_obj=datetime.datetime.strptime(date_str,date_format)
                            completed_dt_str = date_obj.strftime("%m/%d/%Y")
                        except:
                            pass

                        event_for_reporting = {
                            "sub":sub,
                            "survey":closed_payload["name"],
                            "date":report_dt_str,
                            "t_score":float(t_score),
                            "completed_date": completed_dt_str
                        }
                        print(event_for_reporting)
                        eresponse = event_client.put_events(
                            Entries=[
                                {
                                    'Source': "custom.cloudpro.core.survey.complete",
                                    'DetailType': DETAIL_TYPE,
                                    'Detail': json.dumps(event_for_reporting),
                                    'EventBusName':ebus_propack
                                }
                            ]
                        )
                        print(eresponse)

                        audit_payload = {
                            "sid":sid + closed_payload["due"],
                            "state":state_payload,
                            "survey_info":closed_payload
                        }
                        table_survey_audit.put_item ( Item=audit_payload  )
                    
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


