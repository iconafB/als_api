from pydantic import BaseModel
from typing import Optional

class CreateDedupeCampaign(BaseModel):
    branch:str
    campaign_name:str
    campaign_code:str
    maximum_salary:Optional[int]=None
    minimum_salary:Optional[int]=None
    derived_income:Optional[int]=None
    gender:Optional[str]=None
    limit:Optional[int]=None

class SubmitDedupeReturnSchema(BaseModel):
    campaign_name:str
    campaign_code:str
    code:str
