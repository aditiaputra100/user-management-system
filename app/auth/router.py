from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from typing import Annotated
from sqlalchemy.orm import Session
from datetime import datetime, timedelta, timezone
from pydantic import EmailStr
from app.database import get_session
from app.employee.service import get_by_email
from .constants import ACCESS_TOKEN_EXPIRE_MINUTES, SECRET_KEY, ALGORITHM
from .dependencies import authenticate_user, get_current_user
from .schemas import Token, UserSchema
from .models import User
from .utils import verify_password
import jwt

router = APIRouter(tags=["Authentication"])

def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=30)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    return encoded_jwt

@router.post("/login", response_model=Token)
def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], db: Annotated[Session, Depends(get_session)]) -> Token:
    username: str = form_data.username
    password: str = form_data.password

    user = authenticate_user(username, password, db)

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={
            "sub": user.username,
        },
        expires_delta=access_token_expires
    )

    return Token(
        access_token=access_token,
        token_type="bearer"
    )

@router.get("/me")
def read_users_me(current_user: Annotated[User, Depends(get_current_user)]) -> UserSchema:
    return UserSchema(
        username=current_user.username,
        status=current_user.status,
        last_active=current_user.last_active if current_user.last_active else None
    )

@router.put("/me/change-password")
def change_password(password: str, current_user: Annotated[User, Depends(get_current_user)], db: Annotated[Session, Depends(get_session)]):
    new_password: str = password

    if verify_password(new_password, current_user.password_hash):
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail="The password cannot be the same as the old one")
    
    try:
        current_user.reset_password(new_password)
        db.commit()
    except ValueError as err:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail=str(err))

    return {
        "msg": "Your password has been changed successfully"
    }

@router.post("/forgot-password", status_code=status.HTTP_204_NO_CONTENT)
def forgot_password(email: EmailStr, db: Annotated[Session, Depends(get_session)]):
    employee = get_by_email(email=email, db=db)

    if employee is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Employee with this email does not exist")
    
    if employee.user is None:
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, detail="User account for this employee does not exist")
    
    if employee.user.status != "active":
        raise HTTPException(status.HTTP_423_LOCKED, detail="User account is not active")
    
