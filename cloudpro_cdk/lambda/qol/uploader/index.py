import json
import os
import logging
import boto3
from botocore.exceptions import ClientError

CORS_HEADERS = {
    'Access-Control-Allow-Headers': 'Content-Type',
    'Access-Control-Allow-Origin': os.environ["CORS_ALLOW_UI"] if os.environ["LOCALHOST_ORIGIN"] == "" else os.environ["LOCALHOST_ORIGIN"],
    'Access-Control-Allow-Methods': 'OPTIONS,POST,GET,PUT'
}

bucket_name=os.environ["BUCKET_PROPACK_NAME"]

#short circuit for testing
bucket_name="cdk-propack-stack-bucketpropack5dd3828c-uemyj1eyoq46"

def create_presigned_url( object_name, expiration=3600):
    """Generate a presigned URL to share an S3 object

    :param bucket_name: string
    :param object_name: string
    :param expiration: Time in seconds for the presigned URL to remain valid
    :return: Presigned URL as string. If error, returns None.
    """

    # Generate a presigned URL for the S3 object
    s3_client = boto3.client('s3')
    try:
        response = s3_client.generate_presigned_post( Bucket=bucket_name,
                                                      Key="raw/"+object_name,
                                                      ExpiresIn=expiration)
    except ClientError as e:
        logging.error(e)
        return None

    # The response contains the presigned URL
    return response

def handler(event,context):
    field_values=json.loads(event["body"])
    object_name=field_values["file_name"]

    response = create_presigned_url( object_name )

    return {
        "statusCode":200,
        "headers": CORS_HEADERS,
        "body": json.dumps(response,cls=JSONEncoder)
    }