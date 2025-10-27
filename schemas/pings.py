from pydantic import BaseModel
from typing import Union

class PingStatusPayload(BaseModel):
    telnr:str
    duration:Union[str,None]='Null'
    lead_id:int
    status:str

class PingStatusResponse(BaseModel):
    status_code:str
    message:str

class PingStatusUpdateResponse(BaseModel):
    message:str
    status:bool
    pings_updated:int

class SendPingsToDedago(BaseModel):
    message:str
    pings_sent:int
