import json
import boto3
import os
from json_encoder.json_encoder import JSONEncoder
import datetime
from dateutil.relativedelta import relativedelta

client = boto3.resource("dynamodb", region_name=os.environ.get("AWS_REGION"))

user_table = client.Table(os.environ.get("TABLE_USER"))
survey_table = client.Table(os.environ.get("TABLE_SURVEY"))
reporting_table = client.Table(os.environ.get("TABLE_REPORTING"))
surgeon_table = client.Table(os.environ.get("TABLE_SURGEONS"))

CORS_HEADERS = {
    "Access-Control-Allow-Headers": "Content-Type",
    "Access-Control-Allow-Origin": os.environ["CORS_ALLOWED_ORIGIN"],
    "Access-Control-Allow-Methods": "OPTIONS,POST,GET",
}


def get_target(category):
    """
    Get target date for each survey

    Parameters
    ----------
    category : str
        The category header for the survey

    Returns
    -------
    arr:
       target
    """
    header_tags = [
        "Pre-Operation",
        "10 Day After Surgery",
        "1 Month After Surgery",
        "2 Month After Surgery",
        "3 Month After Surgery",
        "4 Month After Surgery",
        "5 Month After Surgery",
        "6 Month After Surgery",
        "7 Month After Surgery",
        "8 Month After Surgery",
        "9 Month After Surgery",
        "10 Month After Surgery",
        "11 Month After Surgery",
        "12 Month After Surgery",
    ]

    if category in header_tags:
        header_tag_index = header_tags.index(category)

        if header_tag_index == 0:
            return {"target": "Baseline", "value": -1}
        elif header_tag_index == 1:
            return {"target": "10 days", "value": 0}
        else:
            return {"target": f"{header_tag_index-1} mo", "value": header_tag_index - 1}

    return {"target": "NA", "value": 99}


def add_t_scores(surveys, sub):
    """
    Add t-scores to survey details of the user

    Parameters
    ----------
    sub : str
        The sub id of the user
    surveys : str
        The survey information of the user

    Returns
    -------
    arr:
       surveys
    """
    response = reporting_table.get_item(Key={"sub": sub}, ConsistentRead=True)
    for survey_type in response.get("Item", {}).get("surveys", []):
        for survey in surveys:
            if survey["pro_type"] == list(survey_type.keys())[0]:
                for survey_result in survey_type[survey["pro_type"]]:
                    completed_date = (
                        datetime.datetime.strptime(
                            survey["completed"]["date"], "%m/%d/%Y"
                        ).strftime("%m/%d/%Y")
                        if survey["completed"]["date"] != "NA"
                        else "NA"
                    )
                    if survey_result.get("completed_date") == completed_date:
                        survey["score"] = str(survey_result["score"])
    return surveys


def get_survey_data(sub: str, surveys: str, surgery_date: str):
    """
    Gets survey details of patients

    Parameters
    ----------
    sub : str
        The sub id of the user
    surveys : str
        The survey information of the user
    surgery_date : str
        The surgery date of the user

    Returns
    -------
    arr:
       survey_data
    """

    survey_data = []
    for i in surveys:
        target = get_target(i.get("category"))
        completed_date = (
            datetime.datetime.strptime(
                i.get("completed_date"), "%Y-%m-%dT%H:%M:%S"
            ).strftime("%m/%d/%Y")
            if i.get("completed_date")
            else "NA"
        )
        survey_data.append(
            {
                "target": target,
                # Value used for sorting
                "completed": {
                    "date": completed_date,
                    "value": completed_date if completed_date != "NA" else "12/12/9999",
                },
                "pro_type": i.get("name"),
                "score": "NA",
                "due": datetime.datetime.strptime(
                    i.get("due"), "%Y-%m-%dT%H:%M:%S"
                ).strftime("%m/%d/%Y"),
                "sid": i.get("sid") + i.get("due"),
                "propack": i.get("propack"),
            }
        )
    survey_data = add_t_scores(survey_data, sub)
    survey_data = sorted(survey_data, key=lambda x: datetime.datetime.strptime(x["due"], "%m/%d/%Y"))

    return survey_data


def get_patients(sub: str):
    """
    Gets name, email and phone for surgeons

    Parameters
    ----------
    sub : str
        The sub id of the user

    Returns
    -------
    arr:
       sub of all the patients
    """
    search_key = {"sub": sub}

    item = surgeon_table.get_item(Key=search_key, ConsistentRead=True).get("Item", {})

    return item.get("pts", [])


def handler(event, context):
    try:
        surgeon_sub = event["pathParameters"]["sub"]

        pts_sub = get_patients(surgeon_sub)

        combined_responses = []
        for sub in pts_sub:
            # Get patient's information and survey details
            patient = user_table.get_item(Key={"sub": sub}, ConsistentRead=True).get(
                "Item", {}
            )
            surveys = survey_table.get_item(Key={"sub": sub}, ConsistentRead=True).get(
                "Item", {}
            )

            all_surveys = []
            # Extract completed surveys
            for survey_group in surveys.get("completed_surveys", []):
                for category, surveys_list in survey_group.items():
                    for survey in surveys_list:
                        survey["category"] = category
                        all_surveys.append(survey)

            # Extract open surveys
            for survey_group in surveys.get("open_surveys", []):
                for category, surveys_list in survey_group.items():
                    for survey in surveys_list:
                        survey["category"] = category
                        all_surveys.append(survey)

            surgery_date = patient.get("profile", {}).get("surgery_date", "NA")
            survey_data = get_survey_data(sub, all_surveys, surgery_date)

            surgery_name = patient.get("profile", {}).get("surgery_name", "NA")

            response = {
                "sub": sub,
                "name": f"{patient['profile']['first_name']} {patient['profile']['last_name']}",
                "surgery_name": surgery_name,
                "surgery_date": (
                    datetime.datetime.strptime(
                        patient["profile"]["surgery_date"], "%Y-%m-%d"
                    ).strftime("%m/%d/%Y")
                    if patient.get("profile", {}).get("surgery_date", "NA") != "NA"
                    else "NA"
                ),
                "survey_data": survey_data,
            }

            combined_responses.append(response)

        return {
            "statusCode": 200,
            "headers": CORS_HEADERS,
            "body": json.dumps(combined_responses, cls=JSONEncoder),
        }
    except Exception as e:
        return {
            "statusCode": 500,
            "headers": CORS_HEADERS,
            "body": json.dumps({"msg": str(e)}),
        }
