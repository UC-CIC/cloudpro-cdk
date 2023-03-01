import json
import boto3
import json
import os

client = boto3.client('cognito-idp')

debug_token=os.environ["DEBUG_TOKEN"]

def generate_policy( principal_id, effect, resource ):
    policy_document = {
        'principalId':principal_id,
        'policyDocument':{
            'Version':'2012-10-17',
            'Statement':[{
                'Action':'execute-api:Invoke',
                'Effect':effect,
                'Resource':resource
            }]
        }
    }
    return policy_document


def handler(event,context):
    #print(event)
    #print(context)
    auth_header = event['authorizationToken']
    token = auth_header.split(' ' )[1]
    #print("TOKEN: ", token)

    try:
        if auth_header==debug_token:
            pass
        else:
            raise("Bad token")

        # 'principalId':'user',
        # if valid allow

        policy_document = generate_policy("user","Allow",event['methodArn'])
        #print("POLICY GOOD: ",policy_document)
        return policy_document
    except Exception as e:
        #print("<EXCEPT>  :", e)
        # bad token
        policy_document = generate_policy("user","Deny",event['methodArn'])
        #print("POLICY Bad: ",policy_document)
        return policy_document