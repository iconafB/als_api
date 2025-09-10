from sqlmodel import SQLModel,Field
from typing import Optional
from datetime import datetime

class pings_table(SQLModel,table=True):
    cell_number:str=Field(primary_key=True,default=None)
    ping_status:str=Field(nullable=False,default=None)
    ping_duration:str=Field(nullable=False,default=None)
    date_pinged:Optional[datetime]=Field(sa_column_kwargs={"server_default":"NOW()"},nullable=False)


class blackList_table(SQLModel,table=True):
    cell_number:str=Field(primary_key=True,default=None)
    dmasa_status:bool=Field(nullable=False,default=None)
    loaded_date:Optional[datetime]=Field(nullable=False,sa_column_kwargs={"server_default":"NOW()"})

