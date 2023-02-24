import json
import boto3
import os
import botocore.exceptions

dynamodb = boto3.resource('dynamodb')
table_name_user=os.environ["TABLE_USER"]

#event.request.userAttributes.email

def init_user_record( contact:str ):
    table = dynamodb.Table(table_name_user)

    user_payload = {
        'email':contact,
        'state':"INIT",
        'tfa':'',
        'profile': {
            'first_name':'',
            'last_name':'',
            'birth_date':'',
            'birth_sex':'',
            'phone':'',
            'hospital':'',
            'surgeon':'',
            'surgery_date':''
        },
        'challenge': {
            'c1q':'',
            'c1a':'',
            'c2q':'',
            'c2a':'',
            'c3q':'',
            'c3a':''
        }
    }
    
    try:
        table.put_item(
            Item=user_payload,
            ConditionExpression='attribute_not_exists(email)'
        )
    except botocore.exceptions.ClientError as e:
        # Ignore the ConditionalCheckFailedException, bubble up
        # other exceptions.
        if e.response['Error']['Code'] != 'ConditionalCheckFailedException':
            raise
        else:
            print("<Existing Staged Record>")

def handler(event, context):
    """Post Confirmation
    
    """
    print(event, '--------- Start --------------')
    
    request = event.get('request')
    contact = request.get('userAttributes').get('email')
    #print("EMAIL: ", contact)

    try:
        init_user_record( contact ) 
    except Exception as e:
        print(e)

    print(event, "-----end---------")
   
    return event