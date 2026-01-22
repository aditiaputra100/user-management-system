from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jwt.exceptions import InvalidTokenError
from sqlalchemy.orm import Session
from sqlalchemy import select
from typing import Annotated
from datetime import datetime, timezone
from app.config import get_settings
from app.database import get_session
from .utils import verify_password
from .models import User
import jwt

settings = get_settings()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")

SECRET_KEY: str = settings.secret_key
ALGORITHM: str = settings.algorithm
ACCESS_TOKEN_EXPIRE_MINUTES: int = settings.access_token_expire_minutes

def get_current_user(token: Annotated[str, Depends(oauth2_scheme)], db: Session = Depends(get_session)) -> User:
    credential_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=ALGORITHM)
        username: str = payload.get("sub")

        if username is None:
            raise credential_exception
        
    except InvalidTokenError:
        raise credential_exception
    
    stmt = select(User).where(User.username == username)
    user: User = db.scalars(stmt).one_or_none()

    if user is None:
        raise credential_exception
    
    return user

def authenticate_user(username: str, password: str, db: Session) -> User | None:
    stmt = select(User).where(User.username == username)
    incorect_exception = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect username or password", headers={"WWW-Authenticate": "Bearer"})

    try:
        user = db.scalars(stmt).one_or_none()
    except Exception as err:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(err))

    if user is None:
        raise incorect_exception

    if not verify_password(password, user.password_hash):
        raise incorect_exception
    
    if user.status != "active":
        raise HTTPException(status_code=status.HTTP_423_LOCKED, detail="Inactive user")

    user.last_active = datetime.now(timezone.utc)
    
    db.commit()
    db.flush(user)

    return user