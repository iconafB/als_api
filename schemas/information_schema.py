
from sqlmodel import SQLModel

class InformationCreate(SQLModel):
    cell_number:str
    id_number:str
    title:str
    fore_name:str
    last_name:str
    date_of_birth:str
    race:str
    gender:str
    status:str
    marital_status:str
    salary:float
    derived_income:float
    type_data:str
    extra_info:str

