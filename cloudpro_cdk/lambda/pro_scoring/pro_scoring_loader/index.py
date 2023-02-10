import json
import boto3
from enum import Enum
import os
import hashlib
from scoring_safety.scoring_safety import ScoringSafety
import configparser

s3_resource = boto3.resource('s3')
dynamodb = boto3.resource('dynamodb')

table_name=os.environ["TABLE_SCORING"]


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



def db_save( payload:json ):
    table = dynamodb.Table(table_name)
    response = table.put_item(Item=payload)
    payload = {
        "scoring_response": response['ResponseMetadata']['HTTPStatusCode']
    }
    return payload

def read_from_s3(
    propack_name:str,
    propack_file:str,
    path:str,
    language:str,
    bucket:str 
):
    key=path + propack_name + "/" + language + "/" + propack_file
    print("[key] | " + key)

    file_obj=s3_resource.Object(bucket_name=bucket, key=key)
    file_contents = file_obj.get()['Body'].read()

    # sanitize formulas
    config = configparser.ConfigParser()
    config.read_string(file_contents.decode())

    try:
        sanitized_formula_set = []
        for section in config.sections():
            sanitized = ScoringSafety(config[section]["formula"])
            sanitized_formula = { "link_id": section, "formula": sanitized.formula }
            sanitized_formula_set.append(sanitized_formula)
    except Exception as e:
        raise( e )

    return sanitized_formula_set



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
        "propack_questionnaire_file": "questionnaire.json",
        "propack_scoring_file": "scoring.algo",
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
    propack_file=""
    path=""
    bucket=""
    language=""

    try:
        propack_name=event["detail"]["propack_name"]
        propack_file=event["detail"]["propack_scoring_file"]
        path="propack/"
        bucket=event["detail"]["bucket"]
        language=event["detail"]["language"]
    except Exception as e:
        pass

    
    if mode == SupportedModes.s3_mode:
        # read contents
        data = read_from_s3( 
            propack_name=propack_name,
            propack_file=propack_file,
            path=path,
            bucket=bucket,
            language=language
        )

        # build storage payload
        propack_hash=hashlib.sha256(propack_name.encode('utf-8')).hexdigest()
        payload = {}
        payload["pro_pack"] = propack_hash
        payload["pro_pack_format"] = pro_format
        payload["formulas"] = data

        # store contents
        response = db_save(payload)
        print(response)
    elif mode == SupportedModes.file_mode:
        # load from local file; not needed to be implemented for this POC
        pass
    

    return {
        'statusCode': 200,
        'body': json.dumps('<<<<<<<<<<<<<<< END >>>>>>>>>>>>>>>')
    }

