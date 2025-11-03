from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from typing import List,Optional
from models.campaigns import campaign_tbl

#create campaign on the master db

async def create_campaign(session:AsyncSession):
    
    return True
