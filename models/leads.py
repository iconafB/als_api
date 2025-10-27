from sqlalchemy import func
from sqlmodel import SQLModel,Field
from typing import Optional
from datetime import datetime


class info_tbl(SQLModel,table=True):
    cell:Optional[str]=Field(primary_key=True,nullable=False,default=None)
    id:str=Field(nullable=False,default=None)
    title:str|None=Field(nullable=False,default=None)
    fore_name:str|None=Field(nullable=False,default=None)
    last_name:str | None=Field(nullable=False,default=None)
    date_of_birth: str =Field(nullable=False,default=None)
    race:str | None=Field(nullable=False,default=None)
    gender:str | None=Field(nullable=False,default=None)
    marital_status:str | None=Field(nullable=False,default=None)
    salary:float=Field(nullable=False,default=None)
    status:str | None=Field(nullable=False,default=None)
    derived_income:float=Field(nullable=False,default=None)
    type_data:str | None=Field(nullable=False,default=None)
    last_used:Optional[datetime]=Field(nullable=False,default=None)
    extra_info:str | None=Field(nullable=False,default=None)
    created_at:Optional[datetime]=Field(sa_column_kwargs={"server_default":func.now()},nullable=False,default=None)


class lead_history_tbl(SQLModel,table=True):
    #serial primary key, increment
    lead_pk:Optional[int]=Field(primary_key=True,default=None,nullable=False)
    cell:str=Field(default=None,nullable=False)
    camp_code:str=Field(default=None,nullable=False)
    date_used:datetime=Field(default=None,nullable=False)
    list_id:str=Field(default=None,nullable=False)
    list_name:str=Field(default=None,nullable=False)
    load_type:str=Field(default=None,nullable=False)
    rule_code:int=Field(default=None,nullable=False)
    created_at:Optional[datetime]=Field(sa_column_kwargs={"server_default":func.now()},nullable=False,default=None)

    #rule code is on the table, pay attention to it


class car_tbl(SQLModel,table=True):
    cell_number:str=Field(primary_key=True,default=None,nullable=False)
    make:str=Field(default=None,nullable=False)
    model:str=Field(default=None,nullable=False)
    year:str=Field(default=None,nullable=False)
    created_at:Optional[datetime]=Field(sa_column_kwargs={"server_default":func.now()},nullable=False,default=None)


class employment_tbl(SQLModel,table=True):
    cell:Optional[str]=Field(primary_key=True,default=None,nullable=False)
    job:str=Field(nullable=False,default=None)
    occupation:str=Field(default=None,nullable=False)
    campany:str=Field(default=None,nullable=False)
    #created_at:Optional[datetime]=Field(sa_column_kwargs={"server_default":func.now()},nullable=False,default=None)


class location_tbl(SQLModel,table=True):
    cell:str=Field(primary_key=True,default=None,nullable=False)
    line_one:str=Field(default=None,nullable=False)
    line_two:str=Field(default=None,nullable=False)
    line_three:str=Field(default=None,nullable=False)
    line_four:str=Field(default=None,nullable=False)
    postal_code:str=Field(default=None,nullable=False)
    province:str=Field(default=None,nullable=False)
    surburb:str=Field(default=None,nullable=False)
    city:str=Field(default=None,nullable=False)


class finance_tbl(SQLModel,table=True):
    cell:str=Field(primary_key=True,nullable=False,default=None)
    cipro_reg:bool=Field(nullable=False,default=None)
    deed_office_reg:bool=Field(nullable=False,default=None)
    vehicle_owner:bool=Field(nullable=False,default=None)
    credit_score:float=Field(nullable=False,default=None)
    monthly_expenditure:float=Field(nullable=False,default=None)
    owns_credit_card:bool=Field(nullable=False,default=None)
    owns_st_card:bool=Field(nullable=False,default=None)
    credit_card_bal:float=Field(nullable=False,default=None)
    st_card_rem_bal:float=Field(nullable=False,default=None)
    has_loan_acc:bool=Field(nullable=False,default=None)
    loan_acc_rem_bal:float=Field(nullable=False,default=None)
    has_st_loan:float=Field(nullable=False,default=None)
    st_loan_bal:float=Field(nullable=False,default=None)
    has1mth_loan_bal:bool=Field(nullable=False,default=None)
    bal_1mth_load:float=Field(nullable=False,default=None)
    sti_insurance:bool=Field(nullable=False,default=None)
    has_sequestration:bool=Field(nullable=False,default=None)
    has_admin_order:bool=Field(nullable=False,default=None)
    under_debt_review:bool=Field(nullable=False,default=None)
    has_judgements:bool=Field(nullable=False,default=None)
    bank:str=Field(nullable=False,default=None)
    bal:float=Field(nullable=False,default=None)

    #created_at:Optional[datetime]=Field(sa_column_kwargs={"server_default":func.now()},nullable=False,default=None)


class contact_tbl(SQLModel,table=True):
    cell:Optional[str]=Field(primary_key=True,nullable=False,default=None)
    home_number:str=Field(nullable=True,default=None)
    work_number:str=Field(nullable=True,default=None)
    mobile_number_one:str=Field(nullable=True,default=None)
    mobile_number_two:str=Field(nullable=True,default=None)
    mobile_number_three:str=Field(nullable=True,default=None)
    email:str=Field(nullable=True,default=None)
    
