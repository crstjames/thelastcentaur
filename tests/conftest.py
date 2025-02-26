"""
Pytest configuration and fixtures for The Last Centaur tests.
"""

import asyncio
import os
import uuid
from typing import AsyncGenerator, Dict, Generator, Any, Optional, List
from unittest.mock import MagicMock

import nest_asyncio
import pytest
import pytest_asyncio
from fastapi import FastAPI
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy import select, text
from fastapi.testclient import TestClient
import asyncpg

from src.auth.security import create_access_token, get_password_hash
from src.core.config import settings
from src.db.base import Base
from src.db.models import User
from src.db.session import get_db
from src.main import app as fastapi_app

# Add the src directory to the Python path for engine tests
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import engine components for fixtures
from src.engine.core.models import Direction, StoryArea, TerrainType
from src.engine.core.player import Player
from src.engine.core.map_system import MapSystem
from src.engine.core.game_systems import TimeSystem
from src.engine.core.command_parser import CommandParser
from src.engine.core.discovery_system import DiscoverySystem, HiddenDiscovery, InteractionType

# Apply nest_asyncio to allow nested event loops
nest_asyncio.apply()

# Test database settings
POSTGRES_SERVER = os.getenv("POSTGRES_SERVER", "localhost")
POSTGRES_USER = os.getenv("POSTGRES_USER", "postgres")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "postgres")
POSTGRES_DB = os.getenv("POSTGRES_DB", "thelastcentaur_test")

# Test database URL
TEST_DATABASE_URL = f"postgresql+asyncpg://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_SERVER}/{POSTGRES_DB}"

# Test session factory
TestSessionLocal = async_sessionmaker(
    autocommit=False, autoflush=False, bind=create_async_engine(TEST_DATABASE_URL), expire_on_commit=False
)

# Test engine
test_engine = create_async_engine(TEST_DATABASE_URL)
TestSessionLocal.configure(bind=test_engine)

# Create a mock session for testing
class MockSession:
    """Mock session for testing that mimics AsyncSession but works synchronously."""
    
    def __init__(self):
        self.users = {}
        self.game_instances = {}
        self.last_added_user = None
        
    async def add(self, obj):
        """Add an object to the session."""
        if isinstance(obj, User):
            # Ensure required fields are set
            if obj.is_active is None:
                obj.is_active = True
            if obj.is_superuser is None:
                obj.is_superuser = False
            
            self.users[obj.id] = obj
            self.last_added_user = obj
        
    async def commit(self):
        """Commit the session."""
        pass
    
    async def refresh(self, obj):
        """Refresh an object."""
        # If this is a user refresh after registration, return the last added user
        if isinstance(obj, User) and self.last_added_user and obj.id == self.last_added_user.id:
            # Copy attributes from last_added_user to obj
            for attr in ['id', 'username', 'email', 'hashed_password', 'is_active', 'is_superuser']:
                setattr(obj, attr, getattr(self.last_added_user, attr))
        
    async def close(self):
        """Close the session."""
        pass
    
    class MockResult:
        def __init__(self, user=None):
            self.user = user
            
        def scalar_one_or_none(self):
            return self.user
    
    async def execute(self, stmt):
        """Execute a statement."""
        # This is a simplified mock that handles User queries
        if hasattr(stmt, 'whereclause') and hasattr(stmt.whereclause, 'right'):
            # Handle User.username == "some_username"
            if stmt.whereclause.right.value == "testuser":
                return self.MockResult(User(
                    id="test-user-id",
                    username="testuser",
                    email="test@example.com",
                    hashed_password=get_password_hash("testpassword"),
                    is_active=True,
                    is_superuser=False
                ))
            # Handle User.username == "newuser"
            elif stmt.whereclause.right.value == "newuser":
                return self.MockResult(None)
            # Handle User.email == "newuser@example.com"
            elif stmt.whereclause.right.value == "newuser@example.com":
                return self.MockResult(None)
            # Handle User.username == "nonexistentuser"
            elif stmt.whereclause.right.value == "nonexistentuser":
                return self.MockResult(None)
            # Handle User.email == "test@example.com" (for test_register_existing_email)
            elif stmt.whereclause.right.value == "test@example.com":
                return self.MockResult(User(
                    id="test-user-id",
                    username="testuser",
                    email="test@example.com",
                    hashed_password=get_password_hash("testpassword"),
                    is_active=True,
                    is_superuser=False
                ))
            # Handle User.username == "differentuser" (for test_register_existing_email)
            elif stmt.whereclause.right.value == "differentuser":
                return self.MockResult(None)
            # Handle User.id == "test-user-id" (for auth deps)
            elif stmt.whereclause.right.value == "test-user-id":
                return self.MockResult(User(
                    id="test-user-id",
                    username="testuser",
                    email="test@example.com",
                    hashed_password=get_password_hash("testpassword"),
                    is_active=True,
                    is_superuser=False
                ))
        
        # Default case
        return self.MockResult(None)

@pytest.fixture(scope="session")
def event_loop_policy():
    """Create a custom event loop policy for tests."""
    return asyncio.get_event_loop_policy()

