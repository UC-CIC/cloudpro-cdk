import json
from typing import Any, Dict

from scoring_safety.scoring_safety import ScoringSafety
from json_encoder.json_encoder import JSONEncoder

def read_question( questionnaire:json, link_id:str ):
    """
    Read a specific question within a questionnaire

    Parameters
    ----------
    questionnaire : json
        Unique ID of the state to retrieve
    
    link_id : str
        Identifier of the question

    Returns
    -------
    json
        Question payload
    """
    questionnaire_payload = questionnaire["questionnaire"]
    for entry in questionnaire_payload:
        if entry["element"]=="question":
            if entry["data"]["link_id"] == link_id:
                return entry["data"]
        elif entry["element"]=="group":
            for question in entry["data"]["questions"]:
                if question["link_id"] == link_id:
                    return question               

    return {}

def read_formula( scoring:json, link_id:str ):
    """
    Read a specific formula algorithm for a specific link_id

    Parameters
    ----------
    scoring : json
        Payload to search for scoring algorithm
    
    link_id : str
        Identifier of the algorithm

    Returns
    -------
    json
        Formula payload
    """
    for formula in scoring:
        if formula["link_id"] == link_id:
            return formula               

    return {}

def evaluate_formula( field_values: Dict[Any, Any], formula:str ):
    # we've already sanitized the formula, but just to be super safe, we resanitize from DB grab
    sanitized_formula = ScoringSafety(formula)

    cpro_loader=field_values
    score = eval(sanitized_formula.formula)

    payload = {
        "result": score
    }

    return payload