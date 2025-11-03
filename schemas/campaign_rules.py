from pydantic import BaseModel,Field
from typing import Optional
from sqlmodel import SQLModel
from models.campaign_rules import RulesBase

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


class RuleCreate(SQLModel):
    rule_name: str = Field(...,max_length=15,min_length=15)
    typedata: str = Field(default="Status", max_length=50)
    start_year: int = Field(..., ge=1900, le=2100)
    end_year: int = Field(..., ge=1900, le=2100)
    min_salary: Optional[float] = None
    days_inactive: int = Field(..., ge=0,default=29)
    record_limit: int = Field(..., ge=1, le=10000)
    gender: Optional[str] = Field(default=None)
    @classmethod
    def validate(cls, values):
        return RulesBase.validate(values)





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


class CreateDedupeCampaignRule(BaseModel):
    rule_name:str
    salary:int
    derived_income:int
    gender:str
    limit:int
    is_deduped:bool=Field(default=True)



