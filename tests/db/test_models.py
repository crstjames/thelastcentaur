import pytest
from sqlalchemy import select
from datetime import datetime

from src.db.models import User, GameInstance
from src.game.schemas import GameStatus

# pytestmark = pytest.mark.asyncio

class TestUserModel:
    async def test_create_user(self, db_session):
        """Test creating a user in the database."""
        # Create a new user with unique email and username
        new_user = User(
            username="testuser_unique",
            email="test_unique@example.com",
            hashed_password="hashedpassword123",
            is_active=True,
        )
        
        db_session.add(new_user)
        await db_session.commit()
        await db_session.refresh(new_user)
        
        # Verify the user was created with an ID
        assert new_user.id is not None
        assert new_user.username == "testuser_unique"
        assert new_user.email == "test_unique@example.com"
        assert new_user.hashed_password == "hashedpassword123"
        assert new_user.is_active is True
        assert new_user.is_superuser is False  # Default value
        
        # Verify created_at and updated_at are set
        assert isinstance(new_user.created_at, datetime)
        assert isinstance(new_user.updated_at, datetime)
    
    async def test_query_user(self, db_session):
        """Test querying a user from the database."""
        # Create a user with unique username and email
        new_user = User(
            username="queryuser_unique",
            email="query_unique@example.com",
            hashed_password="hashedpassword123",
        )
        
        db_session.add(new_user)
        await db_session.commit()
        
        # Query the user
        result = await db_session.execute(select(User).where(User.username == "queryuser_unique"))
        user = result.scalars().first()
        
        assert user is not None
        assert user.username == "queryuser_unique"
        assert user.email == "query_unique@example.com"

class TestGameInstanceModel:
    async def test_create_game_instance(self, db_session):
        """Test creating a game instance in the database."""
        # Create a user first
        user = User(
            username="gameuser",
            email="game@example.com",
            hashed_password="hashedpassword123",
        )
        
        db_session.add(user)
        await db_session.commit()
        await db_session.refresh(user)
        
        # Create a game instance
        game_instance = GameInstance(
            owner_id=user.id,
            name="Test Game",
            status=GameStatus.ACTIVE,
            max_players=4,
            current_players=1,
        )
        
        db_session.add(game_instance)
        await db_session.commit()
        await db_session.refresh(game_instance)
        
        # Verify the game instance was created
        assert game_instance.id is not None
        assert game_instance.owner_id == user.id
        assert game_instance.name == "Test Game"
        assert game_instance.status == GameStatus.ACTIVE
        assert game_instance.max_players == 4
        assert game_instance.current_players == 1
        
        # Verify created_at and updated_at are set
        assert isinstance(game_instance.created_at, datetime)
        assert isinstance(game_instance.updated_at, datetime) 