import json
import boto3
import os
from decimal import Decimal

from datetime import datetime
from datetime import timedelta
from dateutil.relativedelta import relativedelta

from json_encoder.json_encoder import JSONEncoder

dynamodb = boto3.resource('dynamodb')
scheduler = boto3.client('scheduler')

surgeon_table_name=os.environ["TABLE_SURGEON"]
table_name=os.environ["TABLE_USER"]
target_arn=os.environ["SCHEDULER_PROCESSING_ARN"]
target_role=os.environ["SCHEDULER_PROCESSING_ROLE"]


CORS_HEADERS = {
    'Access-Control-Allow-Headers': 'Content-Type',
    'Access-Control-Allow-Origin': os.environ["CORS_ALLOWED_ORIGIN"],
    'Access-Control-Allow-Methods': 'OPTIONS,POST,GET,PUT'
}


def schedule_surveys( surg_date: str, sub: str ):
    print("<New Enrollment For: ", surg_date )
    dt_obj = datetime.strptime(surg_date,"%Y-%m-%d")
    
    event_dates = []

    #testing purposes
    #event_dates.append( dt_obj - timedelta(minutes=2) )

    #real events
    
    event_dates.append( dt_obj - timedelta(days=10) )
    event_dates.append( dt_obj + timedelta(days=10) )
    for i in range(1,13):
        event_dates.append( dt_obj + relativedelta(months=i) )
        print( "Appending: ", (dt_obj + relativedelta(months=i)) )
    

    flex_window = { "Mode": "OFF" }

    header_tags=[
         "Pre-Operation",
         "10 Day After Surgery",
         "1 Month After Surgery",
         "2 Month After Surgery",
         "3 Month After Surgery",
         "4 Month After Surgery",
         "5 Month After Surgery",
         "6 Month After Surgery",
         "7 Month After Surgery",
         "8 Month After Surgery",
         "9 Month After Surgery",
         "10 Month After Surgery",
         "11 Month After Surgery",
         "12 Month After Surgery",

    ]

    i = 0
    for entry in event_dates:
        assigned=entry.strftime("%Y-%m-%dT%H:%M:%S")
        due=(entry + timedelta(days=10)).strftime("%Y-%m-%dT%H:%M:%S")
        ### for testing ==>
        #entry = datetime.now() + timedelta(minutes=2)
        #assigned = entry.strftime("%Y-%m-%dT%H:%M:%S")
        ######

        ### added retry at 0 just to support testing, live we will
        # want to go to sqs or something with retry
        lambda_target = {
            "Arn": target_arn,
            "RoleArn":target_role,
            "Input": json.dumps(
                {
                    "sub":sub,
                    "assigned": assigned,
                    "due": due,
                    "surg_date":surg_date,
                    "header_tag":header_tags[i]
                }
            ),
            'RetryPolicy': {
                'MaximumEventAgeInSeconds': 60,
                'MaximumRetryAttempts': 0
            }
        }
        # at(2022-11-20T13:00:00)
        tstamp = entry.strftime("%Y-%m-%dT%H:%M:%S")
        tstamp_e = entry.strftime("%Y-%m-%dT%Hh%Mm%Ss")
        event_name=sub+"-"+tstamp_e+"-"+str(i)
        expression="at(" + tstamp + ")"
        print("Scheduling @: ", expression)
        result = scheduler.create_schedule(
            Name=event_name,
            ScheduleExpression=expression,
            Target=lambda_target,
            FlexibleTimeWindow=flex_window
        )
        print(result)
        i=i+1
        # for testing only generate one set of survey
        # break
    return


def update_profile( field_values:json ):
    """
    Retrieve full payload for a specific scoring algorithm

    Parameters
    ----------
    field_values : json
        Payload to write to user table
    
    Returns
    -------
    json
        DynamoDB results
    """
    table = dynamodb.Table(table_name)

    
    return table.put_item ( Item=field_values  )

def add_patient_to_surgeon( patient: str, surgeon: str ):
    table = dynamodb.Table(surgeon_table_name)
    item = table.get_item(Key={'sub': surgeon}).get('Item',{})
    item.get('pts', []).append(patient)
    table.put_item(Item=item)

def handler(event,context):
    print(boto3.__version__)
    field_values=json.loads(event["body"])

    try:
        result = update_profile(field_values)
        if result['ResponseMetadata']['HTTPStatusCode'] != 200:
                raise Exception(f"DynamoDB issue")
        surg_date = field_values["profile"]["surgery_date"]
        sub = field_values["sub"]
        print("Read Surg Date: ", surg_date)
        print("Read Sub: ", sub)
        schedule_surveys(surg_date,sub)

        surgeon = field_values["profile"]["surgeon"].split(';')[0]
        add_patient_to_surgeon(sub, surgeon)
        
        return {
            "statusCode":200,
            "headers": CORS_HEADERS,
            "body": json.dumps({},cls=JSONEncoder)
        }
    except Exception as e:
        print("Exception: ",e)
        return {
            "statusCode":500,
            "headers": CORS_HEADERS,
            "body": json.dumps({"msg":str(e)})
        }


