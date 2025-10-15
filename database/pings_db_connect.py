
from sqlmodel import Session,create_engine
from settings.Settings import get_settings

PINGS_DATABASE_URL=f"postgresql+psycopg2://{get_settings().pings_db_name}:{get_settings().pings_db_password}@{get_settings().pings_db_host}:{get_settings().pings_db_port}/{get_settings().pings_db_name}"

#create the connection engine for pings database

pings_engine=create_engine(PINGS_DATABASE_URL,echo=True)

def get_pings_session_db():
    with Session(pings_engine) as pings_db_session:
        yield pings_db_session


