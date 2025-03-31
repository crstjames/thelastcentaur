#!/usr/bin/env python
import sys
import os
import asyncio
import json
import uvicorn
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from typing import Dict

# Add the parent directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# The secret key from auth_secret.json
with open("auth_secret.json", "r", encoding="utf-8") as f:
    data = json.load(f)
    SECRET_KEY = data.get("secret_key", "")

print(f"Secret key from file: {SECRET_KEY}")

# Create a minimal FastAPI app
app = FastAPI()

# OAuth2 scheme for token extraction
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

async def get_token_payload(token: str = Depends(oauth2_scheme)):
    """Extract and validate the token payload."""
    try:
        # Print token for debugging
        print(f"Received token: {token[:20]}...")
        
        # Decode token
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        print(f"Decoded payload: {payload}")
        return payload
    except JWTError as e:
        print(f"JWT Error: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Could not validate credentials: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )

@app.get("/test-auth")
async def test_auth(payload: Dict = Depends(get_token_payload)):
    """Test endpoint that requires authentication."""
    return {"message": "Authentication successful!", "payload": payload}

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "ok"}

if __name__ == "__main__":
    # Run the server on port 8001 to avoid conflicts
    uvicorn.run(app, host="127.0.0.1", port=8001) 