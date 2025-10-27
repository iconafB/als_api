from fastapi import Depends,status,HTTPException
from sqlmodel import Session
from sqlalchemy.ext.asyncio import AsyncSession

from sqlalchemy.dialects import postgresql
from sqlalchemy import insert,and_,or_
from database.master_db_connect import get_master_db_session,get_async_master_db_session
from database.database import get_session

from utils.logger import define_logger
from models.leads import contact_tbl,info_tbl,employment_tbl,location_tbl,car_tbl
from models.leads import finance_tbl

status_data_logger=define_logger("als status logger logs","logs/status_data.log")

#execute whatever is return from these methods

async def insert_data_into_finance_table(data:list,session:Session=Depends(get_master_db_session),async_session:AsyncSession=Depends(get_async_master_db_session)):

    try:
        insert_stmt=postgresql.insert(finance_tbl.__tablename__).values(**data)
        on_conflict_stmt=insert_stmt.on_conflict_do_nothing(index_elements=[finance_tbl.cell])
        if len(data)<5000:
            session.exec(on_conflict_stmt)
            session.commit()
            session.close()
            status_data_logger.info("data inserted on the finance table")
        else:
            await async_session.execute(on_conflict_stmt)
            await async_session.commit()
            async_session.close()
            status_data_logger.info("data inserted on the finance table")
        return True
    
    except Exception as e:
        status_data_logger.critical(f"{str(e)}")
        if len(data)<5000:

            session.rollback()
            session.close()
        else:
            await async_session.rollback()
            await async_session.close()
        
        return False
    
async def insert_data_into_car_table(data:list,session:Session=Depends(get_master_db_session),async_session:AsyncSession=Depends(get_async_master_db_session)):

    try:
        insert_stmt=postgresql.insert(car_tbl.__tablename__).values(**data)
        on_conflict_stmt=insert_stmt.on_conflict_do_nothing(index_elements=[car_tbl.cell])

        if len(data)<5000:
            session.exec(on_conflict_stmt)
            session.commit()
            session.close()
            status_data_logger.info("data inserted on the car table")
        else:
            await async_session.execute(on_conflict_stmt)
            await async_session.commit()
            async_session.close()
            status_data_logger.info("data inserted on the car table")
        
        return True
    
    except Exception as e:
        status_data_logger.error(f"{str(e)}")
        if len(data)<5000:
            session.rollback()
            session.close()
        else:
            await async_session.rollback()
            await async_session.close()
        return False

#return type for these methods

async def insert_data_into_employment_table(data:dict,session:Session=Depends(get_master_db_session),async_session:AsyncSession=Depends(get_async_master_db_session)):
    try:
        insert_stmt=postgresql.insert(employment_tbl.__tablename__).values(**data)
        on_conflict_smt=insert_stmt.on_conflict_do_nothing(index_elements=[employment_tbl.cell])

        if len(data)<5000:
            session.exec(on_conflict_smt)
            session.commit()
            session.close
            status_data_logger.info(f"data inserted:{len(data)} into the employment table")
            
        else:
            #execute asynchronously
            await async_session.execute(on_conflict_smt)
            await async_session.commit()
            async_session.close()
            status_data_logger.info(f"data inserted:{len(data)} into the employment table")

        return True
    except Exception as e:

        status_data_logger.error(f"{str(e)}")
        if len(5000)<5000:
            session.rollback()
            session.close()
        else:  
            await async_session.rollback()
            await async_session.close()

        return False
        #raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail=f"{str(e)}")

