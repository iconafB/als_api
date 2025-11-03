from sqlmodel import create_engine,SQLModel
from typing import AsyncGenerator
from sqlmodel.ext.asyncio.session import AsyncSession
from settings.Settings import get_settings
from sqlalchemy.ext.asyncio import create_async_engine,async_sessionmaker

#main db string 
#DATABASE_URL=f"postgresql+psycopg2://{get_settings().database_owner}:{get_settings().database_password}@{get_settings().database_host_name}:{get_settings().database_port}/{get_settings().database_name}"

#we just want to connect to the master db nothing more
#MASTER_DB_URL=f"potgresql+psycopg2://{get_settings().master_db_user}:{get_settings().master_db_password}@{get_settings().master_db_host_name}:{get_settings().master_db_port_number}/{get_settings().master_db_name}"

ASYNC_MASTER_DB_URL=f"postgresql+asyncpg://{get_settings().master_db_user}:{get_settings().master_db_password}@{get_settings().master_db_host_name}:{get_settings().master_db_port_number}/{get_settings().master_db_name}"

#create the connection engine with the master db
#master_db_engine=create_engine(MASTER_DB_URL,echo=True)

master_async_engine=create_async_engine(ASYNC_MASTER_DB_URL,echo=True,future=True,pool_timeout=30,pool_recycle=1800,pool_size=10,max_overflow=20)

#session factory
async_session_maker=async_sessionmaker(
    bind=master_async_engine,
    class_=AsyncSession,
    expire_on_commit=False
)

#dependency injection
async def get_async_session()->AsyncGenerator[AsyncSession,None]:
    
    async with async_session_maker() as session:
        try:
            yield session #ensure session closes after session
        finally:
            await session.close()


#initialize the db with new tables
async def init_db():
    async with master_async_engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)