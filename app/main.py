from fastapi import FastAPI
# from app.routers import auth, department, user
# from app.dependencies import database, setting
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from sqlalchemy import select, insert
from contextlib import asynccontextmanager
from app.config import get_settings
from app.database import get_session, list_of_tables
from app.auth.router import router as auth_router
from app.auth.utils import get_password_hash
from app.auth.models import User
from app.policy.models import Role, Permission, role_permissions
from app.department.router import router as department_router
from app.employee.router import router as employee_router
from app.presence.router import router as presence_router
from app.policy.router import role_router, permission_router
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
            password_hash=password_hashed,
            is_superuser=True
        )

        db.add(new_user)
        db.commit()
        db.refresh(new_user)

        print("Superuser created successfully.")
    
    else:
        print("Superuser already exists. Skipping creation.")

# Create role system administrator
def create_role_sa(db: Session):
    role = Role(
        name="System Administrator",
        description="Full access of management and system configuration"
    )

    try:
        db.add(role)
        db.commit()
        db.refresh(role)

        stmt = select(Permission.id)
        permissions_ids = db.scalars(stmt).all()

        role_permissions_to_insert = [
            {
                "role_id": role.id,
                "permission_id": permission_id
            }
            for permission_id in permissions_ids
        ]

        db.execute(role_permissions.insert(), role_permissions_to_insert)
        db.commit()

    except IntegrityError:
        db.rollback()
        print("System Administrator had already created")

    except Exception as err:
        db.rollback()
        print("Failed to create system administrator")

# Create all permissions for all resource
def create_all_permissions(db: Session):
    actions = ["create", "read", "update", "delete", "list"]

    resources = list_of_tables
    permissions: list[Permission] = []

    for resource in resources:
        if "alembic" in resource:
            continue
        
        name = " ".join(resource.split("_")).capitalize()

        for action in actions:
            permission = Permission(
                name=f"{action.capitalize()} {name}",
                resource=resource,
                action=action,
                description="",
            )

            permissions.append(permission)

    try:
        db.add_all(permissions)
        db.commit()

    except IntegrityError as err:
        db.rollback()
        print("All permission had already created")

    except Exception:
        db.rollback()
        print("Failed to create all permissions")

@asynccontextmanager
async def lifespan(app: FastAPI):
    db: Session = next(get_session())

    create_first_superuser(db)
    # create_all_permissions(db)
    # create_role_sa(db)

    yield
    logging.info("Application shutdown")

app = FastAPI(lifespan=lifespan)

app.include_router(auth_router)
app.include_router(employee_router)
app.include_router(department_router)
app.include_router(presence_router)
app.include_router(role_router)
app.include_router(permission_router)

@app.get("/healthcheck", include_in_schema=False)
def healthcheck():
    return {
        "msg": "OK"
    }