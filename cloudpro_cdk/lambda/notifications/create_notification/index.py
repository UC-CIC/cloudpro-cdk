import json
import boto3
import os
from decimal import Decimal

from json_encoder.json_encoder import JSONEncoder

dynamodb = boto3.resource('dynamodb')
table_name=os.environ["TABLE_NOTIFICATIONS"]


def write_notification( sub:str,date:str,notification:str,notification_type:str,notification_status:str,notification_id:str):
    """
    Write a new notification

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

    
    add_payload = {
        notification_id: {
            "date":date,
            "notification":notification,
            "notificaiton_type":notification_type,
            "notification_status":notification_status
        }
    }

    
    current_notifications = {}
    payload = {
        "sub": sub,
        "notifications":{}
    }
    
    try:
        current = table.get_item(Key=search_key)["Item"]
        current_notifications = current["notifications"]
        print(current_notifications)
    except:
        pass

    current_notifications.update(add_payload)
    payload["notifications"] = current_notifications

    table.put_item ( Item=payload  )


def handler(event,context):
    '''
    {
        "sub":"test",
        "date":"20230110T11:55:00",
        "notification_id":"jdfakjfskafj",
        "notification":"This is a sample notification",
        "notification_type":"INFO",
        "notification_status":"NEW"
    }
    '''
    source_sub = event["detail"]["sub"]
    source_date = event["detail"]["date"]
    source_notification = event["detail"]["notification"]
    source_notification_type = event["detail"]["notification_type"]
    source_notification_status = event["detail"]["notification_status"]
    source_notification_id = event["detail"]["notification_id"]
    write_notification(sub=source_sub,date=source_date,notification=source_notification,notification_type=source_notification_type,notification_status=source_notification_status,notification_id=source_notification_id)

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


