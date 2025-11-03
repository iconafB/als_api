from sqlmodel import SQLModel,Field,Relationship
from typing import Optional
from datetime import datetime
from models.contact_table import contact_tbl

class ping_tbl(SQLModel,table=True):
    cell:str=Field(primary_key=True,default=None)
    ping_status:str=Field(nullable=False,default=None)
    ping_duration:str=Field(nullable=False,default=None)
    date_pinged:Optional[datetime.date]=Field(sa_column_kwargs={"server_default":"NOW()"},nullable=False)
    contact:Optional[contact_tbl]=Relationship(back_populates="pings")


