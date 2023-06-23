# Windows Setup Details
0) Install tar
1) Install Node 18
2) Install aws cli
3) Install python 3.9.13
4) Make a new directory
5) Clone cloudpro-cdk repo
6) CD into directory
7) create a venv
```
python -m venv .venv
```
8) Activate virtual environment
```
source.bat
```
9)  Install requirements
```
pip install -r requirements.txt
```
10) Set access to your AWS Cloud Account
```
SET AWS_ACCESS_KEY_ID={your_access_key_id}
SET AWS_SECRET_ACCESS_KEY={your_secret_access_key}
SET AWS_SESSION_TOKEN={your_session_token}
```
11) Bootstrap CDK
```
cdk bootstrap --context layer_arn=DUMMY --context layer_boto_arn=DUMMY  --context XKEY=DUMMY --context debug_token=DUMMY
```
12) Build associated python layer deployables
```
build_layers.bat
```
13) [Skippable step]; originally, this project required an expiremental version of boto3 (v1.26.86) to support event bridge scheduling; however, at time of release, this was no longer required. This step initially required the manual creation of the boto3 package for layers.  The zip file would be required to be placed in ./cloudpro_cdk/custom_packages/layers/boto_1.26_86.zip.  Layers.py contains the now commented out code that referenced this file.
14) Update destroy.bat and deploy.bat values for XKEY and debug_token to an alphanumeric 20+ character secure string. XKEY in destroy must match XKEY in deploy; debug_token in destroy must match debug_token in deploy.
15) As an "initial staging", the lambda layers stack is required to be deployed.
```
deploy.bat cdk-layers-stack
```
16) Deploy the full stack
```
deploy.bat *
```
17) In AWS console, go to Amazon Simple Email Service (SES) and add the emails you which to utilize on the prototype to verified emails.
18) Confirm the verification email recieved
19) Zip up your pro packs of choice (alternatively you can zip the skeleton PROs on staged_propacks\cpro)
20) Create a raw/ folder and drop the zip files in here.  Upload to cdk-propack-stack-bucketpropack
21) Validate extraction; cdk-propack-stack-bucketpropack will now have a folder called propack
22) Validate database load; this may take a few minutes for the event to trigger.  Check cdk-dynamodb-stack-dynamoquestionnaire & cdk-dynamodb-stack-scoring
23) Sync your API key from API gateway to the cloudfront distribution pointing to your api gateway (*.execute-api.*) by editting the origin and then updating DUMMY on x-api-key to the appropriate value.  Save your changes.  For convenience, you can now update your deploy/destroy script with this value.
24) Your backend is deployed! Proceed to frontend deployment described in the appropriate branch (TLDR; update UI configs and perform s3deploy.bat cdk-userportal-stack-bucketuserportal)
25) Manually create two cognito users to represent Surgeon 1 & Surgeon 2.  Set email as verified and generate a password.
26) Add `custom:isEmployee` attribute to both users with a value of `1`
27) Add both to `surgeons` group
28) Update the sample JSON on hospitals & surgeon to reference the appropriate user sub id.
29) Create your entries in hospital and surgeon table
30) Force change your two surgeon passwords to a secure random string via aws cli:
```
aws cognito-idp admin-set-user-password \
  --user-pool-id <your-user-pool-id> \
  --username <username> \
  --password <password> \
  --permanent
```

# CloudPRO

"One click" deploy of CloudPRO.

-Bootstrap CDK
-Set console access for AWS
-Run build/deploy process

```
build_layers.bat
deploy cdk-layers-stack
deploy *
```

Please note, registration and login requires SES verified identities to be staged prior to testing as SES will be in Sandbox mode.  Go to SES-> Verified identities and add the email addresses you will be testing with prior to executing login.


-- Boto 1.6.86 zip file created manually. Required to support some of the event bridge scheduler items.
-- Be sure to check the API key on your cfront deployment (inserted DUMMY needs updated)

# Detailed Docs
Detailed docs are housed in a separate repo.


# Welcome to your CDK Python project!

Baseline was generated with CDK for Python.

The `cdk.json` file tells the CDK Toolkit how to execute your app.

This project is set up like a standard Python project.  The initialization
process also creates a virtualenv within this project, stored under the `.venv`
directory.  To create the virtualenv it assumes that there is a `python3`
(or `python` for Windows) executable in your path with access to the `venv`
package. If for any reason the automatic creation of the virtualenv fails,
you can create the virtualenv manually.

To manually create a virtualenv on MacOS and Linux:

```
$ python -m venv .venv
```

After the init process completes and the virtualenv is created, you can use the following
step to activate your virtualenv.

```
$ source .venv/bin/activate
```

If you are a Windows platform, you would activate the virtualenv like this:

```
% .venv\Scripts\activate.bat
```

Once the virtualenv is activated, you can install the required dependencies.

```
$ pip install -r requirements.txt
```

At this point you can now synthesize the CloudFormation template for this code.

```
$ cdk synth
```

To add additional dependencies, for example other CDK libraries, just add
them to your `setup.py` file and rerun the `pip install -r requirements.txt`
command.

## Useful commands

 * `cdk ls`          list all stacks in the app
 * `cdk synth`       emits the synthesized CloudFormation template
 * `cdk deploy`      deploy this stack to your default AWS account/region
 * `cdk diff`        compare deployed stack with current state
 * `cdk docs`        open CDK documentation

Enjoy!
