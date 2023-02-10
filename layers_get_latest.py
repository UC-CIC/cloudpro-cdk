import boto3
latest_version_arn=""
try:
    client=boto3.client("lambda")
    response = client.list_layer_versions(LayerName="layer_cloudpro_lib",MaxItems=1)
    latest_version_arn = response["LayerVersions"][0]["LayerVersionArn"]
    print(latest_version_arn)
except Exception as e:
    print("")