from pydantic import BaseModel

class BlackListCreate(BaseModel):
    cell_number:str
    dma_status:bool

class BlackListed(BaseModel):
    is_black_listed:bool
    