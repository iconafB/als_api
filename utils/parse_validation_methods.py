from fastapi import HTTPException,status,Request,Depends,Form
from schemas.campaign_rules import RuleCreate
from utils.logger import define_logger
from utils.auth import get_current_active_user
from typing import Annotated
from pydantic import ValidationError


campaign_rules_logger=define_logger("als campaign rules","logs/campaign_rules_logs")

async def parse_and_validate_rule(request:Request,user=Depends(get_current_active_user)):
    
    content_type=request.headers.get("content-type","").lower()

    if content_type.startswith("application/json"):
        raw_data=await request.json()
    elif (content_type.startswith("multipart/form-data") or content_type.startswith("application/x-www-form-urlencoded")):
        form=await request.form()
        raw_data={k:v for k,v in form.items()}
    else:
        raise HTTPException(status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,detail=f"Unsupported content type: {content_type}")
    try:
        validated=RuleCreate(**raw_data)
    
    except ValidationError as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,detail=e.errors())
    
    except HTTPException:
        raise

    except Exception as e:
        campaign_rules_logger.exception(f"user id:{user.id},user email:{user.email},parsing data failed for campaign rules:{str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail=f"An internal server error occurred while parsing campaign rule")
    
    return validated
