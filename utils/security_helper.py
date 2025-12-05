from fastapi import status,HTTPException,Depends
from fastapi.security import HTTPBasic,HTTPBasicCredentials
import secrets
from typing import Optional
from settings.Settings import get_settings
security=HTTPBasic()

def get_current_admin(credentials:HTTPBasicCredentials=Depends(security)):
    correct_username=secrets.compare_digest(credentials.username,get_settings().ADMIN_USERNAME)
    correct_password=secrets.compare_digest(credentials.password,get_settings().ADMIN_PASSWORD)
    
    if not (correct_username and correct_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Incorrect username or password",headers={"WWW-Authenticate": "Basic"})
    
    return credentials.username
