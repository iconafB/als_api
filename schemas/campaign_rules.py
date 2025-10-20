from pydantic import BaseModel,Field
from typing import Optional

class CreateCampaignRule(BaseModel):
    campaign_code:str=Field(default=None,min_length=2,max_length=15)
    minimum_salary:Optional[int]=None
    start_year:int
    end_year:int
    limit:int
    typedata:str=Field(default="Status",min_length=1,max_length=20)
    last_used:int
    rule_location:str

class RuleSQLColumn(BaseModel):
    salary:Optional[int]=None
    last_used:Optional[int]=None
    start_year:Optional[int]=None
    end_year:Optional[int]=None
    limit:Optional[int]=None


class ChangeCampaignResponse(BaseModel):
    rule_code:int
    rule_name:str
    rule_sql:RuleSQLColumn


