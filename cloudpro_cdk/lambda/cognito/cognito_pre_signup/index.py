def handler(event, context):
    
    #print(event)
    #event['request']['userAttributes']['custom:isEmployeestr'] = "1"
    #print(event)
    # docs have stated can't set a custom attribute during pre_sign_up trigger
    # Return to Amazon Cognito
    return event