"""FastAPI dependencies for dependency injection."""

from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from supabase import Client

from app.database import get_db
from app.services.auth_service import AuthService
from app.schemas import UserInfo


# Security scheme
security = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: Client = Depends(get_db)
) -> UserInfo:
    """
    Dependency to get current authenticated user.
    Raises 401 if not authenticated.
    """
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    auth_service = AuthService(db)
    user = await auth_service.get_user_from_token(credentials.credentials)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    return user


async def get_optional_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: Client = Depends(get_db)
) -> Optional[UserInfo]:
    """
    Dependency to get current user if authenticated.
    Returns None if not authenticated (for public endpoints).
    """
    if not credentials:
        return None
    
    auth_service = AuthService(db)
    return await auth_service.get_user_from_token(credentials.credentials)
