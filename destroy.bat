@ECHO OFF

ECHO ~~Start Processing~~

for /f "delims=" %%i in ('python layers_get_latest.py layer_cloudpro_lib') do set layer_arn=%%i
REM for /f "delims=" %%i in ('python layers_get_latest.py layer_boto_lib') do set layer_boto_arn=%%i

REM cdk destroy %1 --context layer_arn=%layer_arn% --context layer_boto_arn=%layer_boto_arn% --context XKEY=DUMMY --context debug_token=DummyDebug5568dd5ea5fb41d082ff154b4b8336338b47460173358288f57a6cdd2230dccc

echo %*
cdk destroy %* --context layer_arn=%layer_arn%  --context XKEY=DUMMY --context debug_token=DummyDebug5568dd5ea5fb41d082ff154b4b8336338b47460173358288f57a6cdd2230dccc


ECHO ~~End Processing~~