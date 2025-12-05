from fastapi import HTTPException,status
from sqlalchemy.ext.asyncio.session import AsyncSession
from sqlmodel import update
from typing import Tuple
from utils.logger import define_logger
from models.information_table import info_tbl
from models.campaign_dedupe import Campaign_Dedupe

campaigns_logger=define_logger("als_campaign_logs","logs/campaigns_route.log")

CHUNK_SIZE=1000 #number of code per batch

async def update_records_for_infoTable_campaign_dedupe_tbl(vendor_lead_codes_tuple:Tuple[str],session:AsyncSession)->int:
    if not vendor_lead_codes_tuple:
        campaigns_logger.warning("No vendor lead codes provided; skipping update")
        return 0
    total_ids=len(vendor_lead_codes_tuple)
    try:

        for i in range(0,total_ids,CHUNK_SIZE):

            batch=vendor_lead_codes_tuple[i:i+CHUNK_SIZE]

            if not batch:
                continue
            #update info_tbl 
            await session.execute(update(info_tbl).where(info_tbl.id.in_(batch)).values(extra_info=None))
            #update campaign_dedupe
            await session.execute(update(Campaign_Dedupe).where(Campaign_Dedupe.id.in_(batch)).values(status='U'))

        await session.commit()

        campaigns_logger.info(f"updated {total_ids} rows on the info_tbl and campaign_dedupe table")
        
        return total_ids
    
    #potential error
    except Exception:
        campaigns_logger.exception("An exception occurred while updating rows on the info_tbl and campaign_dedupe table")
        await session.rollback()
        raise 

