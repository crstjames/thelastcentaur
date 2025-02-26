import pytest
from datetime import datetime, timedelta, timezone
from jose import jwt
from unittest.mock import patch, MagicMock

from src.auth.security import (
    create_access_token,
    get_password_hash,
    verify_password,
    ALGORITHM,
)
from src.core.config import settings

class TestPasswordHashing:
    def test_password_hash(self):
        """Test that password hashing works correctly."""
        password = "testpassword123"
        hashed = get_password_hash(password)
        
        # Hashed password should be different from original
        assert hashed != password
        
        # Hashed password should be a string
        assert isinstance(hashed, str)
        
        # Hashed password should be longer than original (due to salt and algorithm)
        assert len(hashed) > len(password)
    
    def test_verify_password_success(self):
        """Test that password verification works with correct password."""
        password = "testpassword123"
        hashed = get_password_hash(password)
        
        assert verify_password(password, hashed) is True
    
    def test_verify_password_failure(self):
        """Test that password verification fails with incorrect password."""
        password = "testpassword123"
        wrong_password = "wrongpassword123"
        hashed = get_password_hash(password)
        
        assert verify_password(wrong_password, hashed) is False

class TestJWTTokens:
    def test_create_access_token(self):
        """Test that access token creation works correctly."""
        data = {"sub": "testuser"}
        token = create_access_token(data)
        
        # Token should be a string
        assert isinstance(token, str)
        
        # Token should be decodable with the correct secret
        decoded = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[ALGORITHM]
        )
        
        # Decoded token should contain the original data
        assert decoded["sub"] == "testuser"
        
        # Decoded token should have an expiration time
        assert "exp" in decoded
    
    def test_token_expiration(self):
        """Test that the token expires after the specified time."""
        # Mock the current time
        fixed_time = datetime(2023, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
        
        # Set a fixed expiration delta
        expires_delta = timedelta(hours=5)
        
        # Create a token with the fixed expiration
        with patch("src.auth.security.datetime") as mock_datetime:
            # Configure the mock to return our fixed time
            mock_datetime.now.return_value = fixed_time
            mock_datetime.utcnow.return_value = fixed_time
            
            # Create a token
            data = "testuser"
            token = create_access_token(subject=data, expires_delta=expires_delta)
            
            # Decode the token
            payload = jwt.decode(
                token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM],
                options={"verify_exp": False}  # Disable expiration verification
            )
            
            # Check that the expiration time is correct
            # The expiration time should be the current time + expires_delta
            expected_exp = int(fixed_time.timestamp()) + int(expires_delta.total_seconds())
            assert payload["exp"] == expected_exp 