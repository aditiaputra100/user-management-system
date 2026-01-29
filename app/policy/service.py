from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from sqlalchemy import select
from .models import Role, Permission

def create_r(name: str, db: Session, description: str | None = None) -> None:
    role = Role(
        name=name,
        description=description
    )

    db.add(role)

    try:
        db.commit()
    except IntegrityError as err:
        db.rollback()
        raise ValueError("Role name has already exists")
    except Exception as err:
        raise RuntimeError(str(err))
    
def get_all_roles(db: Session) -> list[Role]:
    stmt = select(Role)
    roles = db.scalars(stmt).all()

    return roles

def get_r_by_id(id: int, db: Session) -> Role | None:
    role = db.get(Role, id)

    return role

def update_r(id: int, name: str, description: str | None, db: Session) -> None:
    role = db.get(Role, id)

    if not role:
        raise NameError(f"Role with ID {id} is not found")
    
    role.name = name
    role.description = description

    try:
        db.commit()

    except IntegrityError:
        db.rollback()
        raise ValueError(f"Duplicate entry name role {name}")
    
    except Exception as err:
        db.rollback()
        raise RuntimeError(str(err))

def delete_r(id: int, db: Session) -> None:
    role = db.get(Role, id)

    if not role:
        raise NameError(f"Role with ID {id} is not found")
    
    try:
        db.delete(role)
        db.commit()
    
    except Exception as err:
        db.rollback()
        raise RuntimeError(str(err))

def create_p(name: str, resource: str, action: str, db: Session, description: str | None = None) -> None:
    permission = Permission(
        name=name,
        resource=resource,
        action=action,
        description=description
    )

    db.add(permission)

    try:
        db.commit()
    except IntegrityError as err:
        db.rollback()
        raise ValueError("Permission name has already exists")
    except Exception as err:
        raise RuntimeError(str(err))

def get_permissions(db: Session) -> list[Permission]:
    stmt = select(Permission)
    permissions = db.scalars(stmt).all()

    return permissions

def get_p_by_id(id: int, db: Session) -> Permission | None:
    permission = db.get(Permission, id)

    return permission

def update_p(id: int, name: str, resource: str, action: str, description: str | None, db: Session) -> None:
    permission = db.get(Permission, id)

    if not permission:
        raise NameError(f"Permission with ID {id} is not found")
    
    permission.name = name
    permission.resource = resource
    permission.action = action
    permission.description = description

    try:
        db.commit()
    
    except IntegrityError:
        db.rollback()
        raise ValueError(f"Duplicate entry name resource {name}")
    
    except Exception as err:
        db.rollback()
        raise RuntimeError(str(err))
    
def delete_p(id: int, db: Session):
    permission = db.get(Permission, id)

    if not permission:
        raise NameError(f"Permission with ID {id} is not found")
    
    try:
        db.delete(permission)
        db.commit()
    
    except Exception as err:
        db.rollback()
        raise RuntimeError(str(err))