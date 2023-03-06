import json
import boto3
from enum import Enum
import os
import hashlib

SURVEY_TABLE="cdk-dynamodb-stack-dynamosurveyCACB9890-U40FBT5EF39G"
SUB="85a163cc-3d8f-4918-b3e3-d296ed6710ae"
SURVEYS=["mobility","physical_function","upper_extrimity"]

s3_resource = boto3.resource('s3')
dynamodb = boto3.resource('dynamodb')

table_name=SURVEY_TABLE


#propack_hash=hashlib.sha256(propack_name.encode('utf-8')).hexdigest()

payload = {
    "sub":"85a163cc-3d8f-4918-b3e3-d296ed6710ae",
    "completed_surveys":[
        { "yyyyPre Operation": [
                {
                    "sid":hashlib.sha256( (SUB+SURVEYS[0]).encode('utf-8') ).hexdigest(),
                    "propack": hashlib.sha256( (SURVEYS[0]).encode('utf-8') ).hexdigest(),
                    "name": "Mobility",
                    "description": "Lorem MOBILITY ipsum  dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.",
                    "assigned":"2023-03-01",
                    "due":"2023-03-10",
                    "completed":False,
                    "missed":False
                },
                {
                    "sid":hashlib.sha256( (SUB+SURVEYS[1]).encode('utf-8') ).hexdigest(),
                    "propack": hashlib.sha256( (SURVEYS[1]).encode('utf-8') ).hexdigest(),
                    "name": "Physical Function",
                    "description": "Lorem PHYSICAL FUNCTION ipsum  dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.",
                    "assigned":"2023-03-01",
                    "due":"2023-03-10",
                    "completed":False,
                    "missed":False
                },
                {
                    "sid":hashlib.sha256( (SUB+SURVEYS[2]).encode('utf-8') ).hexdigest(),
                    "propack": hashlib.sha256( (SURVEYS[2]).encode('utf-8') ).hexdigest(),
                    "name": "Upper Extremity",
                    "description": "Lorem UPPER EXTREMITY ipsum  dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.",
                    "assigned":"2023-03-01",
                    "due":"2023-03-10",
                    "completed":False,
                    "missed":False
                }
            ] 
        },
                { "zzzzzzPre Operation": [
                {
                    "sid":hashlib.sha256( (SUB+SURVEYS[0]).encode('utf-8') ).hexdigest(),
                    "propack": hashlib.sha256( (SURVEYS[0]).encode('utf-8') ).hexdigest(),
                    "name": "Mobility",
                    "description": "Lorem MOBILITY ipsum  dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.",
                    "assigned":"2023-03-01",
                    "due":"2023-03-10",
                    "completed":False,
                    "missed":True
                },
                {
                    "sid":hashlib.sha256( (SUB+SURVEYS[1]).encode('utf-8') ).hexdigest(),
                    "propack": hashlib.sha256( (SURVEYS[1]).encode('utf-8') ).hexdigest(),
                    "name": "Physical Function",
                    "description": "Lorem PHYSICAL FUNCTION ipsum  dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.",
                    "assigned":"2023-03-01",
                    "due":"2023-03-10",
                    "completed":True,
                    "missed":False
                },
                {
                    "sid":hashlib.sha256( (SUB+SURVEYS[2]).encode('utf-8') ).hexdigest(),
                    "propack": hashlib.sha256( (SURVEYS[2]).encode('utf-8') ).hexdigest(),
                    "name": "Upper Extremity",
                    "description": "Lorem UPPER EXTREMITY ipsum  dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.",
                    "assigned":"2023-03-01",
                    "due":"2023-03-10",
                    "completed":False,
                    "missed":True
                }
            ] 
        }    
    ],
    "open_surveys":[
        { "Pre Operation": [
                {
                    "sid":hashlib.sha256( (SUB+SURVEYS[0]).encode('utf-8') ).hexdigest(),
                    "propack": hashlib.sha256( (SURVEYS[0]).encode('utf-8') ).hexdigest(),
                    "name": "Mobility",
                    "description": "Lorem MOBILITY ipsum  dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.",
                    "assigned":"2023-03-01",
                    "due":"2023-03-10",
                    "completed":True,
                    "missed":False
                },
                {
                    "sid":hashlib.sha256( (SUB+SURVEYS[1]).encode('utf-8') ).hexdigest(),
                    "propack": hashlib.sha256( (SURVEYS[1]).encode('utf-8') ).hexdigest(),
                    "name": "Physical Function",
                    "description": "Lorem PHYSICAL FUNCTION ipsum  dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.",
                    "assigned":"2023-03-01",
                    "due":"2023-03-10",
                    "completed":False,
                    "missed":False
                },
                {
                    "sid":hashlib.sha256( (SUB+SURVEYS[2]).encode('utf-8') ).hexdigest(),
                    "propack": hashlib.sha256( (SURVEYS[2]).encode('utf-8') ).hexdigest(),
                    "name": "Upper Extremity",
                    "description": "Lorem UPPER EXTREMITY ipsum  dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.",
                    "assigned":"2023-03-01",
                    "due":"2023-03-10",
                    "completed":False,
                    "missed":False
                }
            ] 
        },
                { "xxxPre Operation": [
                {
                    "sid":hashlib.sha256( (SUB+SURVEYS[0]).encode('utf-8') ).hexdigest(),
                    "propack": hashlib.sha256( (SURVEYS[0]).encode('utf-8') ).hexdigest(),
                    "name": "Mobility",
                    "description": "Lorem MOBILITY ipsum  dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.",
                    "assigned":"2023-03-01",
                    "due":"2023-03-10",
                    "completed":False,
                    "missed":False
                },
                {
                    "sid":hashlib.sha256( (SUB+SURVEYS[1]).encode('utf-8') ).hexdigest(),
                    "propack": hashlib.sha256( (SURVEYS[1]).encode('utf-8') ).hexdigest(),
                    "name": "Physical Function",
                    "description": "Lorem PHYSICAL FUNCTION ipsum  dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.",
                    "assigned":"2023-03-01",
                    "due":"2023-03-10",
                    "completed":False,
                    "missed":False
                },
                {
                    "sid":hashlib.sha256( (SUB+SURVEYS[2]).encode('utf-8') ).hexdigest(),
                    "propack": hashlib.sha256( (SURVEYS[2]).encode('utf-8') ).hexdigest(),
                    "name": "Upper Extremity",
                    "description": "Lorem UPPER EXTREMITY ipsum  dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.",
                    "assigned":"2023-03-01",
                    "due":"2023-03-10",
                    "completed":False,
                    "missed":False
                }
            ] 
        }
    ]
}


table = dynamodb.Table(table_name)

response = table.put_item(Item=payload)

print(response)