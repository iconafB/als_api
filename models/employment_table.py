from sqlmodel import SQLModel,Field,Relationship
from typing import Optional
from models.information_table import info_tbl

class employment_tbl(SQLModel,table=True):
    cell:Optional[str]=Field(primary_key=True,default=None,nullable=False)
    job:str=Field(nullable=False,default=None)
    occupation:str=Field(default=None,nullable=False)
    campany:str=Field(default=None,nullable=False)
    info_tbl:Optional["info_tbl"]=Relationship(back_populates="employments")