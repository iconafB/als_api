from fastapi import APIRouter,HTTPException,status,Depends,Query,Path,Request
from sqlmodel import Session,select,text,update
from datetime import datetime
from typing import List
from sqlmodel.ext.asyncio.session import AsyncSession
from models.users import users_table
from models.rules_table import rules_tbl
from models.campaigns_table import campaign_tbl
from models.campaign_rules_table import campaign_rule_tbl
from schemas.sql_rule import Sql_Rules,Change_Active_Rule
from schemas.campaign_rules import RuleCreate,AssignCampaignRuleToCampaign,AssignCampaignRuleResponse,CampaignSpecResponse,CreateCampaignRuleResponse,ChangeCampaignRuleResponse,PaginatedCampaignRules
from schemas.campaign_rules_input import FetchRuleResponse,UpdateCampaignRulesResponse
from database.database import get_session
from database.master_db_connect import get_async_session
from utils.logger import define_logger
from utils.auth import get_current_active_user
from crud.campaign_rules import (create_campaign_rule_db,assign_campaign_rule_to_campaign_db,get_campaign_rule_by_rule_name_db,get_all_campaign_rules_db)
from utils.campaigns import (load_campaign_query_builder)
from utils.parse_validation_methods import parse_and_validate_rule

campaign_rule_router=APIRouter(tags=["Generic Campaign Rules"],prefix="/campaign_rules")

campaign_rules_logger=define_logger("als campaign rules","logs/campaign_rules_logs")
@campaign_rule_router.post("",status_code=status.HTTP_200_OK,description="Create a campaign rule by the necessary info",response_model=CreateCampaignRuleResponse)

async def create_campaign_rule(rule:RuleCreate,session:AsyncSession=Depends(get_async_session),user=Depends(get_current_active_user),parsed_data=Depends(parse_and_validate_rule)):
    create_rule=await create_campaign_rule_db(rule,session,user)
    campaign_rules_logger.info(f"user {user.id} with email:{user.email} created campaign rule:{rule.rule_name}")
    return create_rule



