from sqlmodel import SQLModel,Field,Relationship
from typing import Optional
from datetime import datetime
from sqlalchemy import func
from models.contact_table import contact_tbl
#Indexes the tables fool

class finance_tbl(SQLModel,table=True):
    cell:str=Field(primary_key=True,default=None,foreign_key="contact_tbl.cell")
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
    
    contact:Optional[contact_tbl]=Relationship(back_populates="finance_tbl")



