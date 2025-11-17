from sqlalchemy import func
from sqlmodel import SQLModel,Field,Relationship
from typing import Optional,List,TYPE_CHECKING
from datetime import date


if TYPE_CHECKING:
    from models.information_table import info_tbl

class blacklist_tbl(SQLModel,table=True):
    cell:str=Field(primary_key=True,foreign_key="info_tbl.cell")
    dmasa_status:Optional[bool]=None
    dnc_status:Optional[bool]=None
    dma_date:Optional[date]=None
    #info_tbl:Optional["info_tbl"]=Relationship(back_populates="blacklist")
