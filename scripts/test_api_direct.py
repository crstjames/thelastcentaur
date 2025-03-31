#!/usr/bin/env python
import sys
import os
import asyncio
import json
import httpx
from datetime import datetime, timedelta
import jwt
import base64

# Add the parent directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# The secret key from auth_secret.json
with open("auth_secret.json", "r", encoding="utf-8") as f:
    data = json.load(f)
    SECRET_KEY = data.get("secret_key", "")

print(f"Secret key from file: {SECRET_KEY}")

def create_access_token(subject: str, expires_delta: timedelta = None) -> str:
    """Create a new access token."""
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(days=7)
    
    to_encode = {"exp": expire, "sub": subject}
    print(f"Token payload: {to_encode}")
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm="HS256")
    
    # Decode the token to verify it
    try:
        decoded = jwt.decode(encoded_jwt, SECRET_KEY, algorithms=["HS256"])
        print(f"Decoded token: {decoded}")
    except Exception as e:
        print(f"Error decoding token: {e}")
    
    # Print token parts for debugging
    parts = encoded_jwt.split('.')
    if len(parts) == 3:
        header = base64.b64decode(parts[0] + '==').decode('utf-8')
        payload = base64.b64decode(parts[1] + '==').decode('utf-8')
        print(f"Token header: {header}")
        print(f"Token payload: {payload}")
    
    return encoded_jwt

async def test_api():
    """Test the API directly."""
    # User ID from the test user
    user_id = "474f7f5f-eba6-4780-a5b0-66999867c6ff"
    game_id = "a15110b8-317d-4f7b-b873-badb480e63ca"
    
    # Create a new token
    token = create_access_token(user_id)
    print(f"Created token: {token}")
    
    # Test the API
    base_url = "http://localhost:8000/api/v1"
    
    # Test health check
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{base_url.replace('/api/v1', '')}/health")
        print(f"Health check response: {response.status_code} - {response.text}")
    
    # Test command execution
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}"
    }
    data = {
        "command": "look",
        "use_llm": False
    }
    
    print(f"Request headers: {headers}")
    print(f"Request data: {data}")
    
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{base_url}/game/{game_id}/command",
            headers=headers,
            json=data
        )
        print(f"Command execution response: {response.status_code}")
        print(f"Response headers: {response.headers}")
        print(f"Response body: {response.text}")

if __name__ == "__main__":
    asyncio.run(test_api()) 