from fastapi import File,UploadFile,Depends
from sqlmodel import Session,select
from models.leads import leads_history_table
from database.database import get_session
from typing import List
import requests
import json
from settings.Settings import get_settings

#fetch the token based on the provided branch
#initialize
#return the token

class Load_ALS_Class():
    
    def get_token(self,branch:str):
        if branch=='INVTNTDBN':
            return get_settings().INVTNTDBN_TOKEN
        elif branch=='P3':
            return get_settings().P3_TOKEN
        elif branch=='HQ':
            return get_settings().HQ_TOKEN
        else:
            return get_settings().YORK_TOKEN
    
    #you need to properly set this up
    def set_payload(self,branch:str,leads:UploadFile,camp_code:str,list_name:str):
        
        #set the list id inside this method
        status_list= ["BLACKL", "DEC", "INV", "LB", "NDNE", "NEW", "NI", "PTH", "QTR", "SALE", "SENT"]
        payload={}
        payload['campaign_id']=camp_code
        payload['dedup']='dupcamp'
        payload['list_method']='NEW'
        payload['status']=status_list
        payload['active']=False
        payload['days']='30'
        payload['list_name']=list_name
        payload['leads']=leads

        if branch=="INVNTDBN":
            payload['custom_list_id']=[100,108]
        elif branch=="P3":
            payload['custom_list_id']=[106,108]

        elif branch=='HQ':
            payload['custom_list_id']=[100,108]
        else:
            payload['custom_list_id']=[100,112]
        
        return payload

    def send_data_to_dedago(self,token:str,payload:dict):

        dedago_headers={
                "Content-Type":"application/json",
                "Accept":"application/json"
            }
        
        dedago_headers["Authorization"]=token
        #send sh** to dedago
        dedago_response=requests.post(url=get_settings().dedago_url,data=json.dumps(payload),headers=dedago_headers,timeout=20)  
        #we will get the list id only and the status code
        return dedago_response 
    
    def load_leads_to_als_request(leads:List,insert:List[dict],camp_code:str,session:Session=Depends(get_session)):
        
        try:
            new_records=[leads_history_table(**data) for data in leads]
            session.add_all(new_records)
            session.commit()
            return True
        except Exception as e:
            print("print the exception")
            print(e)
            return False


def get_loader_als_loader_service()->Load_ALS_Class:
    return Load_ALS_Class()

