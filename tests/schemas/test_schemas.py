import pytest
from pydantic import ValidationError
from datetime import datetime

from src.auth.schemas import UserCreate, UserUpdate, UserResponse
from src.game.schemas import GameInstanceCreate, GameInstanceUpdate, GameInstanceResponse
from src.db.models import GameStatus

class TestUserSchemas:
    def test_user_create_valid(self):
        """Test creating a valid UserCreate schema."""
        user_data = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "securepassword123"
        }
        
        user = UserCreate(**user_data)
        
        assert user.username == "testuser"
        assert user.email == "test@example.com"
        assert user.password == "securepassword123"
    
    def test_user_create_invalid_email(self):
        """Test that UserCreate validates email format."""
        user_data = {
            "username": "testuser",
            "email": "invalid-email",
            "password": "securepassword123"
        }
        
        with pytest.raises(ValidationError) as exc_info:
            UserCreate(**user_data)
        
        errors = exc_info.value.errors()
        assert any("email" in error["loc"] for error in errors)
    
    def test_user_create_short_password(self):
        """Test that UserCreate validates password length."""
        user_data = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "short"  # Too short
        }
        
        with pytest.raises(ValidationError) as exc_info:
            UserCreate(**user_data)
        
        errors = exc_info.value.errors()
        assert any("password" in error["loc"] for error in errors)
    
    def test_user_update(self):
        """Test updating a user with UserUpdate schema."""
        user_data = {
            "email": "updated@example.com",
            "password": "newpassword123"
        }
        
        user = UserUpdate(**user_data)
        
        assert user.email == "updated@example.com"
        assert user.password == "newpassword123"
    
    def test_user_response(self):
        """Test UserResponse schema."""
        user_data = {
            "id": "1",
            "username": "testuser",
            "email": "test@example.com",
            "is_active": True,
            "is_superuser": False,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        user = UserResponse(**user_data)
        
        assert user.id == "1"
        assert user.username == "testuser"
        assert user.email == "test@example.com"
        assert user.is_active is True
        assert user.is_superuser is False
        assert isinstance(user.created_at, datetime)
        assert isinstance(user.updated_at, datetime)

class TestGameSchemas:
    def test_game_instance_create(self):
        """Test creating a valid GameInstanceCreate schema."""
        game_data = {
            "name": "Test Game",
            "max_players": 4,
            "description": "A test game instance"
        }
        
        game = GameInstanceCreate(**game_data)
        
        assert game.name == "Test Game"
        assert game.max_players == 4
        assert game.description == "A test game instance"
    
    def test_game_instance_update(self):
        """Test updating a game with GameInstanceUpdate schema."""
        game_data = {
            "name": "Updated Game",
            "status": GameStatus.PAUSED,
            "max_players": 6
        }
        
        game = GameInstanceUpdate(**game_data)
        
        assert game.name == "Updated Game"
        assert game.status == GameStatus.PAUSED
        assert game.max_players == 6
    
    def test_game_instance_response(self):
        """Test GameInstanceResponse schema."""
        game_data = {
            "id": "1",
            "user_id": "1",
            "name": "Test Game",
            "status": GameStatus.ACTIVE,
            "max_players": 4,
            "current_players": 1,
            "description": "A test game instance",
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        game = GameInstanceResponse(**game_data)
        
        assert game.id == "1"
        assert game.user_id == "1"
        assert game.name == "Test Game"
        assert game.status == GameStatus.ACTIVE
        assert game.max_players == 4
        assert game.current_players == 1
        assert game.description == "A test game instance"
        assert isinstance(game.created_at, datetime)
        assert isinstance(game.updated_at, datetime) 