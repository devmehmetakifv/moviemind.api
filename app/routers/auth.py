"""Authentication router."""

from fastapi import APIRouter, Depends, HTTPException, status
from supabase import Client

from app.database import get_db
from app.dependencies import get_current_user
from app.schemas import (
    UserRegister, UserLogin, AuthResponse, 
    UserInfo, TokenRefresh, MessageResponse
)
from app.services.auth_service import AuthService


router = APIRouter()


@router.post("/register", response_model=AuthResponse)
async def register(
    user_data: UserRegister,
    db: Client = Depends(get_db)
):
    """
    Register a new user account.
    
    - **email**: Valid email address
    - **password**: Minimum 6 characters
    """
    auth_service = AuthService(db)
    result, error = await auth_service.register(user_data.email, user_data.password)
    
    if error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error
        )
    
    return result


@router.post("/login", response_model=AuthResponse)
async def login(
    user_data: UserLogin,
    db: Client = Depends(get_db)
):
    """
    Login with email and password.
    
    Returns access token and refresh token.
    """
    auth_service = AuthService(db)
    result, error = await auth_service.login(user_data.email, user_data.password)
    
    if error:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=error
        )
    
    return result


@router.post("/logout", response_model=MessageResponse)
async def logout(
    current_user: UserInfo = Depends(get_current_user),
    db: Client = Depends(get_db)
):
    """Logout the current user."""
    auth_service = AuthService(db)
    success, error = await auth_service.logout("")
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error
        )
    
    return MessageResponse(message="Logged out successfully")


@router.post("/refresh", response_model=AuthResponse)
async def refresh_token(
    token_data: TokenRefresh,
    db: Client = Depends(get_db)
):
    """Refresh the access token using refresh token."""
    auth_service = AuthService(db)
    result, error = await auth_service.refresh_token(token_data.refresh_token)
    
    if error:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=error
        )
    
    return result


@router.get("/me", response_model=UserInfo)
async def get_current_user_info(
    current_user: UserInfo = Depends(get_current_user)
):
    """Get current authenticated user information."""
    return current_user
