"""Unit tests for authentication service."""

import pytest
from unittest.mock import MagicMock


class TestAuthValidation:
    """Tests for authentication validation."""
    
    def test_email_format_valid(self):
        """Test valid email format passes validation."""
        from app.schemas import UserRegister
        
        user = UserRegister(email="test@example.com", password="password123")
        assert user.email == "test@example.com"
    
    def test_password_minimum_length(self):
        """Test password minimum length validation."""
        from app.schemas import UserRegister
        
        # Valid password (6+ chars)
        user = UserRegister(email="test@example.com", password="123456")
        assert len(user.password) >= 6
        
        # Invalid password (too short) should raise
        with pytest.raises(ValueError):
            UserRegister(email="test@example.com", password="12345")
    
    def test_login_schema(self):
        """Test login schema accepts email and password."""
        from app.schemas import UserLogin
        
        login = UserLogin(email="test@example.com", password="password")
        assert login.email == "test@example.com"


class TestTokenSchemas:
    """Tests for token-related schemas."""
    
    def test_auth_response_schema(self):
        """Test auth response contains all required fields."""
        from app.schemas import AuthResponse
        
        response = AuthResponse(
            access_token="token123",
            refresh_token="refresh123",
            user_id="user-id",
            email="test@example.com"
        )
        
        assert response.access_token == "token123"
        assert response.refresh_token == "refresh123"
        assert response.user_id == "user-id"
        assert response.email == "test@example.com"
    
    def test_user_info_schema(self):
        """Test user info schema."""
        from app.schemas import UserInfo
        
        user = UserInfo(id="user-id", email="test@example.com")
        assert user.id == "user-id"
        assert user.email == "test@example.com"


class TestAuthService:
    """Tests for auth service methods."""
    
    @pytest.fixture
    def mock_db(self):
        """Create mock database client."""
        mock = MagicMock()
        return mock
    
    def test_auth_service_initialization(self, mock_db):
        """Test auth service can be initialized."""
        from app.services.auth_service import AuthService
        
        service = AuthService(mock_db)
        assert service.db == mock_db
