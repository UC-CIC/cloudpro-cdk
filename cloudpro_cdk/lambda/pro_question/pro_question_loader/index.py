import json
import boto3
from enum import Enum
import os
import hashlib


s3_resource = boto3.resource('s3')
dynamodb = boto3.resource('dynamodb')


class ExtendedEnum(Enum):
    @classmethod
    def list(cls):
        # return list of all enum values
        return list(map(lambda c: c.value, cls))

class SupportedModes(str, ExtendedEnum):
    file_mode = "FILE"
    s3_mode = "S3"
class SupportedFormats(str,ExtendedEnum):
    cpro_r1 = "CPRO_R1"
    fhir_r4 = "FHIR_R4"



def store_questionnaire( questionnaire:json ):
    table_name = os.environ["TABLE_QUESTIONNAIRE"]
    table = dynamodb.Table(table_name)
    questionnaire_response = table.put_item(Item=questionnaire)
    payload = {
        "questionnaire_response": questionnaire_response['ResponseMetadata']['HTTPStatusCode']
    }
    return payload

def read_questionnaire_from_s3(propack_name:str,propack_question_file:str,path:str,language:str,bucket:str):
    questionnaire_key=path + propack_name + "/" + language + "/" + propack_question_file
    print("[questionnaire_key] | " + questionnaire_key)

    questionnaire_file=s3_resource.Object(bucket_name=bucket, key=questionnaire_key)
    questionnaire_contents = questionnaire_file.get()['Body'].read()
    return json.loads(questionnaire_contents)



def handler(event,context):
    #################################################
    # FOR TESTING LAMBDA w/ MANUAL TRIGGER
    #################################################
    '''
    detail_json = {
        "mode": "S3",
        "bucket": os.environ["PROPACK_BUCKET"],
        "propack_name": "Dyspnea Severity – Short Form 10a & Hard Coronary Disease (10-Year risk)",
        "propack_format": "CPRO_R1",
        "language":"EN",
        "status":"extracted"
    }
    event = {
        'source': "custom.lambda.proload.pro_extractor",
        'detail_type': "PRO Extraction",
        'detail': detail_json,
        'eventBusName':"cdk-ebus-cloudpro"
   }
   '''
   #################################################
   
    try:
        mode = event["detail"]["mode"]

        if( mode not in SupportedModes.list() ):
            raise Exception("Non supported mode: ", mode)
    except Exception as e:
        pass
    try:
        pro_format = event["detail"]["propack_format"]

        if( mode not in SupportedModes.list() ):
            raise Exception("Non supported format: ", pro_format)
    except Exception as e:
        pass

    propack_name=""
    propack_question_file=""
    path=""
    bucket=""
    language=""

    try:
        propack_name=event["detail"]["propack_name"]
        propack_question_file="questionnaire.json"
        path="propack/"
        bucket=event["detail"]["bucket"]
        language=event["detail"]["language"]
    except Exception as e:
        pass

    
    if mode == SupportedModes.s3_mode:
        # read contents
        questionnaire_content = read_questionnaire_from_s3( 
            propack_name=propack_name,
            propack_question_file=propack_question_file,
            path=path,
            bucket=bucket,
            language=language
        )

        # build storage payload
        propack_hash=hashlib.sha256(propack_name.encode('utf-8')).hexdigest()
        payload = {}
        payload["pro_pack"] = propack_hash
        payload["pro_pack_format"] = pro_format
        payload["data"] = questionnaire_content

        # store contents
        response = store_questionnaire(payload)
        print(response)
    elif mode == SupportedModes.file_mode:
        # load from local file; not needed to be implemented for this POC
        pass

