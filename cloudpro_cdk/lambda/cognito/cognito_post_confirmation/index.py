import json

import boto3
from boto3.dynamodb.conditions import Key
import botocore.exceptions

import os

dynamodb = boto3.resource('dynamodb')
table_name_user=os.environ["TABLE_USER"]
table_name_user_staged=os.environ["TABLE_USER_STAGED"]
#event.request.userAttributes.email

def init_user_record( contact:str,sub:str ):
    table = dynamodb.Table(table_name_user)
    table_staged = dynamodb.Table(table_name_user_staged)

    user_payload = {
        'sub':sub,
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
        search_key = {
            'email': contact
        }        

        result = table_staged.get_item(Key=search_key)
        print(result)
        if( 'Item' in result ):
            user_payload = result["Item"].copy()
            user_payload['sub'] = sub
            user_payload['state'] = "STAGED"
    except Exception as e:
        print("Exception on staged tabel: ", e)
        raise

    try:
        table.put_item(
            Item=user_payload
        )
    except Exception as e:
        raise Exception("<Irrecoverable write error")

def handler(event, context):
    """Post Confirmation
    
    """
    print(event, '--------- Start --------------')
    
    request = event.get('request')
    contact = request.get('userAttributes').get('email')
    sub = request.get('userAttributes').get('sub')
    #print("EMAIL: ", contact)

    try:
        init_user_record( contact,sub ) 
    except Exception as e:
        print(e)

    #attempting to set to false here
    #event['request']['userAttributes']['custom:isEmployeeDec'] = "1"
    print(event, "-----end---------")
   
    return event