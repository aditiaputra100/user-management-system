from pydantic import BaseModel, ConfigDict
from typing import Optional
from enum import StrEnum


class Action(StrEnum):
    CREATE = "create"
    READ = "read"
    UPDATE = "update"
    DELETE = "delete"
    LIST = "list"


class CreateRoleSchema(BaseModel):
    name: str
    description: Optional[str] = None


class RoleSchema(CreateRoleSchema):
    id: int
    permissions: list["PermissionSchema"] = []

    model_config = ConfigDict(from_attributes=True)


class CreatePermissionSchema(BaseModel):
    name: str
    resource: str
    action: Action
    description: Optional[str] = None


class PermissionSchema(CreatePermissionSchema):
    id: int

    model_config = ConfigDict(from_attributes=True)