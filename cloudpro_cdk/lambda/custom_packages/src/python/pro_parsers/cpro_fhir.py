import json


# note unit test with link id that contains a / as the starting char (assuming this will break)
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
    questionnaire_payload = questionnaire["item"]
    for entry in questionnaire_payload:
        if entry["linkId"] == link_id:
            return entry       

    return {}

def read_formula( scoring:json, link_id:str ):
    # fhir format scoring inline on questionnaire
    pass