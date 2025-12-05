from sqlalchemy.ext.asyncio.session import AsyncSession
from sqlalchemy import text
from typing import List,Tuple
from utils.dedupes.manual_dedupe_queries import INSERT_MANUAL_DEDUPE_QUERY,INSERT_MANUAL_DEDUPE_INFO_TBL_QUERY
from utils.logger import define_logger
dedupe_logger=define_logger("als_dedupe_campaign_logs","logs/dedupe_route.log")

async def insert_campaign_dedupe_batch(session:AsyncSession,data:List[Tuple[str,str,str,str]],user,batch_size:int=1000):
    
    if not data:
        return 0
    insert_stmt=text(INSERT_MANUAL_DEDUPE_QUERY)
    total_inserted=0

    try:

        for i in range(0,len(data),batch_size):
            batch=data[i:i+batch_size]

            batch_dicts = [
                {
                    "id": r[0],
                    "cell": r[1],
                    "campaign_name": r[2],
                    "status": r[3],
                    "code": r[4]
                }
                for r in batch
            ]
            
            await session.execute(insert_stmt,batch_dicts)
            total_inserted+=len(batch_dicts)
        
        await session.commit()

        dedupe_logger.info(f"user:{user.id} with email:{user.email} inserted {total_inserted} records into the campaign_dedupe table")

        return total_inserted
    
    except Exception as e:
        await session.rollback()
        dedupe_logger.exception(f"An exception occurred while inserting dedupe data:{e}")
        raise
    



async def insert_manual_dedupe_info_tbl(session:AsyncSession,update_data:List[Tuple[str,str]],user,batch_size:int=1000):
    try:
        if not update_data:
            return 0
        total_processed=0
        insert_stmt=text(INSERT_MANUAL_DEDUPE_INFO_TBL_QUERY)

        for i in range(0,len(update_data),batch_size):
            batch=update_data[i:i+batch_size]
            batch_dicts = [
                {"cell": r[0], "extra_info": r[1]}
                for r in batch
            ]

            await session.execute(insert_stmt,batch_dicts)
            total_processed+=len(batch_dicts)
        
        
        await session.commit()
        dedupe_logger.info(f"records inserted into the info_tbl:{total_processed} by user:{user.id} with email:{user.email}")
        return total_processed
    except Exception as e:
        session.rollback()
        dedupe_logger.exception(f"an exception occured while inserting dedupe data on the info_tbl:{e}")
        raise