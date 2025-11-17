from fastapi import HTTPException,status,Depends
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from typing import List,Annotated
from models.campaigns_table import campaign_tbl
from schemas.campaigns import CreateCampaign,UpdateCampaignName,CreateCampaignResponse
from utils.logger import define_logger
from utils.auth import get_current_active_user
#create campaign on the master db

campaigns_logger=define_logger("als campaign logs","logs/campaigns_route.log")

#create campaign

async def create_campaign_db(campaign:CreateCampaign,session:AsyncSession,user)->CreateCampaignResponse:
    try:
        exists=await get_campaign_by_code_db(campaign.camp_code,session,user)
        if exists is not None:
            campaigns_logger.info(f"user:{user.id} with email:{user.email} requested campaign:{campaign.campaign_name} with campaign code:{campaign.camp_code} from this branch:{campaign.branch}")
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail=f"campaign:{campaign.campaign_name} with campaign code:{campaign.camp_code} from this branch:{campaign.branch} already exists")
        db_campaign=campaign_tbl(**campaign.model_dump())
        session.add(db_campaign)
        await session.commit()
        await session.refresh(db_campaign)
        campaigns_logger.info(f"user:{user.id} with email:{user.email} created campaign:{campaign.campaign_name} from branch:{campaign.branch}")
        return CreateCampaignResponse.model_validate(db_campaign)
    
    except HTTPException:
        raise
    except Exception as e:
        await session.rollback()
        campaigns_logger.exception(f"internal server error occurred:{e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail=f"an internal server error occurred")

#update campaign name
async def update_campaign_name_db(campaign_new_name:UpdateCampaignName,camp_code:str,session:AsyncSession,user)->CreateCampaignResponse|None:
    #get campaign by code
    result=await get_campaign_by_code_db(camp_code,session,user)
    if result==None:
        return None
    
    result.campaign_name=campaign_new_name.campaign_name
    try:
        session.add(result)
        await session.commit()
        await session.refresh(result)
        campaigns_logger.info(f"user {user.id} with email:{user.email} updated campaign:{campaign_new_name.campaign_name} to {campaign_new_name}")
        return CreateCampaignResponse.model_validate(result)
    except HTTPException:
        raise
    except Exception as e:
        await session.rollback()
        campaigns_logger.exception(f"an internal server error occurred while updating campaign:{camp_code}:{str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail=f"Internal server error occurred")


#get campaign by name
async def get_campaign_by_name_db(campaign_name:str,session:AsyncSession)->CreateCampaignResponse:
    try:
        campaign_query=select(campaign_tbl).where(campaign_tbl.campaign_name==campaign_name)
        campaign=await session.exec(campaign_query)
        result=campaign.first()
        if not result:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f"Campaign:{campaign_name} does not exist")
        return CreateCampaignResponse.model_validate(result)
    
    except HTTPException:
        raise

    except Exception as e:
        campaigns_logger.exception(f"An exception occurred:{e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail=f"An internal server error occurred")

#get campaign by campaign code
async def get_campaign_by_code_db(camp_code:str,session:AsyncSession,user)->CreateCampaignResponse| None:
    try:
        
        campaign_query=select(campaign_tbl).where(campaign_tbl.camp_code==camp_code)
        campaign=await session.exec(campaign_query)
        result=campaign.first()
        print("print values from the database")
        print(result)
        if result is None:
            campaigns_logger.info(f"user:{user.id} with email:{user.email} attempted to retrievE campaign:{camp_code}")
            return None
        print("print values before you return")
        return CreateCampaignResponse.model_validate(result)
    
    except HTTPException:
        raise

    except Exception as e:
        campaigns_logger.exception(f"An internal server error occurred:{e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail=f"An internal server error occurred")


#get all active campaigns
async def get_all_campaigns_by_branch_db(branch:str,session:AsyncSession,user,page:int,page_size:int)->List[CreateCampaignResponse]:
    campaigns_query=await session.exec(select(campaign_tbl).where(campaign_tbl.branch==branch))
    campaigns=campaigns_query.all()
    total=len(campaigns)
    #pagination calculations
    start=(page - 1)*page_size
    end=start + page_size

    paginated_campaigns=campaigns[start:end]

    results=[CreateCampaignResponse.model_validate(c) for c in paginated_campaigns]

    return {
        "total":total,
        "page":page,
        "page_size":page_size,
        "results":results
    }


