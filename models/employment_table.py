from sqlmodel import SQLModel,Field,Relationship
from typing import Optional,TYPE_CHECKING
from models.information_table import info_tbl

if TYPE_CHECKING:
    from models.information_table import info_tbl
class employment_tbl(SQLModel,table=True):
    cell:Optional[str]=Field(primary_key=True,foreign_key="info_tbl.cell")
    job:Optional[str]=None
    occupation:Optional[str]=None
    campany:Optional[str]=None
    #info_tbl:Optional["info_tbl"]=Relationship(back_populates="employment_tbl")