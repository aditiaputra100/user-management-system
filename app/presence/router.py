from fastapi import APIRouter, Depends, HTTPException, status
from typing import Annotated
from sqlalchemy.orm import Session
from app.database import get_session
from app.auth.dependencies import get_current_user
from app.auth.models import User
from .models import StatusType
from .service import create_presence
import uuid

router = APIRouter(prefix="/presence", tags=["Employee", "Presence"])

@router.post("/", status_code=status.HTTP_201_CREATED)
def presence(status_type: StatusType, current_user: Annotated[User, Depends(get_current_user)], db: Annotated[Session, Depends(get_session)]):
    try:
        create_presence(status_type, current_user.employee.id, db)
    except ValueError as err:
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE, detail=str(err))
    
    return {
        "msg": "Success created presence today"
    }