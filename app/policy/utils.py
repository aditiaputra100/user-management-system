from app.auth.models import User
from app.config import get_settings

settings = get_settings()

def has_permission(user: User, resource: str, action: str):
    if user.is_superuser:
        return True

    role = user.role
    if not role:
        return False

    permissions = role.permissions
    
    # Role based permissions
    for permission in permissions:
        if (permission.resource == resource
            and permission.action == action):
            return True
        
    return False