from fastapi import APIRouter,status as http_status,Depends,Query,HTTPException
from sqlalchemy.ext.asyncio.session import AsyncSession
import os
import time
import pandas as pd
import re
from utils.logger import define_logger
from utils.status_data import get_status_tuple,insert_data_into_finance_table,insert_data_into_location_table,insert_data_into_contact_table,insert_data_into_employment_table,insert_data_into_car_table
from utils.auth import get_current_active_user
from schemas.insert_data import StatusData,EnrichedData
from schemas.status_data_routes import InsertStatusDataResponse,InsertEnrichedDataResponse
from database.master_db_connect import get_async_session

status_data_logger=define_logger("als status logger logs","logs/status_data.log")

insert_data_router=APIRouter(tags=["Data Insertion"],prefix="/insert-data")




@insert_data_router.post("/status_data",status_code=http_status.HTTP_200_OK,response_model=InsertStatusDataResponse)
#return the time taken for the queries, number of leads affected

async def insert_status_data(filename:str=Query(...,description="Provided the name of the filename with status data"),session:AsyncSession=Depends(get_async_session),user=Depends(get_current_active_user)):
    try:
        delta_time_1=time.time()
        status_data=[]
        #read a csv file that already exist on the server using the query parameter filename
        #check if the file exists
        if not os.path.exists(filename):
            raise HTTPException(status_code=http_status.HTTP_404_NOT_FOUND,detail=f"filename:{filename} does not exist on this system")
        
        #read the csv file into the pandas dataframe
        status_dataframe=pd.read_csv(filename)
        # convert the csv data into a list
        csv_list=status_dataframe.values.tolist()
        #append the uploaded list into the status data array
        status_data=status_data + csv_list
        #read the total number of leads
        leads_total=len(status_data)
        #seconds passed
        delta_time2=time.time()
        #total time difference
        total_time=delta_time2 - delta_time_1
        #rows list 
        rows=[]
        status_data=['0'+ str(row[15]) for row in status_data]

        for row in status_data:
            
            cell='0'+ str(row[15])

            if re.match('^(\d{10})?$', str(cell)):

                if row[1] is not None:
                    date_created_old=row[1].split('')[0]
                #test the id number if its has 13 characters
                idnum=str(row[3])
                salary=str(row[2])
                name = row[6]
                surname = row[7]
                address1 = row[9]
                address2 = row[10]
                suburb = row[11]
                city = row[12]
                postal = row[13]
                email = row[16]
                status = row[17]
                dob = idnum
                gender = idnum
                date_created=date_created_old

                result=StatusData(
                    idnum=idnum,
                    cell=cell,
                    date_created=date_created,
                    salary=salary,
                    name=name,
                    surname=surname,
                    address1=address1,
                    address2=address2,
                    suburb=suburb,
                    city=city,
                    postal=postal,
                    email=email,
                    status=status,
                    dob=dob,
                    gender=gender
                )

                #append the dictionary
                rows.append(result.model_dump())
             
            #test the rows list if it has the right information
            
            #run queries by making updates on the information table,location table,contact table,employment table,car_table,finance table
        
        for i in range(5):

            if i==1:
                insert_list=get_status_tuple(rows,i)
                if insert_list==False:
                    raise HTTPException(status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,detail=f"internal server error occurred")
                response=insert_data_into_finance_table(insert_list)
                if response==False:
                    raise HTTPException(status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,detail=f"an error occurred while updating the finance table")

            elif i==2:
                insert_list=get_status_tuple(rows,i)
                if insert_list==False:
                    raise HTTPException(status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,detail=f"internal server error occurred")

                response=insert_data_into_location_table(insert_list)
                if response==False:
                    raise HTTPException(status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,detail=f"internal server error occurred")

            elif i==3:
                insert_list=get_status_tuple(rows,i)
                if insert_list==False:
                    
                    raise HTTPException(status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,detail=f"internal server error occurred")

                response=insert_data_into_contact_table(insert_list)
                if response==False:
                    raise HTTPException(status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,detail=f"internal server error occurred")

            elif i==4:
                insert_list=get_status_tuple(rows,i)

                if insert_list==False:
                    raise HTTPException(status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,detail=f"internal server error occurred")

                response=insert_data_into_employment_table(insert_list)
                if response==False:
                    raise HTTPException(status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,detail=f"internal server error occurred")

            elif i==5:
                insert_list=get_status_tuple(rows,i)
                if insert_list==False:
                    raise HTTPException(status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,detail=f"internal server error occurred")

                response=insert_data_into_car_table(insert_list)
                if response==False:
                    raise HTTPException(status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,detail=f"internal server error occurred")

            else:
                insert_list=get_status_tuple(rows,i)
                if insert_list==False:
                    raise HTTPException(status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,detail=f"internal server error occurred")

                response=insert_data_into_finance_table(insert_list)
                if response==False:
                    raise HTTPException(status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,detail=f"internal server error occurred")

        status_data_logger.info(f"{len(rows)} updated on finance, car , location, employment, and finance table(e)")
        
        return InsertStatusDataResponse(number_of_leads=leads_total,status=True,time_taken=total_time,information_table=f"{len(rows)} rows updated",contact_table=f"{len(rows)} rows updated",location_table=f"{len(rows)} updated",car_table=f"{len(rows)} rows updated",finance_table=f"{len(rows)} rows updated")
    
    except Exception as e:
        status_data_logger.exception(f"an internal server error occurred while inserting status data:%s",{str(e)})
        raise HTTPException(status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,detail=f"{str(e)}")
    


