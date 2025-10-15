
from pydantic_settings import BaseSettings,SettingsConfigDict
from functools import lru_cache

class Settings(BaseSettings):
    
    database_password:str
    database_host_name:str
    database_name:str
    database_port:int
    database_owner:str

    #master db information
    master_db_host_name:str
    master_db_port_number:int
    master_db_name:str
    master_db_user:str
    master_db_password:str
    #authentication details

    SECRET_KEY:str
    ALGORITHM:str
    dmasa_api_key:str
    dmasa_member_id:str
    ACCESS_TOKEN_EXPIRES_MINUTES:int
    upload_dmasa_url:str
    read_dmasa_dedupe_status:str
    notification_email:str
    check_credits_dmasa_url:str
    
    dedago_url:str

    INVTNTDBN_TOKEN:str
    P3_TOKEN:str
    HQ_TOKEN:str
    YORK_TOKEN:str


    #pings environment variables
    hopper_level_check_url:str
    icon_ping_url:str
    send_pings_to_kuda_username:str
    send_pings_to_kuda_password:str
    send_pings_to_troy_url:str
    send_pings_to_troy_token:str

    pings_db_name:str
    pings_db_user:str
    pings_db_password:str
    pings_db_port:str
    pings_db_host:str

    #dma environment variables
    dmasa_api_key:str
    dmasa_member_id:str
    upload_dmasa_url:str
    check_credits_dmasa_url:str
    read_dmasa_dedupe_status:str
    read_dmasa_output_url:str
    notification_email:str
    
    #load the environment variables file
    model_config=SettingsConfigDict(env_file=".env")

#cache the settings results
@lru_cache
def get_settings()->Settings:
    
    return Settings()




