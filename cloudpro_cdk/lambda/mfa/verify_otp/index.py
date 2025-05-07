import json
import boto3
import os
from string import digits

from json_encoder.json_encoder import JSONEncoder

dynamodb = boto3.resource("dynamodb")
cognito = boto3.client("cognito-idp")
sns = boto3.client("sns")

table_name = os.environ["TABLE_OTP"]


CORS_HEADERS = {
    "Access-Control-Allow-Headers": "Content-Type",
    "Access-Control-Allow-Origin": os.environ["CORS_ALLOWED_ORIGIN"],
    "Access-Control-Allow-Methods": "OPTIONS,POST,GET",
}


def get_otp_from_dynamo(phone: str):
    """
    Get the otp from the dynamo table

    Parameters
    ----------
    phone : str
        The phone number of the user

    Returns
    -------
    str:
        The otp sent to user
    """

    table = dynamodb.Table(table_name)
    search_key = {"phone": phone}

    return (
        table.get_item(Key=search_key, ConsistentRead=True).get("Item", {}).get("otp")
    )


def verify_otp(otp: str, otp_sent: str):
    """
    Verify otp if sns is out of sandbox

    Parameters
    ----------
    otp : str
        The otp input from the user
    otp_sent: str
        The otp sent to the user

    Returns
    -------
    bool:
        true/false
    """

    if otp_sent == otp:
        return True
    return False


def verify_sns_sandbox_phone(phone: str, otp: str):
    """
    Verify otp if sns is in the sandbox

    Parameters
    ----------
    phone : str
        The phone number of the user
    otp : str
        The otp input from the user

    Returns
    -------
    bool:
        true/false
    """

    try:
        response = sns.verify_sms_sandbox_phone_number(
            PhoneNumber=phone, OneTimePassword=otp
        )
        if response["ResponseMetadata"]["HTTPStatusCode"] == 200:
            return True
        return False
    except Exception as e:
        print(e)
        return False


def update_custom_attribute(email: str, phone: str):
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
            {"Name": "phone_number", "Value": phone},
            {"Name": "phone_number_verified", "Value": "true"},
        ],
    )


def update_user_mfa_settings(email: str):
    """
    Enable mfa for user in cognito

    Parameters
    ----------
    email : str
        The email id of the user
    """

    cognito.admin_set_user_mfa_preference(
        SMSMfaSettings={"Enabled": True, "PreferredMfa": False},
        Username=email,
        UserPoolId=os.environ.get("USERPOOL_ID"),
    )


def delete_otp_in_dynamo(phone: str):
    """
    Delete otp from dynamo

    Parameters
    ----------
    phone : str
        The phone number of the user
    """

    table = dynamodb.Table(table_name)
    table.delete_item(Key={"phone": phone})


def handler(event, context):
    email = json.loads(event["body"])["email"]
    phone = json.loads(event["body"])["phone"]
    otp = json.loads(event["body"])["otp"]

    try:
        otp_sent = get_otp_from_dynamo(phone)
        if otp_sent == "SANDBOX":
            status = verify_sns_sandbox_phone(phone, otp)
        else:
            status = verify_otp(otp, otp_sent)

        if status:
            update_custom_attribute(email, phone)
            update_user_mfa_settings(email)
            delete_otp_in_dynamo(phone)

            return {
                "statusCode": 200,
                "headers": CORS_HEADERS,
                "body": json.dumps("OTP verified successfully", cls=JSONEncoder),
            }

        return {
            "statusCode": 403,
            "headers": CORS_HEADERS,
            "body": json.dumps("Incorrect OTP!"),
        }
    except Exception as e:
        return {
            "statusCode": 500,
            "headers": CORS_HEADERS,
            "body": json.dumps({"msg": str(e)}),
        }
