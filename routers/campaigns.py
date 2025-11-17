from fastapi import APIRouter,status,Depends,HTTPException,Path,Query,BackgroundTasks,Request,Response
from sqlmodel import Session,select,or_,and_,case
from sqlalchemy import cast,text,Integer
from sqlalchemy.ext.asyncio.session import AsyncSession
from sqlalchemy.sql import func
import sqlalchemy as sa
from typing import Dict
from datetime import datetime,timedelta
from models.campaigns_table import campaign_tbl
from models.information_table import info_tbl
from models.dma_service import dma_audit_id_table,list_tracker_table
from models.rules_table import rules_tbl
from models.dma_service import dma_validation_data
from schemas.campaigns import CreateCampaign,LoadCampaignResponse,LoadCampaign,UpdateCampaignName,CreateCampaignResponse,PaginatedCampaigResponse
from database.database import get_session
from database.master_db_connect import get_async_session
#from utils.load_als_service import get_loader_als_loader_service
from utils.dnc_util import dnc_list_numbers
from utils.list_names import get_list_names
from utils.auth import get_current_active_user
from utils.logger import define_logger
from utils.dmasa_service import DMA_Class,get_dmasa_service
from utils.campaigns import build_dynamic_query,load_campaign_query_builder,build_dynamic_dedupe_main_query,build_dynamic_query_finance_tbl
from crud.campaigns import (create_campaign_db,get_all_campaigns_by_branch_db,get_campaign_by_code_db,get_campaign_by_name_db,update_campaign_name_db)
from settings.Settings import get_settings

campaigns_logger=define_logger("als campaign logs","logs/campaigns_route.log")

campaigns_router=APIRouter(tags=["Campaigns"],prefix="/campaigns")

@campaigns_router.post("/create-campaign",status_code=status.HTTP_201_CREATED,description="Create a new campaign by providing a branch, campaign code and campaign name",response_model=CreateCampaignResponse)

