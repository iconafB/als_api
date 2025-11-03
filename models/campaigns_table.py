from sqlmodel import SQLModel,Field,Relationship
from typing import Optional,List
from sqlalchemy import func
from datetime import datetime
from models.campaign_rule_table import campaign_rule_tbl
from models.campaign_dedupe import campaign_dedupe

class campaign_tbl(SQLModel,table=True):
    camp_code:str=Field(default=None,primary_key=True,nullable=False)
    campaign_name:str=Field(default=None,nullable=False)
    branch:str=Field(default=None,nullable=False,index=True)
    is_deduped:Optional[bool]=Field(default=None,nullable=False)
    campaign_rules:List[campaign_rule_tbl]=Relationship(back_populates="campaign")
    campaign_dedupes:List["campaign_dedupe"]=Relationship(back_populates="campaign")


