#!/usr/bin/env python3
"""
Check for game instances in the database.
"""

import asyncio
import os
import sys
from sqlalchemy import select

# Add the parent directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.db.session import AsyncSessionLocal
from src.db.models import GameInstance, User

async def find_games():
    """Find all game instances in the database."""
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(GameInstance))
        games = result.scalars().all()
        
        if not games:
            print("No game instances found in the database.")
            return
        
        print(f"Found {len(games)} game instances:")
        for game in games:
            user_result = await session.execute(select(User).where(User.id == game.user_id))
            user = user_result.scalar_one_or_none()
            username = user.username if user else "Unknown"
            
            print(f"- ID: {game.id}")
            print(f"  Name: {game.name}")
            print(f"  User ID: {game.user_id} (Username: {username})")
            print(f"  Status: {game.status}")
            print(f"  Players: {game.current_players}/{game.max_players}")
            print(f"  Description: {game.description}")
            print(f"  Created: {game.created_at}")
            print()

if __name__ == "__main__":
    asyncio.run(find_games()) 