from fastapi import APIRouter,status,Depends,HTTPException,Path,Query,BackgroundTasks,Request,Response
from sqlmodel import Session,select,or_,and_,case

from sqlalchemy import cast,text,Integer
from sqlalchemy.sql import func

import sqlalchemy as sa
import requests
from datetime import datetime,timedelta
import json
from models.campaigns import campaign_tbl
from models.leads import info_tbl
from models.dma_service import dma_audit_id_table,dma_records_table,list_tracker_table

from models.campaign_rules import rules_tbl

from models.dma_service import dma_validation_data

from schemas.campaigns import CreateCampaign,LoadCampaignSchemas,LoadCampaignResponse,LoadCampaign
from database.database import get_session
#from utils.load_als_service import get_loader_als_loader_service
from utils.dnc_util import dnc_list_numbers
from utils.list_names import get_list_names
from utils.auth import get_current_user,get_current_active_user
from utils.logger import define_logger
from utils.dmasa_service import DMA_Class,get_dmasa_service
from settings.Settings import get_settings

campaigns_logger=define_logger("als campaign logs","logs/campaigns_route.log")

campaigns_router=APIRouter(tags=["Campaigns"],prefix="/campaigns")

@campaigns_router.post("/create-campaign",status_code=status.HTTP_201_CREATED,description="Create a new campaign by providing a branch, campaign code and campaign name",response_model=campaign_tbl)
async def create_campaign(campaign:CreateCampaign,session:Session=Depends(get_session),user=Depends(get_current_active_user)):
    
    try:
        
        #search the database for a campaign,hopefully the db is indexed
        statement=select(campaign_tbl).where(campaign_tbl.camp_code == campaign.camp_code)
        
        campaign_query=session.exec(statement).first()

        if not campaign_query==None:
            campaigns_logger.info(f"user:{user.id} with email:{user.email} created a campaign that already exists")
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail=f"campaign:{campaign.campaign_name} with campaign code:{campaign.camp_code} already exists")
        
        payload=campaign.model_dump()
        new_campaign=campaign_tbl.model_validate(payload)
        session.add(new_campaign)
        session.commit()
        session.refresh(new_campaign)
        campaigns_logger.info(f"campaign:{campaign.campaign_name} with campaign code:{campaign.camp_code} created successfully by user with user_id:{user.id} and email:{user.email}")
        
        return new_campaign
    except Exception as e:
        campaigns_logger.error(f"error occurred:{str(e)} while creating campaign:{campaign.campaign_name} with campaign code:{campaign.camp_code}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail="An internal server error occurred")
    

#load a campaign given the campaign code: camp_code
@campaigns_router.post("/load-campaign/{camp_code}",description="load a campaign to vicdial if it exist. Create one and assign a rule to it",status_code=status.HTTP_200_OK,response_model=LoadCampaignResponse)

#load campaign to a specific branch
#load numbers from the global dnc or king price dnc 

async def load_campaign(load_campaign:LoadCampaign,camp_code:str=Path(...,description="Please provide the campaign code"),session:Session=Depends(get_session),user=Depends(get_current_active_user),background:BackgroundTasks=BackgroundTasks,dma_object:DMA_Class=Depends(get_dmasa_service)):
    
    #calculate the number of entries in table campaign_rules

    try:
        #check if the campaign exist before trying to load it
        load_campaign_stmt=select(campaign_tbl).where(campaign_tbl.camp_code==load_campaign.camp_code)
        #find the campaign to be loaded
        campaign=session.exec(load_campaign_stmt).first()

        #if the campaign does not exist notify the use
        if campaign==None:
            campaigns_logger.info(f"campaign:{camp_code} does not exist")
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f"campaign:{camp_code} does not exist")
        
        # search the rules_table
        rule_query=select(rules_tbl).where(rules_tbl.rule_name==camp_code)
        #execute the query
        first_rule=session.exec(rule_query).first()

        if not first_rule:
            campaigns_logger.info(f"user:{user.id} with email:{user.email} requested a rule that does not exist")
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f"no rule exist for campaign:{camp_code}")
        
        #last used
        today=datetime.now()
        
        thirsty_days_ago=today - timedelta(days=29)

        thirsty_days_ago_start=thirsty_days_ago.replace(hour=0,minute=0,second=0,microsecond=0)

        thirsty_days_ago_end=thirsty_days_ago_start + timedelta(days=1)

        #years filters
        start_year=first_rule.rule_sql['start_year']

        end_year=first_rule.rule_sql['end_year']
        # calculate two-digit year range

        start_two_digit=start_year % 100 # 1980->80 or 2000->00

        end_year_two_digit=end_year % 100 #1995->95 or 2010->10
        #the current year shoulde a dynamic value
        current_year=2025

        century_cutoff=current_year % 100
       
        info_tbl_query=select(info_tbl.id,info_tbl.fore_name,info_tbl.last_name,info_tbl.cell).where((info_tbl.salary>=first_rule.rule_sql["salary"]) | (info_tbl.salary == None)).where(info_tbl.type_data=="Status").where(func.cast(func.cast(info_tbl.id,1,2),Integer).between(min(start_two_digit,end_year_two_digit),max(start_two_digit,end_year_two_digit))).where((func.cast(func.substring(info_tbl.id,1,2),Integer)+1900).between(start_year,end_year) & (func.cast(func.substring(info_tbl.id,1,2),Integer)>century_cutoff)).where((info_tbl.last_used==None) | ((info_tbl.last_used>=thirsty_days_ago_start) & (info_tbl.last_used<thirsty_days_ago_end))).order_by(func.random()).limit(first_rule.rule_sql["limit"])
        #execute the big query
        leads_all=session.exec(info_tbl_query).all()

        if len(leads_all)<=0:
            campaigns_logger.info(f"no leads can be loaded for campaign:{load_campaign.camp_code} in branch:{load_campaign.branch}")
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f"no leads can be loaded for this campaign")
        
        #SELECT id, fore_name, last_name, cell FROM info_tbl WHERE (salary>=16000 or salary is null) and (typedata = "Status") and (last_used is null or (DATE_PART("day",now()::timestamp - last_used::timestamp) > 29)) and (CAST(SUBSTRING(id,1,2) AS INTEGER) <=98 and CAST(SUBSTRING(id,1,2) AS INTEGER) >=68) order by random() limit 3000
        #salary condition
        salary_condition="(salary>=:min_salary OR salary is NULL)"

        raw_sql_query=text(f""" select id,fore_name,last_name,cell from info_tbl where {salary_condition} AND (typedata:=status_val) AND (last_used IS NULL OR (DATE_PART('day',NOW()::timestamp - last_used::timestamp)>29)) AND (CAST(SUBSTRING(id,1,2) AS INTEGER)<=:max_id AND CAST(SUBSTRING(id,1,2) AS INTEGER)>=:min_id) ORDER BY random() LIMIT :row_limit""")
       
        if load_campaign.max_salary is not None:
            params["max_sal"]=load_campaign.max_salary
        
        params={
            "min_sal":load_campaign.min_salary,
            "status_val":"Status",
            "min_id":load_campaign.min_dob_year,
            "max_id":load_campaign.max_dob_year,
            "row_limit":load_campaign.limit
        }


        if load_campaign.max_salary is not None:
            salary_condition=f"({salary_condition} AND salary<=:max_sal)"

        #execute the query

        leads_results=session.exec(raw_sql_query.params(**params)).all()

        fetched_rows=len(leads_all)
        #needs attention
        if leads_all==0 and fetched_rows==0:
            campaigns_logger.info(f"No leads found for campaign:{load_campaign.camp_code}")

            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f"No leads exist for campaign:{camp_code}")

        #rule code and rule sql needs to be addressed

        if leads_all !=0 and fetched_rows!=0:

            #get numbers from the global dnc db

            dnc_list=dnc_list_numbers()

            # for idx, obj in enumerate(leads_results):
            #     if obj[3] in dnc_list:
            #         leads_results.pop(idx)

                
            #filter the numbers on the dnc list
           
            filtered_results = [obj for obj in leads_all if obj[3] not in dnc_list]

            #the number of leads not on the dnc
            leads_length=len(filtered_results)

            #token=get_loader_als_loader_service(load_campaign.branch)

            todays_date=datetime.today().strftime('%Y-%m-%d')
            
            list_name=get_list_names(camp_code)

            if list_name==None:

                campaigns_logger.info(f"An error occurred while generating list name for campaign:{camp_code}")
                raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail=f"An error occurred while generating list name for:{camp_code}")
            
            data_line='\n'.join([i[3] for i in leads_all])
            # send leads for dma
            submit_dma_data=dma_object.upload_data_for_dedupe(data_line)
            
            #audit_id=submit_dma_data.json()['DedupeAuditId']

            #dma_response=requests.post("http://127.0.0.1:8000/dma/upload-data",data=json.dumps(data_line),verify=False,timeout=300)
            
            #check the status of the response
            
            if submit_dma_data.status_code!=200:

                campaigns_logger.error(f"error occurred while uploading leads to dmasa with status code:{submit_dma_data.status_code}")
                raise HTTPException(status_code=submit_dma_data.status_code,detail="An internal server error occurred while uploading files to dmasa")
            
            elif submit_dma_data.status_code==200 and len(submit_dma_data.json()["Errors"])==0:
                #store the audit id on audit id table
                audit_id=submit_dma_data.json()['DedupeAuditId']
                campaigns_logger.info(f"dma submitted with audit id:{submit_dma_data.json()["DedupeAuditId"]}")
                #store audit id on the audit id table
                audit_id_values_commit=dma_audit_id_table(audit_id=submit_dma_data.json()['DedupeAuditId'],records_processed=submit_dma_data.json()['RecordsProcessed'],notification_email=get_settings().notification_email,is_processed=False)
                #commit the audit id on the audit id table
                session.add(audit_id_values_commit)
                session.commit()
                session.close()
                #insert the fetched leads to the dma validation table
                #rollback the session if an error occurs
                load_dmasa_status=f"data uploaded to for dma with audit id:{submit_dma_data.json()['DedupeAuditId']}"

            elif submit_dma_data.status_code!=200 and len(submit_dma_data.json()['Errors'])==0:

                campaigns_logger.error(f"Error occurred while committing to audit table,status code:{submit_dma_data.status_code}")
                raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail=submit_dma_data.json()['Errors'][0])
           
           #faulty logic this route will always raise a 
            else:
                campaigns_logger.error("Internal server error occurred while submitting dma records")
                raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail=submit_dma_data.json()['Errors'])
            
            #add the original data to dma validation to validate with the dma submitted information
            dma_validation_table_rows=[dma_validation_data(id=r[0],fore_name=r[1],last_name=r[2],cell=r[3],audit_id=audit_id,is_processed=False,branch=load_campaign.branch,camp_code=load_campaign.camp_code,opted_out=True) for r in leads_all]

            #add the results filtered against the dnc into the dma validation table
            #all records here are not processed

            session.add(dma_validation_table_rows)

            session.commit()

            session.close()

            campaigns_logger.info(f"inserted dma validation table with data that has audit id:{audit_id} for campaign:{load_campaign.camp_code} from branch:{load_campaign.branch} on this data:{todays_date}")
            #I am gonna need the list name from here
            #populate the list tracker table with the audit id, camp_code,list name,branch,rule_name(camp_code)
            list_entry=list_tracker_table(audit_id=audit_id,list_name=list_name,branch=load_campaign.branch,camp_code=load_campaign.camp_code,rule_name=load_campaign.camp_code)
            session.add(list_entry)
            session.commit()
            session.close()
            campaigns_logger.info(f"list name:{list_name} successfully inserted on the track table with audit id:{audit_id} for campaign code:{load_campaign.camp_code} from branch:{load_campaign.branch} on this day:{todays_date}")


        return LoadCampaignResponse(campaign_code=camp_code,branch=load_campaign.branch,list_name=list_name,audit_id=submit_dma_data.json()['DedupeAuditId'],records_processed=submit_dma_data.json()['RecordsProcessed'],dma_status_code=submit_dma_data.status_code,load_dmasa_status=load_dmasa_status,number_of_leads_submitted=leads_length)

            

        # if results_count==0:
        #     campaigns_logger.info(f"no active leads for the currently active rule:{rule_code} for campaign:{camp_code}")
        #     raise HTTPException(status_code=status.HTTP_200_OK,detail=f"no active leads for the currently active rule:{rule_code} for campaign:{camp_code}")
        
        # if results_leads!=None and results_count!=0:
        #     #fetch the dnc list can be king price or global dnc
        #     dnc_list=dnc_list_numbers()

        #     dnc_set_list=set(dnc_list)
        #     # Use a list comprehension to create a new, filtered list
        #     # The items that are NOT in the dnc_set are kept
        #     filtered_results = [obj for obj in results_leads if obj[3] not in dnc_set_list]
            
        #     #search for the correct token
        #     #load the token from environment variables file
        #     token=get_loader_als_loader_service(branch)
            
        #     #list name goes to ss dedago
        #     list_name=get_list_names(camp_code)

        #     if list_name==None:
        #         campaigns_logger.info(f"an error occurred while generating a list name for campaign code:{camp_code}")
        #         raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail=f"an error occurred while generating a list name for campaign code:{camp_code}")
            
        #     #new list called data line
        #     data_line = '\n'.join([i[3] for i in filtered_results])

        #     #submit dma records
        #     #
        #     #credits_response=requests.get(url=base_url,params=params_values,verify=False,timeout=10)
            
        #     dma_response=requests.post("http://127.0.0.1:8000/dma/upload-data",data=json.dumps(data_line),verify=False,timeout=30)

            
        #     #check the status of the response
        #     if dma_response.status_code!=200:
        #         campaigns_logger.error(f"error occurred while uploading leads to dmasa with status code:{dma_response.status_code}")
        #         raise HTTPException(status_code=dma_response.status_code,detail="An internal server error occurred while uploading files to dmasa")
        #     else:
        #         load_dmasa_status="Files uploaded for dma"
            
        #     return {"campaign code":camp_code,"branch":load_campaign.branch,"list name":list_name,"load dmasa status":load_dmasa_status,"dma_service_status_code":dma_response.status_code}
        
    except Exception as e:
        print(str(e))
        campaigns_logger.critical(f"{str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail=f"An internal server error occurred")


# @campaigns_router.patch("/{camp_code}",status_code=status.HTTP_200_OK)

# async def assign_campaign_rule_to_campaign(camp_code:str=Path(description="provide the campaign code that needs a rule assigned to it"),rule_code:str=Query(description="Provide the rule code for this campaign"),session:Session=Depends(get_session),user=Depends(get_current_user)):
   
#     try:
#         #find the campaign using the campaign code
#         print()
#         print("assign campaign rule to campaign")
#         find_campaign_query=select(campaign_tbl).where(campaign_tbl.camp_code==camp_code)
#         print("print the query")
#         print(find_campaign_query)
#         find_campaign=session.exec(find_campaign_query).first()
#         print("")
#         print("print the query results")
#         print(find_campaign)
#         if find_campaign==None:
#             raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f"campaign:{camp_code} does not exist")
#         #find the rule
#         rule_query=select(campaign_rules).where(campaign_rules.rule_code==rule_code)
#         rule=session.exec(rule_query).first()
#         if rule==None:
#             raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f"campaign rule with code:{rule_code} does not exist")
#         #assign the rule to the campaign
#         find_campaign.rule_code=rule.rule_code
#         #activate the rule
#         #add to the session object
#         session.add(find_campaign)
#         #commit
#         session.commit()
#         #bring the thing you used
#         session.refresh(find_campaign)
#         return find_campaign
    
#     except Exception as e:
#         print("print an exception object for assigning a campaign rule to a campaign")
#         print(e)
#         raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail="An internal server error occurred")


@campaigns_router.get("/{camp_code}",status_code=status.HTTP_200_OK,description="Get campaign by campaing code",response_model=campaign_tbl)
async def get_campaign_by_code(camp_code:str,session:Session=Depends(get_session),user:Session=Depends(get_current_active_user)):
    try:
        campaign_query=select(campaign_tbl).where(campaign_tbl.camp_code==camp_code)
        campaign=session.exec(campaign_query).first()
        if not campaign:
            campaigns_logger.info(f"user:{user.id} with email:{user.email} requested campaign:{camp_code} that does not exist")
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f"Campaign:{camp_code} does not exist")
        campaigns_logger.info(f"user:{user.id} with email:{user.email} successfully fetched campaign:{camp_code}")
        return campaign
    except Exception as e:
        campaigns_logger.error(f"{str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail=f"An internal server error occurred while fetching campaign:{camp_code}")
    
@campaigns_router.patch("/{camp_code}",status_code=status.HTTP_200_OK,description="Update the campaign name,campaign code or move it to another branch")
async def update_campaign(camp_code:str,session:Session=Depends(get_session),user=Depends(get_current_active_user)):
    try:
        return True
    except Exception as e:
        return False