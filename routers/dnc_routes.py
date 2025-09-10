from fastapi import APIRouter

dnc_router=APIRouter(tags=["DNC Enpoints"],prefix="/dnc")

@dnc_router.post("/add-blacklist",description="Add a list of numbers to blacklist locally")

async def add_to_blacklist():
    
    return {"message":"a text file of numbers is added to the blacklist"}

