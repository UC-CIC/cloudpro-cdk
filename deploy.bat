for /f "delims=" %%i in ('python layers_get_latest.py') do set layer_arn=%%i
cdk deploy %1 --context layer_arn=%layer_arn%