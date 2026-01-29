from app.auth.models import User
from app.auth.dependencies import get_current_user
from fastapi import Depends, HTTPException, status
from typing import Annotated
from .utils import has_permission


def require_permission(resource: str, action:str):
    def permission_dependency(current_user: Annotated[User, Depends(get_current_user)]):
        if not has_permission(current_user, resource, action):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"Permission denied: {action} on {resource}")

        return current_user

    return permission_dependency