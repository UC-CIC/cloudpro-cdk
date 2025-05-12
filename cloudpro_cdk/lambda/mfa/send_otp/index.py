import json
import boto3
import os
from string import digits
import secrets

from json_encoder.json_encoder import JSONEncoder

dynamodb = boto3.resource("dynamodb")
sns = boto3.client("sns")

table_name = os.environ["TABLE_OTP"]


CORS_HEADERS = {
    "Access-Control-Allow-Headers": "Content-Type",
    "Access-Control-Allow-Origin": os.environ["CORS_ALLOWED_ORIGIN"],
    "Access-Control-Allow-Methods": "OPTIONS,POST,GET",
}


def send_otp(phone: str):
    """
    Send an otp

    Parameters
    ----------
    phone : str
        The phone number of the user

    Returns
    -------
    str:
        The generated otp
    """

    rand = secrets.SystemRandom()
    otp = "".join(rand.choice(digits) for _ in range(6))

    sns.publish(PhoneNumber=phone, Message=f"Your OTP is: {otp}")

    return otp


def add_otp_in_dynamo(phone: str, otp: str):
    """
    Save the otp in dynamodb to access it during verification

    Parameters
    ----------
    phone : str
        The phone number of the user
    otp : str
        The otp that was sent
    """

    table = dynamodb.Table(table_name)
    table.put_item(Item={"phone": phone, "otp": otp})


def handler(event, context):
    phone = event["pathParameters"]["phone"]
    try:
        otp = send_otp(phone)
        add_otp_in_dynamo(phone, otp)

        return {
            "statusCode": 200,
            "headers": CORS_HEADERS,
            "body": json.dumps("Code sent successfully!", cls=JSONEncoder),
        }
    except Exception as e:
        return {
            "statusCode": 500,
            "headers": CORS_HEADERS,
            "body": json.dumps({"msg": str(e)}),
        }
