from sqlmodel import SQLModel,Field
from typing import Optional
from sqlalchemy.sql.sqltypes import TIMESTAMP
from sqlalchemy import func
from datetime import datetime,date

class users_table(SQLModel,table=True):
    id:Optional[int]=Field(default=None,primary_key=True)
    email:str=Field(default=None,nullable=False)
    password:str=Field(default=None,nullable=False,min_length=5)
    full_name:str=Field(default=None,index=True)
    created_at:Optional[datetime]=Field(sa_column_kwargs={"server_default":func.now()},nullable=False,default=None)