@pytest_asyncio.fixture(scope="session")
async def test_db_setup_teardown() -> AsyncGenerator[None, None]:
    """Set up and tear down the test database."""
    # Connect to the default database to create/drop the test database
    default_engine = create_async_engine(
        f"postgresql+asyncpg://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_SERVER}/postgres",
        isolation_level="AUTOCOMMIT",  # Important for creating/dropping databases
    )
    
    # Create a connection to the default database
    async with default_engine.connect() as conn:
        # Disconnect all users from the test database if it exists
        await conn.execute(text(
            f"SELECT pg_terminate_backend(pg_stat_activity.pid) "
            f"FROM pg_stat_activity "
            f"WHERE pg_stat_activity.datname = '{POSTGRES_DB}' "
            f"AND pid <> pg_backend_pid()"
        ))
        
        # Drop the test database if it exists
        await conn.execute(text(f"DROP DATABASE IF EXISTS {POSTGRES_DB}"))
        
        # Create the test database
        await conn.execute(text(f"CREATE DATABASE {POSTGRES_DB}"))
    
    # Close the connection to the default database
    await default_engine.dispose()
    
    # Create tables in the test database
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    # Yield control to allow tests to run
    yield
    
    # Clean up after tests
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    
    # Close the connection to the test database
    await test_engine.dispose()
    
    # Connect to the default database again to drop the test database
    default_engine = create_async_engine(
        f"postgresql+asyncpg://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_SERVER}/postgres",
        isolation_level="AUTOCOMMIT",
    )
    
    async with default_engine.connect() as conn:
        # Disconnect all users from the test database
        await conn.execute(text(
            f"SELECT pg_terminate_backend(pg_stat_activity.pid) "
            f"FROM pg_stat_activity "
            f"WHERE pg_stat_activity.datname = '{POSTGRES_DB}' "
            f"AND pid <> pg_backend_pid()"
        ))
        
        # Drop the test database
        await conn.execute(text(f"DROP DATABASE IF EXISTS {POSTGRES_DB}"))
    
    # Close the connection to the default database
    await default_engine.dispose()

@pytest_asyncio.fixture
async def db_session(test_db_setup_teardown) -> AsyncGenerator[AsyncSession, None]:
    """Return a database session for testing."""
    session = TestSessionLocal()
    try:
        yield session
    finally:
        await session.close()

async def get_mock_db():
    """Return a mock database session for testing."""
    mock_session = MockSession()
    yield mock_session

@pytest.fixture
def app() -> FastAPI:
    """Create a FastAPI app for testing."""
    return fastapi_app

@pytest.fixture
def client(app: FastAPI) -> TestClient:
    """Return an API client for testing."""
    # Override the get_db dependency to use the mock database
    app.dependency_overrides = {}  # Clear any existing overrides
    app.dependency_overrides[get_db] = get_mock_db

    # Create a TestClient for the FastAPI app
    test_client = TestClient(app)
    
    # Simply yield the TestClient
    yield test_client
    
    # Clear dependency overrides after test
    app.dependency_overrides = {}

@pytest.fixture
def test_user() -> User:
    """Create a test user for testing."""
    return User(
        id="test-user-id",
        username="testuser",
        email="test@example.com",
        hashed_password=get_password_hash("testpassword"),
        is_active=True
    )

@pytest.fixture
def current_user(test_user: User) -> User:
    """Return the current test user."""
    return test_user

@pytest.fixture
def token_headers(test_user: User) -> dict:
    """Return token headers for testing."""
    access_token = create_access_token(
        subject=test_user.id
    )
    return {"Authorization": f"Bearer {access_token}"}

# Engine test fixtures
@pytest.fixture
def mock_map_system():
    """Return a mock map system for testing."""
    map_system = MagicMock()
    map_system.current_weather = MagicMock(value="clear")
    map_system.get_tile_at_position = MagicMock(return_value=None)
    return map_system

@pytest.fixture
def mock_player(mock_map_system):
    """Return a mock player for testing."""
    player = MagicMock()
    player.map_system = mock_map_system
    
    # Set up time_system mock
    player.time_system = MagicMock()
    player.time_system.time = MagicMock()
    player.time_system.time.get_time_of_day = MagicMock(return_value=MagicMock(value="DAY"))
    
    # Set up player state
    player.state = MagicMock()
    player.state.inventory = []
    player.get_current_position = MagicMock(return_value=(5, 5))
    
    # Create a mock tile
    tile = MagicMock()
    tile.position = (5, 5)
    tile.terrain_type = TerrainType.FOREST
    tile.description = "A peaceful forest area."
    tile.items = ["stick", "rock"]
    player.state.current_tile = tile
    
    return player

@pytest.fixture
def discovery_system():
    """Return a discovery system for testing."""
    discovery_system = DiscoverySystem()
    
    # Add test discoveries
    discovery_system.discoveries["test_berries"] = HiddenDiscovery(
        id="test_berries",
        name="Test Berries",
        description="Some test berries for testing.",
        discovery_text="You found some test berries!",
        terrain_types=["FOREST"],
        required_interaction="gather",
        required_keywords=["berries", "bush"],
        chance_to_find=1.0,
        item_reward="test_berries"
    )
    
    discovery_system.discoveries["pretty_flower"] = HiddenDiscovery(
        id="pretty_flower",
        name="Pretty Flower",
        description="A beautiful flower with vibrant colors.",
        discovery_text="You found a pretty flower!",
        terrain_types=["FOREST", "CLEARING"],
        required_interaction="examine",
        required_keywords=["flower", "flowers", "plant"],
        chance_to_find=1.0,
        item_reward="pretty_flower",
        unique=False
    )
    
    return discovery_system

@pytest.fixture
def command_parser(mock_player):
    """Return a command parser for testing."""
    return CommandParser(mock_player)

@pytest.fixture
def real_map_system():
    """Return a real map system for testing."""
    return MapSystem()

@pytest.fixture
def real_player(real_map_system):
    """Return a real player for testing."""
    return Player(real_map_system, player_id="test_player", player_name="Test Player")

@pytest.fixture
def real_command_parser(real_player):
    """Return a real command parser for testing."""
    return CommandParser(real_player) 