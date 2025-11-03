from sqlalchemy import func
from sqlmodel import SQLModel,Field,Relationship
from typing import Optional,List
from datetime import datetime
from models.contact_table import contact_tbl

class car_tbl(SQLModel,table=True):
    cell:str=Field(primary_key=True,default=None,foreign_key="contact_tbl.cell")
    make:str=Field(default=None,nullable=False)
    model:str=Field(default=None,nullable=False)
    year:str=Field(default=None,nullable=False)
    contact:Optional[contact_tbl]=Relationship(back_populates="car_tbl")