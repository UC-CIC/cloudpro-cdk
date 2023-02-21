import json
from string import digits
import secrets




def handler(event, context):
    """Create Challenge and then Send Notification
    """

    print(event, '-------------- start ---------------')
    
    response = event.get('response')
    request = event.get('request')
    session = request.get('session')
    
    rand = secrets.SystemRandom()

    

    if (not session) or len(session) == 0:
        print(event, '--------create Challenge-------------')
        secretLoginCode  = "".join(rand.choice(digits) for _ in range(6))

        #### TEMPORARY FOR TESTING
        #secretLoginCode = "123456"
        #contact = request.get('userAttributes').get('email')
        # send Notification
        
        # << call your notify fn here>>
        print("<<<<<TEMPORARY DELETE ME>>>>>>", secretLoginCode)
    else:
        print(event, '--------Used existing Challenge-------------')
        previousChallenge = session[0]

        #### TEMPORARY FOR TESTING
        previousChallenge = "123456"
        #contact = previousChallenge.get('userAttributes').get('email')
        # added code 
        ############

        secretLoginCode = previousChallenge.get('challengeMetadata')

        print("<<<<<TEMPORARY DELETE ME [prev challenge]>>>>>>", secretLoginCode)

    response.update({
        'privateChallengeParameters': {'answer': secretLoginCode},
        'challengeMetadata': secretLoginCode,
        'publicChallengeParameters': {
            'email': request.get("userAttributes").get("email")
        }
    })    

    print(event, '--------end-------------')
    
    return event
