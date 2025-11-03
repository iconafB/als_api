from sqlmodel import SQLModel,Field,Column
from typing import Optional,Dict,Any
from sqlalchemy import func
from datetime import datetime

class campaign_tbl(SQLModel,table=True):
    #index on the campaign branch
    camp_code:str=Field(default=None,primary_key=True,nullable=False)
    branch:str=Field(default=None,nullable=False,index=True)
    campaign_name:str=Field(default=None,nullable=False)

#leads that have been deduped under a specific campaign
#added a code field on campaign_dedupe table


#store the tokens on the dotenv file
# add a column on campaigns table to specify whether the campaign is a dedupe campaign or not


class Deduped_Campaigns(SQLModel,table=True):
    id:Optional[int]=Field(primary_key=True,nullable=False,default=None)
    branch:str=Field(nullable=False,default=None)
    camp_name:str=Field(nullable=False,default=None,index=True)
    camp_code:str=Field(nullable=False,default=None)
    #camp_rule:Rule=Field(default_factory=Rule,sa_column=Column(JSON))
    created_at:Optional[datetime]=Field(sa_column_kwargs={"server_default":func.now()},nullable=False,default=None)




class dedupe_campaigns_tbl(SQLModel,table=True):
    camp_id:Optional[int]=Field(primary_key=True,nullable=False,default=None)
    branch:str=Field(nullable=False,default=None)
    campaign_name:str=Field(nullable=False,default=None,index=True)
    camp_code:str=Field(nullable=False,default=None,index=True)
    is_active:str=Field(nullable=False,default=True)
    is_deduped:bool=Field(nullable=True,default=None)


class manual_dedupe_keys(SQLModel,table=True):
    id:Optional[int]=Field(primary_key=True,nullable=False,default=None)
    camp_code:str=Field(nullable=False,default=None)
    key_name:str=Field(nullable=False,default=None,index=True)
    created_at:Optional[datetime]=Field(sa_column_kwargs={"server_default":func.now()},nullable=False,default=None)

