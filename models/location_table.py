from sqlmodel import SQLModel,Field,Relationship
from models.information_table import info_tbl
from typing import Optional
class location_tbl(SQLModel,table=True):
    cell:str=Field(primary_key=True,foreign_key="info_tbl.cell")
    line_one:Optional[str]=None
    line_two:Optional[str]=None
    line_three:Optional[str]=None
    line_four:Optional[str]=None
    postal_code:Optional[str]=None
    province:Optional[str]=None
    surburb:Optional[str]=None
    city:Optional[str]=None
    
    #info:Optional[info_tbl]=Relationship(back_populates="location_tbl")