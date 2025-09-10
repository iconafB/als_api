

from pydantic import BaseModel,EmailStr

from sqlmodel import SQLModel,Field

class RegisterUser(SQLModel):
    email:EmailStr=Field(min_length=3,max_length=100)
    password:str=Field(max_length=40)
    full_name:str=Field(max_length=100)


class RegisterUserResponse(SQLModel):
    id:int
    full_name:str
    email:EmailStr

class ForgotPassword(BaseModel):
    email:EmailStr
    new_password:str

class LoginUser(BaseModel):
    email:EmailStr
    password:str


class Token(BaseModel):
    access_token:str
    token_type:str

class TokenData(BaseModel):
    username:int | None=None
    