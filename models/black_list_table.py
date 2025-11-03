from sqlalchemy import func
from sqlmodel import SQLModel,Field,Relationship
from typing import Optional,List
from datetime import datetime
from models.contact_table import contact_tbl

class blacklist_tbl(SQLModel,table=True):
    cell:str=Field(primary_key=True,default=None)
    dmasa_status:bool=Field(nullable=False,default=None)
    dnc_status:bool=Field(nullable=False,default=None)
    dma_date:Optional[datetime.date]=Field(nullable=False,sa_column_kwargs={"server_default":"NOW()"})
    contact:Optional[contact_tbl]=Relationship(back_populates="blacklist")