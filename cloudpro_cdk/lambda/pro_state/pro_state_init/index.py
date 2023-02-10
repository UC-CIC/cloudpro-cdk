import json
import boto3
import os
import hashlib

from datetime import datetime
from decimal import Decimal

from json_encoder.json_encoder import JSONEncoder

dynamodb = boto3.resource('dynamodb')
table_name_state=os.environ["TABLE_STATE"]
table_name_questionnaire=os.environ["TABLE_QUESTIONNAIRE"]


def read_questionnaire( pro_hash:str ):
    """
    Retrieve full payload for a specific questionnaire

    Parameters
    ----------
    pro_hash : str
        Unique ID of the questionnaire
    
    Returns
    -------
    json
        DynamoDB results
    """
    table = dynamodb.Table(table_name_questionnaire)

    search_key = {
        'pro_pack': pro_hash
    }
    

    return table.get_item(Key=search_key)

def init_state( state_payload:json ):
    """
    Store a new state payload

    Parameters
    ----------
    state_payload : json
        Payload representing a state

    Returns
    -------
    json
        DynamoDB results
    """
    table = dynamodb.Table(table_name_state)

    return table.put_item(Item=state_payload)

# extract all matching key values
def search_json(data,key):
    """
    Given a JSON payload, return a list of all values matching a specific key

    Parameters
    ----------
    data : json
        Json payload to search
    
    key : str
        Search value

    Returns
    -------
    list
        A list of link_id values
    """
    matches = []
    def search(data,key):
        if isinstance(data,dict):
            for k,v in data.items():
                if k== key:
                    matches.append(v)
                if isinstance(v,(dict,list)):
                        search(v,key)
        elif isinstance(data,list):
            for item in data:
                if isinstance(item,(dict,list)):
                    search(item,key)
        
    search(data,key)
    return matches


def handler(event,context):
    #################################################
    # FOR TESTING LAMBDA w/ MANUAL TRIGGER
    #################################################
    #'''
    detail_json = {
        "pro_hash": "2d7243474da051a4243697acdaba49dab0795f0ba7815caab4044e6740ac481a"
    }
    event = {
        'source': "custom.lambda.pro_state",
        'detail_type': "State Init",
        'detail': detail_json,
        'eventBusName':"cdk-ebus-cloudpro"
    }
    #'''
    state_hash="abc"
    #################################################
    
    try:
        pro_hash = event["detail"]["pro_hash"]
        result = read_questionnaire(pro_hash)
        if result['ResponseMetadata']['HTTPStatusCode'] != 200:
                raise Exception(f"DynamoDB issue")

        # build doubly linked list
        link_ids = search_json( result,"link_id" )

        # generate unique hash | probably expand out by user and some other fields down the road
        now = datetime.now()
        dt_string = now.strftime("%d%m%Y-%H:%M:%S")
        hash_builder= dt_string + pro_hash
        
        # UNCOMMENT for non testing.
        #state_hash=hashlib.sha256(hash_builder.encode('utf-8')).hexdigest()

        payload = {
            "state_hash": state_hash,
            "state_status": "open",
            "pro_pack": pro_hash,
            "states":{}
        }

        for idx, link_id in enumerate(link_ids):
            entry = {
                "entry_state": "init",
                "entry_response": None
            }
            prv=""
            nxt=""
            if idx == 0:
                prv=-1
                nxt=link_ids[idx+1]
            elif idx == len(link_ids)-1:
                prv=link_ids[idx-1]
                nxt=-1
            else:
                prv=link_ids[idx-1]
                nxt=link_ids[idx+1]

            entry["prev"]=prv
            entry["nxt"]=nxt              

            payload["states"][link_id]=entry

        result = init_state(payload)
        if result['ResponseMetadata']['HTTPStatusCode'] != 200:
                raise Exception(f"DynamoDB issue")

        return {
            "statusCode":200,
            "body": json.dumps({},cls=JSONEncoder)
        }
    except Exception as e:
        return {
            "statusCode":500,
            "body": json.dumps({"msg":str(e)})
        }


