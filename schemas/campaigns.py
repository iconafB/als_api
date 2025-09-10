
from sqlmodel import SQLModel,Field
from pydantic import BaseModel

class CreateCampaign(SQLModel):
    branch:str=Field(min_length=1,max_length=50)
    camp_code:str=Field(min_length=1,max_length=100)
    campaign_name:str=Field(min_length=1,max_length=100)

class CreateCampaignResponse(SQLModel):
    id:int
    camp_code:str=Field(min_length=1,max_length=100)
    campaing_name:str=Field(min_length=1,max_length=100)
    branch:str=Field(min_length=1,max_length=50)


class CreateCampaignResponseMeassage(SQLModel):
    success:bool
    message:str

class LoadCampaign(BaseModel):
    branch:str
    campaign_name:str

class CampaignSpec(SQLModel):
    id_number:str
    fore_name:str
    last_name:str
    cell_number:str