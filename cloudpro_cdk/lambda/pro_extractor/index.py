import json
import boto3
import zipfile
import io
import os
import configparser

ebus_propack = os.environ['EBUS_PROPACK']
SOURCE=os.environ['IDENTIFIER']
DETAIL_TYPE=os.environ['DETAIL_TYPE']

s3_resource = boto3.resource('s3')
event_client = boto3.client('events')

def handler(event,context):
    # TODO implement
    print("<<< LOG ME >>>")
    print(event)
    
    source_bucket = event["detail"]["bucket"]["name"]
    source_key = event["detail"]["object"]["key"]
    filename = source_key[source_key.rfind("/")+1:]
    filename_noext = filename[:-4]

    print("[filename_noext] | " + filename_noext)

    zip_obj = s3_resource.Object(bucket_name=source_bucket, key=source_key)
    buffer = io.BytesIO(zip_obj.get()["Body"].read())
    prefix="propack/" 

    print("[prefix] | " + prefix)

    z = zipfile.ZipFile(buffer)
    for filename in z.namelist():
        file_info = z.getinfo(filename)
        write_name = prefix + filename
        print("[write_name] | " + write_name)
        s3_resource.meta.client.upload_fileobj(
            z.open(filename),
            Bucket=source_bucket,
            Key=f'{write_name}'
        )
    
    # get top level directory(s)
    top = {item.split('/')[0] for item in z.namelist()}
    propack_name = next(iter(top))
    
    print("[pro_name] | " + propack_name)

    # get config elements
    pro_config = "propack/" + propack_name + "/pack.config" 
    #### Read propack config
    config_file = s3_resource.Object(bucket_name=source_bucket, key=pro_config)
    config_file_contents = config_file.get()['Body'].read()
    config = configparser.ConfigParser()
    config.read_string(config_file_contents.decode())
    pro_format=config["MAIN"]["FORMAT"]

    detail_json = {
        "mode": "S3",
        "bucket": source_bucket,
        "propack_name": propack_name,
        "propack_format": pro_format,
        "language": "EN", # only supporting english for prototype
        "status":"extracted"
    }
    response = event_client.put_events(
        Entries=[
            {
                'Source': SOURCE,
                'DetailType': DETAIL_TYPE,
                'Detail': json.dumps(detail_json),
                'EventBusName':ebus_propack
            }
        ]
    )

    print(response)

    print("<<< LOG ME >>>")
    return {
        'statusCode': 200,
        'body': json.dumps('<<<<<<<<<<<<<<< END >>>>>>>>>>>>>>>')
    }
    