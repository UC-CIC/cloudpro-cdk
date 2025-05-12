import json
import boto3
import os
from decimal import Decimal

from json_encoder.json_encoder import JSONEncoder

dynamodb = boto3.resource('dynamodb')

table_name_pt_reporting=os.environ["TABLE_PT_REPORTING"]
table_name_aggregates=os.environ["TABLE_AGGREGATES"]




def write_ptreporting( sub, survey, date, score, completed_date ):
    table = dynamodb.Table(table_name_pt_reporting)

    search_key = {
        'sub': sub
    }
    result = table.get_item(Key=search_key)
    # data exists, copy it over before we rewrite the doc
    # technically should probably patch in a production env to avoid race conditions
    # should probably move the dynamo write/read out to an event too.
    payload = {}

    if( 'Item' in result ):
        found = False
        found_idx=0
        survey_payload = result["Item"]["surveys"]
        print(survey_payload)

        for idx,obj in enumerate(survey_payload):
            for key in obj:
                if key == survey:
                    found = True
                    found_idx = idx
                    break
            if found:
                break
        print(found)
        print(survey)

        if found:
            survey_payload[found_idx][key].append({"date":date,"score":Decimal(score),"completed_date": completed_date})
        else:
            survey_payload.append( { survey:[{"date":date,"score":Decimal(score),"completed_date": completed_date}] })
        
        payload = {
            "sub":sub,
            "surveys": survey_payload
        }

        
        table.put_item ( Item=payload  )
    else:
        payload = {
            "sub":sub,
            "surveys": [
                {
                    survey: [
                        {
                            "date": date,
                            "score": Decimal(score),
                            "completed_date": completed_date
                        },
                    ]
                }
            ]
        }
        table.put_item ( Item=payload  )


    table = dynamodb.Table(table_name_aggregates)
    search_key = {
        'agg': "spec"
    }
    result = table.get_item(Key=search_key)
    new_score = 0
    count = 0
    if( 'Item' in result ):
        new_score = (float(result["Item"]["value"])+ float(score))/2
        count = int(result["Item"]["count"]) + 1
    else:
        new_score = float(score)
        count = int(1)
    payload = {
        "agg":"spec",
        "count":Decimal(count),
        "value":Decimal(new_score)
    }
    table.put_item ( Item=payload  )

def handler(event,context):
    '''
    {
        "sub":"test",
        "survey":"Mobility",
        "date":"01/10/2023",
        "t_score":81,
        "completed_date: "01/10/2023
    }
    '''
    source_sub = event["detail"]["sub"]
    source_survey = event["detail"]["survey"]
    source_date = event["detail"]["date"]
    source_tscore  = event["detail"]["t_score"]
    source_completed_date  = event["detail"]["completed_date"]
    write_ptreporting(sub=source_sub,survey=source_survey,date=source_date,score=source_tscore,completed_date=source_completed_date)

    try:
        return {
            "statusCode":200,
            "body": json.dumps({},cls=JSONEncoder)
        }
    except Exception as e:
        return {
            "statusCode":500,
            "body": json.dumps({"msg":str(e)})
        }


