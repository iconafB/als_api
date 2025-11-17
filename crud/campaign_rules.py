from fastapi import HTTPException,status,Depends
from sqlmodel import select,SQLModel
from typing import Annotated
from datetime import datetime
from sqlalchemy import text,func
from schemas.campaign_rules import CreateCampaignRule
from utils.auth import get_current_active_user
from utils.logger import define_logger
from sqlmodel.ext.asyncio.session import AsyncSession
from typing import List,Optional
from models.rules_table import rules_tbl
from crud.campaigns import (get_campaign_by_code_db)
from models.campaigns_table import campaign_tbl
from schemas.campaign_rules import RuleCreate,AssignCampaignRuleToCampaign,AssignCampaignRuleResponse,CreateCampaignRuleResponse,PaginatedCampaignRules

#rules logger
campaign_rules_logger=define_logger("als campaign rules","logs/campaign_rules_logs")
#create campaign rule 
async def create_campaign_rule_db(rule:RuleCreate,session:AsyncSession,user)->CreateCampaignRuleResponse:
   
    try:
        #get campaign rule by rule name
        print("enter the crud function,print the payload")
        print(rule)
        campaign_rule=await get_campaign_rule_by_rule_name_db(rule.rule_name,session,user)
        if campaign_rule is not None:
            campaign_rules_logger.info(f"user {user.id} with email {user.email} tried to create campaign rule with rule name:{rule.rule_name}")
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail=f"{rule.rule_name} already exists")
        
        db_rule=rules_tbl(**rule.model_dump())
        session.add(db_rule)
        await session.commit()
        await session.refresh(db_rule)
        return CreateCampaignRuleResponse.model_validate(db_rule)
    
    except HTTPException:
        raise
    except Exception as e:
        campaign_rules_logger.exception(f"user id:{user.id} with email:{user.email} created a campaign rule:{rule.rule_name} and exception:{str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail=f"An internal server error occured while creating a campaign rule:{rule.rule_name}")

#search rule_code by rule_name
async def get_rule_by_rule_code_db(rule_code:str,session:AsyncSession,user=Depends(get_current_active_user))->CreateCampaignRuleResponse|None:
    rule_query=await session.exec(select(rules_tbl).where(rules_tbl.rule_code==rule_code))
    rule=rule_query.first()
    if not rule:
        campaign_rules_logger.info(f"user with user id:{user.id} with email:{user.email} requested campaign rule with rule code:{rule_code} but it does not exist")
        return None
    return rule


#assign campaign rule to an existing campaign
async def assign_campaign_rule_to_campaign_db(rule:AssignCampaignRuleToCampaign,session:AsyncSession,user=Depends(get_current_active_user))->AssignCampaignRuleResponse:
    
    try:
        #find campaign, exit and raise an exception if it's does not exist
        rule_code=rule.rule_code
        camp_code=rule.camp_code
        campaign=await get_campaign_by_code_db(rule.camp_code)
        if campaign==None:
            campaign_rules_logger.info(f"user with user id:{user.id} with email:{user.email} requested campaign with code:{rule.rule_code} and it does not exist")
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f"Campaign:{rule.camp_code} does not exist, create it and than assign to rule code:{rule.rule_code}")
        query= text("""
                SELECT r.rule_code
                FROM campaign_rule_tbl AS c
                JOIN rules_tbl AS r
                ON c.rule_code = r.rule_code
                WHERE c.camp_code = :camp_code
                  AND c.is_active = TRUE
                """
        )

        result=await session.execute(query,{"camp_code":camp_code})

        rows=result.fetchall()
        rule_codes=[row.rule_code for row in rows]

        if rule_code in rule_codes:
            rule_code_message=f"rule number:{rule_code} was found active, is now deactivated and {rule_code} is now active for campaign:{camp_code}"
            
            query=text("""
                    UPDATE campaign_rule_tbl
                    SET is_active = FALSE
                    WHERE camp_code = :camp_code
                    """)
            
            await session.execute(query,{"camp_code":camp_code})
            await session.commit()
            campaign_rules_logger.info(f"update campaign code:{camp_code} on table campaign_rule_tbl")
            todays_date=datetime.today().strftime('%Y-%m-%d')

            insert_campaign_rule_tbl_query=text("""
                                INSERT INTO campaign_rule_tbl (camp_code, rule_code, date_rule_created, is_active)
                                VALUES (:camp_code, :rule_code, :todays_date, TRUE)
                                """
                            )
            
            await session.execute(insert_campaign_rule_tbl_query,{
                "camp_code":camp_code,
                "rule_code":rule_code,
                "todays_date":todays_date
            })
            await session.commit()
            campaign_rules_logger.info(f"inserted camp code:{camp_code}, rule code:{rule_code} in table campaign_rule_tbl on:{todays_date}")
       
        else:
            rule_code_message=f'No active rule was found active for campaign {camp_code} but rule {rule_code} was made active for it'
            insert_query= text("""
                INSERT INTO campaign_rule_tbl (camp_code, rule_code, date_rule_created, is_active)
                VALUES (:camp_code, :rule_code, :todays_date, TRUE)
                    """
                )
            
            await session.execute(insert_query,{"camp_code":camp_code,"rule_code":rule_code,"todays_date":todays_date})
            #commit changes
            await session.commit()
            campaign_rules_logger.info(f"inserted camp code:{camp_code}, rule code:{rule_code} in table campaign_rule_tbl on:{todays_date}")  

        return AssignCampaignRuleResponse(message=rule_code_message,Success=True)
    
    except HTTPException:
        raise
    
    except Exception as e:
       campaign_rules_logger.exception(f"user with user id:{user.id} with email:{user.email} caused an exception:{e}")
       raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail=f"An internal server error occurred while assigning campaign:{rule.rule_code} to campaign:{rule.camp_code}")

