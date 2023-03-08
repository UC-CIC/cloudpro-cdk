import json
import boto3
import os
import hashlib


dynamodb = boto3.resource('dynamodb')

TABLE_NAME_SURVEY=os.environ["TABLE_SURVEY"]

SURVEYS=["mobility","physical_function","upper_extrimity"] 



def build_payload(event):
    table = dynamodb.Table(TABLE_NAME_SURVEY)
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
    if( 'Item' in result ):
        survey_payload["completed_surveys"] = result['Item']["completed_surveys"]
        survey_payload["open_surveys"] = result['Item']["open_surveys"]
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
                    "assigned":"2023-03-01",
                    "due":"2023-03-10",
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
                }
            ]
        }
    ]

    survey_payload["open_surveys"].extend(staged_surveys)
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
