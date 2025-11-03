from sqlalchemy import func
from sqlmodel import SQLModel,Field,Relationship
from typing import Optional,List
from datetime import datetime
from models.contact_table import contact_tbl
from models.employment_table import employment_tbl
from models.location_table import location_tbl

class info_tbl(SQLModel,table=True):
    cell:Optional[str]=Field(primary_key=True,default=None,sa_column_kwargs={"comment":"PK"})
    id:str=Field(default=None,foreign_key="contact_tbl.cell")
    title:str|None=Field(nullable=False,default=None)
    fore_name:str|None=Field(nullable=False,default=None)
    last_name:str | None=Field(nullable=False,default=None)
    date_of_birth: str =Field(nullable=False,default=None)
    race:str | None=Field(nullable=False,default=None)
    gender:str | None=Field(nullable=False,default=None)
    marital_status:str | None=Field(nullable=False,default=None)
    salary:float=Field(nullable=False,default=None)
    status:str | None=Field(nullable=False,default=None)
    derived_income:float=Field(nullable=False,default=None)
    type_data:str | None=Field(nullable=False,default=None)
    last_used:Optional[datetime]=Field(nullable=False,default=None)
    extra_info:str | None=Field(nullable=False,default=None)
    created_at:Optional[datetime]=Field(sa_column_kwargs={"server_default":func.now()},nullable=False,default=None)
    
    #relationships
    contact:Optional["contact_tbl"]=Relationship(back_populates="info_tbl")
    employements:List["employment_tbl"]=Relationship(back_populates="info_tbl")
    locations:List["location_tbl"]=Relationship(back_populates="info_tbl")
