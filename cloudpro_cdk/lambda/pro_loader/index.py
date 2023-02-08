import json
import boto3
import configparser

s3_resource = boto3.resource('s3')

def handler(event,context):
    # TODO implement
    print("<<< LOG ME >>>")


    s3_bucket=event["detail"]["bucket"]
    propack_name=event["detail"]["propack"]

    s3_resource = boto3.resource('s3')
    propack_key= propack_name + "/pack.config"


    print("[s3_bucket] | "  + s3_bucket)
    print("[propack_name] | "  + propack_name)
    print("[propack_key] | "+ propack_key )
    

    config_file = s3_resource.Object(bucket_name=s3_bucket, key=propack_key)
    config_file_contents = config_file.get()['Body'].read()
    config = configparser.ConfigParser()
    config.read_string(config_file_contents.decode())

    print('config["MAIN"]["FORMAT"] | ' + config["MAIN"]["FORMAT"])

    
    print( "I AM LOADER")
    print(event)
    print("<<< LOG ME >>>")
    return {
        'statusCode': 200,
        'body': json.dumps('<<<<<<<<<<<<<<< END >>>>>>>>>>>>>>>')
    }
    