@insert_data_router.post("/enriched_data",status_code=http_status.HTTP_200_OK,response_model=InsertEnrichedDataResponse)

async def insert_enriched_data(filename:str=Query(...,description="Provide the name for excel filename with status data")):
    try:
        data_extraction_time_start=time.time()

        try:
            all_sheets=pd.read_excel(filename + '.xlsx',sheet_name=None,dtype=str)
            sheets=all_sheets.keys()

        except Exception as e:
            #you have log this
            raise HTTPException(status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,detail=f"{str(e)}")
        
        for sheet_name in sheets:
            sheet=pd.read_excel(filename,'.xlsx',sheet_name=sheet_name)
            sheet.to_csv(f"{sheet_name}.csv",index=False)
        
        enriched_data=[]

        detected_csv=[i for i in os.listdir() if i.endswith(".csv")]

        for d in detected_csv:

            csv_frame=pd.read_csv(d)

            csv_list=csv_frame.values().tolist()
            #append the contents of csv_list into the enriched data list
            enriched_data.extend(csv_list)
        
        total_leads=len(enriched_data)

        data_extraction_time_end=time.time()

        total_data_extraction_time=data_extraction_time_end - data_extraction_time_start

        rows_list=[]

        for e in enriched_data:

            Title=e[0]
            forename=e[1]
            lastname=e[2]
            IDNo=e[3]
            Race=e[4]
            gender=e[5]
            marital_status=e[6]
            line1=e[7]
            line2=e[8]
            line3=e[9]
            line4=e[10]
            PCode=e[11]
            Province=e[12]
            Home_Number=e[13]
            Work_Number=e[14]
            mobile_Number = e[15]
            mobile_Number2 = e[16]
            mobile_Number3 = e[17]
            mobile_Number4 = e[18]
            mobile_Number5 = e[19]
            mobile_Number6 = e[20]
            derived_income = e[21]

            cipro_reg = e[22]
            Deed_office_reg = e[23]
            vehicle_owner = e[24]
            cr_score_tu = e[25]
            monthly_expenditure = e[26]
            owns_cr_card = e[27]
            cr_card_rem_bal = e[28]
            owns_st_card = e[29]
            st_card_rem_bal = e[30]
            has_loan_acc = e[31]
            loan_acc_rem_bal = e[32]
            has_st_loan = e[33]
            st_loan_bal = e[34]
            has_1mth_loan = e[35]
            onemth_loan_bal = e[36]
            sti_insurance = e[37]
            has_sequestration = e[38]
            has_admin_order = e[39]
            under_debt_review = e[40]
            deceased_status = e[41]
            has_judgements = e[42]
            make = e[43]
            model = e[44]
            year = e[45]
            birth_date = e[3]

            new_convert = EnrichedData(Title=Title, forename=forename, lastname=lastname, IDNo=IDNo,Race=Race,gender=gender, Marital_Status=marital_status, line1=line1,line2=line2,line3=line3, line4=line4, PCode=PCode, Province=Province,Home_number=Home_Number, Work_number=Work_Number,mobile_Number=mobile_Number, mobile_Number2=mobile_Number2,mobile_Number3=mobile_Number3, mobile_Number4=mobile_Number4,mobile_Number5=mobile_Number5, mobile_Number6=mobile_Number6,derived_income=derived_income, cipro_reg=cipro_reg,Deed_office_reg=Deed_office_reg, vehicle_owner=vehicle_owner,cr_score_tu=cr_score_tu, monthly_expenditure=monthly_expenditure,owns_cr_card=owns_cr_card, cr_card_rem_bal=cr_card_rem_bal,owns_st_card=owns_st_card, st_card_rem_bal=st_card_rem_bal,has_loan_acc=has_loan_acc, loan_acc_rem_bal=loan_acc_rem_bal,has_st_loan=has_st_loan, st_loan_bal=st_loan_bal,has_1mth_loan=has_1mth_loan, onemth_loan_bal=onemth_loan_bal,sti_insurance=sti_insurance, has_sequestration=has_sequestration,has_admin_order=has_admin_order, under_debt_review=under_debt_review,deceased_status=deceased_status, has_judgements=has_judgements,make=make,model=model, year=year, birth_date = birth_date)

            rows_list.append(new_convert.model_dump())
        

        insertion_time1=time.time()

        for i in range(5):

            if i==1:
                insert_list=get_status_tuple(rows_list,i)
                if insert_list==False:
                    raise HTTPException(status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,detail=f"an internal server error occurred while generating a list for the finance table")
                response=insert_data_into_finance_table(insert_list)
                if response==False:
                    raise HTTPException(status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,detail=f"An internal server error occurred while inserting data into the finance table")
            elif i==2:
                insert_list=get_status_tuple(rows_list,i)
                if insert_list==False:
                    raise HTTPException(status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,detail="An internal server error occurred while generating a list for location table")
                response=insert_data_into_location_table(insert_list)
                if response==False:
                    raise HTTPException(status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,detail="An internal server error occurred while inserting data on the location table")
            elif i==3:
                insert_list=get_status_tuple(rows_list,i)
                if insert_list==False:
                    raise HTTPException(status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,detail="An internal server error occurred while generating a list for the contact table")
                response=insert_data_into_contact_table(rows_list)
                if response==False:
                    raise HTTPException(status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,detail="An internal server error occurred while inserting a list on the contact table")
            elif i==4:
                insert_list=get_status_tuple(rows_list,i)
                if insert_list==False:
                    raise HTTPException(status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,detail="An internal server error occurred while generating a list for the employment table")
                response=insert_data_into_employment_table(rows_list)
                if response==False:
                    raise HTTPException(status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,detail="An internal server error occurred while insrting to the employment table")
            elif i==5:
                insert_list=get_status_tuple(rows_list,i)
                if insert_list==False:
                    raise HTTPException(status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,detail="An internal server error occurred while generating a list for the car table")
                response=insert_data_into_car_table(insert_list)

                if response==False:
                    raise HTTPException(status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,detail="An internal server error occurred while inserting to the car table")
            else:
                insert_list=get_status_tuple(rows_list,i)

                if insert_list==False:
                    raise HTTPException(status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,detail="An internal server error occurred while generating a list for the finance table")
                response=insert_data_into_finance_table(insert_list)
                if response==False:
                    raise HTTPException(status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,detail="An internal server error occurred while inserting data into the finance table")
                
        insertion_time2=time.time()
        
        total_insertion_time=insertion_time2 - insertion_time1

        return InsertEnrichedDataResponse(number_of_leads=total_leads,status=True,data_extraction_time=total_data_extraction_time,data_insertion_time=total_insertion_time,contact_table=f"Contact table updated with:{len(enriched_data)} records",location_table=f"location table updated with:{len(enriched_data)} records",car_table=f"car table updated with:{len(enriched_data)} records",finance_table=f"finance table updated with:{len(enriched_data)} recorda")
    except Exception as e:
        #you need log here
        status_data_logger.error(f"{str(e)}")
        raise HTTPException(status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,detail=f"{str(e)}")

