from fastapi import APIRouter,status,HTTPException,UploadFile,File
from models.pings import pings_tbl
import pandas as pd
from sqlmodel import SQLModel,select
from utils.pings import send_pings_to_dedago
from utils.logger import define_logger


ping_router=APIRouter(tags=["Pings Endpoints"],prefix="/pings")

pings_logger=define_logger("als pings logs","logs/pings.log")

#get submit pings to dedago
@ping_router.post("submit-pings",description="Get All Pings")

async def submit_pings_to_dedago(file:UploadFile=File(...)):
    try:
        try:
            file_read=await file.read()
            df=pd.DataFrame(file_read.splitlines())
            list_contents=df.values.tolist()

            numbers=[]

            for list in list_contents:
                #potential hazard
                numbers.append(list[0].decode)
            send_numbers=send_pings_to_dedago(numbers)

            if send_numbers.status_code!=200:
                pings_logger.error(f"error occurred sending ping to dedago")
                raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail=f"ping submission failed:{send_numbers.response.json()},status code:{send_numbers.status_cdoe}")
            
            return {
                "Count":len(numbers),
                "List":numbers
            }
        except Exception as e:
            pings_logger.critical(f"error in reading pings file:{e}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail=f"Error when reading file:{file.filename}")
        
    except Exception as e:
        return {"message":f"error:{e}"}
    
#send pings
@ping_router.post("/service",description="Send Pings")
async def send_pings():
    return {"message":"send pings to another service"}
#get specific pings
