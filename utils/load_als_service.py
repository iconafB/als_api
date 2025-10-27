from fastapi import File,UploadFile,Depends,HTTPException,status
from sqlmodel import Session,select,update
from models.leads import lead_history_tbl
from models.campaigns import dedupe_campaigns_tbl
from database.database import get_session
from datetime import datetime,time
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from models.dma_service import dma_validation_data,dma_audit_id_table,list_tracker_table
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
    # Send optins to dedago and get a list_id

    def scan_table_and_call_send_to_dedago(self,session:Session=Depends(get_session)):

        #scan the audit id table,is_processed maining that has the audit id been sent for dma and fetched
        audit_id_data_query=select(dma_audit_id_table).where((dma_audit_id_table.is_processed==True) & (dma_audit_id_table.is_sent_to_dedago==False))
        
        fetched_data=session.exec(audit_id_data_query).all()

        if len(fetched_data)==0:
            #all audit ids have been processed
            load_als_logger.info('All audit ids have been procesed')
            return
        
        #you now have audit ids that are not processed
        #for each audit id fetch the all documents that are unprocessed meaning not sent to dedago
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
            #prepare a list to send to dedago
            dedago_keys=["vendor_lead_code","first_name","last_name","phone_number"]

            #set up the dedago list of dictionaries
            dedago_list=[{"vendor_lead_code":record.id,"first_name":record.fore_name,"last_name":record.last_name,"phone_number":record.cell} for record in dma_records]

            #build list that will be passed to a function to update dedupe campaigns

            list_update_info_tbl_for_dedupe_campaigns=[data['vendor_lead_code'] for data in dedago_list]

            #
            self.data_loader_to_the_info_table(list_update_info_tbl_for_dedupe_campaigns)

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
            payload_response=self.set_payload(branch,dedago_list,camp_code,list_name)
            #get a token using a branch name to send to dedago
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
                #prep the list to send to dedago
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
                # I need the data from dma to build this list on opted out cell numbers
                # you

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
                    for record in dma_records
                ]

                
                self.load_leads_to_als_request(list_to_insert_to_lead_history)

                #set today's date when 
                
            #pass the list to the load_leads_to_als_request, now you need a rule name for that

        return  
 
    #this should be a background task and an asynchronous method to prevent hogging the event loop

    async def load_leads_to_als_request(insert:List[tuple],session:Session=Depends(get_session)):
        
        try:
            #prepare the list to be used to update the lead_history_table
            #fetch the opted_out field record from dma_validation table than from there insert
            insert_sql=""""
                    INSERT INTO lead_history_tbl(cell,camp_code,date_used,list_name,list_id,load_type,rule_code) VALUES(:cell,:camp_code,:date_used,:list_name,:list_id,:load_type,:rule_code)
                        """
            
            params=[
                {
                   "cell":r[0],
                   "camp_code":r[1],
                   "date_used":r[2],
                   "list_name":r[3],
                   "list_id":r[4],
                   "load_type":r[5],
                   "rule_code":r[6] 
                }
                for r in insert
            ]

            session.exec(text(insert_sql),params)
            session.commit()
            session.close()
            load_als_logger.info(f"inserted {len(insert)} records on lead_history_tbl table")
            return
        
        except Exception as e:
            load_als_logger.error(f"{str(e)}")
            session.rollback()
            #raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail=f"an error occurred while inserting data into the lead history table")
            return



    def update_date_leads_last_used_on_info_tbl(records:list[tuple],session:Session=Depends(get_session)):
        try:
            todays_date=datetime.today().strftime("%Y-%m-%d")

            upsert_sql = """
            INSERT INTO info_tbl(cell, last_used) 
                VALUES (:cell, :last_used) 
                ON CONFLICT(cell) 
                DO UPDATE SET last_used = EXCLUDED.last_used 
                WHERE info_tbl.cell = EXCLUDED.cell
            """
            #potential problems
            params=[{"cell":r[0],"last_used":r[1]} for r in records]

            session.exec(text(upsert_sql),params)
            session.commit()
            session.close()
            load_als_logger.info(f"update {len(records)} records on the information table")
            return 
        
        except SQLAlchemyError as e:
            load_als_logger.error(f"transaction rolled back:{e}")
            session.rollback()
            return
        
    
    def update_leads_on_the_info_table_for_dedupe_campaigns(records:list[tuple],session:Session=Depends(get_session)):
        try:

            return True
        except SQLAlchemyError as e:
            load_als_logger.error(f"{str(e)}")
            session.rollback()
            return False


    #this will be for dedupe campaign    
    def load_leads_to_als_Request_Deddupe_Campaigns(leads_list:List,feeds_list:List,camp_code:str,session:Session=Depends(get_master_db_session)):

        try:
            if len(leads_list)<10000:
                return True
            #else process here
            return True
        except Exception as e:
            load_als_logger.critical(f"{str(e)}")
            return False
    
    
    #insert data into the information table and update so that they are not used for next 30 days

    #this should be an asynchronous method
    def data_loader_to_the_info_table(self,insert:List,session:Session=Depends(get_session),batch_size:int=10000,batch_threshold:int=5000):
        try:
            #find the dedupe campaign   

            #update the info_table when the extra info is 
            if not insert:
                return
            
            db_list=tuple(insert)


            stmt = text("UPDATE info_tbl SET extra_info = null WHERE id = ANY(:ids)")
            campaign_dedupe_update=text("UPDATE campaign_dedupe SET status=U WHERE id =ANY(:ids)")

            if len(db_list)>=batch_threshold:

                load_als_logger.info(f"updating info_tbl with {len(db_list)}")

                for i in range(0,len(db_list),batch_size):

                    batch=db_list[i:i+batch_size]
                    session.exec(stmt,{"ids":batch})
                    session.exec(campaign_dedupe_update,{"ids":batch})

            else:
                    load_als_logger.info(f"updating info_tbl with:{len(db_list)}")
                    session.exec(stmt,{"ids":db_list})
                    session.exec(campaign_dedupe_update,{"ids":db_list})
            
            session.commit()

            return 
        
        except Exception as e:
            load_als_logger.error(f"{str(e)}")
            return 
    
    def update_campaign_dedupes_table(self,list_to_update:List,session:Session=Depends(get_session)):
        try:
            return True
        except Exception as e:
            return False

def get_loader_als_loader_service()->Load_ALS_Class:

    return Load_ALS_Class()

