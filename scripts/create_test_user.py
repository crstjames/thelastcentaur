#!/usr/bin/env python3
"""
Create a test user and game instance in the database.
"""

import asyncio
import uuid
import os
import sys
from datetime import datetime, timedelta
from sqlalchemy import select
import jwt

# Add the parent directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.db.session import AsyncSessionLocal
from src.db.models import User, GameInstance
from src.auth.security import get_password_hash

def create_access_token(subject: str, expires_delta: timedelta = None) -> str:
    """Create a new access token."""
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(days=7)
    
    to_encode = {"exp": expire, "sub": subject}
    encoded_jwt = jwt.encode(to_encode, "testsecretkey", algorithm="HS256")
    return encoded_jwt

async def create_test_user():
    """Create a test user and game instance in the database."""
    async with AsyncSessionLocal() as session:
        # Check if the test user already exists
        result = await session.execute(select(User).where(User.username == "testuser"))
        existing_user = result.scalar_one_or_none()
        
        if existing_user:
            print(f"Test user already exists with ID: {existing_user.id}")
            user_id = existing_user.id
        else:
            # Create a new test user
            user_id = str(uuid.uuid4())
            test_user = User(
                id=user_id,
                username="testuser",
                email="test@example.com",
                hashed_password=get_password_hash("testpassword"),
                is_active=True,
                is_superuser=False,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            
            session.add(test_user)
            await session.commit()
            await session.refresh(test_user)
            print(f"Created test user with ID: {user_id}")
        
        # Check if a game instance already exists for this user
        game_result = await session.execute(
            select(GameInstance).where(GameInstance.user_id == user_id)
        )
        existing_game = game_result.scalar_one_or_none()
        
        if existing_game:
            print(f"Test game already exists with ID: {existing_game.id}")
            game_id = existing_game.id
        else:
            # Create a new test game
            game_id = str(uuid.uuid4())
            test_game = GameInstance(
                id=game_id,
                user_id=user_id,
                name="Test Game",
                status="ACTIVE",
                max_players=1,
                current_players=1,
                description="A test game instance",
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            
            session.add(test_game)
            await session.commit()
            await session.refresh(test_game)
            print(f"Created test game with ID: {game_id}")
        
        # Generate a token for the user
        token = create_access_token(
            subject=user_id,
            expires_delta=timedelta(days=7)  # Long expiration for testing
        )
        
        print("\nTest User Information:")
        print(f"- Username: testuser")
        print(f"- Password: testpassword")
        print(f"- User ID: {user_id}")
        print(f"- Game ID: {game_id}")
        print(f"- Token: {token}")
        print("\nTest with:")
        curl_command = f'curl -X POST "http://localhost:8000/api/v1/game/{game_id}/command" -H "Content-Type: application/json" -H "Authorization: Bearer {token}" -d \'{{"command":"look", "use_llm": false}}\''
        print(curl_command)

if __name__ == "__main__":
    asyncio.run(create_test_user()) 