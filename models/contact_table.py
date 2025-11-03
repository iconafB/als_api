from sqlalchemy import func
from sqlmodel import SQLModel,Field,Relationship
from typing import Optional,List
from datetime import datetime
from models.information_table import info_tbl
from models.finance_table import finance_tbl
from models.car_table import car_tbl
from models.black_list_table import blacklist_tbl
from models.lead_history_table import lead_history_tbl
from als_backend_api.models.ping_table import ping_tbl

class contact_tbl(SQLModel,table=True):
    cell:Optional[str]=Field(primary_key=True,nullable=False,default=None)
    home_number:Optional[str]=None
    work_number:Optional[str]=None
    mobile_number_one:Optional[str]=None
    mobile_number_two:Optional[str]=None
    mobile_number_three:Optional[str]=None
    mobile_number_four:Optional[str]=None
    mobile_number_five:Optional[str]=None
    email:Optional[str]=None
    #information table
    info_tbl:Optional["info_tbl"]=Relationship(back_populates="contact_tbl")
    finance_tbl:List["finance_tbl"]=Relationship(back_populates="contact_tbl")
    cars_tbl:List["car_tbl"]=Relationship(back_populates="contact_tbl")
    blacklist_tbl:Optional["blacklist_tbl"]=Relationship(back_populates="contact_tbl")
    lead_history_tbl:List["lead_history_tbl"]=Relationship(back_populates="contact_tbl")
    pings:List["ping_tbl"]=Relationship(back_populates="contact_tbl")
    


