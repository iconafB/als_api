from pydantic import BaseModel
from typing import Optional

class PersonCreate(BaseModel):
    name:str
    id_number:str
    gender:str
    salary:float
    typedata:str
    is_active:bool
    derived_income:float


class PersonCreateResponse(BaseModel):
    id:int
    name:str
    id_number:str
    gender:str
    salary:float
    typedata:str
    is_active:bool
    derived_income:float