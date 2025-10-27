from sqlmodel import SQLModel,Field,JSON,Column
from typing import Optional,Dict,Any
from datetime import datetime
from sqlalchemy import func

#assign a sql rule to a campaign


#final
class rules_tbl(SQLModel,table=True):
    rule_code:Optional[int]=Field(primary_key=True,default=None)
    rule_name:str=Field(nullable=False,default=None)
    #rule_sql:str=Field(nullable=True,default=None)
    rule_location:str=Field(nullable=True,default="")
    salary:int=Field(nullable=True,default=0)
    gender:str=Field(nullable=True,default="")
    birth_year_start:int=Field(nullable=True,default=2025)
    birth_year_end:int=Field(nullable=True,default=2025)
    last_used:int=Field(nullable=True,default=29)
    limit:int=Field(nullable=True,default=10000)
    #created_at:Optional[datetime]=Field(sa_column_kwargs={"server_default":func.now()},nullable=False)


class dedupe_campaign_rules_tbl(SQLModel,table=True):
    rule_code:Optional[int]=Field(primary_key=True,default=None)
    rule_name:str=Field(nullable=False,default=None)
    salary:int=Field(nullable=True,default=None)
    gender:str=Field(nullable=True,default=None)
    derived_income:int=Field(nullable=True,default=None)
    limit:int=Field(nullable=True,default=None)
