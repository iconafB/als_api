from sqlmodel import SQLModel

class DedupesSchema(SQLModel):
    cell_numbers:str
    id_numbers:str
    campaign_name:str
    status:str

