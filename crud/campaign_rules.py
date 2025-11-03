from fastapi import HTTPException,status

from schemas.campaign_rules import CreateCampaignRule
from sqlmodel.ext.asyncio.session import AsyncSession
from typing import List,Optional
from models.campaign_rules import rules_tbl
from schemas.campaign_rules import RuleCreate
#create campaign rule 
async def create_campaign_rule(rule:RuleCreate,session:AsyncSession)->rules_tbl:
    exists=await session.get(rules_tbl,rule.rule_name)
    if exists:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail=f"{rule.rule_name} already exists")
    db_rule=rules_tbl(**rule.model_dump())
    
    session.add(db_rule)
    await session.commit()
    await session.refresh(db_rule)
    return db_rule

#read campaign rule by rule name
async def get_campaign_rule_by_rule_name(rule_name:str,session:AsyncSession)->rules_tbl:
    rule=await session.get(rules_tbl,rule_name)
    if not rule:
        return None
    return rule


#search rule_code by rule_name
async def get_rule_code_by_rule_name():
    
    return True
#delete campaign rule by making the is_active field to false

#get all active campaign rules

#update salary,start year, or end year


