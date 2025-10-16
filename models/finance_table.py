from sqlmodel import SQLModel,Field
from typing import Optional
from datetime import datetime
from sqlalchemy import func


#Indexes the tables fool

class finance_table(SQLModel,table=True):
    
    cell_number:str=Field(primary_key=True,nullable=False,default=None)
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


class car_table(SQLModel):
    cell_number:str=Field(nullable=False,default=None)
    make:str=Field(nullable=False,default=None)
    model:str=Field(nullable=False,default=None)
    year:str=Field(nullable=False,default=None)

class employment_table(SQLModel):
    cell_number:str=Field(primary_key=True,nullable=False,default=None)
    job:str=Field(nullable=False,default=None)
    occupation:str=Field(nullable=False,default=None)
    company:str=Field(nullable=False,default=None)


class location_table(SQLModel):
    cell_number:str=Field(primary_key=True,nullable=False,default=None)
    line_one:str=Field(nullable=False,default=None)
    line_two:str=Field(nullable=False,default=None)
    line_three:str=Field(nullable=False,default=None)
    line_four:str=Field(nullable=False,default=None)
    postal_code:str=Field(nullable=False,default=None)
    suburb:str=Field(nullable=False,default=None)
    city:str=Field(nullable=False,default=None)




""" 
able "location_tbl" { 
"cell" varchar [pk] 
"line_one" varchar 
"line_two" varchar 
"line_three" varchar 
"line_four" varchar 
"postal_code" varchar 
"province" varchar 
"suburb" varchar 
"city" varchar 
} 
 """

""" Table "employment_tbl" { 
"cell" varchar [pk] 
"job" varchar 
"occupation" varchar 
"company" varchar 
} """



""" 
"cell" varchar [pk] 
"make" varchar 
"model" varchar 
"year" varchar 
}  """



""" 
Table "finance_tbl" { 
"cell" varchar [pk] 
"cipro_reg" boolean 
"deed_office_reg" boolean 
"vehicle_owner" boolean 
"credit_score" float 
"monthly_expenditure" float 
"owns_credit_card" boolean 
"credit_card_bal" float 
"owns_st_card" boolean 
"st_card_rem_bal" float 
"has_loan_acc" boolean 
"loan_acc_rem_bal" float 
"has_st_loan" boolean 
"st_loan_bal" float 
"has1mth_loan_bal" boolean 
"bal_1mth_load" float 
"sti_insurance" boolean 
"has_sequestration" boolean 
"has_admin_order" boolean 
"under_debt_review" boolean 
"has_judgements" boolean 
"bank" varchar 
"bal" float 
} 

 """