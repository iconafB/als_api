from typing import Optional,Dict,Any
from pydantic import BaseModel,ValidationError
from schemas.rules_schema import GetCampaignRuleResponse,BetweenOperator

def extract_numeric_rule(data:Dict[str,Any],file_name:str)->Optional[Dict]:

    field_data=data.get(file_name)

    if not field_data:
        return None
    
    operator=field_data.get("operator")

    if operator=="between":
        return {
            "operator":"between",
            "lower":field_data["lower"],
            "upper":field_data["upper"]
        }
    
    else:
        return {
            "operator":operator,
            "value":field_data.get("value")
        }

 
def transform_rule_json(db_rule)->GetCampaignRuleResponse:

    data=db_rule.rule_json #Assume that rule_json is a dict

    return GetCampaignRuleResponse(
        rule_code=db_rule.rule_code,
        rule_name=db_rule.rule_name,
        salary=extract_numeric_rule(data, "salary"),
        age=extract_numeric_rule(data, "age"),
        derived_income=extract_numeric_rule(data, "derived_income"),  # optional
        gender=data.get("gender", {}).get("value") if data.get("gender") else None,
        typedata=data.get("typedata", {}).get("value") if data.get("typedata") else None,
        is_active=db_rule.is_active,
        last_used=data.get("last_used", {}).get("value") if data.get("last_used") else None,
        records_loaded=data.get("number_of_records", {}).get("value") if data.get("number_of_records") else None,
        )