async def create_campaign(campaign:CreateCampaign,session:AsyncSession=Depends(get_async_session),user=Depends(get_current_active_user)):
    try:
        result= await create_campaign_db(campaign,session,user)
        campaigns_logger.info(f"campaign:{campaign.campaign_name} with campaign code:{campaign.camp_code} created successfully by user with user_id:{user.id} and email:{user.email}")
        return result
    except HTTPException:
        raise
    except Exception as e:
        campaigns_logger.error(f"error occurred:{str(e)} while creating campaign:{campaign.campaign_name} with campaign code:{campaign.camp_code}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail="An internal server error occurred")
    

#load a campaign given the campaign code: camp_code
@campaigns_router.post("/load-campaign",description="load campaign by providing campaign code and branch name",status_code=status.HTTP_200_OK,response_model=LoadCampaignResponse)

#load campaign to a specific branch
#load numbers from the global dnc or king price dnc 

async def load_campaign(load_campaign:LoadCampaign,session:AsyncSession=Depends(get_async_session),user=Depends(get_current_active_user),background:BackgroundTasks=BackgroundTasks,dma_object:DMA_Class=Depends(get_dmasa_service)):
    #calculate the number of entries in table campaign_rules
    try:
        #check if the campaign exist before trying to load it
        #load_campaign_stmt=select(campaign_tbl).where(campaign_tbl.camp_code==load_campaign.camp_code)
        #find the campaign to be loaded
        #campaign=session.exec(load_campaign_stmt).first()
        campaign=await get_campaign_by_code_db(load_campaign.camp_code,session)
        # #if the campaign does not exist notify the use
        # if not campaign:
        #     campaigns_logger.info(f"campaign:{load_campaign.camp_code} does not exist,loading requested by {user.id} with email:{user.email}")
        #     raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f"campaign:{load_campaign.camp_code} does not exist")
        
        # search the rules_table
        rule_query=select(rules_tbl).where(rules_tbl.rule_name==load_campaign.camp_code)
        #execute the query
        first_rule=session.exec(rule_query).first()

        if not first_rule:
            campaigns_logger.info(f"user:{user.id} with email:{user.email} requested a rule that does not exist")
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f"no rule exist for campaign:{load_campaign.camp_code}")
        
        #last used
        #today=datetime.now()
        
        #thirsty_days_ago=today - timedelta(days=29)

        #thirsty_days_ago_start=thirsty_days_ago.replace(hour=0,minute=0,second=0,microsecond=0)

        #thirsty_days_ago_end=thirsty_days_ago_start + timedelta(days=1)

        #years filters
        #start_year=first_rule.rule_sql['start_year']

        #end_year=first_rule.rule_sql['end_year']

        # calculate two-digit year range

        #start_two_digit=start_year % 100 # 1980->80 or 2000->00

        #end_year_two_digit=end_year % 100 #1995->95 or 2010->10
        #the current year shoulde a dynamic value
        #current_year=2025

        #century_cutoff=current_year % 100
       
        #info_tbl_query=select(info_tbl.id,info_tbl.fore_name,info_tbl.last_name,info_tbl.cell).where((info_tbl.salary>=first_rule.rule_sql["salary"]) | (info_tbl.salary == None)).where(info_tbl.type_data=="Status").where(func.cast(func.cast(info_tbl.id,1,2),Integer).between(min(start_two_digit,end_year_two_digit),max(start_two_digit,end_year_two_digit))).where((func.cast(func.substr(info_tbl.id,1,2),Integer)+1900).between(start_year,end_year) & (func.cast(func.substr(info_tbl.id,1,2),Integer)>century_cutoff)).where((info_tbl.last_used==None) | ((info_tbl.last_used>=thirsty_days_ago_start) & (info_tbl.last_used<thirsty_days_ago_end))).order_by(func.random()).limit(first_rule.rule_sql["limit"])
        
        #load a generic campaign based on specific conditions

        campaign_type=first_rule.is_dedupe
        ping_status=first_rule.is_ping_status_null
        is_deduped=first_rule.is_dedupe

        if is_deduped is None and ping_status is not None:

            query,params=load_campaign_query_builder(first_rule)
        
        #load a dedupe campaign
        elif campaign_type is not None and is_deduped is not None:

            query,params=build_dynamic_dedupe_main_query(first_rule)
        
        elif ping_status is None and campaign_type is not None:

            query,params=build_dynamic_query_finance_tbl(first_rule)

        else:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail=f"An internal server error occurred while loading campaign:{load_campaign.camp_code} for branch:{load_campaign.branch}")
        
        rows= await session.execute(query,params).mappings().all()

        #execute the big query, thus producing a list of dictionaries

        leads_all=[dict(row) for row in rows]

        if len(leads_all)<=0:
            campaigns_logger.info(f"no leads can be loaded for campaign:{load_campaign.camp_code} in branch:{load_campaign.branch}")
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f"no leads can be loaded for this campaign")
        
        #SELECT id, fore_name, last_name, cell FROM info_tbl WHERE (salary>=16000 or salary is null) and (typedata = "Status") and (last_used is null or (DATE_PART("day",now()::timestamp - last_used::timestamp) > 29)) and (CAST(SUBSTRING(id,1,2) AS INTEGER) <=98 and CAST(SUBSTRING(id,1,2) AS INTEGER) >=68) order by random() limit 3000
        #salary condition

        fetched_rows=len(leads_all)

        #needs attention
        if leads_all==0 and fetched_rows==0:
            campaigns_logger.info(f"No leads found for campaign:{load_campaign.camp_code}")
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f"No leads exist for campaign:{load_campaign.camp_code}")

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
            
            list_name=get_list_names(load_campaign.camp_code)

            if list_name==None:

                campaigns_logger.info(f"An error occurred while generating list name for campaign:{load_campaign.camp_code}")
                raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail=f"An error occurred while generating list name for:{load_campaign.camp_code}")
            
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
                await session.commit()
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

            await session.commit()

            campaigns_logger.info(f"inserted dma validation table with data that has audit id:{audit_id} for campaign:{load_campaign.camp_code} from branch:{load_campaign.branch} on this data:{todays_date}")
            #I am gonna need the list name from here
            #populate the list tracker table with the audit id, camp_code,list name,branch,rule_name(camp_code)
            list_entry=list_tracker_table(audit_id=audit_id,list_name=list_name,branch=load_campaign.branch,camp_code=load_campaign.camp_code,rule_name=load_campaign.camp_code)
            session.add(list_entry)
            await session.commit()
            campaigns_logger.info(f"list name:{list_name} successfully inserted on the track table with audit id:{audit_id} for campaign code:{load_campaign.camp_code} from branch:{load_campaign.branch} on this day:{todays_date}")

        return LoadCampaignResponse(campaign_code=load_campaign.camp_code,branch=load_campaign.branch,list_name=list_name,audit_id=submit_dma_data.json()['DedupeAuditId'],records_processed=submit_dma_data.json()['RecordsProcessed'],dma_status_code=submit_dma_data.status_code,load_dmasa_status=load_dmasa_status,number_of_leads_submitted=leads_length)

            

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
        campaigns_logger.critical(f"{str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail=f"An internal server error occurred")


@campaigns_router.get("/{camp_code}",status_code=status.HTTP_200_OK,description="Get campaign by campaing code from the master database",response_model=CreateCampaignResponse)
async def get_campaign_by_code(camp_code:str=Path(...,description="Campaign Code"),session:AsyncSession=Depends(get_async_session),user:Session=Depends(get_current_active_user)):
    try:
        # campaign_query=select(campaign_tbl).where(campaign_tbl.camp_code==camp_code)
        # campaign=session.exec(campaign_query).first()
        campaign=await get_campaign_by_code_db(camp_code,session,user)
        if campaign is None:
            campaigns_logger.info(f"user:{user.id} with email:{user.email} requested campaign:{camp_code} that does not exist")
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f"Campaign:{camp_code} does not exist")
        campaigns_logger.info(f"user:{user.id} with email:{user.email} successfully fetched campaign:{camp_code}")
        return campaign
    except HTTPException:
        raise 
    except Exception as e:
        campaigns_logger.error(f"{str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail=f"An internal server error occurred while fetching campaign:{camp_code}")

  
@campaigns_router.patch("/update/{camp_code}",status_code=status.HTTP_200_OK,description="update campaign name",response_model=CreateCampaignResponse)
async def update_campaign_name(new_campaign_name:UpdateCampaignName,camp_code:str=Path(...,description="Provide the campaign code"),session:AsyncSession=Depends(get_async_session),user=Depends(get_current_active_user)):
    try:
        #get the campaign to be updated
        campaign=await get_campaign_by_code_db(camp_code,session,user)
        if campaign is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f"requested campaign:{new_campaign_name.campaign_name} does not exists")
        result=await update_campaign_name_db(new_campaign_name,camp_code,session,user)
        if result==None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f"campaign with campaign code:{camp_code} does not exist")
        return result
    
    except HTTPException:
        raise  
    except Exception as e:
        campaigns_logger.exception(f"An internal server error while updating campaign:{camp_code}:{str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail=f"An internal server error occurred while updating campaign with campaign code:{camp_code}")


@campaigns_router.get("/branch/{branch}",status_code=status.HTTP_200_OK,description="Get all campaigns by branch",response_model=PaginatedCampaigResponse)
async def get_all_campaigns_by_branch(branch:str,page:int=Query(1,ge=1,description="Page number"),page_size:int=Query(10,ge=1,le=100,description="Number of records per page"),user=Depends(get_current_active_user),session:AsyncSession=Depends(get_async_session)):
    return await get_all_campaigns_by_branch(branch,session,user,page,page_size)