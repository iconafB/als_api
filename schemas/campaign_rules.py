from pydantic import BaseModel,Field
from typing import Optional,List

class CreateCampaignRule(BaseModel):
    rule_name:str=Field(default=None,min_length=2,max_length=15)
    salary:Optional[int]=None
    gender:str
    birth_year_start:int
    birth_year_end:int
    limit:int
    typedata:str=Field(default="Status",min_length=1,max_length=20)
    last_used:int
    rule_location:str

class CreateCampaignRuleResponse(BaseModel):
    rule_code:int
    rule_name: str 
    typedata: str
    status:str
    age_lower_limit: int 
    age_upper_limit: int 
    minimum_salary: int
    last_used: int 
    number_of_records: int 
    gender: Optional[str] 
    is_dedupe:Optional[bool]=None
    is_ping_status_null:Optional[bool]=None
    model_config={
        "from_attributes":True
    }

class PaginatedCampaignRules(BaseModel):
    total:int
    page:int
    page_size:int
    rules:List[CreateCampaignRuleResponse]


class RuleCreate(BaseModel):
    rule_name: str 
    typedata: str
    status:str
    age_lower_limit: int 
    age_upper_limit: int 
    minimum_salary: int
    last_used: int 
    number_of_records: int 
    gender: Optional[str] 
    is_dedupe:Optional[bool]=None
    is_ping_status_null:Optional[bool]=None

    model_config={
        "from_attributes":True
    }


    # @classmethod
    # def validate(cls, values):
    #     return RulesBase.validate(values)

class RuleSQLColumn(BaseModel):
    salary:Optional[int]=None
    last_used:Optional[int]=None
    start_year:Optional[int]=None
    end_year:Optional[int]=None
    limit:Optional[int]=None

class AssignCampaignRuleToCampaign(BaseModel):
    rule_code:int
    camp_code:str


class AssignCampaignRuleResponse(BaseModel):
    message:str
    Success:bool

class ChangeCampaignResponse(BaseModel):
    rule_code:int
    rule_name:str
    rule_sql:RuleSQLColumn


class CreateDedupeCampaignRule(BaseModel):
    rule_name:str
    salary:int
    derived_income:int
    gender:str
    limit:int
    is_deduped:bool=Field(default=True)

class CampaignSpecResponse(BaseModel):
    Success:bool
    Number_Of_Leads:int

class ChangeCampaignRuleResponse(BaseModel):
    Success:bool
    Message:str



