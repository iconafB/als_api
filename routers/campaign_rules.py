from fastapi import APIRouter,HTTPException,status,Depends
from sqlmodel import Session,select
from models.campaign_rules import campaign_rules
from schemas.sql_rule import Sql_Rules,Change_Active_Rule
from database.database import get_session
from utils.logger import define_logger

campaign_rule_router=APIRouter(tags=["Campaign Rules"],prefix="/campaign-rules")

#Take Care of the response model
@campaign_rule_router.post("",status_code=status.HTTP_201_CREATED,description="Create SQL Rule for filtering leads by providing the rule",response_model=campaign_rules)
async def create_campaign_rule(rule:Sql_Rules,session:Session=Depends(get_session)):
    
    try:
        #find the rule query
        exist_rule=select(campaign_rules).where(campaign_rules.rule_code==rule.rule_code)
         #execute the query
        query_rule=session.exec(exist_rule)

        if not query_rule.first()==None:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail=f"rule code:{rule.rule_code} already exist please choose another code")
       
        data=rule.model_dump()

        data_obj=campaign_rules.model_validate(data)

        session.add(data_obj)
        session.commit()
        session.refresh(data_obj)
        return data_obj
    except Exception as e:
        print("print the exception object")
        print(e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail="An intrnal server error occurred")



#assign campaign rule to a campaign
@campaign_rule_router.post("/assign-rule/{rule_code}",description="assign a campaign rule to a campaign")
async def assign_active_rule_to_campaign(camp_code:str):
    #fetch the campaign using the camp_code
    #fetch the rule using the rule code

    return {"message":"assign rule to campaign"}

#change an active rule
@campaign_rule_router.patch("/change-active-rule/{rule_code}",description="Provide a rule code to change an active rule")
async def update_active_rule(rule_code:str,incoming_rule:Change_Active_Rule,session:Session=Depends(get_session)):
    #find the rule using a rule code using the below query
    print("Print the incoming data")
    print(incoming_rule)
    rule_query=select(campaign_rules).where(campaign_rules.rule_code==rule_code)
    #execute the query
    rule=session.exec(rule_query).first()
    if rule == None:
        #raise an exception and break
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f"rule code:{rule_code} does not exist")
    print("Print the incoming rule")
    print(rule)
    #the below code is unacceptable

    #update the salary min and max
    if incoming_rule.max_salary !=rule.max_salary:
        print("print update max salary")
        rule.max_salary=incoming_rule.max_salary
        session.add(rule)
        session.commit()
    
    if incoming_rule.min_salary != rule.min_salary:
        print("print update minimum salary")
        rule.min_salary=incoming_rule.min_salary
        session.add(rule)
        session.commit()

    #update min and max age
    if incoming_rule.min_age != rule.min_age:
        print("print update min age")
        rule.min_age=incoming_rule.min_age
        session.add(rule)
        session.commit()

    if incoming_rule.max_age != rule.max_age:
        print("print update max age")
        rule.max_age=incoming_rule.max_age
        session.add(rule)
        session.commit()

    #update gender
    if incoming_rule.gender != rule.gender:
        print("print update gender")
        rule.gender=incoming_rule.gender
        session.add(rule)
        session.commit()

    #update city
    if incoming_rule.city != rule.city:
        print("print update city")
        rule.city=incoming_rule.city
        session.add(rule)
        session.commit()
    #update province
    if incoming_rule.province == rule.province:
        # update and commit the value(s)
        print("print update province")
        rule.province=incoming_rule.province

    #update the values and commit it using the session object
    data=rule.model_dump()
    #validate the data against the existing model
    data_obj=campaign_rules.model_validate(data)

    return data_obj

#activate an existing campaign
@campaign_rule_router.put("/activate-rule/{rule_code}",description="Activate the rule to use it on other leads")
async def activate_rule(rule_code:str,session:Session=Depends(get_session)):
    #find the campaign to activate
    query=select(campaign_rules).where(campaign_rules.rule_code==rule_code)
    #execute the query
    stmt=session.exec(query).first()
    if stmt==None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f"rule:{rule_code} code does not exist")
    stmt.is_active=True
    #assign a campaign to a campaign 
    session.add(stmt)
    #commit the session
    session.commit()
    session.refresh(stmt)

    return {"message":f"sql rule:{rule_code} is not active"}



#confirm the number of leads
@campaign_rule_router.get("/count-leads")
async def get_number_of_leads():
    return {"message":"calculate the number of leads"}