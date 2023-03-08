import json
import boto3
import os

def handler(event,context):
    print("<SCHEDULER_PROCESSING:Hello>")
    return {
        "statusCode":200,
        "body": json.dumps("Scheduler Processing Hello World")
    }
