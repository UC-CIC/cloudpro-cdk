import json
import boto3
import configparser

from enum import Enum
from supported_loader import cpro_r1
from supported_loader import cpro_fhir

s3_resource = boto3.resource('s3')


### Enum extensions
class ExtendedSupportedFormatsEnum(Enum):
    @classmethod
    def list(cls):
        # return list of all enum values
        return list(map(lambda c: c.value, cls))
    @classmethod
    def list_key_values(cls):
        # return list of all dictionary keys
        output = list(set().union(*(d.keys() for d in list(map(lambda c: c.value, cls)))))
        return output
    @classmethod
    def function_calls(cls):
        # merge enum into a dictionary of text: func_call()
        enum_list = list(map(lambda c: c.value, cls))
        return {k: v for d in enum_list for k, v in d.items()}

class ExtendedEnum(Enum):
    @classmethod
    def list(cls):
        # return list of all enum values
        return list(map(lambda c: c.value, cls))

### Base Enums
class SupportedFormats(str,ExtendedEnum):
    cpro_r1 = "CPRO_R1"
    fhir_r4 = "FHIR_R4"
class SupportedFormatsFuncMapping(ExtendedSupportedFormatsEnum):
    cpro_r1 = {"CPRO_R1":cpro_r1}
    fhir_r4 = {"FHIR_R4":cpro_fhir}

class SupportedModes(str, ExtendedEnum):
    file_mode = "FILE"
    s3_mode = "S3"


def handler(event,context):
    mode = SupportedModes.s3_mode

    #################################################
    # FOR TESTING LAMBDA w/ MANUAL TRIGGER
    #################################################
    #'''
    detail_json = {
        "bucket": "cdk-propack-stack-cdkbucketpropackb412a3c9-154c3q9ssmsvm",
        "propack": "propack/Dyspnea Severity – Short Form 10a & Hard Coronary Disease (10-Year risk)",
        "status":"extracted"
    }
    event = {
        'source': "custom.lambda.proload.pro_extractor",
        'detail_type': "PRO Extraction",
        'detail': detail_json,
        'eventBusName':"cdk-ebus-cloudpro"
   }
   #'''
   #################################################

    print("<<< LOG ME >>>")


    # Get format of propack
    s3_bucket=event["detail"]["bucket"]
    propack_name=event["detail"]["propack"]

    propack_key= propack_name + "/pack.config"


    print("[s3_bucket] | "  + s3_bucket)
    print("[propack_name] | "  + propack_name)
    print("[propack_key] | "+ propack_key )
    

    config_file = s3_resource.Object(bucket_name=s3_bucket, key=propack_key)
    config_file_contents = config_file.get()['Body'].read()
    config = configparser.ConfigParser()
    
    propack_format=config.read_string(config_file_contents.decode())

    print('config["MAIN"]["FORMAT"] | ' + config["MAIN"]["FORMAT"])


    # Load handler for format

    # make sure we have bucket name in S3 Mode
    if mode==SupportedModes.s3_mode and s3_bucket is None:
        return {
            'statusCode': 200,
            'body': json.dumps('<<<<<<<<<<<<<<< ERROR: Invalid Mode Combo >>>>>>>>>>>>>>>')
        }
    
    # make sure format value is a valid format
    if not config["MAIN"]["FORMAT"] in SupportedFormats.list():
        return {
            'statusCode': 200,
            'body': json.dumps('<<<<<<<<<<<<<<< ERROR: Invalid file format >>>>>>>>>>>>>>>')
        }
    
    try:
        # note; right now only supporting english
        load_data=SupportedFormatsFuncMapping.function_calls()[propack_format].load(
            mode=mode,
            pro_pack_format=propack_format,
            pro_pack_name=propack_name,
            pro_pack_question_file="questionnaire.json",
            pro_pack_scoring_file="scoring.algo",
            path="/EN/",
            bucket=s3_bucket,
            s3_resource=s3_resource
        )
        print(load_data)
    except Exception as e:
        pass


    
    print( "I AM LOADER")
    print(event)
    print("<<< LOG ME >>>")
    return {
        'statusCode': 200,
        'body': json.dumps('<<<<<<<<<<<<<<< END >>>>>>>>>>>>>>>')
    }
    