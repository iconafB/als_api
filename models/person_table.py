from sqlmodel import SQLModel,Field
from typing import Optional
from datetime import date,datetime
from sqlalchemy import Column,DateTime,text
class Person(SQLModel,table=True):
    id:Optional[int]=Field(default=None,primary_key=True)
    name:str
    id_number:str
    gender:str
    salary:float
    typedata:str
    is_active:bool
    derived_income:float
    last_used:Optional[datetime]=Field(sa_column=Column(DateTime(timezone=True),nullable=False,server_default=text("CURRENT_TIMESTAMP")))