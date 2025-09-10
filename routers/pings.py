from fastapi import APIRouter,status,HTTPException
from models.pings import pings_table
from sqlmodel import SQLModel,select

ping_router=APIRouter(tags=["Pings Endpoints"],prefix="/pings")

#get pings 
@ping_router.get("",description="Get All Pings")
async def get_pings():
    return {"message":"get pings"}
#send pings
@ping_router.post("/service",description="Send Pings")
async def send_pings():
    return {"message":"send pings to another service"}
#get specific pings
