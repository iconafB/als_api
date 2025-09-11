from fastapi import APIRouter,status,Depends,HTTPException,Path,Query,BackgroundTasks
from sqlmodel import Session,select,or_,and_
import sqlalchemy as sa
import requests
import json
from sqlalchemy import func
from models.campaigns import Campaigns
from models.leads import information_table
from models.campaign_rules import campaign_rules
from schemas.campaigns import CreateCampaign
from database.database import get_session
from utils.load_als_service import get_loader_als_loader_service
from utils.dnc_util import dnc_list_of_numbers
from utils.list_names import get_list_names
from utils.auth import get_current_user

campaigns_router=APIRouter(tags=["Campaigns"],prefix="/campaigns")

@campaigns_router.post("/create-campaign",status_code=status.HTTP_201_CREATED,description="Create a new campaign by providing a branch, campaign code and campaign name",response_model=Campaigns)
async def create_campaign(campaign:CreateCampaign,session:Session=Depends(get_session),user=Depends(get_current_user)):
    
    try:
        #search the database for a campaign,hopefully the db is indexed
        statement=select(Campaigns).where(Campaigns.camp_code == campaign.camp_code)
        campaign_query=session.exec(statement).first()
        if not campaign_query==None:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail=f"campaign:{campaign.campaign_name} with campaign code:{campaign.camp_code} already exists")
        payload=campaign.model_dump()
        new_campaign=Campaigns.model_validate(payload)
        session.add(new_campaign)
        session.commit()
        session.refresh(new_campaign)
        return new_campaign
    
    except Exception as e:
        print("print the exception object")
        print(e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail="An internal server error occurred")
#load a campaign given the campaign code: camp_code
@campaigns_router.post("/load-campaign/{camp_code}",description="load a campaign to vicdial if it exist. Create one and assign a rule to it",status_code=status.HTTP_200_OK,response_model=Campaigns)

