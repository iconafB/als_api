from fastapi import APIRouter,HTTPException,status,Depends,Query,Path,Request
from sqlmodel import Session,select
from datetime import datetime
from typing import List
from models.users import users_table
from models.campaign_rules import rules_tbl
from models.campaigns import campaign_tbl,campaign_rules_tbl
from schemas.sql_rule import Sql_Rules,Change_Active_Rule
from schemas.campaign_rules import CreateCampaignRule,ChangeCampaignResponse
from schemas.campaign_rules_input import FetchRuleResponse,UpdateCampaignRulesResponse
from database.database import get_session
from utils.logger import define_logger
from utils.auth import get_current_active_user

campaign_rule_router=APIRouter(tags=["Campaign Rules"],prefix="/campaign-rules")

campaign_rules_logger=define_logger("als campaign rules","logs/campaign_rules_logs")

#Take Care of the response model
# @campaign_rule_router.post("",status_code=status.HTTP_201_CREATED,description="Create SQL Rule for filtering leads by providing the rule",response_model=campaign_rules)
# async def create_campaign_rule(rule:Sql_Rules,session:Session=Depends(get_session),user=Depends(get_current_user)):
    
#     try:
#         #find the rule query
#         exist_rule=select(campaign_rules).where(campaign_rules.rule_code==rule.rule_code)
#          #execute the query
#         query_rule=session.exec(exist_rule)

#         if not query_rule.first()==None:
#             raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail=f"rule code:{rule.rule_code} already exist please choose another code")
       
#         data=rule.model_dump()
#         data_obj=campaign_rules.model_validate(data)
#         session.add(data_obj)
#         session.commit()
#         session.refresh(data_obj)
#         return data_obj
    
#     except Exception as e:
#         print("print the exception object")
#         print(e)
#         raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail="An intrnal server error occurred")


@campaign_rule_router.post("",status_code=status.HTTP_200_OK,description="Create a campaign rule by the necessary info",response_model=rules_tbl)

async def create_campaign_rule(req:Request,rule:CreateCampaignRule,session:Session=Depends(get_session)):
    
    try:
        #search if the user exists
        #see if the campaign rule exists
        print("print the request object headers type")
        print(req.headers['content-type'])
        campaign_rule_query=select(rules_tbl).where(rules_tbl.rule_name==rule.rule_name)
        campaign_rule=session.exec(campaign_rule_query).first()
        if not campaign_rule==None:
            #campaign_rules_logger.info(f"user:{user.id} with email:{user.email} tried to create campaign rule:{rule.campaign_code}")
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail=f"rule_name:{rule.rule_name} already exists")
        #create the campaign rule

        if rule.birth_year_start > rule.birth_year_end:

            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="start year cannot be greater than the end year")
       

        # json_data={
        #     "salary":rule.minimum_salary,
        #     "start_year":rule.start_year,
        #     "end_year":rule.end_year,
        #     "limit":rule.limit,
        #     "last_used":rule.last_used,
        #     "gender":rule.gender
        # }

        create_rule=rules_tbl(rule_name=rule.rule_name,rule_location=rule.rule_location,salary=rule.salary,gender=rule.gender,birth_year_start=rule.birth_year_start,birth_year_end=rule.birth_year_end,last_used=rule.last_used,limit=rule.limit)

        session.add(create_rule)
        session.commit()
        session.refresh(create_rule)

        #campaign_rules_logger.info(f"user:{user.id} with email:{user.email} created campaign rule with rule name:{rule.campaign_code}")
        campaign_rules_logger.info(f"campaign rule created:{rule.rule_name}")
        
        return create_rule
    
    except Exception as e:
        campaign_rules_logger.error(f"{str(e)}")
        print("print the error that occurred with status code 500")
        print(e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail=f"An internal server error occured while creating a campaign rule:{rule.rule_name}")


#assign campaign rule to a campaign
@campaign_rule_router.post("/assign-rule/{rule_code}",description="assign a campaign rule to a campaign")

