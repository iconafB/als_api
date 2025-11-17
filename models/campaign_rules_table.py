import sqlalchemy as sa
from sqlalchemy import func
from sqlmodel import SQLModel,Field,Relationship
from typing import Optional,List,TYPE_CHECKING
from datetime import datetime



if TYPE_CHECKING:
    from models.rules_table import rules_tbl
    from models.campaigns_table import campaign_tbl

class campaign_rule_tbl(SQLModel,table=True):
    cr_code:Optional[int]=Field(primary_key=True,nullable=False,default=None)
    camp_code:str=Field(nullable=False,foreign_key="campaign_tbl.camp_code")
    rule_code:int=Field(nullable=False,foreign_key="rules_tbl.rule_code")
    date_rule_created:Optional[datetime]=Field(sa_column_kwargs={"server_default":func.now()},nullable=False)
    is_active:bool=Field(nullable=False)
    #rules_tbl:Optional["rules_tbl"]=Relationship(back_populates="campaign rules")
    #campaign:Optional["campaign_tbl"]=Relationship(back_populates="rules")

    