from sqlmodel import SQLModel,Field
from pydantic import BaseModel
from datetime import date

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
    camp_code:str

class CampaignSpec(SQLModel):
    id_number:str
    fore_name:str
    last_name:str
    cell_number:str

class LoadCampaignSchemas(BaseModel):
    branch:str
    min_salary:int
    max_salary:int
    min_dob_year:str
    max_dob_year:str
    min_age:int
    max_age:int
    days_last_used:int
    limit:int


class LoadCampaignResponse(BaseModel):
    campaign_code:str
    branch:str
    list_name:str
    audit_id:str
    records_processed:int
    dma_status_code:int
    load_dmasa_status:str
    number_of_leads_submitted:int


