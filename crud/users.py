from fastapi import HTTPException,Depends,status
from fastapi.security import OAuth2PasswordRequestForm
from typing import Annotated
from sqlmodel import select
from datetime import timedelta
from sqlalchemy.ext.asyncio.session import AsyncSession
from models.users import users_table
from schemas.auth import RegisterUser,RegisterUserResponse,Token,ForgotPassword,ForgotPasswordRequest
from utils.auth import verify_password,hash_password,create_access_token
from utils.logger import define_logger
from settings.Settings import get_settings

auth_logger=define_logger("als auth logger","logs/auth_route.log")

async def create_user(user:RegisterUser,session:AsyncSession)->RegisterUserResponse:
    try:
        #find the user

        user_query=select(users_table).where(users_table.email==user.email)
        user_resource=await session.execute(user_query)
        result=user_resource.one_or_none()
        if result is not None:
            auth_logger.info(f"user with email:{user.email} already exists")
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f"user with {user.email} already exist")
        
        user.password=hash_password(user.password)
        new_user=users_table(email=user.email,password=user.password,first_name=user.first_name,last_name=user.last_name,is_active=True)
        session.add(new_user)
        await session.commit()
        await session.refresh(new_user)
        return new_user
    
    except HTTPException:
        raise 
    except Exception as e:
        auth_logger.exception(f"an internal server error occurred while registering user:{user.email}:{str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail="An internal server error occurred while registering a user")

async def login_user(user:Annotated[OAuth2PasswordRequestForm,Depends()],session:AsyncSession):
    try:
        print("print the user trying to login")
        print(user)
        login_query=select(users_table).where(users_table.email==user.username)
        logged_in_user=await session.execute(login_query)
        
        result=logged_in_user.one_or_none()
        print("print the user found")
        print(result)
        if result is not None:
            auth_logger.info(f"user with:{user.username} does not exist")
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail=f"Invalid credentials")
        if not verify_password(user.password,result.password):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail=f"Invalid credentials")
        
        access_token_expires=timedelta(minutes=get_settings().ACCESS_TOKEN_EXPIRES_MINUTES)
        token=create_access_token(data={'user_id':login_user.id},expires_delta=access_token_expires)
         #return the token
        auth_logger.info(f"username:{user.username} successfully logged in")
        return Token(access_token=token,token_type='Bearer')

    except HTTPException:
        raise

    except Exception as e:
        auth_logger.exception(f"An internal server error occured while logging user:{user.username}:{str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail=f"An internal server error occurred while logging in user")


async def forgot_password(data:ForgotPasswordRequest,session:AsyncSession):
    try:
        #find the user from the database
        user_query=await session.execute(select(users_table).where(users_table.email==data.email))
        result=user_query.one_or_none()

        if result is None:
            auth_logger.info(f"user with:{data.email} tried to reset password")
            raise HTTPException(status_code=status.HTTP_202_ACCEPTED,detail=f"An email will be sent with reset details")
        
        return True
    except HTTPException:
        raise

    except Exception as e:
        auth_logger.exception(f"An exception occurred while resetting a password:{str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail=f"An internal server errror occurred while resetting a password")