@campaign_rule_router.put("/change_rule/{rule_name}")
#How would the user of this route know the rule code
async def change_rule(rule_code:int,camp_code:str=Path(...,description="provide the campaign code"),session:AsyncSession=Depends(get_async_session),user=Depends(get_current_active_user)):
    try:
        #find the campaign code on the campaign_rule_tbl
        campaign_code_query=await session.exec(select(campaign_rule_tbl).where(campaign_rule_tbl.camp_code==camp_code))
        campaign_code_value=campaign_code_query.first()
        #Accounted for

        if campaign_code_value is None:
            campaign_rules_logger.info(f"user:{user.id} with email:{user.email} attempted to change campaign rule:{camp_code} but it does not exist")
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f"Campaign code:{camp_code} does not exist on the campaign rule table,Create campaign before setting a rule for it")
        

        stmt1=text("""
                    SELECT r.rule_code
                    FROM campaign_rule_tbl c
                    JOIN rules_tbl r ON c.rule_code = r.rule_code
                    WHERE c.camp_code = :camp_code
                    AND c.is_active = TRUE
                    """)
        

        stmt1_result=await session.execute(stmt1,{"camp_code":camp_code})
        todaysdate=datetime.today().strftime("%Y-%m-%d")

        rule_codes:list[int]=stmt1_result.scalars().all()
        #so here I am getting a list of rule codes e.g. [12,24,10]
        old_rule_code=rule_codes[0]

        result_count=len(rule_codes)

       

        if result_count!=0:
            message=f"rule code:{old_rule_code} was found and deactivated,rule code:{rule_code} is now active for campaign code:{camp_code}"
            
            stmt_update=text("""
                        UPDATE campaign_rule_tbl 
                        SET is_active = False 
                        WHERE camp_code = :camp_code
                         """)
            
           
            result=await session.execute(stmt_update,{"camp_code":camp_code})

            await session.commit()

            campaign_rules_logger.info(f"user:{user.id} with email {user.email} updated campaign code:{rule_code}")
            #List of updated database objects
            update_length=len(result.all())

            stmt_insert=text("""
                            INSERT INTO campaign_rule_tbl(camp_code,rule_code,date_rule_created,is_active)
                            VALUES(:camp_code,:rule_code,:date_rule_created,TRUE)
                        """)
            
            insert_result_stmt=await session.execute(stmt_insert,{"camp_code":camp_code,"rule_code":rule_code,"date_rule_created":todaysdate})
            
            await session.commit()

            
        else:
            message = f'NO ACTIVE RULE was found active for campaign {rule_code} but rule {campaign_code_value.rule_code} was made active for it'
            
            stmt_insert=text("""
                            INSERT INTO campaign_rule_tbl(camp,rule_code,date_rule_created,is_active)
                            VALUES(:camp_code,:rule_code,:date_rule_created,TRUE)
                        """)
            stmt_result_insert=await session.execute(stmt_insert,{"camp_code":camp_code,"rule_code":campaign_code_value.rule_code,"date_rule_created":todaysdate})
            
            insert_query_length=stmt_result_insert.all()

            await session.commit()

            #the route ends here
        return ChangeCampaignRuleResponse(Success=True,Message=message)
    
    except Exception as e:
        campaign_rules_logger.exception(f"exception:{str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail=f"An internal server error occurred while changing the rule name:{rule_name}")



#assign campaign rule to a campaign
@campaign_rule_router.post("/assign/{rule_code}",description="assign a campaign rule to an existing campaign")

async def assign_active_rule_to_campaign(rule_code:int,camp_code:str,session:AsyncSession=Depends(get_async_session),user=Depends(get_current_active_user)):
    try:
        campaign_code_query=select(campaign_tbl).where(campaign_tbl.camp_code==camp_code)
        
        campaign_code=await session.exec(campaign_code_query).first()
        
        if campaign_code==None:
            campaign_rules_logger.info(f"campaign with campaign code:{camp_code} does not exist")
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f"campaign with campaign code:{camp_code} does not exist")
       
        #search the campaign code from the 
        find_campaign_rule_query=select(campaign_rule_tbl,rules_tbl).join(rules_tbl,campaign_rule_tbl.rule_code==rules_tbl.rule_code).where(campaign_rule_tbl.camp_code==camp_code,campaign_rule_tbl.is_active==True)
        find_campaign_rule=await session.exec(find_campaign_rule_query).first()

        if not find_campaign_rule:
            campaign_rules_logger.info(f"campaign rule with rule code:{rule_code} does not exist")
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f"rule code:{rule_code} does not exist")
        
        todaysdate=datetime.today().strftime("%Y-%m-%d")
        #update the code
        campaign_code_rule_tbl_query=select(campaign_rule_tbl).where(campaign_rule_tbl.camp_code==camp_code)
        
        campaign_rule_tbl=await session.exec(campaign_code_rule_tbl_query).first()
        
        campaign_rule_tbl.is_active=False

        session.add(campaign_rule_tbl)
        await session.commit()
        message=f"rule code:{find_campaign_rule.rule_code} has been deactivated and rule code:{rule_code} is now active"
        new_rule=campaign_rule_tbl(camp_code=camp_code,rule_code=rule_code,date_rule_created=todaysdate,is_active=True)
        session.add(new_rule)
        await session.commit()
        campaign_rules_logger.info(f"Campaign rule:{rule_code} activated")
        session.close()
        return UpdateCampaignRulesResponse(message=message,update_date=todaysdate)
    
    except HTTPException:
        raise

    except Exception as e:
        campaign_rules_logger(f"{str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail="internal server error occurred")

#change an active rule
# @campaign_rule_router.patch("/change-active-rule/{rule_code}",description="Provide a rule code to change an active rule")

# async def update_active_rule(rule_code:str,incoming_rule:Change_Active_Rule,session:Session=Depends(get_session),user=Depends(get_current_active_user)):
#     #find the rule using a rule code using the below query
#     print("Print the incoming data")
#     print(incoming_rule)
#     rule_query=select(campaign_rules).where(campaign_rules.rule_code==rule_code)
#     #execute the query
#     rule=session.exec(rule_query).first()
#     if rule == None:
#         #raise an exception and break
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f"rule code:{rule_code} does not exist")
#     print("Print the incoming rule")
#     print(rule)
#     #the below code is unacceptable

#     #update the salary min and max
#     if incoming_rule.max_salary !=rule.max_salary:
#         print("print update max salary")
#         rule.max_salary=incoming_rule.max_salary
#         session.add(rule)
#         session.commit()
    
#     if incoming_rule.min_salary != rule.min_salary:
#         print("print update minimum salary")
#         rule.min_salary=incoming_rule.min_salary
#         session.add(rule)
#         session.commit()

#     #update min and max age
#     if incoming_rule.min_age != rule.min_age:
#         print("print update min age")
#         rule.min_age=incoming_rule.min_age
#         session.add(rule)
#         session.commit()

#     if incoming_rule.max_age != rule.max_age:
#         print("print update max age")
#         rule.max_age=incoming_rule.max_age
#         session.add(rule)
#         session.commit()

#     #update gender
#     if incoming_rule.gender != rule.gender:
#         print("print update gender")
#         rule.gender=incoming_rule.gender
#         session.add(rule)
#         session.commit()

#     #update city
#     if incoming_rule.city != rule.city:
#         print("print update city")
#         rule.city=incoming_rule.city
#         session.add(rule)
#         session.commit()
#     #update province
#     if incoming_rule.province == rule.province:
#         # update and commit the value(s)
#         print("print update province")
#         rule.province=incoming_rule.province

