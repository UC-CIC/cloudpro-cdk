import json
import boto3
import os

from datetime import datetime
from datetime import timedelta
from dateutil.relativedelta import relativedelta

from json_encoder.json_encoder import JSONEncoder

scheduler = boto3.client('scheduler')
target_arn=os.environ["SCHEDULER_PROCESSING_ARN"]
target_role=os.environ["SCHEDULER_PROCESSING_ROLE"]

CORS_HEADERS = {
    'Access-Control-Allow-Headers': 'Content-Type',
    'Access-Control-Allow-Origin': os.environ["CORS_ALLOW_UI"] if os.environ["LOCALHOST_ORIGIN"] == "" else os.environ["LOCALHOST_ORIGIN"],
    'Access-Control-Allow-Methods': 'OPTIONS,POST,GET,PUT'
}

def handler(event,context):
    print(event)
    field_values=json.loads(event["body"])
    schedule_name=field_values["name"]

    curtime = datetime.now()
    print( "Cur time: ", curtime)
    runtime = (curtime + timedelta(minutes=1)).strftime("%Y-%m-%dT%H:%M:%S")
    print( "Plus 1 Min time: ", runtime)


    print(boto3.__version__)
    try:
        response = scheduler.get_schedule(
            Name=schedule_name
        )
        print("~~~~~~~~~~~~~~Get Schedule Response~~~~~~~~~~~~~~~")
        print(response)
        update_response=scheduler.update_schedule(
            Name=schedule_name,
            FlexibleTimeWindow={
                'Mode': 'OFF'
            },
            ScheduleExpression="at(" + runtime + ")",
            ScheduleExpressionTimezone="UTC",
            State='ENABLED',
            Target={
                'Arn': response["Target"]["Arn"],
                'Input': response["Target"]["Input"],
                'RetryPolicy': {
                    'MaximumEventAgeInSeconds': response["Target"]["RetryPolicy"]["MaximumEventAgeInSeconds"],
                    'MaximumRetryAttempts':response["Target"]["RetryPolicy"]["MaximumRetryAttempts"]
                },
                'RoleArn': response["Target"]["RoleArn"],
            })
        
        print("~~~~~~~~~~~~~~Update Schedule Response~~~~~~~~~~~~~~~")
        print(update_response)
        
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

#            ScheduleExpression=f'cron({schedule_time.minute} {schedule_time.hour} {schedule_time.day} {schedule_time.month} ? {schedule_time.year})',
