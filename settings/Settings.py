
from pydantic_settings import BaseSettings,SettingsConfigDict
from functools import lru_cache

class Settings(BaseSettings):
    database_password:str
    database_host_name:str
    database_name:str
    database_port:int
    database_owner:str
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
    #load the environment variables file
    model_config=SettingsConfigDict(env_file=".env")


#cache the settings results
@lru_cache
def get_settings()->Settings:
    return Settings()




