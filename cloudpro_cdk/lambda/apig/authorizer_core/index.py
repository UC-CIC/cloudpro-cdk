import json
import boto3
import json

client = boto3.client('cognito-idp')

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
        response = client.get_user(
            AccessToken=token
        )

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