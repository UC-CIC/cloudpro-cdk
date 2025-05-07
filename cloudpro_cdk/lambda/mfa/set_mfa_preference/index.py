import json
import boto3
import os

from json_encoder.json_encoder import JSONEncoder

cognito = boto3.client("cognito-idp")

CORS_HEADERS = {
    "Access-Control-Allow-Headers": "Content-Type",
    "Access-Control-Allow-Origin": os.environ["CORS_ALLOWED_ORIGIN"],
    "Access-Control-Allow-Methods": "OPTIONS,POST,GET",
}


def check_phone_verification(email: str):
    """
    Checks if user has a verified phone

    Parameters
    ----------
    email : str
        The email id of the user

    Returns
    -------
    bool:
        true/false
    """
    user_attributes = cognito.admin_get_user(
        UserPoolId=os.environ.get("USERPOOL_ID"), Username=email
    )["UserAttributes"]

    for attr in user_attributes:
        if attr['Name'] == 'phone_number' and attr['Value']:
            return True
    return False

def update_custom_attribute(email: str, otp_method: str):
    """
    Update custom:otp_method for the user in cognito

    Parameters
    ----------
    email : str
        The email id of the user
    otp_method : str
        The otp method the user wants to set - email/sms

    Returns
    -------
    json:
        Cognito result
    """
    return cognito.admin_update_user_attributes(
        UserPoolId=os.environ.get("USERPOOL_ID"),
        Username=email,
        UserAttributes=[
            {"Name": "custom:otp_method", "Value": otp_method},
        ],
    )


def handler(event, context):
    email = json.loads(event["body"])["email"]
    otp_method = json.loads(event["body"])["otp_method"]

    try:
        if otp_method ==  'sms':
            verified_phone = check_phone_verification(email)
            if not verified_phone:
                return {
                    "statusCode": 400,
                    "headers": CORS_HEADERS,
                    "body": json.dumps('Phone number is not verified'),
                }
        
        update_custom_attribute(email, otp_method)
        return {
            "statusCode": 200,
            "headers": CORS_HEADERS,
            "body": json.dumps("Successfully updated the otp method", cls=JSONEncoder),
        }
    except Exception as e:
        return {
            "statusCode": 500,
            "headers": CORS_HEADERS,
            "body": json.dumps({"msg": str(e)}),
        }