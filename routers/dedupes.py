from fastapi import APIRouter,HTTPException,status,Depends,UploadFile,File,Query
from sqlmodel import Session
import openpyxl
from io import BytesIO
import os
from models.campaigns import Campaign_Dedupes
from database.database import get_session

dedupe_routes=APIRouter(tags=["Dedupes"],prefix="/dedupes")

@dedupe_routes.post("/add-dedupes-manually")

async def add_dedupes_manually(campaign_name:str=Query(description="Please provide the campaign name"),file:UploadFile=File(...,description="Please provide a file for a manual dedupe"),session:Session=Depends(get_session)):
    
    #we are going to use these rows
    all_rows=[]

    file_path=f"temp_{file.filename}"

    #check the extension of the file format being uploaded
    if not file.filename.endswith((".csv",".xlsx",".xls")):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="Invalid file format")
    
    try:
        #read the file's content into a BytesIO object(memory file)
        file_content=await file.read()
        file_stream=BytesIO(file_content)

        if file.filename.endswith(".csv"):
            #csv processing logic
            pass
        else:
            #check the campaign codes chiefs??
            workbook=openpyxl.load_workbook(file_stream,read_only=True)

            for sheet in workbook.worksheets:
                extracted_data=[
                  [
                      str(row[0] if row[0] is not None else ""),
                      str(row[1] if row[1] is not None else "")
                  ]
                  for row in sheet.iter_rows(min_col=1,max_col=2,values_only=True)
                  if row[0] is not None or row[1] is not None
                ]
                
                all_rows.extend(extracted_data)
                
            #insert the data into the campaign_dedupe using bulk insert, we still need the campaign name and is_verified field filled
            data_to_insert=[
                {
                    "id_number":row[0],
                    "cell_number":row[1],
                    "campaign_codes":campaign_name,
                    "is_verified":True
                }
                for row in all_rows
            ]
            session.bulk_insert_mappings(Campaign_Dedupes,data_to_insert)
            session.commit()
            session.close()

            return {"message":f"file with name:{file.filename} for campaign:{campaign_name} uploaded successfully"}

    except Exception as e:
        if os.path.exists(file_path):
            os.remove(file_path)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail=f"{str(e)}")
    
    finally:
        #close the session
        session.close()
    

# this should an automated script that polls the dmasa api and post it to vc dial
@dedupe_routes.post("/submit-dedupe-return")
async def submit_dedupe_return():

    return {"message":"submit dedupe return"}

#get the rowcount to get the number leads
