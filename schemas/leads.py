from pydantic import BaseModel

class LeadsCount(BaseModel):
    message:str
    number:int