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

CORS_HEADERS = {
    "Access-Control-Allow-Headers": "Content-Type",
    "Access-Control-Allow-Origin": os.environ["CORS_ALLOWED_ORIGIN"],
    "Access-Control-Allow-Methods": "OPTIONS,POST,GET",
}


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

    return add_t_scores(survey_data, sub)


def get_patient_details(pt_sex, pt_sub, pt_surgery_name):
    """
    Gets similar patients based on sex and age range

    Parameters
    ----------
    pt_sex : str
        The sex of the patient
    pt_sub : str
        The sub of the patient
    pt_surgery_name : str
        The surgery name the patient is going through

    Returns
    -------
    arr:
       List of similar patient's sub
    """
    users = user_table.scan().get(
        "Items", {}
    )  # Expensive operation, might need to change for prod

    similar_pts = []
    all_pts = []

    for user in users:
        if user.get("profile", {}).get("birth_sex"):
            sex = user["profile"]["birth_sex"]

            if (
                sex == pt_sex
                and pt_surgery_name == user["profile"].get("surgery_name")
                and user["sub"] != pt_sub
            ):
                similar_pts.append(user["sub"])

        if user.get("profile", {}).get("surgery_name") == pt_surgery_name:
            all_pts.append(
                {"sub": user["sub"], "surgery_name": user["profile"]["surgery_name"]}
            )

    return similar_pts, all_pts


def get_aggs_score(similar_pts, all_pts):
    """
    Gets average scores for each survey

    Parameters
    ----------
    similar_pts : arr
        The subs of similar patients
    pt_details : dict
        The surgery date for all users

    Returns
    -------
    arr:
       Aggs score for national average and similar patients
    """
    aggs_score = {"national_average": {}, "similar_patients": {}}

    # Calculate score aggs from each patient
    for pt in all_pts:
        patient_id = pt["sub"]

        item = reporting_table.get_item(Key={"sub": patient_id}).get("Item", {})
        if item:
            patient_surveys = (
                survey_table.get_item(Key={"sub": patient_id})
                .get("Item", {})
                .get("completed_surveys", [])
            )

            survey_headers = {}
            for i in patient_surveys:
                for header, completed_surveys in i.items():
                    for completed_survey in completed_surveys:
                        if completed_survey["name"] not in survey_headers:
                            survey_headers[completed_survey["name"]] = {}
                        survey_headers[completed_survey["name"]][
                            datetime.datetime.strptime(
                                completed_survey["due"], "%Y-%m-%dT%H:%M:%S"
                            ).strftime("%m/%d/%Y")
                        ] = get_target(header)

            for survey in item["surveys"]:
                for survey_name, survey_reports in survey.items():
                    for survey_report in survey_reports:
                        target = (
                            survey_headers.get(survey_name, {})
                            .get(survey_report["date"], {})
                            .get("target", "NA")
                        )
                        if target != "NA":
                            if survey_name not in aggs_score["national_average"]:
                                aggs_score["national_average"][survey_name] = {}

                            if (
                                target
                                not in aggs_score["national_average"][survey_name]
                            ):
                                aggs_score["national_average"][survey_name][target] = {
                                    "total_score": 0,
                                    "total_surveys": 0,
                                }

                            aggs_score["national_average"][survey_name][target][
                                "total_score"
                            ] += float(survey_report["score"])
                            aggs_score["national_average"][survey_name][target][
                                "total_surveys"
                            ] += 1

                            if patient_id in similar_pts:
                                if survey_name not in aggs_score["similar_patients"]:
                                    aggs_score["similar_patients"][survey_name] = {}

                                if (
                                    target
                                    not in aggs_score["similar_patients"][survey_name]
                                ):
                                    aggs_score["similar_patients"][survey_name][
                                        target
                                    ] = {
                                        "total_score": 0,
                                        "total_surveys": 0,
                                    }

                                aggs_score["similar_patients"][survey_name][target][
                                    "total_score"
                                ] += float(survey_report["score"])
                                aggs_score["similar_patients"][survey_name][target][
                                    "total_surveys"
                                ] += 1

    # Calculate averages
    for category, surveys in aggs_score.items():
        for survey_name, periods in surveys.items():
            for period, values in periods.items():
                total_score = values["total_score"]
                total_surveys = values["total_surveys"]
                average_score = total_score / total_surveys if total_surveys > 0 else 0
                periods[period] = average_score

    return aggs_score


def handler(event, context):
    try:
        sub = event["pathParameters"]["sub"]

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

        pt_compliance_rate = get_patient_statistics(
            surveys.get("completed_surveys", []),
            surveys.get("open_surveys", []),
        )

        surgery_name = patient.get("profile", {}).get("surgery_name", "NA")

        # Get aggs score for national average and similar patients
        similar_pts, all_pts = get_patient_details(
            patient.get("profile", {}).get("birth_sex", "NA"), sub, surgery_name
        )
        aggs_score = get_aggs_score(similar_pts, all_pts)

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
            "national_average_scores": aggs_score["national_average"],
            "similar_patients_scores": aggs_score["similar_patients"],
        }

        response["patient_compliance_rate"] = {
            "total_survey": 0,
            "completed_survey": 0,
            "overdue_survey": 0,
            "pending_survey": 0,
        }  # This is the overall compliance rate of all the patients

        response["patient_compliance_rate"]["total_survey"] += pt_compliance_rate[0]
        response["patient_compliance_rate"]["completed_survey"] += pt_compliance_rate[1]
        response["patient_compliance_rate"]["overdue_survey"] += pt_compliance_rate[2]
        response["patient_compliance_rate"]["pending_survey"] += pt_compliance_rate[3]

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
