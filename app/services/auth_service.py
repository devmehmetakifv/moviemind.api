"""Authentication service using Supabase Auth."""

from typing import Optional, Tuple
from supabase import Client
from gotrue.errors import AuthApiError

from app.schemas import AuthResponse, UserInfo
from app.config import get_settings


class AuthService:
    """Service for authentication operations."""
    
    def __init__(self, db: Client):
        self.db = db
    
    async def register(self, email: str, password: str) -> Tuple[Optional[AuthResponse], Optional[str]]:
        """Register a new user."""
        try:
            result = self.db.auth.sign_up({
                "email": email,
                "password": password
            })
            
            if result.user and result.session:
                return AuthResponse(
                    access_token=result.session.access_token,
                    refresh_token=result.session.refresh_token,
                    user_id=result.user.id,
                    email=result.user.email
                ), None
            
            return None, "Registration failed. Please try again."
            
        except AuthApiError as e:
            return None, str(e.message)
        except Exception as e:
            return None, f"Registration error: {str(e)}"
    
    async def login(self, email: str, password: str) -> Tuple[Optional[AuthResponse], Optional[str]]:
        """Login an existing user."""
        try:
            result = self.db.auth.sign_in_with_password({
                "email": email,
                "password": password
            })
            
            if result.user and result.session:
                return AuthResponse(
                    access_token=result.session.access_token,
                    refresh_token=result.session.refresh_token,
                    user_id=result.user.id,
                    email=result.user.email
                ), None
            
            return None, "Invalid credentials"
            
        except AuthApiError as e:
            return None, str(e.message)
        except Exception as e:
            return None, f"Login error: {str(e)}"
    
    async def logout(self, access_token: str) -> Tuple[bool, Optional[str]]:
        """Logout the current user."""
        try:
            self.db.auth.sign_out()
            return True, None
        except Exception as e:
            return False, str(e)
    
    async def refresh_token(self, refresh_token: str) -> Tuple[Optional[AuthResponse], Optional[str]]:
        """Refresh the access token."""
        try:
            result = self.db.auth.refresh_session(refresh_token)
            
            if result.user and result.session:
                return AuthResponse(
                    access_token=result.session.access_token,
                    refresh_token=result.session.refresh_token,
                    user_id=result.user.id,
                    email=result.user.email
                ), None
            
            return None, "Token refresh failed"
            
        except AuthApiError as e:
            return None, str(e.message)
        except Exception as e:
            return None, f"Refresh error: {str(e)}"
    
    async def get_user_from_token(self, access_token: str) -> Optional[UserInfo]:
        """Get user info from access token."""
        try:
            result = self.db.auth.get_user(access_token)
            
            if result.user:
                return UserInfo(
                    id=result.user.id,
                    email=result.user.email
                )
            
            return None
            
        except Exception:
            return None
