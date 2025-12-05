from sqlalchemy import text
from sqlmodel.ext.asyncio.session import AsyncSession
from utils.logger import define_logger

status_data_logger=define_logger("als_status_logger_logs","logs/status_data.log")

def get_status_tuple(datadictlist, num):
    """
    Build tuples for inserting into specific tables depending on `num`.
    """

    # Mapping of num → list of fields to extract from each dict
    field_map = {
        1: ["cell", "idnum", "name", "surname", "dob", "date_created",
            "gender", "salary", "status"],
        2: ["cell", "address1", "address2", "suburb", "city", "postal"],
        3: ["cell", "email"],
        4: ["cell", "company", "job"],
        5: ["cell", "car", "model"],
        6: ["cell", "bank", "bal"],
    }

    if num not in field_map:
        raise ValueError(f"Invalid num value: {num}")

    fields = field_map[num]
    rows = []

    for r in datadictlist:
        tuple_data = tuple(r[field] for field in fields)
        # Special case: num==1 needs typedata appended

        if num == 1:
            tuple_data = tuple_data + ("Status",)
        rows.append(tuple_data)

    return rows



async def insert_vendor_list_status(sqlsmt: str, vendor_list: list[tuple], session: AsyncSession,batch_size:int=1000):
    """
    Insert vendor list data using async SQLAlchemy sessions.
    Works with raw SQL and executemany.
    """

    if not vendor_list:
        return {"success":True,"inserted":0,"message":"No data to insert"}
    
    total_inserted=0

    try:
        # Bulk insert using SQLAlchemy async executemany

        # await session.execute(
        #     text(sqlsmt),
        #     vendor_list
        # )
        # await session.commit()

        #process in batches

        for i in range(0,len(vendor_list),batch_size):
            batch = vendor_list[i:batch_size]
            await session.execute(sqlsmt,batch)
            total_inserted+=len(batch)
        await session.commit()
        return {"success":True,"inserted":total_inserted,"message":f"Successfully inserted {total_inserted} rows in batches of {batch_size}"}
    
    except Exception as e:
        await session.rollback()

        status_data_logger.exception(f"An exception occurred while inserting the data:{e}")
        raise e
