from sqlmodel import SQLModel,Field,Relationship
from models.information_table import info_tbl
from typing import Optional
class location_tbl(SQLModel,table=True):
    cell:str=Field(primary_key=True,default=None,foreign_key="info_tbl.cell")
    line_one:str=Field(default=None,nullable=False)
    line_two:str=Field(default=None,nullable=False)
    line_three:str=Field(default=None,nullable=False)
    line_four:str=Field(default=None,nullable=False)
    postal_code:str=Field(default=None,nullable=False)
    province:str=Field(default=None,nullable=False)
    surburb:str=Field(default=None,nullable=False)
    city:str=Field(default=None,nullable=False)
    info:Optional[info_tbl]=Relationship(back_populates="locations")