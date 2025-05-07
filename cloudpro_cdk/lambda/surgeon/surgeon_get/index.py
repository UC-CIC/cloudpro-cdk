import json
import boto3
import os
from json_encoder.json_encoder import JSONEncoder
import datetime

client = boto3.resource("dynamodb", region_name=os.environ.get("AWS_REGION"))

surgeon_table = client.Table(os.environ.get("TABLE_SURGEONS"))
user_table = client.Table(os.environ.get("TABLE_USER"))
survey_table = client.Table(os.environ.get("TABLE_SURVEY"))

CORS_HEADERS = {
    "Access-Control-Allow-Headers": "Content-Type",
    "Access-Control-Allow-Origin": os.environ["CORS_ALLOWED_ORIGIN"],
    "Access-Control-Allow-Methods": "OPTIONS,POST,GET",
}


def get_surgeon_details(sub: str):
    """
    Gets name, email and phone for surgeons

    Parameters
    ----------
    sub : str
        The sub id of the user

    Returns
    -------
    arr:
       [name, email, phone]
    """
    search_key = {"sub": sub}

    item = surgeon_table.get_item(Key=search_key, ConsistentRead=True).get("Item", {})

    return [item.get("name"), item.get("email"), item.get("phone"), item.get("pts")]


def get_patient_statistics(completed_survey_list: list, open_survey_list: list):
    """
    Gets name, email and phone for surgeons

    Parameters
    ----------
    completed_survey_list : arr
        The list of completed surveys by the patient
    open_survey_list : arr
        The list of open surveys by the patient

    Returns
    -------
    arr:
       [total_surveys, total_completed, total_overdue, total_pending]
    """
    total_surveys = 0
    total_completed = 0
    total_pending = 0
    total_overdue = 0

    for completed_surveys in completed_survey_list:
        for key in completed_surveys.keys():
            for survey in completed_surveys[key]:
                if survey.get("completed"):
                    total_completed += 1
                else:
                    try:
                        survey_due_date = datetime.datetime.strptime(
                            survey["due"], "%Y-%m-%dT%H:%M:%S"
                        ).date()
                    except:
                        survey_due_date = datetime.datetime.strptime(
                            survey["due"], "%Y-%m-%d"
                        ).date()
                    if datetime.datetime.today().date() > survey_due_date:
                        total_overdue += 1
                    else:
                        total_pending += 1

    for open_surveys in open_survey_list:
        for key in open_surveys.keys():
            for survey in open_surveys[key]:
                try:
                    survey_due_date = datetime.datetime.strptime(
                        survey["due"], "%Y-%m-%dT%H:%M:%S"
                    ).date()
                except:
                    survey_due_date = datetime.datetime.strptime(
                        survey["due"], "%Y-%m-%d"
                    ).date()
                if datetime.datetime.today().date() > survey_due_date:
                    total_overdue += 1
                else:
                    total_pending += 1

    total_surveys = total_completed + total_overdue + total_pending

    return total_surveys, total_completed, total_overdue, total_pending


def handler(event, context):
    try:
        sub = event["pathParameters"]["sub"]

        pts = []  # Contains information of patients
        surveys = {}  # Contains completed and assigned surveys for each patient
        response = {}  # This is response object to be returned
        response["patients"] = (
            []
        )  # This contains the information related to doctor's patients
        response["overall_patient_compliance_rate"] = {
            "total_survey": 0,
            "completed_survey": 0,
            "overdue_survey": 0,
            "pending_survey": 0,
        }  # This is the overall compliance rate of all the patients
        response["total_patients"] = 0  # This shows the total count for patients

        # Get surgeon details
        response["name"], response["email"], response["phone"], pts_sub = (
            get_surgeon_details(sub)
        )

        # Get patient's information and survey details
        for pt in pts_sub:
            user = user_table.get_item(Key={"sub": pt}, ConsistentRead=True).get(
                "Item", {}
            )
            if user:
                pts.append(
                    user_table.get_item(Key={"sub": pt}, ConsistentRead=True).get(
                        "Item", {}
                    )
                )
                surveys[pt] = survey_table.get_item(
                    Key={"sub": pt}, ConsistentRead=True
                ).get("Item", {})

        for pt in pts:
            pt_compliance_rate = get_patient_statistics(
                surveys[pt["sub"]].get("completed_surveys", []),
                surveys[pt["sub"]].get("open_surveys", []),
            )

            survey_completed_dates = []
            for entry in surveys[pt["sub"]].get("completed_surveys", []):
                for key in entry:
                    for item in entry[key]:
                        survey_completed_dates.append(
                            datetime.datetime.fromisoformat(
                                item.get("completed_date", "1111-11-11")
                            )
                        )

            max_survey_completed_date = (
                max(survey_completed_dates).strftime("%m/%d/%Y")
                if survey_completed_dates
                else "NA"
            )
            last_activity = (
                max_survey_completed_date
                if max_survey_completed_date != "11/11/1111"
                else "NA"
            )

            response["patients"].append(
                {
                    "sub": pt["sub"],
                    "name": f"{pt['profile']['first_name']} {pt['profile']['last_name']}",
                    "surgery_name": pt["profile"].get("surgery_name", "NA"),
                    "surgery_date": (
                        datetime.datetime.strptime(
                            pt["profile"]["surgery_date"], "%Y-%m-%d"
                        ).strftime("%m/%d/%Y")
                        if pt.get("profile", {}).get("surgery_date", "NA") != "NA"
                        else "NA"
                    ),
                    "last_activity": {
                        "date": last_activity,
                        "value": (
                            last_activity if last_activity != "NA" else "11/11/1111"
                        ),
                    },
                }
            )
            response["overall_patient_compliance_rate"][
                "total_survey"
            ] += pt_compliance_rate[0]
            response["overall_patient_compliance_rate"][
                "completed_survey"
            ] += pt_compliance_rate[1]
            response["overall_patient_compliance_rate"][
                "overdue_survey"
            ] += pt_compliance_rate[2]
            response["overall_patient_compliance_rate"][
                "pending_survey"
            ] += pt_compliance_rate[3]
            response["total_patients"] += 1

        return {
            "statusCode": 200,
            "headers": CORS_HEADERS,
            "body": json.dumps(response, cls=JSONEncoder),
        }
    except Exception as e:
        return {
            "statusCode": 500,
            "headers": CORS_HEADERS,
            "body": json.dumps({"msg": str(e)}),
        }
