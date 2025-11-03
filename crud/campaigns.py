from fastapi import HTTPException,status
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from typing import List
from models.campaigns import campaign_tbl
from schemas.campaigns import CreateCampaign
from utils.logger import define_logger
#create campaign on the master db

campaigns_logger=define_logger("als campaign logs","logs/campaigns_route.log")

async def create_campaign(campaign:CreateCampaign,session:AsyncSession)->campaign_tbl:
    try:
        exists=await session.get(campaign_tbl,campaign.camp_code)
        if exists:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail=f"campaign:{campaign.camp_name} with campaign code:{campaign.camp_code} from this branch:{campaign.branch} already exists")
        db_campaign=campaign_tbl(**campaign.model_dump())
        session.add(db_campaign)
        await session.commit()
        await session.refresh(db_campaign)
        return db_campaign
    except Exception as e:
        await session.rollback()
        campaigns_logger.exception(f"internal server error occurred:{e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail=f"an internal server error occurred")

#update campaign name
async def update_campaign_name(campaign_old_name,campaign_new_name:str,session:AsyncSession)->campaign_tbl:
    exists_query=select(campaign_tbl).where(campaign_tbl.campaign_name==campaign_old_name)
    campaign=await session.exec(exists_query)
    result=campaign.first()
    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f"requested campaign:{campaign_old_name} does not exists")
    result.campaign_name=campaign_new_name
    try:
        session.add(result)
        await session.commit()
        await session.refresh(result)
        return result
    except Exception as e:
        await session.rollback()
        campaigns_logger.error(f"error occurred:{e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail=f"Internal server error occurred")

#get campaign by name
async def get_campaign_by_name(campaign_name:str,session:AsyncSession)->campaign_tbl:

    try:
        campaign_query=select(campaign_tbl).where(campaign_tbl.campaign_name==campaign_name)
        campaign=await session.exec(campaign_query)
        result=campaign.first()
        if not result:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f"Campaign:{campaign_name} does not exist")
        return result
    except Exception as e:
        campaigns_logger.exception(f"An exception occurred:{e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail=f"An internal server error occurred")

#get campaign by campaign code
async def get_campaign_by_code(camp_code:str,session:AsyncSession)->campaign_tbl:
    try:
        campaign_query=select(campaign_tbl).where(campaign_tbl.camp_code==camp_code)
        campaign=await session.exec(campaign_query)
        result=campaign.first()
        if not result:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f"Campaign with campaign code:{camp_code} does not exist")
        return result
    except Exception as e:
        campaigns_logger.exception(f"An internal server error occurred:{e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail=f"An internal server error occurred")
#get all active campaigns
async def get_all_campaigns_by_branch(branch:str,session:AsyncSession)->List[campaign_tbl]:

    campaigns=await session.exec(select(campaign_tbl).where(campaign_tbl.branch==branch))
    return campaigns


