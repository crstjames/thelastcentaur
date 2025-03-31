#!/usr/bin/env python
import sys
import os
import asyncio
from jose import jwt, JWTError
from datetime import datetime, timedelta

# Add the parent directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.core.config import settings

def create_access_token(subject: str, expires_delta: timedelta = None) -> str:
    """Create a new access token."""
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(days=7)
    
    to_encode = {"exp": expire, "sub": subject}
    encoded_jwt = jwt.encode(to_encode, "testsecretkey", algorithm="HS256")
    return encoded_jwt

def decode_token(token: str):
    """Decode a token and print the payload."""
    try:
        payload = jwt.decode(
            token, "testsecretkey", algorithms=["HS256"]
        )
        print(f"Token is valid! Payload: {payload}")
        return payload
    except JWTError as e:
        print(f"Token validation failed: {e}")
        return None

async def main():
    # User ID from the test user
    user_id = "474f7f5f-eba6-4780-a5b0-66999867c6ff"
    
    # Create a new token
    token = create_access_token(user_id)
    print(f"Created token: {token}")
    
    # Decode the token
    payload = decode_token(token)
    
    # Test the token from the script
    test_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3NDI0NzgxMTEsInN1YiI6IjQ3NGY3ZjVmLWViYTYtNDc4MC1hNWIwLTY2OTk5ODY3YzZmZiJ9.iBPJ2wDrMOWtz_T-3NCwC9FE6zbazDYnTSitqLKjkIw"
    print("\nTesting token from script:")
    payload = decode_token(test_token)
    
    # Print the secret key being used
    print(f"\nSettings Secret key: {settings.SECRET_KEY}")
    print(f"Settings Algorithm: {settings.ALGORITHM}")
    print(f"Hardcoded Secret key: testsecretkey")
    print(f"Hardcoded Algorithm: HS256")
    
    # Create a curl command for testing
    print("\nCurl command for testing:")
    curl_cmd = f'curl -X POST "http://localhost:8000/api/v1/game/a15110b8-317d-4f7b-b873-badb480e63ca/command" -H "Content-Type: application/json" -H "Authorization: Bearer {token}" -d \'{{"command":"look", "use_llm": false}}\''
    print(curl_cmd)

if __name__ == "__main__":
    asyncio.run(main()) 