#delete campaign rule by making the is_active field to false
async def delete_campaign_rule_db(rule_name:str,session:AsyncSession,user=Depends(get_current_active_user)):
    try:
        #find the campaign rule
        campaign_rule_query=select(rules_tbl.is_active).where(rules_tbl.rule_name==rule_name)
        campaign_rule=await session.exec(campaign_rule_query)
        result=campaign_rule.first()
        if not result:
            return False
        result=False
        session.add(result)
        await session.commit()
        return True
    except HTTPException:
        raise
    except Exception as e:
        campaign_rules_logger.exception(f"an exception occurred for user:{user.id} with email:{user.email} while deleting campaign:{rule_name}:{str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail=f"an exception occurred for user:{user.id} with email:{user.email} while deleting campaign:{rule_name}")


#get all active campaign rules
async def get_campaign_rule_by_rule_name_db(rule_name:str,session:AsyncSession,user)->CreateCampaignRuleResponse|None:
    try:
        #find the campaign rule by rule name
        campaign_rule_query=await session.exec(select(rules_tbl).where(rules_tbl.rule_name==rule_name))
        print("print enter the get campaign rule by rule name")
        print(rule_name)
        campaign_rule=campaign_rule_query.first()
        if campaign_rule is None:
           campaign_rules_logger.info(f"campaign rule:{rule_name} requested by user {user.id} with email:{user.email} does not exist")
           return None

        return CreateCampaignRuleResponse.model_validate(campaign_rule)
    
    except HTTPException:
        raise 
    except Exception as e:
        campaign_rules_logger.exception(f"an internal server error occurred while requesting campaign rule:{rule_name},{str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail=f"An internal server error occurred while requesting campaign rule:{rule_name}")


#get all campaign rules
async def get_all_campaign_rules_db(page:int,page_size:int,session:AsyncSession,user)->PaginatedCampaignRules|None:

    try:
        print("Enter crud method")
        total=await session.scalar(select(func.count(rules_tbl.rule_code)))
        print(f"total:{total}")
        offset=(page - 1)*page_size
        print(f"offset:{offset}")
        print(f"page size:{page_size}")
        result=await session.exec(select(rules_tbl).offset(offset).limit(page_size))
        print("result fetched")
        results=result.all()
        campaign_rules=[CreateCampaignRuleResponse.model_validate(r) for r in results]
        campaign_rules_logger.info(f"user:{user.id} with email:{user.email} retrieved records for campaign rules:{len(campaign_rules)}")
        return PaginatedCampaignRules(total=total or 0,page=page,page_size=page_size,rules=campaign_rules)
    except Exception as e:
        campaign_rules_logger.exception(f"an exception occurred while fetching all campaign rules by user {user.id} with email:{user.email}:{str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail=f"An internal server error occurred while fetching all campaign rules")
#get rules within a salary range

#update salary,start year, or end year


