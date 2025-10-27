from pydantic import BaseModel

class LeadsCount(BaseModel):
    message:str
    number:int
    status:bool

class SpecLevel(BaseModel):
    status:bool
    specLevel:int
    message:str
