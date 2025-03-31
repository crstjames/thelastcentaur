#!/usr/bin/env python
import sys
import os
import json
from pathlib import Path

# Add the parent directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.core.config import settings, get_or_create_secret_key, SECRET_KEY_FILE

def main():
    # Print the settings SECRET_KEY
    print(f"Settings SECRET_KEY: {settings.SECRET_KEY}")
    
    # Print the environment variable
    env_key = os.getenv("SECRET_KEY", "Not set")
    print(f"Environment SECRET_KEY: {env_key}")
    
    # Print the contents of the auth_secret.json file
    if SECRET_KEY_FILE.exists():
        try:
            with open(SECRET_KEY_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                file_key = data.get("secret_key", "Not found")
                print(f"File SECRET_KEY: {file_key}")
        except (json.JSONDecodeError, KeyError) as e:
            print(f"Error reading SECRET_KEY file: {e}")
    else:
        print(f"SECRET_KEY file does not exist: {SECRET_KEY_FILE}")
    
    # Call the get_or_create_secret_key function
    function_key = get_or_create_secret_key()
    print(f"Function SECRET_KEY: {function_key}")
    
    # Check if the keys match
    if settings.SECRET_KEY == function_key:
        print("Settings and function keys match.")
    else:
        print("WARNING: Settings and function keys do not match!")
    
    if settings.SECRET_KEY == env_key:
        print("Settings and environment keys match.")
    elif env_key == "Not set":
        print("Environment key is not set.")
    else:
        print("WARNING: Settings and environment keys do not match!")

if __name__ == "__main__":
    main() 