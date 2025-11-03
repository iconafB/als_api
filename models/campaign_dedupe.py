from sqlmodel import SQLModel,Field,Relationship
from typing import Optional
from models.campaigns_table import campaign_tbl

class campaign_dedupe(SQLModel,table=True):
    lead_pk:Optional[int]=Field(default=None,primary_key=True)
    cell:str=Field(default=None,foreign_key="contact_tbl.cell")
    id:str=Field(default=None,nullable=False)
    campaign_name:str=Field(default=None,nullable=False)
    status:str=Field(default=None,nullable=False)
    code:str=Field(default=None,nullable=False)
    campaign:Optional[campaign_tbl]=Relationship(back_populates="campaign_dedupes")