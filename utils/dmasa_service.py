from fastapi import HTTPException,Depends,BackgroundTasks,status
from sqlalchemy import update,text
from sqlmodel import Session,select
import requests
import json
from settings.Settings import get_settings
#I don't remember why is this here
import urllib3
from utils.load_als_service import get_loader_als_loader_service

import pandas as pd
#update the audit id on this table to avoid processing already used ids
from models.dma_service import dma_audit_id_table
from models.dma_service import dma_validation_data
from database.database import get_session
from utils.logger import define_logger

dma_logger=define_logger("dmasa ","logs/dma.log")


#For all the methods use try catch nigga, shitty code
class DMA_Class():
    
    def __init__(self):
        self.dmasa_api_key=get_settings().dmasa_api_key
        self.dmasa_member_id=get_settings().dmasa_member_id
        self.check_credits_dmasa_url=get_settings().check_credits_dmasa_url
        self.notification_email=get_settings().notification_email
        self.submit_dedupes_dmasa_url=get_settings().upload_dmasa_url
        self.read_dmasa_dedupe_status=get_settings().read_dmasa_dedupe_status
        self.read_dedupe_output_url=get_settings().read_dmasa_output_url

    #ping the dmasa api to check if it's everytime before calling any of these methods
    #This run every morning and provide updates on the platform and send an email to somewhere when the credits run out
    def check_credits(self):
        # we need verification certificate for production environment
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning) 
        base_url=self.check_credits_dmasa_url

        params_values={
            'API_Key':self.dmasa_api_key,
            'MemberID':self.dmasa_member_id
        }
        
        credits_response=requests.get(url=base_url,params=params_values,verify=False,timeout=10)
        
        return credits_response
    
    #extract values from a file 
    def read_file(file_path):

        try:
            if file_path.endswith('.csv'):
                df=pd.read_csv(file_path)
            elif file_path.endswith('.xlsx'):
                df=pd.read_excel(file_path)
            else:
                print("Unsupported file type")
                return None
        except FileNotFoundError:
            return None
        return df
    
    def extract_data(df,extractedType):

        if df is None:
            return None
        if extractedType=='id':
            if 'id' in df.columns:
                return "\n".joins(df['id'].astype(str))
            else:
                print("Error: id and phone number column not found")
                return None
        elif extractedType == 'cell_number':
            if 'cell number' in df.columns:
                return "\n".joins(df['cell number']).astype(str)
            else:
                print("error: cell number column not found")
                return None
        elif extractedType == 'both':
            if 'id' in df.columns and 'cell number' in df.columns:
                extracted_dict={}
                for index,row in df.iterrows():
                    extracted_dict[str(row('id'))]=str(row['cell number'])
                return extracted_dict
            else:
                print("Error: Required columns id and cell number not found")
                return None
        else:
            print("Invalid extracted type: Choose id, cell number or both")
            return None
        
    #this should be a straight route
    def upload_data_for_dedupe(self,data):
        #convert the data to numbers which is a list of numbers
        #construct the payload using the above methods
        payload={
            "API_KEY":self.dmasa_api_key,
            "Data":data,
            "DataType":'C',
            "MemberID":self.dmasa_member_id,
            "NotificationEmail":self.notification_email
        }
        
        headers={
            'Content-Type':'application/json'
        }

        response=requests.post('POST',headers=headers,url=self.submit_dedupes_dmasa_url,data=json.dump(payload),verify=False,timeout=54000)
        
        return response        

    #Poll this nonsense and provide an update when the dedupe is ready

    def check_dedupe_status(self,audit_id,records):
        #define the url for checking the status of dma
        #url=self.read_dmasa_dedupe_status + self.dmasa_api_key + '&MemberID='+self.dmasa_member_id + '&DedupeAuditId='+ audit_id + '&RecordsProcessed'+records
        params_dict={}
        
        # params_values={
        #     'API_Key':self.dmasa_api_key,
        #     'MemberID':self.dmasa_member_id,
        #     'DedupeAuditId':audit_id,
        #     'RecordsProcessed':records
        #     }
        
        params_dict['API_Key']=self.dmasa_api_key
        params_dict['MemberID']=self.dmasa_member_id
        params_dict['DedupeAuditId']=audit_id
        params_dict['RecordsProcessed']=records

        response=requests.get(url=self.read_dmasa_dedupe_status,params=params_dict,verify=False,timeout=10)
        #check the dedupe status if it's download ready process the file
        
        return response
    
    #you need to poll this nonsense
    def read_dedupe_output(self,audit_id):
        #This is nonsense
        try:
            #try statement
            #dmasa_output_url=self.read_dedupe_output_url + self.dmasa_member_id + '&API_Key'+ self.dmasa_api_key + '&AuditId'+ audit_id
            
            base_url=self.read_dedupe_output_url
            params_dict={}

            # params_values={
            #     "DedupeAuditId":audit_id,
            #     "MemberID":self.dmasa_member_id,
            #     "API_Key":self.dmasa_api_key
            # }
            
            params_dict['DedupeAuditId']=audit_id
            params_dict['MemberID']=self.dmasa_member_id
            params_dict['API_Key']=self.dmasa_api_key

            response_output=requests.get(url=base_url,params=params_dict,verify=False,timeout=10)
            
            return response_output
        
        except Exception as e:
            dma_logger.error(f"{str(e)}")
            print(e)
            return {"message":"an exception occurred"}
    

    def fetch_audit_ids_from_the_db(self,session:Session=Depends(get_session)):

        
        try:
            #read data from the audit id table where the values read are not yet processed
            audit_id_stmt=select(dma_audit_id_table.audit_id,dma_audit_id_table.number_of_records).where(dma_audit_id_table.is_processed==False)
            #audit id results
            results=session.exec(audit_id_stmt).all()
            #check if this for loop works fine
            audit_ids=[(audit_id,number_of_records) for audit_id,number_of_records in results]

            for audit_id ,number_of_records in audit_ids:

                status_response=self.check_status_and_return_records(audit_id,number_of_records)

                #check the status returned from 
                
                if isinstance(status_response,list):
                    #You now have the numbers to processed with zeros append,no update the audit id table
                    #fetch the audit id to update
                    update_audit_stmt=select(dma_audit_id_table).where(dma_audit_id_table.audit_id==audit_id)
                    
                    update_session_result=session.exec(update_audit_stmt).first()
                    
                    if update_session_result==None:
                        dma_logger.error('Audit ID not found')
                        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Audit ID does not exist")
                    #update the status to True signifying that the audit id table entry has been
                    
                    update_session_result.is_processed=True
                    session.add(update_session_result)
                    session.commit()

                    dma_logger.info(f"dedupe with audit id:{audit_id} retrieved from dmasa")

                    #remove the optouts from the list

                    no_optouts=[value for value in status_response if value['OptedOut']=='True']

                    return no_optouts
                
                elif status_response==False:
                    continue

                elif status_response=='Download Not Ready' or status_response=='Dedupe Not Complete' or status_response=='Dedupe Incomplete':
                    continue
                else:
                    continue
            #analyze this returned value
            return True
        
        except Exception as e:
            session.rollback()
            dma_logger.error(f"{str(e)}")



    def check_status_and_return_records(self,audit_id,number_of_records,session:Session=Depends(get_session)):
        #check dedupe status
        status_response=self.check_dedupe_status(audit_id,number_of_records)
        #
        if status_response.json()['Status']=='Download Ready' and status_response.status_code==200 and len(status_response.json()['Errors'])==0:
            
            #Fetch the audit id table ,using the given audit id to update the is processed flag to true meaning records for that audit id have been processed

            audit_id_table_query=select(dma_audit_id_table).where(dma_audit_id_table.audit_id==audit_id)
            #fetch 
            execute_audit_id_table=session.exec(audit_id_table_query).first()
            #check if it exist and log appropriately. needs attention 
            if execute_audit_id_table==None:
                dma_logger.info(f"Audit ID:{audit_id} does not exist,no processing can be performed")
                # raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f"Audit ID:{audit_id} does not exist,no processing can be peformed")
                return
            
            #update the is_processed flag from dma_audit_table table
            execute_audit_id_table.is_processed=True
            #add it to the session object and commit the changes
            session.add(execute_audit_id_table)
            session.commit()
            #read the dma output for the dedupe 
            
            records_response=self.read_dedupe_output(audit_id)

            if len(records_response.json()['Errors'])!=0:
                print("return the errors returned from dmasa")
                dma_logger.info(records_response.json()['Errors'])
                #record errors occurred on the dma
                for error_record in len(records_response.json()['Errors']):
                    dma_logger.error(f"{error_record}")
                return
            
            #take the list of actual records from the dmasa api endpoint
            dedupe_records=records_response.json()['ReadOutput']
            # #append zeros on the cell numbers
            # cellphone_numbers_map={entry['DataEntry'] for entry in dedupe_records}
            # cellphone_numbers_map[1]['DataEntry']="0"+cellphone_numbers_map[1]['DataEntry']
            
            #append zero on all the numbers from dmasa,slow find another approach

            for record in dedupe_records:
                print("records retrieved from dmasa")
                #append zeros on the numbers returned from dmasa
                record['DataEntry'] = '0'+ record['DataEntry']

                #cell numbers only, needs to be 

            #unnecessary database call/query
            
            #make a database call to fetch information that was previously stored with the same audit id and is not processed
            submitted_records_query=select(dma_validation_data).where((dma_validation_data.audit_id==audit_id) and (dma_validation_data.is_processed==False))
            
            #execute the query to fetch the list of tuples from the db
            submitted_records=session.exec(submitted_records_query).all()
            #do the comparison here than submit to dedago and update the status
            
            # deduped_list_numbers['DataEntry']=

            if submitted_records==None:
                dma_logger.error(f'error fetching data from table dma_validation_data with audit id:{audit_id}')
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f"error fetching data from after deduping")
            
            #update and commit the is_processed flag to true on dma_validation_data table
            session.exec(update(dma_validation_data).where((dma_validation_data.is_processed==False) & (dma_validation_data.audit_id==audit_id)).values(is_processed=True))
            #I can propagate these changes from the audit_id_table, and use a direct sql query for faster updates
            session.commit()

            #filter optedouts which can be done by updating the db stored values, the opted out are
            # run this for larger loads 
            if len(dedupe_records)>10000:
                #build a new list 
                opted_out_true=[e for e in dedupe_records if e.get("OptedOut") is True]

                #return if there are not opted out

                if not opted_out_true:
                    print("No opted outs")
                    dma_logger.info(f"No records to process for audit id:{audit_id}")
                    return
                
                session.exec(text(""" CREATE TEMP TABLE temp_opted_out_table(id TEXT,opted_out BOOLEAN) ON COMMIT DROP;"""))

                session.exec(text("INSERT INTO temp_opted_out_table (id,opted_out) VALUES(:id,:opted_out)"),opted_out_true)

                session.exec(text(""" UPDATE dma_validation_data AS d
                                    SET opted_out=TRUE
                                    FROM temp_opted_out_table AS t
                                    WHERE d.id=t.id
                                    AND t.opted_out=TRUE
                                    AND d.opted_out=FALSE;
                                   """))
                
                session.commit()
                session.close()

                dma_logger.info(f"updated length:{len(opted_out_true)} records where opted out is TRUE")

                print(f"updated length:{len(opted_out_true)} records where opted out is TRUE")

                return
            #run this for smaller loads

            if len(dedupe_records)<10000:
                #use cell numbers to filter not id

                small_opted_out_list=[record["id"] for record in dedupe_records if record.get("OptedOut") is True]
                
                if not small_opted_out_list:

                    print("No records to updates")
                    dma_logger.info("No records to updates no opted outs")
                    return 
                #needs attention 

                dedupe_stmt=(update(dma_validation_data).where(dma_validation_data.id.in_(small_opted_out_list)).where(dma_validation_data.opted_out==False).values(opted_out=True))
                small_dedupe_result=session.exec(dedupe_stmt)
                session.commit()
                #check the following maybe faulty
                results_stmt=small_dedupe_result.rowcount()
                dma_logger.info(f"Updated records:{results_stmt}")
                #
                return 
            # don't fetch the data but update the is_processed flag  to True for processed document  
            #compare the returned data from dmasa and from dma_validation table

            #list of tuples from the db submitted_records and list of dictionaries from dmasa based on the number of optsout

            #call a function that will run as a background task

            return dedupe_records
        
        elif status_response.status_code==200 and status_response.json()['Status']!='Download Ready' and len(status_response.json()['Errors'])==0:
            print("print download is not ready")
            #return the status string
            return status_response.json()['Status']
        else:
            return False
        
    #method to run updates on the is_processed flag on the dma_validation table


def get_dmasa_service():

    return DMA_Class()


