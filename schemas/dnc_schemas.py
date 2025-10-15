from pydantic import BaseModel

class DNCNumberResponse(BaseModel):
    status:bool
    message:str

