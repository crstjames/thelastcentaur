#!/usr/bin/env python3
"""
Check for users in the database.
"""

import asyncio
import os
import sys
from sqlalchemy import select
from datetime import timedelta

# Add the parent directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.db.session import AsyncSessionLocal
from src.db.models import User
from src.auth.security import create_access_token

async def find_users():
    """Find all users in the database."""
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(User))
        users = result.scalars().all()
        
        if not users:
            print("No users found in the database.")
            return
        
        print(f"Found {len(users)} users:")
        for user in users:
            token = create_access_token(
                subject=user.id,
                expires_delta=timedelta(days=1)
            )
            print(f"- ID: {user.id}")
            print(f"  Username: {user.username}")
            print(f"  Email: {user.email}")
            print(f"  Is active: {user.is_active}")
            print(f"  Is superuser: {user.is_superuser}")
            print(f"  Created: {user.created_at}")
            print(f"  Token: {token}")
            print()

if __name__ == "__main__":
    asyncio.run(find_users()) 