async def assign_active_rule_to_campaign(rule_code:int,camp_code:str,session:Session=Depends(get_session),user=Depends(get_current_active_user)):
    try:
        campaign_code_query=select(campaign_tbl.camp_code).where(campaign_tbl.camp_code==camp_code)
        campaign_code=session.exec(campaign_code_query).first()

        if campaign_code==None:
            campaign_rules_logger.info(f"campaign with campaign code:{camp_code} does not exist")
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f"campaign with campaign code:{camp_code} does not exist")
        #search the campaign code from the 
        find_campaign_rule_query=select(campaign_rules_tbl,rules_tbl).where((campaign_rules_tbl.rule_code==rules_tbl.rule_code) & (campaign_rules_tbl.camp_code==camp_code) & (campaign_rules_tbl.is_active==True))
        
        find_campaign_rule=session.exec(find_campaign_rule_query).first()

        if find_campaign_rule==None:
            campaign_rules_logger.info(f"campaign rule with rule code:{rule_code} does not exist")
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f"rule code:{rule_code} does not exist")
        
        todaysdate=datetime.today().strftime("%Y-%m-%d")
        #update the code
        campaign_code_rule_tbl_query=select(campaign_rules_tbl).where(campaign_rules_tbl.camp_code==camp_code)
        
        campaign_rule_tbl=session.exec(campaign_code_rule_tbl_query).first()

        campaign_rule_tbl.is_active=False

        session.add(campaign_rule_tbl)
        session.commit()
        message=f"rule code:{find_campaign_rule.rule_code} has been deactivated and rule code:{rule_code} is now active"
        new_rule=campaign_rules_tbl(camp_code=camp_code,rule_code=rule_code,date_rule_created=todaysdate,is_active=True)
        session.add(new_rule)
        session.commit()

        campaign_rules_logger.info(f"Campaign rule:{rule_code} activated")

        return UpdateCampaignRulesResponse(message=message,update_date=todaysdate)
    
    except Exception as e:
        return False

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

@campaign_rule_router.get("/{rule_name}",status_code=status.HTTP_200_OK)

async def fetch_rule_code(rule_name:str=Path(...,description="Provide the campaign code as the rule name"),session:Session=Depends(get_session),user=Depends(get_current_active_user)):
    try:
        rule_name_query=select(rules_tbl).where(rules_tbl.rule_name==rule_name)
        rule_name_entry=session.exec(rule_name_query).first()
        if rule_name_entry==None:
            campaign_rules_logger.info(f"user with id:{user.id} and email:{user.email} requested a campaign with rule name:{rule_name}")
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f"campaign rule with:{rule_name} does not exist")
        return rule_name_entry
    
    except Exception as e:
        campaign_rules_logger.error(f"{str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail=f"internal server error occurred while fetching campaign rule name:{rule_name}")

#change the rule code
@campaign_rule_router.patch("/{rule_name}",status_code=status.HTTP_200_OK)

async def change_rule_code(rule_name:int,rule_code:str,session:Session=Depends(get_session),user=Depends(get_current_active_user)):
    try:
        #find the campaign rule using the rule name
        rule_query=select(rules_tbl).where(rules_tbl.rule_name==rule_name)
        rule=session.exec(rule_query).first()
        if rule==None:
            campaign_rules_logger.info(f"user: {user.id}, email:{user.email} requested a change in rule name:{rule_name} but it does not exist")
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f"user: {user.id}, email:{user.email} requested a change in rule name:{rule_name} but it does not exist")
        
        rule.rule_code=rule_code
        session.add(rule)
        session.commit()
        session.refresh(rule)
        return rule
    
    except Exception as e:
        campaign_rules_logger.error(f"{str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail=f"An internal server error occurred")


#fetch all the rules on the database ,add pagination and search
@campaign_rule_router.get("",status_code=status.HTTP_200_OK,response_model=List[rules_tbl])

async def fetch_campaign_rules(session:Session=Depends(get_session),user=Depends(get_current_active_user)):
    try:
        rules_query=select(rules_tbl)
        campaign_rules=session.exec(rules_query).all()
        if len(campaign_rules)==0:
            campaign_rules_logger.info(f"user id:{user.id} with email:{user.email} requested all the campaign rules")
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f"No campaign rules have been created")
        campaign_rules_logger.info(f"user id:{user.id} with email:{user.email} retrieved camapign rule of this length:{len(campaign_rules)}")
        return campaign_rules
    except Exception as e:
        campaign_rules_logger.error(f"{str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail=f"Internal server error")

@campaign_rule_router.put("/{rule_code}")
async def assign_campaign_rule_to_campaign():
    try:
        return True
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail=f"An internal server error occurred while assigning campaign to campaign rule")


# We can't do hard delete, we need a soft delete field 
@campaign_rule_router.patch("/delete/{rule_code}")
async def delete_campaign_rule(rule_code:int,session:Session=Depends(get_session),user=Depends(get_current_active_user)):
    try:
        #find the rule using

        return True
    except Exception as e:
        
        return False