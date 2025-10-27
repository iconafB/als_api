from pydantic import BaseModel
from typing import Optional

class InsertStatusDataResponse(BaseModel):
    number_of_leads:int
    status:bool
    time_taken:int
    information_table:str
    contact_table:str
    location_table:str
    car_table:str
    finance_table:str

class InsertEnrichedDataResponse(BaseModel):
    number_of_leads:int
    status:bool
    data_insertion_time:int
    data_extraction_time:int
    information_table:str
    contact_table:str
    location_table:str
    car_table:str
    finance_table:str
