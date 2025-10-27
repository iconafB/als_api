from fastapi import APIRouter,Depends,status,HTTPException,Query
from sqlmodel import select,Session
from database.database import get_session
from models.pings import blacklist_tbl
from schemas.black_list import BlackListCreate
from typing import List
from utils.auth import get_current_user
black_router=APIRouter(tags=["Black List"],prefix="/blacklist")

# blacklist a number
@black_router.post("",description="Provide a number to black list",status_code=status.HTTP_201_CREATED,response_model=blacklist_tbl)
async def black_list_number(black_list:BlackListCreate,session:Session=Depends(get_session),user=Depends(get_current_user)):
    #search the database for the number first to prevent blacklisting number twice you fool
    black_listed_number=select(blacklist_tbl).where(blacklist_tbl.cell== black_list.cell_number)
    #execute the query
    query=session.exec(black_listed_number).first()
    #validate if the cell number is blacklisted

    """ if query.cell_number == None and query.created_at == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f"cell number:{black_list.cell_number} is not blacklisted")
     """
    
    data=black_list.model_dump()
    # get a dmasa status using the number from somewhere
    obj_data=blacklist_tbl.model_validate(data)
    session.add(obj_data)
    session.commit()
    session.refresh(obj_data)
    
    return obj_data

# get the full black list
@black_router.get("",description="Get all the blacklisted cell number",response_model=List[blacklist_tbl])
async def get_black_listed_number(session:Session=Depends(get_session),user=Depends(get_current_user)):
    #paginate the query
    query=select(blacklist_tbl).where(blacklist_tbl.dmasa_status==True)
    statement=session.exec(query).all()
    if not statement:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Error while fetching blacklisted numbers")
    return statement