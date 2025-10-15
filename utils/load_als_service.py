from fastapi import File,UploadFile,Depends,HTTPException,status
from sqlmodel import Session,select,update
from models.leads import leads_history_table
from database.database import get_session
from datetime import datetime,time
from sqlalchemy import text
from models.dma_service import dma_validation_data,dma_audit_id_table
from typing import List
import requests
import json
from settings.Settings import get_settings
from utils.logger import define_logger
from database.master_db_connect import get_master_db_session
#fetch the token based on the provided branch
#initialize
#return the token

load_als_logger=define_logger("als load als request","logs/load_als_request")

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
        
        #from the audit id table fetch the all the audit ids

        #lookup the dma_validation table for opted out to send to dedago
        #opted_out_records=select(dma_validation_data).where()
        #the data contains campaign code and branch code, extract the branch and load the token from the .env file

        #the token will be loaded from the env file based on branch

        #send record to dedago when they are ready

        #build the list to send to dedago

        #dedago_list=[]

        dedago_headers={
                "Content-Type":"application/json",
                "Accept":"application/json"
            }
        
        dedago_headers["Authorization"]=token

        #send sh** to dedago
        dedago_response=requests.post(url=get_settings().dedago_url,data=json.dumps(payload),headers=dedago_headers,timeout=20)  
        #we will get the list id only and the status code
        return dedago_response 
    
    #this method with scan the audit_id_table
    # 
    def scan_table_and_call_send_to_dedago(self,session:Session=Depends(get_session)):
        #fetch the audit ids dma_audit_id_table
        #fetch processed audit id
        processed_audit_query=select(dma_audit_id_table).where(dma_audit_id_table.is_processed==True)

        processed_audit_ids=session.exec(processed_audit_query).all()
        
        if processed_audit_ids==None:
            print("all audit ids have been processed")
            return
        
        for record in processed_audit_ids:
            
            print("print record")
            
        records_query=select(dma_validation_data).where(dma_validation_data.is_processed==True)
        
        records=session.exec(records_query).all()

        return True 
    
    def get_token_branch(records:List):

        return 
    
    def load_leads_to_als_request(leads:List,insert:List[dict],camp_code:str,session:Session=Depends(get_session)):
        
        try:
            #insert the records into the leads history table
            new_records=[leads_history_table(**data) for data in leads]

            #add all the documents into
            session.add_all(new_records)
            session.commit()
            
            todaysdate=datetime.today().strftime("%Y-%m-%d")

            new_list=[]

            for lead in leads:
                #append phone number on the new list
                new_list.append(lead['phone_number'])

            time1=time()

            #update_raw_sql_statement=text("""INSERT INTO info_tbl(cell, last_used) VALUES (%s, %s) ON CONFLICT(cell) DO UPDATE SET last_used = EXCLUDED.last_used WHERE info_tbl.cell = EXCLUDED.cell""")
            update_raw_sql_statement = text(
                        """
                        INSERT INTO info_tbl(cell, last_used) 
                        VALUES (:cell_val, :last_used_val) 
                        ON CONFLICT(cell) DO UPDATE 
                        SET last_used = EXCLUDED.last_used
                        WHERE info_tbl.cell = EXCLUDED.cell;
                        """
                        )

            session.exec(update_raw_sql_statement,params={"cell_val":cell_val,"last_used":last_used_val})

            session.commit()



        except Exception as e:
            print("print the exception")
            load_als_logger.error(f"{str(e)}")
            session.rollback()
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail=f"error while loading leads to the als")
        
    def load_leads_to_als_Request(session:Session=Depends(get_master_db_session)):

        try:

            return True
        except Exception as e:
            load_als_logger.critical(f"{str(e)}")
            return False


def get_loader_als_loader_service()->Load_ALS_Class:

    return Load_ALS_Class()

