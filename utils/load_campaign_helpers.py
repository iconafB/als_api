from utils.dynamic_sql_rule_function import build_dynamic_rule_engine
from fastapi import Depends,HTTPException,status
from sqlalchemy.ext.asyncio.session import AsyncSession
from database.master_db_connect import get_async_session
from crud.campaign_rules import get_campaign_rule_by_rule_name_db
from crud.rule_engine_db import get_rule_by_name_db

async def load_leads_for_campaign(rule_name:str,session:AsyncSession):
    try:
        result=await get_rule_by_name_db(rule_name,session)
        if result==None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f"The requested rule does not exist")
        stmt,params=build_dynamic_rule_engine(result[0].rule_json)
        rows=await session.execute(stmt,params)
        return rows.mappings().all()
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail=f"An internal server error occurred while loading for a campaign:{str(e)}")
    

async def filter_dnc_numbers(leads_results,dnc_list):
    dnc_set=set(dnc_list)
    return [r for r in leads_results if r['cell'] not in dnc_set]