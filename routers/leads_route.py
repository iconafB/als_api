from fastapi import APIRouter,status,Query,HTTPException,Depends
from models.leads import information_table
from models.campaigns import Campaign_Dedupes
from database.database import get_session
from sqlalchemy import select
from schemas.leads import LeadsCount
from sqlmodel import Session
from utils.auth import get_current_user
from utils.logger import define_logger

leads_router=APIRouter(tags=["Leads Route"],prefix="/leads")

leads_logger=define_logger("als leads als","logs/leads_route.log")

@leads_router.get("/get-count",status_code=status.HTTP_200_OK,response_model=LeadsCount)
async def get_number_of_leads(campaign_name:str=Query(description="Please enter the campaign name"),status:str=Query(description="Enter the campaign status"),session:Session=Depends(get_session),user=Depends(get_current_user)):
    #build the EXISTS subquery
    exists_query=select(1).where(Campaign_Dedupes.cell_number==information_table.cell_number).exists()
    #construct the final query
    final_query=select(information_table.id_number,information_table.fore_name,information_table.last_name,information_table.cell_number).where(exists_query,Campaign_Dedupes.status==status,Campaign_Dedupes.campaign_name==campaign_name)
    
    results=session.exec(final_query).all()

    count=len(results)
    
    leads=LeadsCount(message="Leads Fetched Successfully",number=count)
    return leads

#check spec levels

@leads_router.get("/check-spec-levels")
async def check_spec_levels(rule_code:int):

    try:

        return True
    except Exception as e:

        return False