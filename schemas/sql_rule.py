from sqlmodel import SQLModel
from pydantic import BaseModel
from typing import Optional

class Sql_Rules(BaseModel):
    min_salary:int
    max_salary:int
    min_age:int
    max_age:int
    rule_code:str
    camp_code:str
    cellphone_number_checked:bool
    id_number_checked:bool
    gender:str
    city:str
    province:str
    is_active:bool

class SQL_Rule_Response(Sql_Rules):
    id:int

class Change_Active_Rule(BaseModel):
    min_salary:Optional[int]=None
    max_salary:Optional[int]=None
    max_age:Optional[int]=None
    min_age:Optional[int]=None
    cell_number_checked:Optional[str]=None
    id_number_checked:Optional[str]=None
    rule_code:str
    gender:Optional[str]=None
    city:Optional[str]=None
    province:Optional[str]=None

