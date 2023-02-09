from .scoring_safety import ScoringSafety
import hashlib
import json
import boto3


####
####  Currently supports just one formula -- as dev cycles happen extend out for support of
####  multiple custom formulas
####



def load( mode:str, pro_pack_format:str, pro_pack_name:str, path:str, pro_pack_question_file:str,pro_pack_scoring_file:str, bucket=None, boto_resource=None ):
    """
    Load a PRO Pack that is in FHIR format

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
        questionnaire_json=read_questionnaire_from_s3(path,pro_pack_question_file)
        pass
    
    scoring["pro_pack"] = pro_pack_hash
    scoring["pro_pack_format"] = pro_pack_format
    scoring["formula"] = formula

    questionnaire["pro_pack"] = pro_pack_hash
    questionnaire["pro_pack_format"] = pro_pack_format
    questionnaire["data"] = questionnaire_json

    payload = {
        "scoring": scoring,
        "questionnaire": questionnaire
    }

    return payload

def read_questionnaire_from_s3(path:str,filename:str):
    """
    Handle s3 read of file of questionnaire

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

def read_questionnaire_from_s3(path:str,bucket:str):
    pass

def read_scoring_from_file(path:str,filename:str):
    """
    Handle local file system read of file of scoring. We return null as we expect scoring to be inline to questionnaire

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
    try:
        f = open(path+filename,"r")
        formula = f.read()
        f.close()
    except Exception as e:
        raise Exception(f"File not found: {e}")

    # scoring is managed by fhir standard; any scoring file content ignored
    return ""