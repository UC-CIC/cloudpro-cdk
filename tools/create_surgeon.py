import json
import boto3
from enum import Enum
import os
import hashlib

SURGEON_TABLE = "cdk-dynamodb-stack-dev-dynamosurgeonsD667B836-1RY4D27TH2FLS"
USERPOOL_ID = "us-east-1_at4O9Hx40"
HOSPITAL_TABLE = "cdk-dynamodb-stack-dev-dynamohospitals5569DB0A-8AJGK8P1C7J"

dynamodb = boto3.resource("dynamodb")
client = boto3.client("cognito-idp")

table_name = SURGEON_TABLE

name = "Dr. Bob Sinclair"
email = "bob@surgeon.com"
phone = "+1111111111" # include the country code in the phone (+1 for USA)
patients = [] # add sub of patients
password = "cip#!bu0ido?HAxestad"
hid = "2" # hospital id (1 - Most General Named Hospital, 2 - Most Specific Named Hospital)

# Create a new user in Cognio User Pool
response = client.admin_create_user(
    UserPoolId=USERPOOL_ID,
    Username=email,
    UserAttributes=[
        {"Name": "custom:isEmployee", "Value": "1"},
        {"Name": "custom:otp_method", "Value": "sms"},
        {"Name": "email", "Value": email},
        {"Name": "email_verified", "Value": "true"},
        {"Name": "phone_number", "Value": phone},
        {"Name": "phone_number_verified", "Value": "true"},
    ],
    TemporaryPassword=password,
    MessageAction="SUPPRESS",
)
sub = response["User"]["Username"]

# Update temporary password to set the status as confirmed
response = client.admin_set_user_password(
    UserPoolId=USERPOOL_ID, Username=email, Password=password, Permanent=True
)

# Add user to the "surgeon" group
response = client.admin_add_user_to_group(
    UserPoolId=USERPOOL_ID, Username=email, GroupName="surgeons"
)

# Enable MFA
response = client.admin_set_user_mfa_preference(
    SMSMfaSettings={"Enabled": True, "PreferredMfa": False},
    Username=email,
    UserPoolId=USERPOOL_ID,
)

# Add the new user to surgeon table in dynamodb
payload = {"sub": sub, "email": email, "name": name, "phone": phone, "pts": patients}

surgeon_table = dynamodb.Table(SURGEON_TABLE)
response = surgeon_table.put_item(Item=payload)

hospital_table = dynamodb.Table(HOSPITAL_TABLE)
item = hospital_table.get_item(Key={"hid": hid}).get('Item', {})
item.get("surgeons", []).append({
    "name": name,
    "sub": sub
})
response = hospital_table.put_item(Item=item)