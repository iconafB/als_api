from sqlmodel import SQLModel
from pydantic import BaseModel
class DedupesSchema(SQLModel):
    cell_numbers:str
    id_numbers:str
    campaign_name:str
    status:str


class DataInsertionSchema(BaseModel):
    data_extraction_time:str
    insertion_time:str
    number_of_leads:int
    Success:bool


class AddDedupeListResponse(BaseModel):
    status:bool
    file_name:str
    campaign_name:str
    key:str
    


