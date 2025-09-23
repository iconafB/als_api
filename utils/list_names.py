from fastapi import Depends,HTTPException
from sqlalchemy import distinct,func
from database.database import get_session
from models.leads import leads_history_table
from sqlmodel import Session,select
from datetime import datetime

def get_list_names(camp_code:str,session:Session=Depends(get_session)):

    try:
        #send the current time
        current_date=datetime.now().strftime("%Y-%m-%d")
        #test the current time
        #query the leads history table using the campaign name and the present date
        leads_query_count=select(func.count(distinct(leads_history_table.list_name))).where(leads_history_table.camp_code==camp_code and leads_history_table.created_at==current_date)
        #execute the query
        execute_the_leads_count_query=session.exec(leads_query_count)
        
        index=0
        if execute_the_leads_count_query==0:
            index=1
        else:
            index=execute_the_leads_count_query+1
        #close the session
        session.close() 
        #formulate the list name string
        list_name = camp_code + '_' + current_date[2:] + '_' + str(index) + 'CS'
        #return the list name

        return list_name
    
    except Exception as e:
        print("The exception object for getting the list name")
        print(e)
        return None
    



