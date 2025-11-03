from sqlmodel import Field,Relationship,SQLModel
from typing import Optional
from datetime import datetime
from models.contact_table import contact_tbl

class lead_history_tbl(SQLModel,table=True):
    lead_pk:Optional[int]=Field(primary_key=True,default=None,nullable=False)
    cell:str=Field(default=None,nullable=False,foreign_key="contact_tbl.cell")
    camp_code:Optional[str]=Field(default=None,nullable=False,foreign_key="campaign_tbl.camp_code")
    date_used:Optional[datetime.date]=Field(default=None,nullable=False)
    list_id:str=Field(default=None,nullable=False)
    list_name:str=Field(default=None,nullable=False)
    load_type:str=Field(default=None,nullable=False)
    rule_code:int=Field(default=None,nullable=False,foreign_key="rule_tbl.rule_code")
    contact:Optional[contact_tbl]=Relationship(back_populates="lead_history")