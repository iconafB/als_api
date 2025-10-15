from sqlmodel import SQLModel,Field,Column
from typing import Optional,Dict,Any
from sqlalchemy import func
from sqlalchemy.types import JSON
from datetime import datetime


class campaign_tbl(SQLModel,table=True):
    id:Optional[int]=Field(nullable=False,default=None,primary_key=True)
    #index on the campaign branch
    branch:str=Field(default=None,nullable=False,index=True)
    camp_code:str=Field(default=None,nullable=False)
    campaign_name:str=Field(default=None,nullable=False)
    created_at:Optional[datetime]=Field(sa_column_kwargs={"server_default":func.now()},nullable=False,default=None)
    
#leads that have been deduped under a specific campaign
#added a code field on campaign_dedupe table
class Campaign_Dedupes(SQLModel,table=True):
    id:Optional[int]=Field(nullable=False,default=None,primary_key=True)
    cell_number:str=Field(default=None,nullable=False)
    id_number:str=Field(default=None,nullable=False)
    campaign_name:str=Field(default=None,nullable=False)
    status:str=Field(default=None,nullable=False)
    code:str=Field(default=None,nullable=False)
    created_at:Optional[datetime]=Field(sa_column_kwargs={"server_default":func.now()},nullable=False,default=None)

#store the tokens on the dotenv file
# add a column on campaigns table to specify whether the campaign is a dedupe campaign or not

class Rule(SQLModel):
    minimum_salary:int=Field(nullable=True,default=None)
    maximum_salary:int=Field(nullable=True,default=None)
    derived_income:int=Field(nullable=True,default=None)
    created_at:str=Field(sa_column_kwargs={"server_default":func.now()},nullable=False,default=None)
    gender:str=Field(nullable=True,default=None)
    limit:int=Field(nullable=True,default=None)



class Deduped_Campaigns(SQLModel,table=True):

    id:Optional[int]=Field(primary_key=True,nullable=False,default=None)
    branch:str=Field(nullable=False,default=None)
    camp_name:str=Field(nullable=False,default=None)
    camp_code:str=Field(nullable=False,default=None)
    camp_rule:Rule=Field(default_factory=Rule,sa_column=Column(JSON))
    created_at:Optional[datetime]=Field(sa_column_kwargs={"server_default":func.now()},nullable=False,default=None)


