from sqlmodel import Field,SQLModel,Relationship,Column,JSON
from typing import Optional,List,TYPE_CHECKING


if TYPE_CHECKING:
    from models.campaign_rules_table import campaign_rule_tbl
    from models.lead_history_table import lead_history_tbl

class RulesBase(SQLModel):
    rule_code:Optional[int]=Field(primary_key=True,default=None)
    typedata:str=Field(default="Status",max_length=50)
    birth_year_start:int=Field(nullable=False)
    birth_year_end:int=Field(nullable=False)
    min_salary:int=Field(nullable=True)
    last_used:int=Field(nullable=False,default=29)
    record_limit:int=Field(nullable=False)
    gender:Optional[str]=Field(default=None,nullable=True,max_length=10)
    

    @classmethod
    def validate(cls,values):
        if values.get("birth_year_start")>values.get("birth_year_end"):
            raise ValueError("birth_year_start must be <= birth_year_end")
        return values


class rules_tbl(SQLModel,table=True):
    rule_code:Optional[int]=Field(primary_key=True)
    rule_name:str=Field(nullable=False)
    status:str=Field(default=None,nullable=False)
    typedata:str=Field(nullable=False,default=None)
    age_lower_limit:int=Field(nullable=False)
    age_upper_limit:int=Field(nullable=False)
    minimum_salary:int=Field(default=None,nullable=True)
    last_used:int=Field(nullable=False)
    number_of_records:int=Field(nullable=False)
    gender:Optional[str]=Field(default=None,nullable=True)
    #rule_location:str=Field(nullable=True,default=None)
    is_dedupe:bool=Field(nullable=False,default=False)
    is_active:bool=Field(nullable=False,default=False)
    is_ping_status_null:bool=Field(nullable=False,default=False)
    #campaign_rules:List["campaign_rule_tbl"]=Relationship(back_populates="rules")
    #lead_histories:List["lead_history_tbl"]=Relationship(back_populates="rules")


class RulesTable(SQLModel,table=True):
    id:Optional[int]=Field(default=None,primary_key=True)
    name:str
    status:str
    rule_json:dict=Field(sa_column=Column(JSON))



