import re
from typing import Optional
from datetime import datetime
from pydantic import BaseModel, field_validator
class InsertStatusDataResponse(BaseModel):
    number_of_leads:int
    status:bool
    time_taken:int
    information_table:str
    contact_table:str
    location_table:str
    car_table:str
    finance_table:str

class InsertEnrichedDataResponse(BaseModel):
    number_of_leads:int
    status:bool
    data_insertion_time:int
    data_extraction_time:int
    information_table:str
    contact_table:str
    location_table:str
    car_table:str
    finance_table:str







class StatusedData(BaseModel):
    
    idnum: Optional[str] = None
    cell: str
    date_created: Optional[str] = None
    salary: Optional[float] = None
    name: Optional[str] = None
    surname: Optional[str] = None
    address1: Optional[str] = None
    address2: Optional[str] = None
    suburb: Optional[str] = None
    city: Optional[str] = None
    postal: Optional[str] = None
    email: Optional[str] = None
    status: Optional[str] = None
    dob: Optional[str] = None
    gender: Optional[str] = None
    company: Optional[str] = None
    job: Optional[str] = None
    car: Optional[str] = None
    model: Optional[str] = None
    bank: Optional[str] = None
    bal: Optional[float] = None

    # ----------------------
    # Global cleaning for all fields
    # ----------------------
    @field_validator('*', mode='before')
    @classmethod
    def clean_empty_and_null(cls, value):
        if isinstance(value, str):
            if value.strip().lower() in {"", "null", "nan"}:
                return None
        return value

    # ----------------------
    # Field-specific validators
    # ----------------------
    @field_validator('idnum')
    @classmethod
    def validate_idnum(cls, value):
        if value and re.match(r'^\d{13}$', value):
            return value
        return None

    @field_validator('postal')
    @classmethod
    def validate_postal(cls, value):
        if value and isinstance(value, str):
            value = value.split('.')[0] if '.' in value else value
            if value.isdigit() and 4 <= len(value) <= 5:
                return value
        return None

    @field_validator('dob', mode='before')
    @classmethod
    def validate_dob(cls, value):
        if not value or not isinstance(value, str):
            return None
        try:
            if re.match(r'^\d{13}$', value):
                prefix = '20' if int(value[:2]) <= 30 else '19'
                year = prefix + value[:2]
                month = value[2:4]
                day = value[4:6]
                datetime(int(year), int(month), int(day))  # validation
                return f"{year}-{month}-{day}"
        except:
            return None
        return None

    @field_validator('date_created', mode='before')
    @classmethod
    def validate_date_created(cls, value):
        if not value or not isinstance(value, str):
            return None
        try:
            if '/' in value:
                day, month, year_time = value.split('/')
                year_parts = re.split(r'\D+', year_time.strip())
                year = year_parts[0]
                dt = datetime(int(year), int(month), int(day))
                return dt.strftime("%Y-%m-%d")
            else:
                dt = datetime.strptime(value, "%Y-%m-%d")
                return dt.strftime("%Y-%m-%d")
        except:
            return None

    @field_validator('gender', mode='after')
    @classmethod
    def extract_gender_from_id(cls, value, info):
        idnum = info.data.get('idnum')
        if idnum and re.match(r'^\d{13}$', idnum):
            gender_digit = int(idnum[6])
            return "FEMALE" if gender_digit <= 4 else "MALE"
        return None

