#!/usr/bin/env python
import sys
import os
import asyncio
import json
import httpx
from datetime import datetime, timedelta
import base64
import random
import string

# Add the parent directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.core.config import settings

def generate_random_string(length=8):
    """Generate a random string of fixed length."""
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for _ in range(length))

async def test_auth_flow():
    """Test the entire authentication flow."""
    # API base URL
    base_url = "http://localhost:8000/api/v1"
    
    # Step 1: Generate a random username and password
    username = f"test_user_{generate_random_string()}"
    password = f"test_pass_{generate_random_string()}"
    email = f"{username}@example.com"
    
    print(f"Testing with username: {username}, password: {password}")
    
    # Step 2: Register a new user
    register_data = {
        "username": username,
        "email": email,
        "password": password
    }
    
    print("\n=== Step 1: Register User ===")
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{base_url}/auth/register",
            json=register_data
        )
        print(f"Register response status: {response.status_code}")
        print(f"Register response body: {response.text}")
        
        if response.status_code != 200 and response.status_code != 201:
            print("Registration failed, exiting test")
            return
        
        user_data = response.json()
        user_id = user_data.get("id")
        print(f"User ID: {user_id}")
    
    # Step 3: Log in to get a token
    login_data = {
        "username": username,
        "password": password
    }
    
    print("\n=== Step 2: Login ===")
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{base_url}/auth/login",
            data=login_data
        )
        print(f"Login response status: {response.status_code}")
        
        if response.status_code != 200:
            print(f"Login failed: {response.text}")
            return
        
        login_result = response.json()
        token = login_result.get("access_token")
        
        if not token:
            print("No access token in response")
            return
        
        print(f"Received token: {token[:20]}...")
        
        # Print token parts for debugging
        parts = token.split('.')
        if len(parts) == 3:
            try:
                header = base64.b64decode(parts[0] + '==').decode('utf-8')
                payload = base64.b64decode(parts[1] + '==').decode('utf-8')
                print(f"Token header: {header}")
                print(f"Token payload: {payload}")
            except Exception as e:
                print(f"Error decoding token parts: {e}")
    
    # Step 4: Create a game instance
    game_data = {
        "name": f"Test Game {generate_random_string()}",
        "description": "A test game instance",
        "max_players": 1
    }
    
    print("\n=== Step 3: Create Game Instance ===")
    async with httpx.AsyncClient() as client:
        headers = {
            "Authorization": f"Bearer {token}"
        }
        
        response = await client.post(
            f"{base_url}/game",
            json=game_data,
            headers=headers
        )
        print(f"Create game response status: {response.status_code}")
        
        if response.status_code != 200 and response.status_code != 201:
            print(f"Create game failed: {response.text}")
            return
        
        game_data = response.json()
        game_id = game_data.get("id")
        print(f"Game ID: {game_id}")
    
    # Step 5: Execute a command
    command_data = {
        "command": "look",
        "use_llm": False
    }
    
    print("\n=== Step 4: Execute Command ===")
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{base_url}/game/{game_id}/command",
            json=command_data,
            headers=headers
        )
        print(f"Execute command response status: {response.status_code}")
        print(f"Execute command response body: {response.text}")

if __name__ == "__main__":
    asyncio.run(test_auth_flow()) 