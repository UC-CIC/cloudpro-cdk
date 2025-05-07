import json
from string import digits
import secrets
import boto3

ses_client = boto3.client("ses")
sns_client = boto3.client("sns")


def send_plain_email(contact, secretLoginCode):
    # we are running SES in sandbox.  function needs modified in live production mode
    CHARSET = "UTF-8"

    ses_response = ses_client.send_email(
        Destination={
            "ToAddresses": [
                contact,
            ],
        },
        Message={
            "Body": {
                "Text": {
                    "Charset": CHARSET,
                    "Data": "Hello, your login code is: " + secretLoginCode,
                }
            },
            "Subject": {
                "Charset": CHARSET,
                "Data": "Your CloudPRO Login OTC",
            },
        },
        Source=contact,
    )
    return ses_response


def send_plain_sms(contact, secretLoginCode):
    return sns_client.publish(
        PhoneNumber=contact,
        Message=f"Thanks for signing up to our CloudPRO app! Your verification code is {secretLoginCode}",
        MessageAttributes={
            'AWS.MM.SMS.OriginationNumber': {
                'DataType': 'String',
                'StringValue': '+18559321105',
            }
        }
    )


def handler(event, context):
    """Create Challenge and then Send Notification"""

    print(event, "-------------- start ---------------")

    response = event.get("response")
    request = event.get("request")
    session = request.get("session")

    rand = secrets.SystemRandom()

    preferred_mfa = event["request"]["userAttributes"].get("custom:otp_method", "email")

    if preferred_mfa == "email":
        if (not session) or len(session) == 0:
            print(event, "--------create Challenge-------------")
            secretLoginCode = "".join(rand.choice(digits) for _ in range(6))

            #### TEMPORARY FOR TESTING
            # secretLoginCode = "123456"
            contact = request.get("userAttributes").get("email")
            try:
                ses_response = send_plain_email(
                    contact=contact, secretLoginCode=secretLoginCode
                )
                print("SES response: ", ses_response)
            except Exception as e:
                print("SES error: ", str(e))
            # send Notification

            # << call your notify fn here>>
            print("<<<<<TEMPORARY DELETE ME>>>>>>", secretLoginCode)
        else:
            print(event, "--------Used existing Challenge-------------")
            previousChallenge = session[0]

            #### TEMPORARY FOR TESTING
            # previousChallenge = "123456"
            # contact = previousChallenge.get('userAttributes').get('email')
            # added code
            ############

            secretLoginCode = previousChallenge.get("challengeMetadata")
            contact = previousChallenge.get("userAttributes").get("email")

            try:
                ses_response = send_plain_email(
                    contact=contact, secretLoginCode=secretLoginCode
                )
                print("SES response: ", ses_response)
            except Exception as e:
                print("SES error: ", str(e))
            print("<<<<<TEMPORARY DELETE ME [prev challenge]>>>>>>", secretLoginCode)

        response.update(
            {
                "privateChallengeParameters": {"answer": secretLoginCode},
                "challengeMetadata": secretLoginCode,
                "publicChallengeParameters": {
                    "email": request.get("userAttributes").get("email")
                },
            }
        )

    else:
        if (not session) or len(session) == 0:
            print(event, "--------create Challenge-------------")
            secretLoginCode = "".join(rand.choice(digits) for _ in range(6))

            #### TEMPORARY FOR TESTING
            # secretLoginCode = "123456"
            contact = request.get("userAttributes", {}).get("phone_number")
            try:
                sns_response = send_plain_sms(
                    contact=contact, secretLoginCode=secretLoginCode
                )
                print("SNS response: ", ses_response)
            except Exception as e:
                print("SNS error: ", str(e))
            # send Notification

            # << call your notify fn here>>
            print("<<<<<TEMPORARY DELETE ME>>>>>>", secretLoginCode)
        else:
            print(event, "--------Used existing Challenge-------------")
            previousChallenge = session[0]

            #### TEMPORARY FOR TESTING
            # previousChallenge = "123456"
            # contact = previousChallenge.get('userAttributes').get('email')
            # added code
            ############

            secretLoginCode = previousChallenge.get("challengeMetadata")
            contact = previousChallenge.get("userAttributes", {}).get("phone_number")

            try:
                sns_response = send_plain_sms(
                    contact=contact, secretLoginCode=secretLoginCode
                )
                print("SNS response: ", ses_response)
            except Exception as e:
                print("SNS error: ", str(e))
            print("<<<<<TEMPORARY DELETE ME [prev challenge]>>>>>>", secretLoginCode)

        response.update(
            {
                "privateChallengeParameters": {"answer": secretLoginCode},
                "challengeMetadata": secretLoginCode,
                "publicChallengeParameters": {
                    "phone_number": request.get("userAttributes", {}).get(
                        "phone_number"
                    )
                },
            }
        )

    print(event, "--------end-------------")

    return event
