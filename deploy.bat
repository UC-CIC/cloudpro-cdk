for /f "delims=" %%i in ('python layers_get_latest.py layer_cloudpro_lib') do set layer_arn=%%i
for /f "delims=" %%i in ('python layers_get_latest.py layer_boto_lib') do set layer_boto_arn=%%i

cdk deploy %1 --context layer_arn=%layer_arn% --context layer_boto_arn=%layer_boto_arn%  --context XKEY=DUMMY --context debug_token=DummyDebug5568dd5ea5fb41d082ff154b4b8336338b47460173358288f57a6cdd2230dccc