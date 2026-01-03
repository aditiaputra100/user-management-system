from fastapi import FastAPI
from app.routers import auth, department, user
from app.dependencies import database, setting
from app.models.user import User
from sqlalchemy.orm import Session
from sqlalchemy import select
from contextlib import asynccontextmanager
import logging

settings = setting.get_settings()

def create_first_superuser(db: Session) -> None:
    print("Checking for superuser...")
    username: str = settings.superuser_username
    password: str = settings.superuser_password

    if username == "" or password == "":
        logging.warning("Superuser credentials are not set. Skipping superuser creation.")
        return

    password_hashed: str = auth.get_password_hash(password)
   
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
    db: Session = next(database.get_session())

    create_first_superuser(db)

    yield
    logging.info("Application shutdown")

app = FastAPI(lifespan=lifespan)

app.include_router(auth.router)
app.include_router(department.router)
app.include_router(user.router)

@app.get("/")
def hello_world():
    return {
        "Hello": "World"
    }