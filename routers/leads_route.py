from fastapi import APIRouter,Query,HTTPException,Depends,status
from models.leads import info_tbl
from models.campaign_rules import rules_tbl
from models.campaigns import Campaign_Dedupe
from database.database import get_session
from sqlmodel import select
from sqlalchemy import exists
from sqlalchemy.sql import func,text
from sqlalchemy.sql.sqltypes import Integer
from schemas.leads import LeadsCount,SpecLevel
from sqlmodel import Session
from utils.auth import get_current_user
from utils.logger import define_logger

leads_router=APIRouter(tags=["Leads Route"],prefix="/leads")

leads_logger=define_logger("als leads als","logs/leads_route.log")

@leads_router.get("/get-count",status_code=status.HTTP_200_OK,response_model=LeadsCount)
async def get_number_of_leads(campaign_name:str=Query(description="Please enter the campaign name"),status:str=Query(description="Enter the campaign status"),session:Session=Depends(get_session),user=Depends(get_current_user)):
    #build the EXISTS subquery
    try:
        subquery=(select(Campaign_Dedupe.id).where(Campaign_Dedupe.cell==info_tbl.cell))
        sql_statement=(select(info_tbl.id,info_tbl.fore_name,info_tbl.last_name,info_tbl.cell).where(exists(subquery),info_tbl.id.is_not(None)))
        results=session.exec(sql_statement).all()
        if not results:
            leads_logger.info(f"no leads found for campaign:{campaign_name}")
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f"No leads found for campaign:{campaign_name}")
        leads_count=len(results)
        leads_logger.info(f"{len(leads_count)} leads for campaign:{campaign_name}")
        return LeadsCount(message=f"Leads found for campaign:{campaign_name}",number=leads_count,status=True)
    except Exception as e:
        session.rollback()
        leads_logger.exception(f"An exception occurred while getting leads count:{e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail=f"An internal server occurred while checking spec level for rule code provided")    


    # leads=LeadsCount(message="Leads Fetched Successfully",number=count)
    # return leads

#check spec levels

@leads_router.get("/check-spec-levels/{rule_code}")
async def check_spec_levels(rule_code:int,last_used:str,session:Session=Depends(get_session)):
    try:
        rules_code_query=select(rules_tbl).where(rules_tbl.rule_code==rule_code)
        rule=session.exec(rules_code_query).first()
        if not rule:
            leads_logger.info(f"No rule code exist that matches rule code:{rule_code}")
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f"No rule code exist that matches rule code:{rule_code}")
        
        # query=select(info_tbl.id,info_tbl.fore_name,info_tbl.last_name,info_tbl.cell).where((info_tbl.salary>=rule.salary)|(info_tbl.salary.is_(None))).where(info_tbl.type_data=="Status").where((info_tbl.last_used.is_(None) | (text('EXTRACT(DAY FROM(NOW() - last_used))>29')))).where(func.case([
        #     (func.cast(func.substring(info_tbl.id,1,2),Integer)>=25,1900+ func.cast(func.substring(info_tbl.id,1,2),Integer))
        # ],else_=2000+func.cast(func.substring(info_tbl.id,1,2),Integer).between(rule.birth_year_start,rule.birth_year_end)).order_by(func.random()).limit(rule.limit)

        # results=session.exec(query).all()

        leads_query=select(info_tbl.id,info_tbl.fore_name,info_tbl.last_name,info_tbl.cell).where((info_tbl.salary>=rule.salary)|(info_tbl.salary.is_(None))).where(info_tbl.type_data=="Status").where((info_tbl.last_used.is_(None))|(text('EXTRACT(DAY FROM(NOW() - last_used))>29'))).where(func.case([
            (func.cast(func.substring(info_tbl.id,1,2),Integer)>=25,
             1900 + func.cast(func.substring(info_tbl.id,1,2)),
             )
        ],else_=2000 + func.cast(func.substring(info_tbl.id,1,2),Integer)
        ).between(rule.birth_year_start,rule.birth_year_end)).order_by(func.random()).limit(rule.limit)    

        leads=session.exec(leads_query).all()

        if not leads:
            leads_logger.info(f"no leads for rule code:{rule_code} meets the campaign spec")
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f"No leads meet the spec level of:{rule_code}")
        leads_length=len(leads)
        return SpecLevel(status=True,specLevel=leads_length,message=f"number of leads meeting the spec level:{rule_code} is {leads_length}")
    
    except Exception as e:
        leads_logger.exception(f"an exception occurred while checking the spec level for rule code:{rule_code},exception:{e}")
        session.rollback()
        session.close()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail=f"An internal server occurred while checking spec level for rule code:{rule_code}")