from .scoring_safety import ScoringSafety
import hashlib
import json
import configparser
import boto3


def load( mode:str, pro_pack_format:str, pro_pack_name:str, path:str, pro_pack_question_file:str,pro_pack_scoring_file:str, bucket=None, s3_resource=None ):
    """
    Load a PRO Pack that is in CloudPRO format

    Parameters
    ----------
    mode : str
        Mode represents if we are reading the file locally (FILE) or from a S3 (S3) bucket.
    
    pro_pack_format : str
        Format the PRO pack is in

    path : str
        Path to the PRO pack (where the questionnaire and scoring files reside)
    
    pro_pack_question_file: str
        Questionnaire json file name

    pro_pack_scoring_file: str
        Scoring algorithm file name

    bucket: str : Optional
        Bucket name


    Returns
    -------
    json
        Load status payload
    """
    questionnaire={}
    scoring={}
    
    # "mapper" for pro pack to both formula and contents
    # this will be unique ID that can be searched on in Dynamo
    pro_pack_hash=hashlib.sha256(pro_pack_name.encode('utf-8')).hexdigest()

    if( mode == "FILE" ):
        formula=read_scoring_from_file(path,pro_pack_scoring_file)
        questionnaire_json=read_questionnaire_from_file(path,pro_pack_question_file)
    if( mode == "S3" ):
        formula=""
        questionnaire_json=read_questionnaire_from_s3(pro_pack_name,pro_pack_question_file,path,pro_pack_question_file)
        
    scoring["pro_pack"] = pro_pack_hash
    scoring["pro_pack_format"] = pro_pack_format
    scoring["formulas"] = formula

    questionnaire["pro_pack"] = pro_pack_hash
    questionnaire["pro_pack_format"] = pro_pack_format
    questionnaire["data"] = questionnaire_json

    payload = {
        "scoring": scoring,
        "questionnaire": questionnaire
    }

    return payload


def read_questionnaire_from_s3(pro_pack_name,pro_pack_question_file,path:str,bucket:str,s3_resource):
    '''
        mode=mode,
        pro_pack_format=propack_format,
        pro_pack_name=propack_name,
        pro_pack_question_file="questionnaire.json",
        pro_pack_scoring_file="scoring.algo",
        path="/EN/",
        bucket=s3_bucket,
        s3_resource=s3_resource
    '''
    questionnaire_key=pro_pack_name + path + pro_pack_question_file
    questionnaire_file=s3_resource.Object(bucket_name=bucket, key=questionnaire_key)
    questionnaire_contents = questionnaire_file.get()['Body'].read()
    return json.loads(questionnaire_contents)


def read_questionnaire_from_file(path:str,filename:str):
    """
    Handle local file system read of file of questionnaire

    Parameters
    ----------
    path : str
        Path to read from
    
    filename : str
        Filename for the questionnaire

    Returns
    -------
    json
        Question payload
    """
    try:
        f = open(path+filename,"r")
        questionnaire = json.load(f)
        f.close()
    except Exception as e:
        raise Exception(f"File not found: {e}")
    
    return questionnaire

def read_scoring_from_file(path:str,filename:str):
    """
    Handle local file system read of file of scoring

    Parameters
    ----------
    path : str
        Path to read from
    
    filename : str
        Filename for the scoring

    Returns
    -------
    json
        Scoring payload
    """
    config = configparser.ConfigParser()
    
    try:
        config.read(path+filename)
    except Exception as e:
        raise Exception(f"File not found: {e}")

    try:
        sanitized_formula_set = []

        for section in config.sections():
            sanitized = ScoringSafety(config[section]["formula"])
            sanitized_formula = { "link_id": section, "formula": sanitized.formula }
            sanitized_formula_set.append(sanitized_formula)

        return sanitized_formula_set
    except Exception as e:
        raise( e )