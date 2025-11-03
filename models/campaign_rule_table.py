from sqlalchemy import func
from sqlmodel import SQLModel,Field,Relationship
from typing import Optional,List
from datetime import datetime
from models.rules_table import rules_tbl
from models.campaigns_table import campaign_tbl

class campaign_rule_tbl(SQLModel,table=True):
    cr_code:Optional[int]=Field(primary_key=True,nullable=False,default=None)
    camp_code:str=Field(nullable=False,default=None)
    rule_code:str=Field(default=None,foreign_key="rule_tbl.rule_code")
    date_rule_created:Optional[datetime]=Field(sa_column_kwargs={"server_default":func.now()},nullable=False,default=None)
    is_active:bool=Field(nullable=False,default=None)
    rule:Optional["rules_tbl"]=Relationship(back_populates="campaign rules")
    campaign:Optional["campaign_tbl"]=Relationship(back_populates="campaign rules")

    