from fastapi import Depends,status,HTTPException
from sqlmodel import Session
from sqlalchemy.dialects import postgresql
from sqlalchemy import insert,and_,or_
from database.master_db_connect import get_master_db_session
from utils.logger import define_logger
from models.finance_table import finance_table,car_table,employment_table,location_table

from models.leads import contact_table,information_table
status_data_logger=define_logger("als status logger logs","logs/status_data.log")

async def execute_sql_status_statement(master_session:Session=Depends(get_master_db_session)):
    try:

        return True
    except Exception as e:
        status_data_logger.critical(f"{str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail=f"{str(e)}")
    
async def insert_vendor_list_status(master_session:Session=Depends(get_master_db_session)):
    try:

        return True
    except Exception as e:
        status_data_logger.critical(f"{str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail=f"{str(e)}")
    
#get tuple

#execute whatever is return from these methods

async def insert_data_into_finance_table(data:dict):

    try:
        insert_stmt=postgresql.insert(finance_table.__tablename__).values(**data)
        on_conflict_stmt=insert_stmt.on_conflict_do_nothing(index_elements=[finance_table.cell_number])
        status_data_logger.info("data inserted on the finance table")
        return on_conflict_stmt
    
    except Exception as e:
        status_data_logger.critical(f"{str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail=f"{str(e)}")
    
async def insert_data_into_car_table(data:dict):

    try:
        insert_stmt=postgresql.insert(car_table.__tablename__).values(**data)
        on_conflict_stmt=insert_stmt.on_conflict_do_nothing(index_elements=[car_table.cell_number])
        status_data_logger.info("data inserted on the car table")
        return on_conflict_stmt
    
    except Exception as e:
        status_data_logger.critical(f"{str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail=f"{str(e)}")

#return type for these methods

async def insert_data_into_employment_table(data:dict):
    try:
        insert_stmt=postgresql.insert(employment_table.__tablename__).values(**data)
        on_conflict_smt=insert_stmt.on_conflict_do_nothing(index_elements=[employment_table.cell_number])
        status_data_logger.info("data insert into the employment table")
        return on_conflict_smt
    except Exception as e:
        status_data_logger.critical(f"{str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail=f"{str(e)}")

async def insert_data_into_contact_table(data:dict):
    try:
        insert_stmt=postgresql.insert(contact_table.__tablename__).values(**data)
        excluded=insert_stmt.excluded
        #define the where condition 
        update_where_clause=contact_table.cell_number==excluded.cell_number
        on_conflict_stmt=insert_stmt.on_conflict_do_update(index_elements=[contact_table.cell_number],set_={'email':excluded.email},where=update_where_clause)
        status_data_logger.info(f"update data on contact table")
        return on_conflict_stmt
    except Exception as e:
        status_data_logger.critical(f"{str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail=f"{str(e)}")

async def insert_data_into_location_table(data:dict):
    try:
        insert_stmt=postgresql.insert(location_table.__tablename__).values(**data)
        on_conflict_stmt=insert_stmt.on_conflict_do_nothing(index_elements=[location_table.cell_number])
        status_data_logger.info("data insert into the location table")
        return on_conflict_stmt
    except Exception as e:
        status_data_logger.critical(f"{str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail=f"{str(e)}")

async def insert_data_into_information_table(data:dict):
    try:
        insert_stmt=postgresql.insert(information_table.__tablename__).values(**data)

        excluded=insert_stmt.excluded
        #define where condition
        update_where_clause=and_(
            information_table.cell_number==excluded.cell_number,
            or_(
                information_table.id_number==excluded.id_number,
                and_(
                    information_table.fore_name == excluded.fore_name,
                    information_table.last_name == excluded.last_name
                )
            )
        )
        on_conflict_stmt=insert_stmt.on_conflict_do_update(
            index_elements=[information_table.cell_number],
            set={
                'created_at':excluded.created_at,
                'salary':excluded.salary,
                'status':excluded.status
            },
            where=update_where_clause
        )
        status_data_logger.info("insert data into the information table")
        return on_conflict_stmt
    
    except Exception as e:
        status_data_logger.critical(f"{str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail=f"{str(e)}")



async def get_status_tuple():
    try:
        return postgresql.insert(finance_table.__tablename__).values()
    
    except Exception as e:
        #
        status_data_logger.critical(f"{str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail=f"{str(e)}")