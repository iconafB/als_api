
from fastapi import APIRouter,Query,UploadFile,File,Depends,HTTPException,status
from sqlmodel import Session,select
from typing import List
from utils.load_als_service import get_loader_als_loader_service,Load_ALS_Class

load_als_router=APIRouter(tags=["Load The ALS"])

#take care of the campaign code
@load_als_router.post("/",status_code=status.HTTP_201_CREATED)
#leads may come in a spread sheet react to that
async def load_data_to_the_als(branch:str=Query(...,description="Please provide the branch code/name"),camp_code:str=Query(...,description="Please provide the campaign code"),list_name:str=Query(description="Please provide the list name"),leads:UploadFile=File(...,description="please provide a file with leads"),get_loader_data:Load_ALS_Class=Depends(get_loader_als_loader_service)):
    #fetch the token using the branch name from the tokens table

    #check the if the file extension is correct, don't upload emojis respect yourself
    if not leads.filename.endswith(".csv",".xlsx"):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="Only csv files allowed to be uploaded")
    token=get_loader_data.get_token(branch)
    if token == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f"branch:{branch} has no token, can't load to this branch")
    #set the payload to send to dedago
    payload_data=get_loader_data.set_payload(branch,camp_code,leads,list_name)
    #send data to ss dedago
    response_data=get_loader_data.send_data_to_dedago(token,payload_data)
    #continuously check the health of ss dedago
    if response_data.status_code !=200:
        
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail=f"error occurred while submitting data to dedago")
    
    if response_data.status_code==200 and response_data.json()['list_id']!=0:

        response=response_data.json()
        
        list_id=response['list_id']

    return {"list_id":list_id}

