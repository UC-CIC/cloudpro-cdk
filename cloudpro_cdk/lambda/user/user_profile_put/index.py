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


table_name=os.environ["TABLE_USER"]
target_arn=os.environ["SCHEDULER_PROCESSING_ARN"]
target_role=os.environ["SCHEDULER_PROCESSING_ROLE"]


CORS_HEADERS = {
    'Access-Control-Allow-Headers': 'Content-Type',
    'Access-Control-Allow-Origin': os.environ["CORS_ALLOW_UI"],
    'Access-Control-Allow-Methods': 'OPTIONS,POST,GET,PUT'
}


def schedule_surveys( surg_date: str ):
    print("<New Enrollment For: ", surg_date )
    dt_obj = datetime.strptime(surg_date,"%Y-%m-%d")
    
    event_dates = []

    #testing purposes
    event_dates.append( dt_obj - timedelta(minutes=2) )

    #real events
    '''
    event_dates.append( dt_obj - timedelta(days=10) )
    event_dates.append( dt_obj + timedelta(days=10) )
    for i in range(1,13):
        event_dates.append( dt_obj + relativedelta(months=i) )
    '''

    flex_window = { "Mode": "OFF" }
    lambda_target = {
            "Arn": target_arn,
            "RoleArn":target_role,
            "Input": json.dumps({"foo": "bar"})
    }

    for entry in event_dates:
        # at(2022-11-20T13:00:00)
        expression="at(" + entry.strftime("%Y-%m-%dT%H:%M:%S") + ")"
        print("Scheduling @: ", expression)
        result = scheduler.create_schedule(
            Name="lambda-python-templated",
            ScheduleExpression=expression,
            Target=lambda_target,
            FlexibleTimeWindow=flex_window
        )
        print(result)
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


def handler(event,context):
    print(boto3.__version__)
    field_values=json.loads(event["body"])

    try:
        result = update_profile(field_values)
        if result['ResponseMetadata']['HTTPStatusCode'] != 200:
                raise Exception(f"DynamoDB issue")
        surg_date = field_values["profile"]["surgery_date"]
        print("Read Surg Date: ", surg_date)
        schedule_surveys(surg_date)
        
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