#load campaign to a specific branch
#load numbers from the global dnc or king price dnc 
async def load_campaign(camp_code:str=Path(...,description="Please provide the campaign code"),rule_code:str=Query(description="Please provide the rule code for the campaign to load"),dnc_type:str=Query(description="Global DNC or King Price Optional"),branch:str=Query(description="Branch for the campaign"),session:Session=Depends(get_session),user=Depends(get_current_user)):
    #calculate the number of entries in table campaign_rules
    statement=select(func.count()).select_from(campaign_rules).where(campaign_rules.camp_code==camp_code and campaign_rules.rule_code==rule_code)
    
    statement_query=session.exec(statement).first()

    try:
        #check if the campaign exist before trying to load it
        load_campaign=select(Campaigns).where(Campaigns.camp_code==camp_code)
        #find the campaign to be loaded
        campaign=session.exec(load_campaign).first()
        #if the campaign does not exist notify the use
        if campaign==None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f"campaign:{camp_code} does not exist")
        #find the campaign rule for the this campaign
        campaign_rule_query=select(campaign_rules).where(campaign_rules.camp_code==campaign.camp_code)
        print("print the campaign rule query")
        print(campaign_rule_query)
        print("print what the query returns")
        rule_query=session.exec(campaign_rule_query).first()
        print(rule_query)
        if rule_query == None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f"no campaign rule exist for this campaign with campaign code:{camp_code}")
        #SELECT id, fore_name, last_name, cell FROM info_tbl WHERE (salary>=16000 or salary is null) and (typedata = "Status") and (last_used is null or (DATE_PART("day",now()::timestamp - last_used::timestamp) > 29)) and (CAST(SUBSTRING(id,1,2) AS INTEGER) <=98 and CAST(SUBSTRING(id,1,2) AS INTEGER) >=68) order by random() limit 3000
        
        #query for the information table
        statement=select(information_table.id,information_table.fore_name,information_table.last_name,information_table.cell_number)
        #the where clauses
        salary_condition=or_(information_table.salary>rule_query.max_salary,information_table.salary.is_(None))
        #type data = "Status"
        typedata_condition=information_table.type_data=="Status"
        #last used condition
        last_used_condition = or_(information_table.last_used.is_(None), func.date_part('day', func.now() - information_table.last_used) > 29)
        # The id substring needs to be cast to an integer
        id_part = func.cast(sa.func.substring(information_table.id, 1, 2), sa.Integer)
        #id test condition
        id_condition = and_(id_part <= 98, id_part >= 68)
        #combined where clause
        combined_where_clause = and_(salary_condition, typedata_condition, last_used_condition, id_condition)

        final_results_statement = statement.where(combined_where_clause).order_by(func.random()).limit(3000)
        #execute the query
        results_leads=session.exec(final_results_statement)
        #redundant statements
        results_count=session.exec(final_results_statement).one()

        if results_count==0:
            raise HTTPException(status_code=status.HTTP_200_OK,detail=f"no active leads for the currently active rule:{rule_code} for campaign:{camp_code}")
        
        if results_leads!=None and results_count!=0:
            #fetch the dnc list can be king price or global dnc
            dnc_list=dnc_list_of_numbers(dnc_type)
            dnc_set_list=set(dnc_list)
            # Use a list comprehension to create a new, filtered list
            # The items that are NOT in the dnc_set are kept
            filtered_results = [obj for obj in results_leads if obj[3] not in dnc_set_list]
            
            #search for the correct token
            #load the token from environment variables file
            token=get_loader_als_loader_service(branch)
            
            #list name goes to ss dedago
            list_name=get_list_names(camp_code)

            if list_name==None:
                raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail=f"an error occurred while generating a list name for campaign code:{camp_code}")
            
            #new list called data line
            data_line = '\n'.join([i[3] for i in filtered_results])
            #submit dma records
            #
            #credits_response=requests.get(url=base_url,params=params_values,verify=False,timeout=10)
            dma_response=requests.post("http://127.0.0.1:8000/dma/upload-data",data=json.dumps(data_line),verify=False,timeout=30)
            
            #check the status of the response
            if dma_response.status_code!=200:
                raise HTTPException(status_code=dma_response.status_code,detail="An internal server error occurred while uploading files to dmasa")
            else:
                load_dmasa_status="Files uploaded for dma"
            
            return {"token":token,"branch":branch,"list name":list_name,"load dmasa status":load_dmasa_status}

    except Exception as e:
        #
        print("error object")
        print(e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail=f"An internal server error occurred")
    return {"message":f"load campaign:{camp_code}"}


@campaigns_router.patch("/{camp_code}",status_code=status.HTTP_200_OK)

async def assign_campaign_rule_to_campaign(camp_code:str=Path(description="provide the campaign code that needs a rule assigned to it"),rule_code:str=Query(description="Provide the rule code for this campaign"),session:Session=Depends(get_session),user=Depends(get_current_user)):
   
    try:
        #find the campaign using the campaign code
        print()
        print("assign campaign rule to campaign")
        find_campaign_query=select(Campaigns).where(Campaigns.camp_code==camp_code)
        print("print the query")
        print(find_campaign_query)
        find_campaign=session.exec(find_campaign_query).first()
        print("")
        print("print the query results")
        print(find_campaign)
        if find_campaign==None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f"campaign:{camp_code} does not exist")
        #find the rule
        rule_query=select(campaign_rules).where(campaign_rules.rule_code==rule_code)
        rule=session.exec(rule_query).first()
        if rule==None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f"campaign rule with code:{rule_code} does not exist")
        #assign the rule to the campaign
        find_campaign.rule_code=rule.rule_code
        #activate the rule
        #add to the session object
        session.add(find_campaign)
        #commit
        session.commit()
        #bring the thing you used
        session.refresh(find_campaign)
        return find_campaign
    
    except Exception as e:
        print("print an exception object for assigning a campaign rule to a campaign")
        print(e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail="An internal server error occurred")
