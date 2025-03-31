#!/usr/bin/env python
"""
API Endpoint Test Script

This script tests all the API endpoints defined in the docs/api-reference.md file.
It validates that each endpoint is accessible and returns the expected response.

Usage:
    python scripts/test_api_endpoints.py

The script will output the test results for each endpoint.
"""

import sys
import os
import asyncio
import httpx
import json
from termcolor import colored
from datetime import datetime
import random
import string
import traceback

# Add the parent directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Helper function to generate random strings
def generate_random_string(length=8):
    """Generate a random string of fixed length."""
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for _ in range(length))

class APITester:
    """Class to test API endpoints."""
    
    def __init__(self, base_url="http://localhost:8000/api/v1"):
        """Initialize the tester with base URL."""
        self.base_url = base_url
        self.token = None
        self.user_id = None
        self.game_id = None
        self.username = f"test_user_{generate_random_string()}"
        self.password = f"test_pass_{generate_random_string()}"
        self.email = f"{self.username}@example.com"
        
        # Test results tracking
        self.passed = 0
        self.failed = 0
        self.total = 0
    
    def log_success(self, message):
        """Log a success message."""
        print(colored(f"✅ {message}", "green"))
        self.passed += 1
        self.total += 1
    
    def log_failure(self, message, error=None):
        """Log a failure message with optional error."""
        print(colored(f"❌ {message}", "red"))
        if error:
            print(colored(f"   Error: {error}", "red"))
        self.failed += 1
        self.total += 1
    
    def log_info(self, message):
        """Log an informational message."""
        print(colored(f"ℹ️ {message}", "blue"))
    
    def log_warning(self, message):
        """Log a warning message."""
        print(colored(f"⚠️ {message}", "yellow"))
    
    def log_header(self, message):
        """Log a section header."""
        print("\n" + "=" * 80)
        print(colored(f"🧪 {message}", "cyan"))
        print("=" * 80)
    
    async def test_register(self):
        """Test user registration."""
        self.log_header("Testing User Registration")
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/auth/register",
                    json={
                        "username": self.username,
                        "email": self.email,
                        "password": self.password
                    }
                )
                
                if response.status_code in (200, 201):
                    user_data = response.json()
                    self.user_id = user_data.get("id")
                    self.log_success(f"User registration successful. Status: {response.status_code}")
                    self.log_info(f"Created user: {self.username} with ID: {self.user_id}")
                    return True
                else:
                    self.log_failure(f"User registration failed. Status: {response.status_code}", response.text)
                    return False
        except Exception as e:
            self.log_failure("Exception during user registration", str(e))
            return False
    
    async def test_login(self):
        """Test user login."""
        self.log_header("Testing User Login")
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/auth/login",
                    data={
                        "username": self.username,
                        "password": self.password
                    }
                )
                
                if response.status_code == 200:
                    login_result = response.json()
                    self.token = login_result.get("access_token")
                    
                    if self.token:
                        self.log_success(f"Login successful. Status: {response.status_code}")
                        self.log_info(f"Received token: {self.token[:20]}...")
                        return True
                    else:
                        self.log_failure("No access token in response")
                        return False
                else:
                    self.log_failure(f"Login failed. Status: {response.status_code}", response.text)
                    return False
        except Exception as e:
            self.log_failure("Exception during login", str(e))
            return False
    
    async def test_create_game(self):
        """Test creating a game instance."""
        self.log_header("Testing Create Game")
        
        if not self.token:
            self.log_warning("Skipping test: No authentication token available")
            return False
        
        try:
            game_name = f"Test Game {generate_random_string()}"
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/game",
                    json={
                        "name": game_name,
                        "description": "A test game instance",
                        "max_players": 1
                    },
                    headers={"Authorization": f"Bearer {self.token}"}
                )
                
                if response.status_code in (200, 201):
                    game_data = response.json()
                    self.game_id = game_data.get("id")
                    self.log_success(f"Game creation successful. Status: {response.status_code}")
                    self.log_info(f"Created game: {game_name} with ID: {self.game_id}")
                    return True
                else:
                    self.log_failure(f"Game creation failed. Status: {response.status_code}", response.text)
                    return False
        except Exception as e:
            self.log_failure("Exception during game creation", str(e))
            return False
    
    async def test_list_games(self):
        """Test listing games."""
        self.log_header("Testing List Games")
        
        if not self.token:
            self.log_warning("Skipping test: No authentication token available")
            return False
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/game",
                    headers={"Authorization": f"Bearer {self.token}"}
                )
                
                if response.status_code == 200:
                    games = response.json()
                    self.log_success(f"List games successful. Status: {response.status_code}")
                    self.log_info(f"Found {len(games)} games")
                    return True
                else:
                    self.log_failure(f"List games failed. Status: {response.status_code}", response.text)
                    return False
        except Exception as e:
            self.log_failure("Exception during list games", str(e))
            return False
    
    async def test_get_game(self):
        """Test getting a specific game."""
        self.log_header("Testing Get Game")
        
        if not self.token or not self.game_id:
            self.log_warning("Skipping test: No authentication token or game ID available")
            return False
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/game/{self.game_id}",
                    headers={"Authorization": f"Bearer {self.token}"}
                )
                
                if response.status_code == 200:
                    game = response.json()
                    self.log_success(f"Get game successful. Status: {response.status_code}")
                    self.log_info(f"Retrieved game: {game.get('name')}")
                    return True
                else:
                    self.log_failure(f"Get game failed. Status: {response.status_code}", response.text)
                    return False
        except Exception as e:
            self.log_failure("Exception during get game", str(e))
            return False
    
    async def test_update_game(self):
        """Test updating a game."""
        self.log_header("Testing Update Game")
        
        if not self.token or not self.game_id:
            self.log_warning("Skipping test: No authentication token or game ID available")
            return False
        
        try:
            updated_name = f"Updated Game {generate_random_string()}"
            
            async with httpx.AsyncClient() as client:
                response = await client.put(
                    f"{self.base_url}/game/{self.game_id}",
                    json={
                        "name": updated_name,
                        "description": "An updated test game instance"
                    },
                    headers={"Authorization": f"Bearer {self.token}"}
                )
                
                if response.status_code == 200:
                    game = response.json()
                    self.log_success(f"Update game successful. Status: {response.status_code}")
                    self.log_info(f"Updated game name to: {game.get('name')}")
                    return True
                else:
                    self.log_failure(f"Update game failed. Status: {response.status_code}", response.text)
                    return False
        except Exception as e:
            self.log_failure("Exception during update game", str(e))
            return False
    
    async def test_execute_command(self):
        """Test executing a command on a game."""
        self.log_header("Testing Execute Command")
        
        if not self.token or not self.game_id:
            self.log_warning("Skipping test: No authentication token or game ID available")
            return False
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/game/{self.game_id}/command",
                    json={
                        "command": "look",
                        "use_llm": False
                    },
                    headers={"Authorization": f"Bearer {self.token}"}
                )
                
                if response.status_code == 200:
                    result = response.json()
                    self.log_success(f"Execute command successful. Status: {response.status_code}")
                    self.log_info(f"Command result: {result.get('response')[:50]}...")
                    return True
                else:
                    self.log_failure(f"Execute command failed. Status: {response.status_code}", response.text)
                    return False
        except Exception as e:
            self.log_failure("Exception during execute command", str(e))
            return False
    
    async def test_get_map(self):
        """Test getting the game map."""
        self.log_header("Testing Get Map")
        
        if not self.token or not self.game_id:
            self.log_warning("Skipping test: No authentication token or game ID available")
            return False
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/game/{self.game_id}/map",
                    headers={"Authorization": f"Bearer {self.token}"}
                )
                
                if response.status_code == 200:
                    map_data = response.json()
                    self.log_success(f"Get map successful. Status: {response.status_code}")
                    self.log_info(f"Map has {len(map_data.get('tiles', []))} tiles")
                    return True
                else:
                    self.log_failure(f"Get map failed. Status: {response.status_code}", response.text)
                    return False
        except Exception as e:
            self.log_failure("Exception during get map", str(e))
            return False
    
    async def test_delete_game(self):
        """Test deleting a game."""
        self.log_header("Testing Delete Game")
        
        if not self.token or not self.game_id:
            self.log_warning("Skipping test: No authentication token or game ID available")
            return False
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.delete(
                    f"{self.base_url}/game/{self.game_id}",
                    headers={"Authorization": f"Bearer {self.token}"}
                )
                
                if response.status_code in (200, 204):
                    self.log_success(f"Delete game successful. Status: {response.status_code}")
                    return True
                else:
                    self.log_failure(f"Delete game failed. Status: {response.status_code}", response.text)
                    return False
        except Exception as e:
            self.log_failure("Exception during delete game", str(e))
            return False
    
    async def test_debug_routes(self):
        """Test the debug/routes endpoint."""
        self.log_header("Testing Debug Routes")
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{self.base_url}/game/debug/routes")
                
                if response.status_code == 200:
                    routes = response.json()
                    self.log_success(f"Debug routes successful. Status: {response.status_code}")
                    self.log_info(f"Found {len(routes)} routes")
                    return True
                else:
                    self.log_failure(f"Debug routes failed. Status: {response.status_code}", response.text)
                    return False
        except Exception as e:
            self.log_failure("Exception during debug routes", str(e))
            return False
    
    def log_summary(self):
        """Log the summary of all tests."""
        print("\n" + "=" * 80)
        print(colored(f"🏁 TEST SUMMARY", "magenta"))
        print("=" * 80)
        print(f"Total tests: {self.total}")
        print(colored(f"Passed: {self.passed}", "green"))
        print(colored(f"Failed: {self.failed}", "red"))
        print("=" * 80)
    
    async def run_all_tests(self):
        """Run all API tests."""
        print(colored(f"\n🚀 Starting API Tests at {datetime.now()}", "cyan"))
        print(colored(f"Base URL: {self.base_url}", "cyan"))
        print(colored(f"Test Username: {self.username}", "cyan"))
        
        # Authentication tests
        await self.test_register()
        await self.test_login()
        
        # Game tests
        await self.test_create_game()
        await self.test_list_games()
        await self.test_get_game()
        await self.test_update_game()
        await self.test_execute_command()
        await self.test_get_map()
        await self.test_delete_game()
        
        # Debug tests
        await self.test_debug_routes()
        
        # Print summary
        self.log_summary()

async def main():
    """Main function to run the tests."""
    try:
        # Create the tester
        tester = APITester()
        
        # Run all tests
        await tester.run_all_tests()
    except Exception as e:
        print(colored(f"❌ Unhandled exception during tests: {e}", "red"))
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main()) 