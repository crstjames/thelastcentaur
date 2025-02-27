import os
import sys
import json
import asyncio
import argparse
import getpass
from typing import Dict, Any, Optional
import httpx
from termcolor import colored

from src.game.llm_interface import LLMInterface

class GameCLI:
    """
    CLI interface for playing The Last Centaur with natural language.
    
    This CLI allows players to:
    1. Register or login to the game
    2. Create a new game or load an existing one
    3. Interact with the game using natural language
    4. Receive rich, immersive responses
    """
    
    def __init__(self, api_port: int = 8003):
        """Initialize the game CLI."""
        self.api_base_url = f"http://localhost:{api_port}/api/v1"
        self.llm_interface = LLMInterface(api_base_url=self.api_base_url, api_port=api_port)
        self.access_token = None
        self.user_id = None
        self.game_id = None
        self.username = None
    
    async def register_user(self, username: str, email: str, password: str) -> bool:
        """
        Register a new user.
        
        Args:
            username: The desired username
            email: The user's email
            password: The user's password
            
        Returns:
            True if registration was successful, False otherwise
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.api_base_url}/auth/register",
                    headers={"Content-Type": "application/json"},
                    json={"username": username, "email": email, "password": password},
                    timeout=10.0
                )
                
                if response.status_code in [200, 201]:  # Accept both 200 OK and 201 Created
                    data = response.json()
                    self.user_id = data.get("id")
                    self.username = username
                    print(colored(f"Successfully registered as {username}!", "green"))
                    return True
                else:
                    print(colored(f"Registration failed: {response.text}", "red"))
                    return False
                
        except Exception as e:
            print(colored(f"Error during registration: {str(e)}", "red"))
            return False
    
    async def login(self, username: str, password: str) -> bool:
        """
        Login with existing credentials.
        
        Args:
            username: The user's username
            password: The user's password
            
        Returns:
            True if login was successful, False otherwise
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.api_base_url}/auth/login",
                    data={"username": username, "password": password},
                    timeout=10.0
                )
                
                if response.status_code == 200:
                    data = response.json()
                    self.access_token = data.get("access_token")
                    self.username = username
                    print(colored(f"Successfully logged in as {username}!", "green"))
                    return True
                else:
                    print(colored(f"Login failed: {response.text}", "red"))
                    return False
                
        except Exception as e:
            print(colored(f"Error during login: {str(e)}", "red"))
            return False
    
    async def create_game(self, name: str, description: str) -> bool:
        """
        Create a new game instance.
        
        Args:
            name: The name of the game
            description: A description of the game
            
        Returns:
            True if game creation was successful, False otherwise
        """
        if not self.access_token:
            print(colored("You must be logged in to create a game.", "red"))
            return False
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.api_base_url}/game",
                    headers={
                        "Content-Type": "application/json",
                        "Authorization": f"Bearer {self.access_token}"
                    },
                    json={"name": name, "max_players": 1, "description": description},
                    timeout=10.0
                )
                
                if response.status_code == 200:
                    data = response.json()
                    self.game_id = data.get("id")
                    self.user_id = data.get("user_id")
                    print(colored(f"Successfully created game: {name}!", "green"))
                    return True
                else:
                    print(colored(f"Game creation failed: {response.text}", "red"))
                    return False
                
        except Exception as e:
            print(colored(f"Error creating game: {str(e)}", "red"))
            return False
    
    async def list_games(self) -> Optional[Dict[str, Any]]:
        """
        List all games for the current user.
        
        Returns:
            Dictionary of games or None if failed
        """
        if not self.access_token:
            print(colored("You must be logged in to list games.", "red"))
            return None
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.api_base_url}/game",
                    headers={"Authorization": f"Bearer {self.access_token}"},
                    timeout=10.0
                )
                
                if response.status_code == 200:
                    games = response.json()
                    if not games:
                        print(colored("You don't have any games yet.", "yellow"))
                        return {}
                    
                    print(colored("Your games:", "cyan"))
                    for i, game in enumerate(games, 1):
                        print(colored(f"{i}. {game['name']} (ID: {game['id']})", "cyan"))
                        print(f"   Description: {game['description']}")
                        print(f"   Created: {game['created_at']}")
                        print()
                    
                    return {game['id']: game for game in games}
                else:
                    print(colored(f"Failed to list games: {response.text}", "red"))
                    return None
                
        except Exception as e:
            print(colored(f"Error listing games: {str(e)}", "red"))
            return None
    
    async def load_game(self, game_id: str) -> bool:
        """
        Load an existing game.
        
        Args:
            game_id: The ID of the game to load
            
        Returns:
            True if game loading was successful, False otherwise
        """
        if not self.access_token:
            print(colored("You must be logged in to load a game.", "red"))
            return False
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.api_base_url}/game/{game_id}",
                    headers={"Authorization": f"Bearer {self.access_token}"},
                    timeout=10.0
                )
                
                if response.status_code == 200:
                    data = response.json()
                    self.game_id = game_id
                    self.user_id = data.get("user_id")
                    print(colored(f"Successfully loaded game: {data.get('name')}!", "green"))
                    return True
                else:
                    print(colored(f"Game loading failed: {response.text}", "red"))
                    return False
                
        except Exception as e:
            print(colored(f"Error loading game: {str(e)}", "red"))
            return False
    
    async def play_game(self):
        """Start the game loop for playing with natural language."""
        if not self.access_token or not self.game_id:
            print(colored("You must be logged in and have a game loaded to play.", "red"))
            return
        
        print(colored("\n=== Welcome to The Last Centaur ===", "magenta", attrs=["bold"]))
        print(colored("You are Centaur Prime, the last of your kind, seeking to reclaim your destiny.", "magenta"))
        print(colored("Type your actions in natural language. Type 'quit' to exit.\n", "magenta"))
        
        # Start with a look command to see the surroundings
        initial_response = await self.llm_interface.process_user_input(
            "look around", self.user_id, self.game_id, self.access_token
        )
        print(colored(initial_response, "cyan"))
        
        while True:
            try:
                user_input = input(colored("\nWhat would you like to do? ", "yellow")).strip()
                
                if user_input.lower() in ["quit", "exit", "bye"]:
                    print(colored("Thank you for playing The Last Centaur. Your progress has been saved.", "magenta"))
                    break
                
                print(colored("Thinking...", "grey"))
                response = await self.llm_interface.process_user_input(
                    user_input, self.user_id, self.game_id, self.access_token
                )
                
                print(colored(response, "cyan"))
                
            except KeyboardInterrupt:
                print(colored("\nExiting game. Your progress has been saved.", "magenta"))
                break
            except Exception as e:
                print(colored(f"Error: {str(e)}", "red"))
    
    async def setup_and_play(self):
        """Setup the game (login/register, create/load game) and start playing."""
        print(colored("=== The Last Centaur ===", "magenta", attrs=["bold"]))
        print(colored("A text-based RPG with natural language interface\n", "magenta"))
        
        # Login or register
        auth_choice = input(colored("Do you want to (1) login or (2) register? ", "yellow")).strip()
        
        if auth_choice == "1":
            # Login
            username = input(colored("Username: ", "yellow")).strip()
            password = getpass.getpass(colored("Password: ", "yellow"))
            
            if not await self.login(username, password):
                return
        elif auth_choice == "2":
            # Register
            username = input(colored("Username: ", "yellow")).strip()
            email = input(colored("Email: ", "yellow")).strip()
            password = getpass.getpass(colored("Password: ", "yellow"))
            
            if not await self.register_user(username, email, password):
                return
            
            # Login after registration
            if not await self.login(username, password):
                return
        else:
            print(colored("Invalid choice. Exiting.", "red"))
            return
        
        # List existing games or create a new one
        games = await self.list_games()
        
        if games:
            game_choice = input(colored("\nDo you want to (1) load an existing game or (2) create a new one? ", "yellow")).strip()
            
            if game_choice == "1":
                # Load existing game
                game_id = input(colored("Enter the game ID to load: ", "yellow")).strip()
                if not await self.load_game(game_id):
                    return
            elif game_choice == "2":
                # Create new game
                name = input(colored("Game name: ", "yellow")).strip()
                description = input(colored("Game description: ", "yellow")).strip()
                
                if not await self.create_game(name, description):
                    return
            else:
                print(colored("Invalid choice. Exiting.", "red"))
                return
        else:
            # Create new game if no existing games
            print(colored("\nYou don't have any games yet. Let's create one!", "yellow"))
            name = input(colored("Game name: ", "yellow")).strip()
            description = input(colored("Game description: ", "yellow")).strip()
            
            if not await self.create_game(name, description):
                return
        
        # Start playing
        await self.play_game()

async def main(port=8000):
    """Main entry point for the CLI."""
    cli = GameCLI(api_port=port)
    await cli.setup_and_play()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="The Last Centaur - Natural Language CLI")
    parser.add_argument("--port", type=int, default=8000, help="Port for the game API")
    args = parser.parse_args()
    
    asyncio.run(main(args.port)) 