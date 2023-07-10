import json
import boto3
import os
import hashlib


dynamodb = boto3.resource('dynamodb')

TABLE_NAME_SURVEY=os.environ["TABLE_SURVEY"]
TABLE_SURVEYS_AUDIT=os.environ["TABLE_SURVEY_AUDIT"]
TABLE_STATE=os.environ["TABLE_STATE"]


SURVEYS=["mobility","physical_function","upper_extremity","upper_extremity_group"] 



def build_payload(event):
    table = dynamodb.Table(TABLE_NAME_SURVEY)

    table_state = dynamodb.Table(TABLE_STATE)
    table_survey_audit = dynamodb.Table(TABLE_SURVEYS_AUDIT)


    sub = event["sub"]
    assigned = event["assigned"]
    due = event["due"]
    surg_date=event["surg_date"]
    header_tag=event["header_tag"]

    survey_payload = {
        "sub":event["sub"],
        "completed_surveys":[],
        "open_surveys":[]
    }


    search_key = {
        'sub': sub
    }
    result = table.get_item(Key=search_key)

    # data exists, copy it over before we rewrite the doc
    # technically should probably patch in a production env to avoid race conditions
    # should probably move the dynamo write/read out to an event too.
    if( 'Item' in result ):
        survey_payload["completed_surveys"] = result['Item']["completed_surveys"]
        survey_payload["open_surveys"] = result['Item']["open_surveys"]
        for idx,group in enumerate(survey_payload["open_surveys"]):
            for key in group.keys():
                for sdx,survey in enumerate(survey_payload["open_surveys"][idx][key]):
                    if survey_payload["open_surveys"][idx][key][sdx]["completed"] == False:
                        survey_payload["open_surveys"][idx][key][sdx]["missed"] = True

                    sid = survey_payload["open_surveys"][idx][key][sdx]["sid"]
                    sid += survey_payload["open_surveys"][idx][key][sdx]["due"] 
                    
                    search_key = {
                        'state_hash': sid
                    }
                    print("state-search:",search_key)
                    result = table_state.get_item(Key=search_key)
                    state_payload={}
                    try:
                        state_payload=result["Item"]
                    except:
                        pass

                    audit_payload = {
                        "sid":sid,
                        "state":state_payload,
                        "survey_info":survey_payload["open_surveys"][idx][key][sdx]
                    }
                    table_survey_audit.put_item ( Item=audit_payload  )




        survey_payload["completed_surveys"].extend(survey_payload["open_surveys"])
    # add in new payload(s)
    staged_surveys = [
        {
            header_tag:[
                {
                    "sid":hashlib.sha256( (sub+SURVEYS[0]).encode('utf-8') ).hexdigest(),
                    "propack": hashlib.sha256( (SURVEYS[0]).encode('utf-8') ).hexdigest(),
                    "name": "Mobility",
                    "description": "Lorem MOBILITY ipsum  dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.",
                    "assigned":assigned,
                    "due":due,
                    "completed":False,
                    "missed":False
                },
                {
                    "sid":hashlib.sha256( (sub+SURVEYS[1]).encode('utf-8') ).hexdigest(),
                    "propack": hashlib.sha256( (SURVEYS[1]).encode('utf-8') ).hexdigest(),
                    "name": "Physical Function",
                    "description": "Lorem PHYSICAL FUNCTION ipsum  dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.",
                    "assigned":assigned,
                    "due":due,
                    "completed":False,
                    "missed":False
                },
                {
                    "sid":hashlib.sha256( (sub+SURVEYS[2]).encode('utf-8') ).hexdigest(),
                    "propack": hashlib.sha256( (SURVEYS[2]).encode('utf-8') ).hexdigest(),
                    "name": "Upper Extremity",
                    "description": "Lorem UPPER EXTREMITY ipsum  dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.",
                    "assigned":assigned,
                    "due":due,
                    "completed":False,
                    "missed":False
                },
                {
                    "sid":hashlib.sha256( (sub+SURVEYS[3]).encode('utf-8') ).hexdigest(),
                    "propack": hashlib.sha256( (SURVEYS[3]).encode('utf-8') ).hexdigest(),
                    "name": "Upper Extremity Group",
                    "description": "Lorem UPPER EXTREMITY GROUP ipsum  dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.",
                    "assigned":assigned,
                    "due":due,
                    "completed":False,
                    "missed":False
                }
            ]
        }
    ]

    #survey_payload["open_surveys"].extend(staged_surveys)

    
    survey_payload["open_surveys"] = staged_surveys

    return table.put_item ( Item=survey_payload  )

def handler(event,context):
    print("<SCHEDULER_PROCESSING:Hello>")
    print(event)


    try:
        response = build_payload(event)
        print(response)
    except Exception as e:
        print("<exception>", e)


    return {
        "statusCode":200,
        "body": json.dumps("Scheduler Processing Hello World")
    }
