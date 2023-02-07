import json
import boto3
import zipfile
import io

s3_resource = boto3.resource('s3')

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
    
    print("<<< LOG ME >>>")
    return {
        'statusCode': 200,
        'body': json.dumps('Hello 2 from Lambda!')
    }