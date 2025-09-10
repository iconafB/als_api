from pydantic import BaseModel

class Create_Token(BaseModel):
    branch:str
    token:str
    is_active:bool

class Return_Token(Create_Token):
    id:int
    created_at:str
