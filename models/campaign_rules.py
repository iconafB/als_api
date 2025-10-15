from sqlmodel import SQLModel,Field,or_,and_,cast
from typing import Optional,Dict,Any
from datetime import datetime
from sqlalchemy import func

#assign a sql rule to a campaign

class campaign_rules(SQLModel,table=True):
    id:Optional[int]=Field(primary_key=True,default=None)
    rule_code:str=Field(nullable=False,default=None)
    camp_code:str=Field(nullable=False,default=None)
    min_salary:int=Field(nullable=False,default=None)
    max_salary:int=Field(nullable=False,default=None)
    min_age:int=Field(nullable=False,default=None)
    max_age:int=Field(nullable=False,default=None)
    cell_number_checked:bool=Field(default=True,nullable=True)
    id_number_checked:bool=Field(default=True,nullable=True)
    gender:str=Field(nullable=False,default=None)
    city:str=Field(nullable=False,default=None)
    province:str=Field(nullable=False,default=None)
    is_active:bool=Field(nullable=False,default=True)
    created_at:Optional[datetime]=Field(sa_column_kwargs={"server_default":func.now()},nullable=False,default=None)


class campaign_rules(SQLModel,table=True):
    
    rule_code:Optional[int]=Field(primary_key=True,default=None)
    rule_name:str=Field(nullable=False,default=None)
    rule_values:Dict[str,Any]=Field(nullable=True,default=None)
    created_at:Optional[datetime]=Field(sa_column_kwargs={"server_default":func.now()},nullable=False,default=None)


