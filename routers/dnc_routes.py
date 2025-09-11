from fastapi import APIRouter,Depends
from utils.auth import get_current_user
dnc_router=APIRouter(tags=["DNC Enpoints"],prefix="/dnc")

@dnc_router.post("/add-blacklist",description="Add a list of numbers to blacklist locally")

async def add_to_blacklist(user=Depends(get_current_user)):
    
    return {"message":"a text file of numbers is added to the blacklist"}

