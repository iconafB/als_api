from sqlmodel import Field,SQLModel,Relationship
from typing import Optional,List
from models.campaign_rule_table import campaign_rule_tbl
class RulesBase(SQLModel):
    rule_code:Optional[int]=Field(primary_key=True,default=None)
    typedata:str=Field(default="Status",max_length=50)
    birth_year_start:int=Field(...,ge=1900,le=2100)
    birth_year_end:int=Field(...,ge=1900,le=2100)
    min_salary:int=Field(default=None,nullable=True)
    last_used:int=Field(...,ge=0,default=29)
    record_limit:int=Field(...,ge=1,le=3000000)
    gender:Optional[str]=Field(default=None,nullable=True,max_length=10)

    @classmethod
    def validate(cls,values):
        if values.get("birth_year_start")>values.get("birth_year_end"):
            raise ValueError("birth_year_start must be <= birth_year_end")
        return values


class rules_tbl(RulesBase,table=True):
    __tablename__ = 'rules_tbl'
    rule_name: str = Field(max_length=25,min_length=25)
    rule_location:str=Field(nullable=True,default=None)
    campaign_rules:List[campaign_rule_tbl]=Relationship(back_populates="rules")
    
