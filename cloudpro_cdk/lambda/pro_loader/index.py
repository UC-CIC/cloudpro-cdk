import json

def handler(event,context):
    # TODO implement
    print("<<< LOG ME >>>")
    return {
        'statusCode': 200,
        'body': json.dumps('Hello 2 from Lambda!')
    }