import json
import boto3



def handler(event,context):
    # TODO implement
    print("<<< LOG ME >>>")
    print( "I AM LOADER")
    print(event)
    print("<<< LOG ME >>>")
    return {
        'statusCode': 200,
        'body': json.dumps('<<<<<<<<<<<<<<< END >>>>>>>>>>>>>>>')
    }
    