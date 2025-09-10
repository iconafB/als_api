from fastapi import HTTPException,Depends,status
from sqlmodel import Session
from fastapi.security import OAuth2PasswordBearer,OAuth2PasswordRequestForm
from passlib.context import CryptContext
from typing import Annotated
from datetime import datetime,timedelta,timezone
import jwt
from jwt.exceptions import InvalidTokenError
from settings.Settings import get_settings
from database.database import get_session
from schemas.auth import TokenData

pwd_context=CryptContext(schemes=["bcrypt"],deprecated="auto")

oauth_scheme=OAuth2PasswordBearer(tokenUrl='token')

#hash password
def hash_password(password):
    return pwd_context.hash(password)
#verify password
def verify_password(plain_password,hashed_password):
    return pwd_context.verify(plain_password,hashed_password)

#create access token
def access_token(data:dict,expires_delta:timedelta | None=None):
    #strings to encode
    print(data)
    to_encode=data.copy()
    if expires_delta:
        expire=datetime.now(timezone.utc) + expires_delta
    else:
        expire=datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({'exp':expire})
    encoded_jwt=jwt.encode(to_encode,get_settings().SECRET_KEY,algorithm=get_settings().ALGORITHM)

    return encoded_jwt

#get the current user to secure the protected routes
async def get_current_user(token:Annotated[str,Depends(oauth_scheme)],auth:str=Depends(oauth_scheme),session:Session=Depends(get_session)):

    credentials_exception=HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Could not validate credentials",headers={"WWW-Authenticate": "Bearer"})
    #decode the token 
    try:
        payload=jwt.decode(token,get_settings().SECRET_KEY,algorithms=get_settings().ALGORITHM)
        token_data=TokenData(username=payload['user_id'])
        print(f"token_data:{token_data}")
    except InvalidTokenError:
        raise credentials_exception
    
    return "access granted"
       
#generate an otp to be confirmed by the user who wants to reset the password
async def generate_otp():
    # generate the otp
    return   

