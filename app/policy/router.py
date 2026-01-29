from app.auth.models import User
from app.database import get_session
from fastapi import APIRouter, status, Depends, HTTPException
from typing import Annotated
from sqlalchemy.orm import Session
from .dependencies import require_permission
from .schemas import CreateRoleSchema, RoleSchema, CreatePermissionSchema, PermissionSchema
from .service import create_r, get_all_roles, get_r_by_id, update_r, delete_r, create_p, get_permissions, get_p_by_id, update_p, delete_p

role_router = APIRouter(prefix="/roles")
permission_router = APIRouter(prefix="/permission")

@role_router.post("/", status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_permission("roles", "create"))])
def create_role(role: CreateRoleSchema, db: Annotated[Session, Depends(get_session)]):
    try:
        create_r(name=role.name, db=db, description=role.description)
    except ValueError as err:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(err))
    except RuntimeError as err:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(err))
    
    return {
        "msg": f"Successfuly created role {role.name}"
    }

@role_router.get("/", response_model=list[RoleSchema], dependencies=[Depends(require_permission("roles", "list"))])
def get_roles(db: Annotated[Session, Depends(get_session)]):
    roles = get_all_roles(db)

    return roles

@role_router.get("/{id}", response_model=RoleSchema, dependencies=[Depends(require_permission("roles", "read"))])
def get_role(id: int, db: Annotated[Session, Depends(get_session)]):
    role = get_r_by_id(id, db)

    if not role:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Role is not found")
    
    return role

@role_router.put("/{id}", dependencies=[Depends(require_permission("roles", "update"))])
def update_role(id: int, role: CreateRoleSchema, db: Annotated[Session, Depends(get_session)]):
    try:
        update_r(
            id,
            role.name,
            role.description,
            db
        )
    
    except NameError as err:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(err))
    
    except ValueError as err:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(err))
    
    except RuntimeError as err:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(err))
    
    return {
        "msg": "Success updated role"
    }

@role_router.delete("/{id}", dependencies=[Depends(require_permission("roles", "delete"))])
def delete_role(id: int, db: Annotated[Session, Depends(get_session)]):
    try:
        delete_r(
            id,
            db
        )
    
    except NameError as err:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(err))
    
    except RuntimeError as err:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(err))
    
    return {
        "msg": "Success deleted role"
    }

# Permission router
@permission_router.post("/", status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_permission("permissions", "create"))])
def create_permission(permission: CreatePermissionSchema, db: Annotated[Session, Depends(get_session)]):
    try:
        create_p(
            name=permission.name,
            resource=permission.resource,
            action=permission.action,
            description=permission.description,
            db=db
        )
    except ValueError as err:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(err))
    except RuntimeError as err:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(err))
    
    return {
        "msg": "Successfuly created permission"
    }

@permission_router.get("/", response_model=list[PermissionSchema], dependencies=[Depends(require_permission("permissions", "list"))])
def get_all_permissions(db: Annotated[Session, Depends(get_session)]):
    permissions = get_permissions(db)

    return permissions

@permission_router.get("/{id}", response_model=PermissionSchema, dependencies=[Depends(require_permission("permissions", "read"))])
def get_permission(id: int, db: Annotated[Session, Depends(get_session)]):
    permission = get_p_by_id(id, db)

    if not permission:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Permission is not found")
    
    return permission

@permission_router.put("/{id}", dependencies=[Depends(require_permission("permissions", "update"))])
def update_permission(id: int, permission: PermissionSchema, db: Annotated[Session, Depends(get_session)]):
    try:
        update_p(
            id,
            permission.name,
            permission.resource,
            permission.action,
            permission.description,
            db
        )
    
    except NameError as err:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(err))
    
    except ValueError as err:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(err))
    
    except RuntimeError as err:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(err))
    
    return {
        "msg": "Success updated permission"
    }

@permission_router.delete("/{id}", dependencies=[Depends(require_permission("permissions", "delete"))])
def delete_permission(id: int, db: Annotated[Session, Depends(get_session)]):
    try:
        delete_p(id, db)
    
    except NameError as err:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(err))

    except RuntimeError as err:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(err))

    return {
        "msg": "Success deleted permission"
    }
    