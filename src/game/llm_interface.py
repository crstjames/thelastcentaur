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
            "take": ["take", "grab", "pick up", "collect", "get", "yoink", "snag", "swipe", "nab", "steal", "five-finger discount", "loot"],
            "drop": ["drop", "discard", "throw away", "put down", "ditch", "dump", "toss"],
            "attack": ["attack", "fight", "hit", "strike", "battle", "throw hands", "square up", "catch these", "mess up", "throw down", "beat", "slay"],
            "talk": ["talk", "speak", "chat", "converse", "ask", "holla", "spit game", "rap with", "shoot the breeze", "drop a line"],
            "inventory": ["inventory", "items", "possessions", "backpack", "bag", "stash", "gear", "stuff", "loot", "what am i carrying", "what's in my", "show me my"],
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
        - "Yoink that sword" → "take sword"
        - "Snag that potion" → "take potion"
        - "Gimme that gold" → "take gold"
        - "Swipe the map" → "take map"
        
        Combat:
        - "Let's throw hands with that wolf" → "attack wolf"
        - "Square up against the goblin" → "attack goblin"
        - "Catch these hooves, troll!" → "attack troll"
        - "Mess up that orc" → "attack orc"
        
        Talking:
        - "Holla at that merchant" → "talk merchant"
        - "Spit some game to the innkeeper" → "talk innkeeper"
        - "Drop a line to that guard" → "talk guard"
        - "Shoot the breeze with the old man" → "talk old man"
        - "Rap with the wizard" → "talk wizard"
        
        Dropping Items:
        - "Drop this useless sword" → "drop sword"
        - "Toss away the empty bottle" → "drop bottle"
        - "Ditch the broken shield" → "drop shield"
        - "I don't need this map anymore" → "drop map"
        - "Get rid of these old boots" → "drop boots"
        - "Throw out the rotten food" → "drop food"
        
        Important distinction for drop commands:
        - "Drop a line to the merchant" → "talk merchant" (this is slang for talking)
        - "Drop my sword" → "drop sword" (this is actually dropping an item)
        - "Toss away the useless rock" → "drop rock"
        - "I don't need this potion anymore" → "drop potion"
        
        Respond ONLY with the exact game command, nothing else. For example:
        - If the user says "I want to go north", respond with "north"
        - If the user says "Pick up the sword", respond with "take sword"
        - If the user says "Check what I'm carrying", respond with "inventory"
        - If the user says "I want to get rid of this heavy armor", respond with "drop armor"
        
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
            
            # Convert natural language to game command
            game_command = await self._interpret_command(user_input)
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
    
    async def _interpret_command(self, user_input: str) -> str:
        """
        Use LLM to interpret natural language input and convert to a game command.
        
        Args:
            user_input: The natural language input from the user
            
        Returns:
            Game command string
        """
        try:
            # First try simple pattern matching for efficiency
            lower_input = user_input.lower()
            
            # Check for direct direction commands
            directions = {"north": ["north", "n"], "south": ["south", "s"], 
                         "east": ["east", "e"], "west": ["west", "w"]}
            
            for direction, patterns in directions.items():
                for pattern in patterns:
                    if pattern == lower_input or f"go {pattern}" in lower_input or f"move {pattern}" in lower_input:
                        return direction
            
            # Check for inventory-related slang expressions
            inventory_slang = ["stash", "gear", "packin", "carrying", "pockets", "what am i carrying", "what's in my", "show me my"]
            if any(term in lower_input for term in inventory_slang):
                return "inventory"
            
            # Check for taking items slang
            take_slang = ["yoink", "snag", "gimme", "swipe", "nab", "steal", "five-finger discount"]
            if any(term in lower_input for term in take_slang):
                # Try to extract the item
                if "five-finger discount" in lower_input:
                    parts = lower_input.split("five-finger discount on", 1)
                    if len(parts) > 1 and parts[1]:
                        item = parts[1].strip()
                        # Clean up the item name
                        item = item.replace("that ", "").replace("the ", "").strip()
                        return f"take {item}"
                
                words = lower_input.split()
                for i, word in enumerate(words):
                    if word in take_slang and i < len(words) - 1:
                        item = " ".join(words[i+1:])
                        # Clean up the item name
                        item = item.replace("that ", "").replace("the ", "").strip()
                        return f"take {item}"
            
            # Check for attack slang
            attack_slang = ["throw hands", "square up", "catch these", "mess up", "throw down"]
            if any(term in lower_input for term in attack_slang):
                # Try to extract the enemy
                for term in attack_slang:
                    if term in lower_input:
                        parts = lower_input.split(term, 1)
                        if len(parts) > 1 and parts[1]:
                            enemy = parts[1].strip()
                            # Clean up the enemy name
                            enemy = enemy.replace("with ", "").replace("against ", "").replace("the ", "").strip()
                            # Special case for "Catch these hooves, troll!"
                            if "hooves" in enemy and "troll" in enemy:
                                return "attack troll"
                            return f"attack {enemy}"
            
            # Check for talk slang
            talk_slang = ["holla", "spit game", "rap with", "shoot the breeze", "drop a line"]
            if any(term in lower_input for term in talk_slang):
                # Try to extract the NPC
                for term in talk_slang:
                    if term in lower_input:
                        parts = lower_input.split(term, 1)
                        if len(parts) > 1 and parts[1]:
                            npc = parts[1].strip()
                            # Clean up the NPC name
                            npc = npc.replace("to ", "").replace("with ", "").replace("at ", "").replace("the ", "").strip()
                            # Fix "thmerchant" and "thguard" issues
                            if npc.startswith("th"):
                                npc = npc[2:]
                            return f"talk {npc}"
            
            # Check for drop commands - distinguish between "drop a line" (talk) and "drop an item"
            drop_patterns = ["drop", "discard", "throw away", "put down", "ditch", "dump", "toss"]
            get_rid_patterns = ["get rid of", "don't need", "throw out", "dispose of"]
            
            # First check for "get rid of" type expressions
            if any(pattern in lower_input for pattern in get_rid_patterns):
                for pattern in get_rid_patterns:
                    if pattern in lower_input:
                        parts = lower_input.split(pattern, 1)
                        if len(parts) > 1 and parts[1]:
                            item = parts[1].strip()
                            # Clean up the item name
                            item = item.replace("this ", "").replace("these ", "").replace("the ", "").replace("my ", "").strip()
                            # Remove any trailing words like "anymore"
                            item_words = item.split()
                            if "anymore" in item_words:
                                item_words.remove("anymore")
                            item = " ".join(item_words)
                            if item:
                                return f"drop {item}"
            
            # Then check for regular drop patterns
            if any(pattern in lower_input for pattern in drop_patterns):
                # Check if this is "drop a line" or similar talk slang
                if "drop a line" in lower_input or "drop some lines" in lower_input:
                    # This is talk slang, not a drop command
                    if "to " in lower_input:
                        npc = lower_input.split("to ", 1)[1].strip()
                        return f"talk {npc}"
                    else:
                        return "talk"
                
                # This is a genuine drop command
                for pattern in drop_patterns:
                    if pattern in lower_input:
                        # Try to extract what they want to drop
                        parts = lower_input.split(pattern, 1)
                        if len(parts) > 1 and parts[1]:
                            item = parts[1].strip()
                            # Clean up the item name
                            item = item.replace("the ", "").replace("this ", "").replace("my ", "").replace("away ", "").strip()
                            if item:
                                return f"drop {item}"
                
                # If we couldn't extract an item, just return the drop command
                return "drop"
            
            # Direction-specific handling for movement commands
            direction_words = {
                "north": ["north", "n", "up", "forward"],
                "south": ["south", "s", "down", "backward", "back"],
                "east": ["east", "e", "right"],
                "west": ["west", "w", "left"]
            }
            
            # Check for direction-specific movement
            for direction, words in direction_words.items():
                if any(word in lower_input.split() for word in words):
                    return direction
            
            # Check for other common command patterns
            for command, patterns in self.command_patterns.items():
                for pattern in patterns:
                    if pattern == lower_input or pattern in lower_input:
                        # Handle special cases
                        if command == "look" and "at " in lower_input:
                            # Extract what they want to look at
                            target = lower_input.split("at ", 1)[1].strip()
                            return f"examine {target}"
                        elif command == "take" and any(p in lower_input for p in ["up", "get", "grab"]):
                            # Extract what they want to take
                            for prep in ["up", "get", "grab"]:
                                if f"{prep} " in lower_input:
                                    target = lower_input.split(f"{prep} ", 1)[1].strip()
                                    return f"take {target}"
                        elif command == "talk" and "to " in lower_input:
                            # Extract who they want to talk to
                            target = lower_input.split("to ", 1)[1].strip()
                            return f"talk {target}"
                        elif command == "attack":
                            # Extract what they want to attack
                            for attack_word in ["attack", "fight", "hit"]:
                                if f"{attack_word} " in lower_input:
                                    target = lower_input.split(f"{attack_word} ", 1)[1].strip()
                                    return f"attack {target}"
                        
                        # Default case - just return the command
                        return command
            
            # If pattern matching fails, use LLM for more complex interpretation
            response = await self.openai_client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": self.command_system_prompt},
                    {"role": "user", "content": user_input}
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