async def insert_data_into_contact_table(data:dict,session:Session=Depends(get_master_db_session),async_session:AsyncSession=Depends(get_async_master_db_session)):
    try:
        insert_stmt=postgresql.insert(contact_tbl.__tablename__).values(**data)
        excluded=insert_stmt.excluded
        update_where_clause=contact_tbl.cell==excluded.cell
        on_conflict_stmt=insert_stmt.on_conflict_do_update(index_elements=[contact_tbl.cell],set_={'email':excluded.email},where=update_where_clause)
        
        if len(data)<5000:
            session.exec(on_conflict_stmt)
            session.commit()
            session.close()
            status_data_logger.info(f"updated {len(data)} rows on the contact table")
        else:
            await async_session.execute(on_conflict_stmt)
            await async_session.commit()
            async_session.close()
            status_data_logger.info(f"updated {len(data)} rows on contact table")
        return True
        #return on_conflict_stmt
    except Exception as e:
        status_data_logger.critical(f"{str(e)}")

        if len(data)<5000:
            session.rollback()
            session.close()
        else:
            await async_session.rollback()
            await async_session.close()

        return False


async def insert_data_into_location_table(data:dict,session:Session=Depends(get_master_db_session),async_session:AsyncSession=Depends(get_async_master_db_session)):
    try:
        insert_stmt=postgresql.insert(location_tbl.__tablename__).values(**data)
        on_conflict_stmt=insert_stmt.on_conflict_do_nothing(index_elements=[location_tbl.cell])
        
        if len(data)<5000:

            session.exec(on_conflict_stmt)
            session.commit()
            session.close()
            status_data_logger.info(f"data:{len(data)} inserted into the location table")
            
        else:
            await async_session.execute(on_conflict_stmt)
            await async_session.commit()
            async_session.close()
            status_data_logger.info(f"data:{len(data)} inserted into the location table")
        return True
    
    except Exception as e:
        status_data_logger.critical(f"{str(e)}")
        if len(data)<5000:
            session.rollback()
            session.close()
        else:
            await async_session.rollback()
            await async_session.close()
        return False

async def insert_data_into_information_table(data:list,session:Session=Depends(get_master_db_session),async_session:AsyncSession=Depends(get_async_master_db_session)):
    try:
        insert_stmt=postgresql.insert(info_tbl.__tablename__).values(**data)

        excluded=insert_stmt.excluded
        #define where condition
        update_where_clause=and_(
            info_tbl.cell==excluded.cell,
            or_(
                info_tbl.id==excluded.id,
                and_(
                    info_tbl.fore_name == excluded.fore_name,
                    info_tbl.last_name == excluded.last_name
                )
            )
        )
        
        on_conflict_stmt=insert_stmt.on_conflict_do_update(
            index_elements=[info_tbl.cell],
            set={
                'created_at':excluded.created_at,
                'salary':excluded.salary,
                'status':excluded.status
            },
            where=update_where_clause
        )

        if len(data)<5000:
            session.exec(on_conflict_stmt)
            session.commit()
            session.close
            status_data_logger.info(f"insert:{len(data)} data into the information table")
        else:
            await async_session.execute(on_conflict_stmt)
            await async_session.commit()
            await async_session.close()
            status_data_logger.info(f"insert:{len(data)} data into the information table")
        return True
    
    except Exception as e:
        status_data_logger.critical(f"{str(e)}")

        if len(data)<5000:
            session.rollback()
            session.close()
        else:
            await async_session.rollback()
            await async_session.close()
        return False
        #raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail=f"{str(e)}")


def get_status_tuple(dataList:list,num:int):
    #build tuples to insert on the table,build a list comprehension
    try:
        if num==1:
            return [(d['idnum'],d['cell'],d['date_created'],d['salary'],d['name'],d['surname'],d['status'],d['dob'],d['gender'],d['typedata']) for d in dataList]
        elif num==2:
            return [(d['cell'],d['address1'],d['address2'],d['surburb'],d['city'])for d in dataList]
        elif num==3:
            return [(d['email'],d['cell']) for d in dataList]
        elif num==4:
            return [(d['cell'],d['company'],d['job']) for d in dataList]
        elif num==5:
            return [(d['cell'],d['car'],d['model']) for d in dataList]
        else:
            return [(d['cell'],d['bank'],d['bal'])for d in dataList]
    
    except Exception as e:
        status_data_logger.critical(f"{str(e)}")
        return False
    

