from fastapi import FastAPI
# from app.routers import auth, department, user
# from app.dependencies import database, setting
from sqlalchemy.orm import Session
from sqlalchemy import select
from contextlib import asynccontextmanager
from app.config import get_settings
from app.database import get_session
from app.auth.router import router as auth_router
from app.auth.utils import get_password_hash
from app.auth.models import User
from app.department.router import router as department_router
from app.employee.router import router as employee_router
import logging

settings = get_settings()

def create_first_superuser(db: Session) -> None:
    print("Checking for superuser...")
    username: str = settings.superuser_username
    password: str = settings.superuser_password

    if username == "" or password == "":
        logging.warning("Superuser credentials are not set. Skipping superuser creation.")
        return

    password_hashed: str = get_password_hash(password)
   
    stmt = select(User).where(User.username == username)

    user = db.scalars(stmt).one_or_none()

    if not user:
        new_user: User = User(
            username=username,
            password_hash=password_hashed
        )

        db.add(new_user)
        db.commit()
        db.refresh(new_user)

        print("Superuser created successfully.")
    
    else:
        print("Superuser already exists. Skipping creation.")

@asynccontextmanager
async def lifespan(app: FastAPI):
    db: Session = next(get_session())

    create_first_superuser(db)

    yield
    logging.info("Application shutdown")

app = FastAPI(lifespan=lifespan)

app.include_router(auth_router)
app.include_router(employee_router)
app.include_router(department_router)

@app.get("/healthcheck", include_in_schema=False)
def healthcheck():
    return {
        "msg": "OK"
    }