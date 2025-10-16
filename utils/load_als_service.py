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

    #Send data to dedago to get a list id

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
    

    #this method will scan if the audit id table has been processed or not 

    #this method with scan the audit_id_table
    # 
    def scan_table_and_call_send_to_dedago(self,session:Session=Depends(get_session)):
        #scan the audit id table
        audit_id_data_query=select(dma_audit_id_table).where(dma_audit_id_table.is_processed==False and dma_audit_id_table.is_sent_to_dedago==False)
        
        fetched_data=session.exec(audit_id_data_query).all()

        if len(fetched_data)==0:
            #all audit ids have been processed
            load_als_logger.info('All audit ids have been procesed')
            return
        
        #you now have audit ids that are not processed
        #for each audit id fetch the all documents that are unprocessed 
        for record in fetched_data:
            print(record.audit_id)
            #
            dma_records_query=select(dma_validation_data.id,dma_validation_data.fore_name,dma_validation_data.last_name,dma_validation_data.cell,dma_validation_data.branch,dma_validation_data.camp_code).where(dma_validation_data.audit_id==record.audit_id and dma_validation_data.is_processed==True)
            #execute the query, now I have all the records I need to send to dedago than update dma_audit_id_table is_sent_to_dedago flag

            dma_records=session.exec(dma_records_query).all()
            #get the branch to load the correct token and campaign code to send to dedago

            branch=dma_records[0][4] if dma_records else None
            camp_code=dma_records[0][5] if dma_records else None

            #remove the branch and campaign code columns
            trimmed_records=[record[:4] for record in dma_records]
            #prepare a list to send to 
            dedago_keys=["vendor_lead_code","first_name","last_name","cell"]
            #dedago list

            dedago_list=[dict(zip(dedago_keys,value)) for value in trimmed_records]
            #get a token using a branch name 
            token=self.get_token(branch)

            dedago_response=self.send_data_to_dedago(token,dedago_list)

            if dedago_response.status_code!=200:
                load_als_logger.error("")

        return True 
 
    
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

