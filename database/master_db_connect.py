from sqlmodel import Session,create_engine
from settings.Settings import get_settings
from sqlalchemy.ext.asyncio import AsyncSession,create_async_engine

#main db string 
DATABASE_URL=f"postgresql+psycopg2://{get_settings().database_owner}:{get_settings().database_password}@{get_settings().database_host_name}:{get_settings().database_port}/{get_settings().database_name}"

#we just want to connect to the master db nothing more
MASTER_DB_URL=f"potgresql+psycopg2://{get_settings().master_db_user}:{get_settings().master_db_password}@{get_settings().master_db_host_name}:{get_settings().master_db_port_number}/{get_settings().master_db_name}"

ASYNC_MASTER_DB_URL=f"potgresql+asyncpg://{get_settings().master_db_user}:{get_settings().master_db_password}@{get_settings().master_db_host_name}:{get_settings().master_db_port_number}/{get_settings().master_db_name}"
#create the connection engine with the master db
master_db_engine=create_engine(MASTER_DB_URL,echo=True)
#asynchronous insertion for large documents
master_async_engine=create_async_engine(ASYNC_MASTER_DB_URL,echo=True)
#start a session with the database for comms
def get_master_db_session():
    with Session(master_db_engine) as master_db_sesssion:
        yield master_db_sesssion

#insertion for large datasets
async def get_async_master_db_session():
    async with AsyncSession(master_async_engine) as async_db_session:
        yield async_db_session