#     #update the values and commit it using the session object
#     data=rule.model_dump()
#     #validate the data against the existing model
#     data_obj=campaign_rules.model_validate(data)

#     return data_obj


#fetch rule code based on campaign code

@campaign_rule_router.get("/{rule_name}",status_code=status.HTTP_200_OK,response_model=rules_tbl)
async def fetch_rule_code(rule_name:str=Path(...,description="Provide the rule name which is the same as the campaign code"),session:AsyncSession=Depends(get_async_session),user=Depends(get_current_active_user)):
    try:
        rule_name_query=select(rules_tbl).where(rules_tbl.rule_name==rule_name)
        rule_name_entry=await session.exec(rule_name_query).first()
        if not rule_name_entry:
            campaign_rules_logger.info(f"user with id:{user.id} and email:{user.email} requested a campaign with rule name:{rule_name}")
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f"campaign rule with:{rule_name} does not exist")
        return rule_name_entry
    
    except Exception as e:
        campaign_rules_logger.error(f"{str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail=f"internal server error occurred while fetching campaign rule name:{rule_name}")

#change the rule code
#Do not change the rule code because it's auto generated by the database
@campaign_rule_router.patch("/{rule_code}",status_code=status.HTTP_200_OK,response_model=rules_tbl)

async def change_rule_name(rule_code:int=Path(...,description="Campaign code or rule name of a campaign"),rule_name:str=Query(...,description="Campaign name or rule name"),session:Session=Depends(get_async_session),user=Depends(get_current_active_user)):
    try:
        rule_query=select(rules_tbl).where(rules_tbl.rule_name==rule_code)
        rule=await session.exec(rule_query).first()
        if not rule:
            campaign_rules_logger.info(f"user: {user.id}, email:{user.email} requested a change in rule name:{rule_name} but it does not exist")
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f"user: {user.id}, email:{user.email} requested a change in rule name:{rule_name} but it does not exist")
        rule.rule_name=rule_name
        session.add(rule)
        await session.commit()
        await session.refresh(rule)
        campaign_rules_logger.info(f"campaign with rule code:{rule_code} updated with rule name:{rule_name} by user:{user.id} with email:{user.email}")
        return rule
    
    except Exception as e:
        campaign_rules_logger.exception(f"An exception occurred while changing rule name:{rule_code}:{str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail=f"An internal server error occurred")

#fetch all the rules on the database ,add pagination and search
@campaign_rule_router.get("",status_code=status.HTTP_200_OK,description="Get all campaign rules",response_model=PaginatedCampaignRules)
async def fetch_campaign_rules(page:int=Query(1,ge=1,description="Page Number,Value should be greater than 1"),page_size:int=Query(10,ge=1,le=100,description="Number of items in a page,maximum is 100"),session:AsyncSession=Depends(get_async_session),user=Depends(get_current_active_user)):
    return await get_all_campaign_rules_db(page,page_size,session,user)
    



@campaign_rule_router.put("/change_rule",status_code=status.HTTP_200_OK,description="Assign campaign rule to an existing campaign if the campaign does not exist create it",response_model=AssignCampaignRuleResponse)
async def change_rule(rule:AssignCampaignRuleToCampaign,session:AsyncSession=Depends(get_async_session)):
    return await assign_campaign_rule_to_campaign_db(rule,session)

#calculate the number of leads for a rule
#Questionable check again
@campaign_rule_router.get("/campaign_spec",description="Provide a rule name or campaign code to get the number of leads for that spec. The rule name is the spec name",status_code=status.HTTP_200_OK)
async def check_number_of_leads_for_campaign_rule(rule_name:str,user=Depends(get_current_active_user),session:AsyncSession=Depends(get_async_session)):
    try:
        spec_query=select(rules_tbl).where(rules_tbl.rule_name==rule_name)
        spec_number_call=await session.exec(spec_query)
        result=spec_number_call.first()
        if result is None:
            campaign_rules_logger.exception(f"user {user.id} with email {user.email} caused exception:{str(e)}")
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f"Campaign spec has nothing")
        #campaign spec for a generic campaign
        query,params=load_campaign_query_builder(result)
        #check the spec
        number_of_leads=await session.execute(query,params)
        results=number_of_leads.fetchall()
        campaign_rules_logger.info(f"user {user.id} with email {user.email} checked specification for campaign:{rule_name}")
        return CampaignSpecResponse(Success=True,Number_Of_Leads=len(results))
    except HTTPException:
        raise
    except Exception as e:
        campaign_rules_logger.exception(f"user {user.id} with email {user.email} caused exception:{str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail=f"An internal server error occurred while checking spec for campaign code:{rule_name}")

