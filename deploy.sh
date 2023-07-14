#!/bin/bash -f

echo ~~Start Processing~~

layer_arn="$(python3 layers_get_latest.py layer_cloudpro_lib)"
for var in "$@"
do
    cdk deploy $var --context layer_arn=$layer_arn --context XKEY=DUMMY --context debug_token=DummyDebug5568dd5ea5fb41d082ff154b4b8336338b47460173358288f57a6cdd2230dccc
done