from fastapi import HTTPException,Depends,status
from sqlmodel import Session,select
from fastapi.security import OAuth2PasswordBearer,OAuth2PasswordRequestForm,SecurityScopes
from passlib.context import CryptContext
from typing import Annotated
from datetime import datetime,timedelta,timezone
import jwt
from jwt.exceptions import InvalidTokenError
from settings.Settings import get_settings
from database.database import get_session
from models.users import users_table
from schemas.auth import TokenData

pwd_context=CryptContext(schemes=["bcrypt"],deprecated="auto")

oauth_scheme=OAuth2PasswordBearer(tokenUrl='auth/login')

#hash password
def hash_password(password):
    return pwd_context.hash(password)

#verify password
def verify_password(plain_password,hashed_password):
    return pwd_context.verify(plain_password,hashed_password)

#create access token
def create_access_token(data:dict,expires_delta:timedelta | None=None):
    to_encode=data.copy()
    #create expires_dalta
    if expires_delta:
        expire=datetime.now(timezone.utc) + expires_delta
    else:
        expire=datetime.now(timezone.utc) + timedelta(minutes=15)
    
    to_encode.update({'exp':expire})
    encoded_jwt=jwt.encode(to_encode,get_settings().SECRET_KEY,algorithm=get_settings().ALGORITHM)
    return encoded_jwt

#verify access token
def verify_token(token:str,credentials_exception):
    try:
        payload=jwt.decode(token,get_settings().SECRET_KEY,algorithms=get_settings().ALGORITHM)
        id:str=payload.get("user_id")
        if id is None:
            raise credentials_exception 
    except Exception as e:
        print(e)
        raise credentials_exception

    return id

#get current user
async def get_current_user(token:Annotated[str,Depends(oauth_scheme)]):
    
    credential_exception=HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail=f"Could not validate credentials",headers={"WWW-Authenticate": "Bearer"})
    try:
        #nonsense replication of code verify token method would do easily
        payload=jwt.decode(token,get_settings().SECRET_KEY,algorithms=get_settings().ALGORITHM)
        user_id=payload['user_id']
        if user_id==None:
            raise credential_exception
    except InvalidTokenError:
        raise credential_exception
    
    return user_id

async def get_current_active_user(current_user:Annotated[int,Depends(get_current_user)],session:Session=Depends(get_session)):
    
    credential_exception=HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail=f"Could not validate credentials",headers={"WWW-Authenticate": "Bearer"})
    
    if current_user==None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="Inactive user")
    #get the current user
    user_query=select(users_table).where(users_table.id==current_user)
    #exceute the query and get user data
    user=session.exec(user_query).first()
    #raise an exception if the user does not exist
    if user==None:
        raise credential_exception
    return user

#get the current user to secure the protected routes


 

