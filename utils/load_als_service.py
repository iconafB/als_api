from fastapi import File,UploadFile,Depends,HTTPException,status
from sqlmodel import Session,select,update
from models.leads import lead_history_table
from database.database import get_session
from datetime import datetime,time
from sqlalchemy import text
from models.dma_service import dma_validation_data,dma_audit_id_table,list_tracker_table
from models.leads import lead_history_table

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
    def set_payload(self,branch:str,leads:List,camp_code:str,list_name:str):

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
        #this is what you will dump on the send to dedago
        return payload

    #Send data to dedago to get a list id

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
    

    #this method will scan if the audit id table has been processed or not 

    #this method with scan the audit_id_table
    # Send optins to dedago

    def scan_table_and_call_send_to_dedago(self,session:Session=Depends(get_session)):
        
        #scan the audit id table
        audit_id_data_query=select(dma_audit_id_table).where((dma_audit_id_table.is_processed==False) & (dma_audit_id_table.is_sent_to_dedago==False))
        
        fetched_data=session.exec(audit_id_data_query).all()

        if len(fetched_data)==0:
            #all audit ids have been processed
            load_als_logger.info('All audit ids have been procesed')
            return
        
        #you now have audit ids that are not processed
        #for each audit id fetch the all documents that are unprocessed 
        for record in fetched_data:

            print("print the audit id")
            print(record.audit_id)
            #record have been processed and opted in
            #You need to 
            dma_records_query=select(dma_validation_data.id,dma_validation_data.fore_name,dma_validation_data.last_name,dma_validation_data.cell,dma_validation_data.branch,dma_validation_data.camp_code).where((dma_validation_data.audit_id==record.audit_id) & (dma_validation_data.is_processed==True) & (dma_validation_data.opted_out==False))
            #execute the query, now I have all the records I need to send to dedago than update dma_audit_id_table is_sent_to_dedago flag

            dma_records=session.exec(dma_records_query).all()
            #get the branch to load the correct token and campaign code to send to dedago

            branch=dma_records[0][4] if dma_records else None
            #campaign code
            camp_code=dma_records[0][5] if dma_records else None
            #list name query using the audit id
            list_name_query=select(list_tracker_table.list_name).where(list_tracker_table.audit_id==record.audit_id)
            #execute the query
            list_name=session.exec(list_name_query).first()

            if not list_name:
                load_als_logger.info(f"list with audit id:{record.audit_id} has no list name")
                #analyze if you have to raise an exception or just log and continue
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f"list that matches audit id:{record.audit_id} does not exist")
            
            #remove the branch and campaign code columns
            trimmed_records=[record[:4] for record in dma_records]
            #prepare a list to send to 
            dedago_keys=["vendor_lead_code","first_name","last_name","cell"]
            #prep the dedago list
            #list to send to dedago
            combined_dedago_list=[]

            for record in trimmed_records:
                #convert the list of objects to a dictionary
                record_dict=record.dict()
                # new_dict is  
                new_dict={}

                for key,value in record_dict.items():
                    
                    new_dict[key]=value
                    if key=="first_name":
                        new_dict["list_name"]=list_name

                combined_dedago_list.append(new_dict)
            

            dedago_list=[dict(zip(dedago_keys,value)) for value in trimmed_records]
            #today's side

            todays_date=datetime.today().strftime("%Y-%m-%d")

            #call the set_payload method
            payload_response=self.set_payload(branch,combined_dedago_list,camp_code,list_name)
            #get a token using a branch name 
            token=self.get_token(branch)
            #dedago returns a list id
            dedago_response=self.send_data_to_dedago(token,payload_response)

            #the list that is sent to dedago is the that is used to update the lead history table
            
            if dedago_response['status_code']!=200:
                # loading error response
                load_als_logger.error("Error occurred while fetching list id from dedago")
                return
            
            #update the
            if dedago_response['status_code']==200 and dedago_response['list_id']!=None:
                
                dedago_list_id=dedago_response['list_id']

                #update the list tracker table find it using the audit id and list name
                list_tracker_query=select(list_tracker_table).where(list_tracker_table.list_name==list_name).where(list_tracker_table.audit_id==record.audit_id)
                
                list_tracker_entry=session.exec(list_tracker_query).first()

                if not list_tracker_entry:
                    load_als_logger.info(f"List with list name:{list_name} with audit id:{record.audit_id} does not exist on the list tracker table")
                    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f"List with list name:{list_name} with audit id:{record.audit_id} does not exist on the list tracker table")
                
                list_tracker_entry.list_id=dedago_list_id

                new_list_name=list_tracker_entry.list_name

                load_type='AUTOLOAD'

                list_id=dedago_list_id

                #try to update the list id and 
                session.add(list_tracker_entry)
                #commit the list id to the list tracker table
                session.commit()

                #let's build the list that will be inserted into the lead history table
                # I need the data from dma to build this list on optedout cell numbers


                list_to_insert_to_lead_history=[
                    {
                        "cell":record.cell,
                        "camp_code":record.camp_code,
                        "date_used":todays_date,
                        "list_id":list_id,
                        "list_name":new_list_name,
                        "load_type":load_type,
                        "rule_code":record.camp_code
                    }
                    for record in insert_records
                ]

                self.load_leads_to_als_request(list_to_insert_to_lead_history)

            #pass the list to the load_leads_to_als_request, now you need a rule name for that

        return  
 
    #this should be a background task and an asynchronous method to prevent hogging the event loop

    async def load_leads_to_als_request(insert:List[dict],session:Session=Depends(get_session)):
        
        try:
            #prepare the list to be used to update the lead_history_table
            new_records=[
                lead_history_table(
                    cell=record.cell,
                    camp_code=record.camp_code,
                    date_used=record.todays_date,
                    list_id=record.list_id,
                    list_name=record.list_name,
                    load_type='AUTOLOAD',
                    rule_code=record.camp_code

                )
                for record in insert
            ]

            if len(new_records)<=100000:

                session.add(new_records)
                session.commit()
                session.close()

            #insert in batches
            batch_size=10000

            for i in range(0,len(new_records),batch_size):
                #insert the data in batch  of 10000
                batch=new_records[i:i+batch_size]
                session.add_all(batch)
                session.commit()
            
            return
        
        except Exception as e:
            load_als_logger.error(f"{str(e)}")
            session.rollback()
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail=f"error while loading leads to the als")

    #this will be for dedupe campaign    
    def load_leads_to_als_Request(leads_list:List,feeds_list:List,camp_code:str,session:Session=Depends(get_master_db_session)):

        try:
            if len(leads_list)<10000:
                return True
            #else process here
            return True
        except Exception as e:
            load_als_logger.critical(f"{str(e)}")
            return False
    
    def data_load_to_info_table():
        try:

            return True
        except Exception as e:
            load_als_logger.error(f"{str(e)}")
            return 

def get_loader_als_loader_service()->Load_ALS_Class:

    return Load_ALS_Class()

