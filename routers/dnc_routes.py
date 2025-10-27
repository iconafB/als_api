from fastapi import APIRouter,Depends,HTTPException,BackgroundTasks,UploadFile,File,Query,status
import pandas as pd
import re
from utils.auth import get_current_user
from utils.logger import define_logger
from schemas.dnc_schemas import DNCNumberResponse
from utils.dnc_util import send_dnc_list_to_db

dnc_logger=define_logger("als dnc logs","logs/dnc_route.log")


dnc_router=APIRouter(tags=["DNC Enpoints"],prefix="/dnc")

@dnc_router.post("/add-blacklist",description="Add a list of numbers to blacklist locally",response_model=DNCNumberResponse)

async def add_to_blacklist(bg_tasks:BackgroundTasks,camp_code:str=Query(...,description="Add the campaign code"),file:UploadFile=File(...,description="Add File With numbers to blacklist"),user=Depends(get_current_user)):
    
    try:
        contents=await file.read()

        list_contents=pd.DataFrame(contents.splitlines()).values().tolist()

        list_to_dnc=[]
        new_list=[str(new[0],'UTF-8') for new in list_contents]

        #dnc_list=[new for new in new_list if re.match('^\d{10}$',new)]

        dnc_list=[str(item[0],'UTF-8') for item in list_contents if re.match('^\d{10}$',str(item[0],'UTF-8'))]

        # for list_content in list_contents:

        #     new=str(list_content[0],'UTF-8')

        #     if re.match('^\d{10}$',new):
        #         list_to_dnc.append(new)
        

        if len(dnc_list)>0:
            status=True
            result=str(len(dnc_list)) + 'records added to the dnc'
            bg_tasks.add_task(send_dnc_list_to_db,dnc_list,camp_code)
            #add this to the dnc using a background task
        
        else:
            status=False
            result=str(len(dnc_list)) + 'records added to the dnc'

        dnc_logger.info(f"{len(dnc_list)} numbers added to the dnc list")

        return DNCNumberResponse(status=status,message=result)
    
    except Exception as e:
        dnc_logger.error(f"{str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail=f"error reading file")



