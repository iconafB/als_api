from sqlmodel import SQLModel,Field
from typing import Optional
from sqlalchemy import func
from datetime import datetime

class Campaigns(SQLModel,table=True):
    id:Optional[int]=Field(nullable=False,default=None,primary_key=True)
    #index on the campaign branch
    branch:str=Field(default=None,nullable=False,index=True)
    camp_code:str=Field(default=None,nullable=False)
    campaign_name:str=Field(default=None,nullable=False)
    created_at:Optional[datetime]=Field(sa_column_kwargs={"server_default":func.now()},nullable=False,default=None)
    
#leads that have been deduped under a specific campaign
class Campaign_Dedupes(SQLModel,table=True):
    id:Optional[int]=Field(nullable=False,default=None,primary_key=True)
    lead_pk:str=Field(default=None,nullable=False)
    cell_number:str=Field(default=None,nullable=False)
    id_number:str=Field(default=None,nullable=False)
    campaign_name:str=Field(default=None,nullable=False)
    status:str=Field(default=None,nullable=False)
    created_at:Optional[datetime]=Field(sa_column_kwargs={"server_default":func.now()},nullable=False,default=None)

#store the tokens on the dotenv file
# add a column on campaigns table to specify whether the campaign is a dedupe campaign or not


class Deduped_Campaigns(SQLModel,table=True):
    id:Optional[int]=Field(primary_key=True,nullable=False,default=None)
    campaign:str=Field(nullable=False,default=None)
    camp_code:str=Field(nullable=False,default=None)
    rule_code:str=Field(nullable=False,default=None)
    created_at:Optional[datetime]=Field(sa_column_kwargs={"server_default":func.now()},nullable=False,default=None)
