from fastapi import APIRouter,Depends,status,HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import Session,select
from typing import Annotated
from datetime import timedelta
from models.users import users_table
from schemas.auth import LoginUser,RegisterUser,RegisterUserResponse,ForgotPassword,Token,GetUserResponse
from utils.auth import verify_password,hash_password,create_access_token,get_current_active_user
from settings.Settings import get_settings
from database.database import get_session

auth_router=APIRouter(tags=["Authentication"],prefix="/auth")

# register response model after database integration

@auth_router.post("/register",status_code=status.HTTP_201_CREATED,response_model=RegisterUserResponse,description="Register user to the als by providing email,password, and full name")

async def register_user(user:RegisterUser,session:Session=Depends(get_session)):
    #verify if the user exist
    user_exists=session.exec(select(users_table).where(users_table.email==user.email)).first()
    #return an error if the user does not exist already
    if not user_exists==None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail=f"user with email:{user.email} already exists")
    #hash the password before storing it
    user.password=hash_password(user.password)
    #serialize the data before committing
    new_user=users_table(email=user.email,password=user.password,first_name=user.first_name,last_name=user.last_name,is_active=True)
    
    if not new_user:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail=f"a server error occurred while creating user:{user.full_name}")
    
    #add the new user to the session object
    session.add(new_user)
    #commit the new user to the database
    session.commit()
    #refresh to get the auto-generated id and default values
    session.refresh(new_user)
    #return the registered user
    return new_user

@auth_router.post("/login",status_code=status.HTTP_200_OK,response_model=Token,description="Login to the als by providing a password and email")

async def login_user(user:Annotated[OAuth2PasswordRequestForm,Depends()],session:Session=Depends(get_session)):
    #index on email
    #find the user using the email 
    
    login_user=session.exec(select(users_table).where(users_table.email==user.username)).first()
    #return an error if the user is not found
    
    if not login_user.email == user.username:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail="Invalid Credentials")
    #verify the password and return an error if the password is wrong
    if not verify_password(user.password,login_user.password):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail="Invalid Credentials")
    #set the token expiration time
    access_token_expires=timedelta(minutes=get_settings().ACCESS_TOKEN_EXPIRES_MINUTES)
    #generate the access token
    token=create_access_token(data={'user_id':login_user.id},expires_delta=access_token_expires)
    #return the token
    return Token(access_token=token,token_type='Bearer')

#reset password
@auth_router.post("/forgot-password",response_model=RegisterUserResponse,description="Please provide your email and new password to reset your password")
async def forgot_password(data:ForgotPassword,session:Session=Depends(get_session)):
    #find the user resource using the email
    user=session.exec(select(users_table).where(users_table.email==data.email)).first()
    #return an error if the user does not exist
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f"user with email:{data.email} does not exist")
    
    #if the email exist send an OTP to the email provided and delay the system for 120 seconds
    

    #else the user does not exist than show the necessary response

    # find the user using the otp than hash the password and store it again

    #wait for verification

    #hash the new password
    user.password=hash_password(data.new_password)
    #save the new password
    session.add(user)
    #commit the user
    session.commit()
    #refresh the session object
    session.refresh(user)
    #return the success message
    return user

#get current user and build proper authentication

@auth_router.get("/user",response_model=GetUserResponse)
async def get_the_current_user(user=Depends(get_current_active_user)):
    return user
