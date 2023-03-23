import json
import boto3
import os


cognito_client = boto3.client("cognito-idp")



def handler(event, context):
    """Verify Auth Challenge
    
    """
    print(event, '--------- Start --------------')
    
    response = event.get('response')
    request = event.get('request')
    session = request.get('session')
    
    answerCorrect = False
    
    expectedAnswer = request.get('privateChallengeParameters').get('answer') 
    challengeAnswer = request.get('challengeAnswer')

    if challengeAnswer == expectedAnswer:
        answerCorrect = True
        pool_id = event.get('userPoolId')
        userName = event.get('userName')
        
        result = cognito_client.admin_list_groups_for_user(
            Username=userName,
            UserPoolId=pool_id,
            Limit=1
        )
        print("result:",result)
        ugroup = ""
        try:
            ugroup = result["Groups"][0]["GroupName"]
            print("GROUP: ",ugroup)
        except: 
            result = cognito_client.admin_add_user_to_group(
                UserPoolId=pool_id,
                Username=userName,
                GroupName="patients"
            )

        isEmployee = "0"
        if ugroup == "surgeons":
            isEmployee = "1"
        
        # Update user Attributes
        result = cognito_client.admin_update_user_attributes(
            UserPoolId=pool_id,
            Username=userName,
            UserAttributes=[
                {
                    'Name': 'email_verified',
                    'Value': 'true'
                },
                {
                    'Name': 'custom:isEmployee',
                    'Value': isEmployee
                },
            ]
        )
        
    response.update({
        'answerCorrect': answerCorrect
    })
   
    print(event, "-----end---------")
   
    return event