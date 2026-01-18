from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pwdlib import PasswordHash
from typing import Annotated
from sqlalchemy import select
from sqlalchemy.orm import Session
from sqlalchemy.exc import NoResultFound
from app.dependencies.database import get_session
from app.models.user import User
from app.dependencies.setting import get_settings
from datetime import datetime, timedelta, timezone
from app.schemas import Token, UserResponse, PasswordRequest
from jwt.exceptions import InvalidTokenError
import jwt

settings = get_settings()

SECRET_KEY: str = settings.secret_key
ALGORITHM: str = settings.algorithm
ACCESS_TOKEN_EXPIRE_MINUTES: int = settings.access_token_expire_minutes

password_hash = PasswordHash.recommended()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/signin")

router = APIRouter(tags=["Authentication"])

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return password_hash.verify(plain_password, hashed_password)

def get_password_hash(password: str):
    return password_hash.hash(password)

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
        
    except InvalidTokenError as err:
        raise credential_exception
    
    stmt = select(User).where(User.username == username)
    user: User = db.scalars(stmt).one_or_none()

    if user is None:
        raise credential_exception
    
    return user

def authenticate_user(username: str, password: str, db: Session) -> User | None:
    stmt = select(User).where(User.username == username)
    
    try:
        user = db.scalars(stmt).one()
    except NoResultFound:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect username or password", headers={"WWW-Authenticate": "Bearer"})
    except Exception as err:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(err))

    if not verify_password(password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect username or password", headers={"WWW-Authenticate": "Bearer"})

    if user.status != "active":
        raise HTTPException(status_code=status.HTTP_423_LOCKED, detail="Inactive user")

    return user

def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=30)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    return encoded_jwt

@router.post("/auth/signup", status_code=status.HTTP_201_CREATED)
def signup(current_user: Annotated[UserResponse, Depends(get_current_user)]):
    if current_user.status != "active":
        raise HTTPException(status.HTTP_403_FORBIDDEN, detail="Only active users can create new users")
    


@router.post("/auth/signin", response_model=Token)
def signin(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], db: Session = Depends(get_session)) -> Token:
    username: str = form_data.username
    password: str = form_data.password

    user = authenticate_user(username, password, db)

    user.last_active = datetime.now(timezone.utc)
    
    db.commit()
    db.flush(user)

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

@router.get("/user/me", response_model=UserResponse)
def read_users_me(current_user: Annotated[UserResponse, Depends(get_current_user)]):
    return current_user

@router.put("/user/password")
def update_password(password: PasswordRequest, current_user: Annotated[UserResponse, Depends(get_current_user)], db: Session = Depends(get_session)):
    new_password: str = password.password

    stmt = select(User).where(User.username == current_user.username)
    user = db.scalars(stmt).one_or_none()

    if user is None:
        raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    if verify_password(new_password, user.password_hash):
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail="The password cannot be the same as the old one")
    
    password_hashed: str = get_password_hash(new_password)
    user.password_hash = password_hashed

    db.commit()
    db.flush(user)

    return {
        "msg": "Your password has been changed successfully"
    }

