import os
import json
import asyncio
import logging
from typing import Dict, List, Any, Optional, Tuple
import httpx
from openai import AsyncOpenAI

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LLMInterface:
    """
    LLM-powered interface for The Last Centaur game.
    
    This class provides:
    1. Natural language understanding to convert user input to game commands
    2. Rich fantasy descriptions based on game responses
    3. Context-aware assistance and suggestions
    """
    
    def __init__(self, api_base_url: str, api_port: int = 8003):
        """Initialize the LLM interface."""
        self.api_base_url = f"http://localhost:{api_port}/api/v1"
        self.openai_client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.context_history = {}  # Store conversation history by user_id
        self.max_history_length = 10  # Maximum number of turns to keep in history
        
        # Command mapping for common natural language patterns
        self.command_patterns = {
            "move": ["go", "walk", "run", "travel", "head", "move", "bounce", "roll", "scoot", "head", "cruise", "stroll"],
            "look": ["look", "examine", "inspect", "observe", "check", "see", "peep", "scope", "scout", "scan"],
            "take": ["take", "grab", "pick up", "collect", "get", "yoink", "snag", "swipe", "nab", "steal", "five-finger discount", "loot", "pick"],
            "drop": ["drop", "discard", "throw away", "put down", "ditch", "dump", "toss"],
            "attack": ["attack", "fight", "hit", "strike", "battle", "throw hands", "square up", "catch these", "mess up", "throw down", "beat", "slay"],
            "talk": ["talk", "speak", "chat", "converse", "ask", "holla", "spit game", "rap with", "shoot the breeze", "drop a line"],
            "inventory": ["inventory", "items", "possessions", "backpack", "bag", "stash", "gear", "stuff", "loot", "what am i carrying", "what's in my", "show me my", "check inventory", "check my inventory", "what do i have", "what am i holding"],
            "help": ["help", "assist", "guide", "instructions", "how to", "what can i do"],
            "map": ["map", "location", "where am i", "surroundings", "what's around"]
        }
        
        # System prompt for command interpretation
        self.command_system_prompt = """
        You are an AI assistant for the text-based RPG game "The Last Centaur". Your task is to interpret the player's natural language input and convert it to a valid game command.
        
        Valid game commands include:
        - Movement: north, south, east, west (or n, s, e, w)
        - Look: look, examine [object]
        - Inventory: inventory, take [item], drop [item]
        - Combat: attack [enemy], defend, dodge
        - Interaction: talk [npc]
        - Game: save, help, hint, map
        
        CRITICAL: Use the provided context to understand what the player is referring to. When the player refers to items, enemies, or NPCs, you MUST use the EXACT names as they appear in the game state. For example:
        - If the game shows "old_map" as an item, and the player says "take the map", you MUST return "take old_map"
        - If the game shows "Wolf Pack" as an enemy, and the player says "attack wolves", you MUST return "attack Wolf Pack"
        - If the game shows "basic_supplies" as an item, and the player says "get supplies", you MUST return "take basic_supplies"
        
        Pay close attention to the current location description, visible items, enemies present, and other environmental details to understand the context of the player's command. The player may refer to objects described in the environment without using their exact names.
        
        For roleplay interactions with the environment that aren't explicitly listed in the game state:
        - "Pick up some leaves" → "take leaves"
        - "Gather stones from the ground" → "take stones"
        - "Collect flowers" → "take flowers"
        
        The player may use slang or informal language. Here are some examples of slang and their interpretations:
        
        Movement:
        - "Let's bounce to the north" → "north"
        - "Imma head north" → "north"
        - "Yo, let's roll outta here to the east" → "east"
        - "Bounce to the west side" → "west"
        - "Scoot over south" → "south"
        
        Looking/Examining:
        - "Peep that chest" → "examine chest"
        - "Yo, check out that weird tree" → "examine weird tree"
        - "What's the 411 on this place?" → "look"
        - "Scope the surroundings" → "look"
        
        Inventory:
        - "What's in my stash?" → "inventory"
        - "Lemme see my gear" → "inventory"
        - "What am I packin'?" → "inventory"
        - "Show me the goods I'm carrying" → "inventory"
        - "What's in my pockets, precious?" → "inventory"
        
        Taking Items:
        - "Yoink that sword" → "take sword" (or the exact item name from the game state)
        - "Snag that potion" → "take potion" (or the exact item name from the game state)
        - "Gimme that gold" → "take gold" (or the exact item name from the game state)
        - "Swipe the map" → "take old_map" (if "old_map" is the exact item name in the game state)
        
        Combat:
        - "Let's throw hands with that wolf" → "attack wolf" (or the exact enemy name from the game state)
        - "Square up against the goblin" → "attack goblin" (or the exact enemy name from the game state)
        - "Catch these hooves, troll!" → "attack troll" (or the exact enemy name from the game state)
        - "Mess up that orc" → "attack orc" (or the exact enemy name from the game state)
        
        Talking:
        - "Holla at that merchant" → "talk merchant" (or the exact NPC name from the game state)
        - "Spit some game to the innkeeper" → "talk innkeeper" (or the exact NPC name from the game state)
        - "Drop a line to that guard" → "talk guard" (or the exact NPC name from the game state)
        - "Shoot the breeze with the old man" → "talk old man" (or the exact NPC name from the game state)
        - "Rap with the wizard" → "talk wizard" (or the exact NPC name from the game state)
        
        Dropping Items:
        - "Drop this useless sword" → "drop sword" (or the exact item name from the game state)
        - "Toss away the empty bottle" → "drop bottle" (or the exact item name from the game state)
        - "Ditch the broken shield" → "drop shield" (or the exact item name from the game state)
        - "I don't need this map anymore" → "drop old_map" (if "old_map" is the exact item name in the game state)
        - "Get rid of these old boots" → "drop boots" (or the exact item name from the game state)
        - "Throw out the rotten food" → "drop food" (or the exact item name from the game state)
        
        Important distinction for drop commands:
        - "Drop a line to the merchant" → "talk merchant" (this is slang for talking)
        - "Drop my sword" → "drop sword" (this is actually dropping an item)
        - "Toss away the useless rock" → "drop rock"
        - "I don't need this potion anymore" → "drop potion"
        
        Respond ONLY with the exact game command, nothing else. For example:
        - If the user says "I want to go north", respond with "north"
        - If the user says "Pick up the sword", respond with "take sword" (or the exact item name)
        - If the user says "Check what I'm carrying", respond with "inventory"
        - If the user says "I want to get rid of this heavy armor", respond with "drop armor" (or the exact item name)
        - If the user says "Pick up some leaves from the ground", respond with "take leaves"
        - If the user says "Gather a few stones", respond with "take stones"
        - If the user says "Take the map" and the game state shows "old_map", respond with "take old_map"
        
        Be precise and concise. Do not add explanations or additional text.
        """
        
        # System prompt for response enhancement
        self.response_system_prompt = """
        You are an AI storyteller for the text-based RPG game "The Last Centaur". Your task is to enhance the game's responses with rich, immersive fantasy descriptions.
        
        The player is Centaur Prime, the last of their kind, seeking to reclaim their destiny in a world filled with ancient magic, forgotten lore, and challenging choices.
        
        Given the original game response, create a more vivid and detailed description that:
        1. Maintains all the factual information from the original response
        2. Adds sensory details (sights, sounds, smells, etc.)
        3. Incorporates the emotional and physical state of the centaur character
        4. Uses rich, evocative fantasy language
        5. Keeps a consistent tone that matches the game world
        
        Important: Never contradict or omit information from the original response. All items, enemies, exits, and game mechanics must be preserved exactly as they appear in the original.
        """
    
    async def process_user_input(self, user_input: str, user_id: str, game_id: str, access_token: str) -> str:
        """
        Process natural language input from the user and return an enhanced response.
        
        Args:
            user_input: The natural language input from the user
            user_id: The user's ID for context tracking
            game_id: The game instance ID
            access_token: The user's access token
            
        Returns:
            Enhanced response text
        """
        try:
            # Initialize context history for this user if it doesn't exist
            if user_id not in self.context_history:
                self.context_history[user_id] = []
            
            # Add user input to history
            self.context_history[user_id].append({"role": "user", "content": user_input})
            
            # Trim history if it exceeds max length
            if len(self.context_history[user_id]) > self.max_history_length * 2:  # *2 because we have user and assistant messages
                self.context_history[user_id] = self.context_history[user_id][-self.max_history_length * 2:]
            
            # Get current game state for context
            game_state = await self.get_game_state(game_id, access_token)
            
            # Convert natural language to game command with game state context
            game_command = await self._interpret_command(user_input, game_state)
            logger.info(f"Interpreted command: {game_command}")
            
            # Send command to game API
            game_response = await self._send_command_to_game(game_command, game_id, access_token)
            logger.info(f"Game response: {game_response}")
            
            # Enhance the response
            enhanced_response = await self._enhance_response(game_response, user_input, game_command)
            logger.info(f"Enhanced response: {enhanced_response}")
            
            # Add enhanced response to history
            self.context_history[user_id].append({"role": "assistant", "content": enhanced_response})
            
            return enhanced_response
            
        except Exception as e:
            logger.error(f"Error processing user input: {e}")
            return f"I encountered an error while processing your request: {str(e)}"
    
    async def _interpret_command(self, user_input: str, game_state: Dict[str, Any] = None) -> str:
        """
        Use LLM to interpret natural language input and convert to a game command.
        
        Args:
            user_input: The natural language input from the user
            game_state: The current game state for context
            
        Returns:
            Game command string
        """
        try:
            # Extract relevant information from game state if available
            current_items = []
            current_enemies = []
            current_exits = []
            tile_description = ""
            terrain_type = ""
            weather = ""
            time_of_day = ""
            player_inventory = []
            
            if game_state:
                # Extract current tile information
                if "current_tile" in game_state:
                    current_tile = game_state["current_tile"]
                    
                    # Extract visible items in the current location
                    if "items" in current_tile:
                        current_items = current_tile["items"]
                    
                    # Extract visible enemies
                    if "enemies" in current_tile:
                        current_enemies = current_tile["enemies"]
                    
                    # Extract available exits
                    if "exits" in current_tile:
                        current_exits = current_tile["exits"]
                    
                    # Extract tile description
                    if "description" in current_tile:
                        tile_description = current_tile["description"]
                    
                    # Extract terrain type
                    if "terrain_type" in current_tile:
                        terrain_type = current_tile["terrain_type"]
                
                # Extract environmental information
                if "environment" in game_state:
                    if "weather" in game_state["environment"]:
                        weather = game_state["environment"]["weather"]
                    if "time_of_day" in game_state["environment"]:
                        time_of_day = game_state["environment"]["time_of_day"]
                
                # Extract player inventory
                if "inventory" in game_state:
                    player_inventory = game_state["inventory"]
            
            # For simple, unambiguous commands, use pattern matching for efficiency
            lower_input = user_input.lower()
            
            # Check for direct direction commands
            directions = {"north": ["north", "n"], "south": ["south", "s"], 
                         "east": ["east", "e"], "west": ["west", "w"]}
            
            for direction, patterns in directions.items():
                for pattern in patterns:
                    if pattern == lower_input or f"go {pattern}" in lower_input or f"move {pattern}" in lower_input:
                        return direction
            
            # Check for inventory command
            if lower_input in ["inventory", "i", "check inventory", "check my inventory", "what am i carrying"]:
                return "inventory"
            
            # For more complex commands, use the LLM with comprehensive context
            context = f"""
            User input: {user_input}
            
            Current game state:
            """
            
            if tile_description:
                context += f"Current location description: {tile_description}\n"
            
            if terrain_type:
                context += f"Terrain type: {terrain_type}\n"
            
            if current_items:
                context += f"Items visible: {', '.join(current_items)}\n"
            
            if current_enemies:
                context += f"Enemies present: {', '.join(current_enemies)}\n"
            
            if current_exits:
                context += f"Available exits: {', '.join(current_exits)}\n"
            
            if weather:
                context += f"Current weather: {weather}\n"
            
            if time_of_day:
                context += f"Time of day: {time_of_day}\n"
            
            if player_inventory:
                context += f"Items in inventory: {', '.join(player_inventory)}\n"
            
            # Use OpenAI for command interpretation with comprehensive context
            response = await self.openai_client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": self.command_system_prompt},
                    {"role": "user", "content": context + f"\nWhat is the appropriate game command for: '{user_input}'?"}
                ],
                temperature=0.2,
                max_tokens=50
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logger.error(f"Error interpreting command: {e}")
            # Fall back to passing the input directly as a command
            return user_input
    
    async def _send_command_to_game(self, command: str, game_id: str, access_token: str) -> str:
        """
        Send a command to the game API and return the response.
        
        Args:
            command: The game command to send
            game_id: The game instance ID
            access_token: The user's access token
            
        Returns:
            Game response string
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.api_base_url}/game/{game_id}/command",
                    headers={
                        "Content-Type": "application/json",
                        "Authorization": f"Bearer {access_token}"
                    },
                    json={"command": command},
                    timeout=10.0
                )
                
                response.raise_for_status()
                data = response.json()
                
                # Extract the response text from the API response
                return data.get("response", "No response from game")
                
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error sending command to game: {e}")
            return f"Error communicating with the game: {e.response.status_code}"
        except httpx.RequestError as e:
            logger.error(f"Request error sending command to game: {e}")
            return "Error connecting to the game server"
        except Exception as e:
            logger.error(f"Unexpected error sending command to game: {e}")
            return f"Unexpected error: {str(e)}"
    
    async def _enhance_response(self, game_response: str, user_input: str, game_command: str) -> str:
        """
        Use LLM to enhance the game response with rich fantasy descriptions.
        
        Args:
            game_response: The original response from the game
            user_input: The original user input
            game_command: The interpreted game command
            
        Returns:
            Enhanced response string
        """
        try:
            # If the game response is empty or very short, return a default message
            if not game_response or len(game_response.strip()) < 3:
                if "look" in game_command or "examine" in game_command:
                    return "You see nothing special about that."
                elif "attack" in game_command:
                    return "You swing at the air, finding no target for your attack."
                elif "take" in game_command:
                    return "You reach out, but there's nothing there to take."
                elif "talk" in game_command:
                    return "There's no one here to talk to."
                else:
                    return "Nothing happens."
            
            # Prepare context for the LLM
            context = f"""
            User input: {user_input}
            Game command: {game_command}
            Original game response: {game_response}
            """
            
            # Use OpenAI for response enhancement
            response = await self.openai_client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": self.response_system_prompt},
                    {"role": "user", "content": context}
                ],
                temperature=0.7,
                max_tokens=1000
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logger.error(f"Error enhancing response: {e}")
            # Fall back to the original response
            return game_response
    
    async def get_game_state(self, game_id: str, access_token: str) -> Dict[str, Any]:
        """
        Get the current game state from the API.
        
        Args:
            game_id: The game instance ID
            access_token: The user's access token
            
        Returns:
            Game state dictionary
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.api_base_url}/game/{game_id}",
                    headers={"Authorization": f"Bearer {access_token}"},
                    timeout=10.0
                )
                
                response.raise_for_status()
                return response.json()
                
        except Exception as e:
            logger.error(f"Error getting game state: {e}")
            return {}
    
    async def get_game_map(self, game_id: str, access_token: str) -> Dict[str, Any]:
        """
        Get the game map from the API.
        
        Args:
            game_id: The game instance ID
            access_token: The user's access token
            
        Returns:
            Game map dictionary
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.api_base_url}/game/{game_id}/map",
                    headers={"Authorization": f"Bearer {access_token}"},
                    timeout=10.0
                )
                
                response.raise_for_status()
                return response.json()
                
        except Exception as e:
            logger.error(f"Error getting game map: {e}")
            return {} 