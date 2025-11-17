from sqlalchemy import func
from sqlmodel import SQLModel,Field,Relationship
from typing import Optional,List,TYPE_CHECKING
from datetime import datetime


if TYPE_CHECKING:
    from models.information_table import info_tbl
class car_tbl(SQLModel,table=True):
    cell:str=Field(primary_key=True,foreign_key="info_tbl.cell")
    make:Optional[str]=None
    model:Optional[str]=None
    year:Optional[str]=None
    #info_tbl:Optional["info_tbl"]=Relationship(back_populates="car_tbl")