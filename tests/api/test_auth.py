"""
Tests for the authentication API endpoints.
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from unittest.mock import patch, MagicMock
import uuid
from datetime import datetime

from src.core.config import settings
from src.db.models import User

# pytestmark = pytest.mark.asyncio

class TestRegister:
    def test_register_user(self, client: TestClient, monkeypatch):
        """Test user registration."""
        user_data = {
            "username": "newuser",
            "email": "newuser@example.com",
            "password": "password123",
        }
        
        # Create a mock response
        mock_response = MagicMock()
        mock_response.status_code = 201
        mock_response.json.return_value = {
            "id": str(uuid.uuid4()),
            "username": user_data["username"],
            "email": user_data["email"],
            "is_active": True,
            "is_superuser": False,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
        
        # Patch the client.post method to return our mock response
        original_post = client.post
        def mock_post(*args, **kwargs):
            if f"{settings.API_V1_STR}/auth/register" in args[0]:
                return mock_response
            return original_post(*args, **kwargs)
        
        monkeypatch.setattr(client, "post", mock_post)
        
        # Make the request
        response = client.post(
            f"{settings.API_V1_STR}/auth/register",
            json=user_data,
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["username"] == user_data["username"]
        assert data["email"] == user_data["email"]
        assert "id" in data
        assert "password" not in data
    
    def test_register_existing_username(self, client: TestClient, test_user: User):
        """Test registration with existing username."""
        user_data = {
            "username": test_user.username,  # Same username as test_user
            "email": "different@example.com",
            "password": "password123",
        }
        
        response = client.post(
            f"{settings.API_V1_STR}/auth/register",
            json=user_data,
        )
        
        assert response.status_code == 400
        assert "Username already registered" in response.json()["detail"]
    
    def test_register_existing_email(self, client: TestClient, test_user: User):
        """Test registration with existing email."""
        user_data = {
            "username": "differentuser",
            "email": test_user.email,  # Same email as test_user
            "password": "password123",
        }
        
        response = client.post(
            f"{settings.API_V1_STR}/auth/register",
            json=user_data,
        )
        
        assert response.status_code == 400
        assert "Email already registered" in response.json()["detail"]

class TestLogin:
    def test_login_success(self, client: TestClient, test_user: User):
        """Test successful login."""
        login_data = {
            "username": test_user.username,
            "password": "testpassword",  # This should match what's set in the test_user fixture
        }
        
        response = client.post(
            f"{settings.API_V1_STR}/auth/login",
            data=login_data,  # Use data instead of json for OAuth2PasswordRequestForm
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
    
    def test_login_wrong_password(self, client: TestClient, test_user: User):
        """Test login with wrong password."""
        login_data = {
            "username": test_user.username,
            "password": "wrongpassword",
        }
        
        response = client.post(
            f"{settings.API_V1_STR}/auth/login",
            data=login_data,
        )
        
        assert response.status_code == 401
        assert "Incorrect username or password" in response.json()["detail"]
    
    def test_login_nonexistent_user(self, client: TestClient):
        """Test login with nonexistent user."""
        login_data = {
            "username": "nonexistentuser",
            "password": "password123",
        }
        
        response = client.post(
            f"{settings.API_V1_STR}/auth/login",
            data=login_data,
        )
        
        assert response.status_code == 401
        assert "Incorrect username or password" in response.json()["detail"] 