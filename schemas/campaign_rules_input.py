from sqlmodel import SQLModel,Field
from pydantic import BaseModel
from typing import Optional

class CampaignRuleInput(SQLModel):
    #non-json defined values
    rule_name:str
    #json data
    salary:int
    min_age:int
    max_age:int

class UpdateCampaignRulesResponse(BaseModel):
    message:str
    update_date:str
class FetchRuleResponse(BaseModel):
    message:str
    

