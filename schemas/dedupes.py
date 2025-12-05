from sqlmodel import SQLModel
from pydantic import BaseModel

class DedupesSchema(SQLModel):
    cell_numbers:str
    id_numbers:str
    campaign_name:str
    status:str


class DataInsertionSchema(BaseModel):
    data_extraction_time:str
    insertion_time:str
    number_of_leads:int
    Success:bool

    
class AddDedupeListResponse(BaseModel):
    FileName:str
    TotalRecordsInserted:int
    TotalBatches:int
    TotalBatchedTime:int
    TotalTimeTaken:int
    DedupeKey:str



class SubmitDedupeReturnResponse(BaseModel):
       success:bool
       updated_ids_with_return_status:int
       retrieved_pending_ids_from_campaign_dedupe_table:int
       deleted_pending_ids_from_campaign_dedupe_table:int
       updated_ids_from_info_tbl:int
       deleted_pending_ids_with_status_code_u:int


class AddManualDedupeResponse(BaseModel):
     success:bool
     campaign_dedupe_records:int
     info_table_records:int
     key:int


