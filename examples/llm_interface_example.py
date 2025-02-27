#!/usr/bin/env python3
"""
Example script demonstrating how to use the LLM interface programmatically.

This script shows how to:
1. Connect to the game API
2. Login and create a game instance
3. Process natural language commands using the LLM interface
4. Enhance game responses with rich descriptions

Usage:
    python examples/llm_interface_example.py

Requirements:
    - The Last Centaur game server running
    - OpenAI and Anthropic API keys set in environment variables
"""

import os
import sys
import asyncio
import json
from dotenv import load_dotenv
import httpx
from termcolor import colored

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import the LLM interface
from src.game.llm_interface import LLMInterface

# Load environment variables
load_dotenv()

# Check for required API keys
if not os.getenv("OPENAI_API_KEY") or not os.getenv("ANTHROPIC_API_KEY"):
    print(colored("Error: Missing API keys. Please set OPENAI_API_KEY and ANTHROPIC_API_KEY in your .env file.", "red"))
    sys.exit(1)

async def main():
    """Main function demonstrating the LLM interface."""
    # Configuration
    api_base_url = "http://localhost:8000/api/v1"
    username = "testuser"
    password = "password123"
    game_name = "LLM Test Adventure"
    
    print(colored("=== The Last Centaur - LLM Interface Example ===", "magenta", attrs=["bold"]))
    
    # Initialize the LLM interface
    llm_interface = LLMInterface(api_base_url=api_base_url)
    
    # Step 1: Login to get an access token
    print(colored("\nLogging in...", "yellow"))
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{api_base_url}/auth/login",
                data={"username": username, "password": password},
                timeout=10.0
            )
            
            if response.status_code != 200:
                # Try to register if login fails
                print(colored("Login failed. Attempting to register...", "yellow"))
                register_response = await client.post(
                    f"{api_base_url}/auth/register",
                    headers={"Content-Type": "application/json"},
                    json={"username": username, "email": "test@example.com", "password": password},
                    timeout=10.0
                )
                
                if register_response.status_code != 200:
                    print(colored(f"Registration failed: {register_response.text}", "red"))
                    return
                
                # Try login again
                response = await client.post(
                    f"{api_base_url}/auth/login",
                    data={"username": username, "password": password},
                    timeout=10.0
                )
                
                if response.status_code != 200:
                    print(colored(f"Login failed after registration: {response.text}", "red"))
                    return
            
            data = response.json()
            access_token = data.get("access_token")
            print(colored("Successfully logged in!", "green"))
            
            # Step 2: List existing games or create a new one
            print(colored("\nListing games...", "yellow"))
            games_response = await client.get(
                f"{api_base_url}/game",
                headers={"Authorization": f"Bearer {access_token}"},
                timeout=10.0
            )
            
            games = games_response.json()
            game_id = None
            
            if games:
                print(colored(f"Found {len(games)} existing games:", "cyan"))
                for i, game in enumerate(games, 1):
                    print(colored(f"{i}. {game['name']} (ID: {game['id']})", "cyan"))
                
                # Use the first game
                game_id = games[0]['id']
                print(colored(f"Using game: {games[0]['name']}", "green"))
            else:
                # Create a new game
                print(colored("No existing games found. Creating a new one...", "yellow"))
                create_response = await client.post(
                    f"{api_base_url}/game",
                    headers={
                        "Content-Type": "application/json",
                        "Authorization": f"Bearer {access_token}"
                    },
                    json={"name": game_name, "max_players": 1, "description": "An example game for testing the LLM interface"},
                    timeout=10.0
                )
                
                if create_response.status_code != 200:
                    print(colored(f"Game creation failed: {create_response.text}", "red"))
                    return
                
                game_data = create_response.json()
                game_id = game_data.get("id")
                print(colored(f"Successfully created game: {game_name} (ID: {game_id})", "green"))
            
            # Step 3: Process some example commands
            print(colored("\n=== Starting Game Session ===", "magenta"))
            
            # Get user ID from the game data
            game_info_response = await client.get(
                f"{api_base_url}/game/{game_id}",
                headers={"Authorization": f"Bearer {access_token}"},
                timeout=10.0
            )
            
            game_info = game_info_response.json()
            user_id = game_info.get("user_id")
            
            # Example commands to process
            commands = [
                "look around",
                "check my inventory",
                "go north",
                "examine the surroundings carefully",
                "pick up any useful items"
            ]
            
            for command in commands:
                print(colored(f"\nUser: {command}", "yellow"))
                
                # Process the command using the LLM interface
                response = await llm_interface.process_user_input(
                    command, user_id, game_id, access_token
                )
                
                print(colored(f"Game: {response}", "cyan"))
                
                # Add a small delay between commands
                await asyncio.sleep(1)
            
            print(colored("\n=== End of Example ===", "magenta"))
            print(colored("This example demonstrated how to use the LLM interface programmatically.", "magenta"))
            print(colored("You can integrate this into your own applications or interfaces!", "magenta"))
            
    except Exception as e:
        print(colored(f"Error: {str(e)}", "red"))

if __name__ == "__main__":
    asyncio.run(main()) 