import os
import json
import asyncio
import logging
from typing import Dict, List, Any, Optional, Tuple
import httpx
from openai import AsyncOpenAI

from src.game.environmental_items import is_environmental_item, update_inventory_with_item

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
        - If the game shows "shadow_scout" as an NPC, and the player says "talk to the scout", you MUST return "talk shadow_scout"
        
        NPC INTERACTIONS: When the player wants to talk to an NPC, you MUST use the exact NPC ID as it appears in the game state. NPCs are listed in the "NPCs present" section of the context. For example:

        ENVIRONMENTAL INTERACTIONS: The player can interact with environmental elements that aren't explicitly listed but would naturally be present based on the terrain type and description. For example:
        - In a forest: leaves, twigs, bark, berries, moss, flowers, herbs
        - Near mountains: rocks, stones, pebbles, dirt, snow, ice
        - By a river: water, reeds, clay, mud, sand
        - On a beach: sand, shells, seaweed, driftwood
        - In a cave: rocks, stones, crystals, dust, dirt
        - In a clearing: grass, flowers, weeds, dirt, soil
        - Among ruins: dust, debris, fragments, stones, rubble
        
        When the player wants to interact with these environmental elements, convert their request to the appropriate command (e.g., "take leaves", "take stones", etc.).
        
        Pay close attention to the current location description, visible items, enemies present, and other environmental details to understand the context of the player's command. The player may refer to objects described in the environment without using their exact names.
        
        For roleplay interactions with the environment that aren't explicitly listed in the game state:
        - "Pick up some leaves" → "take leaves"
        - "Gather stones from the ground" → "take stones"
        - "Collect flowers" → "take flowers"
        - "Scoop up some water" → "take water"
        - "Break off a piece of bark" → "take bark"
        
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
        - "Talk to the scout" → "talk shadow_scout" (if "shadow_scout" is the exact NPC ID in the game state)
        - "Ask the scout about the shadow key" → "talk shadow_scout" (if "shadow_scout" is the exact NPC ID in the game state)
        - "Speak with the scout" → "talk shadow_scout" (if "shadow_scout" is the exact NPC ID in the game state)
        
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
        - If the user says "Talk to the scout" and the game state shows "shadow_scout", respond with "talk shadow_scout"
        
        Be precise and concise. Do not add explanations or additional text.
        """
        
        # System prompt for response enhancement
        self.response_system_prompt = """
        You are an AI storyteller for the text-based RPG game "The Last Centaur". Your task is to enhance the game's responses with concise, immersive fantasy descriptions.
        
        The player is Centaur Prime, the last of their kind, seeking to reclaim their destiny in a world filled with ancient magic, forgotten lore, and challenging choices.
        
        IMPORTANT RULES TO FOLLOW:
        1. For movement commands or "look around" commands: Provide a rich but concise description of the location.
        2. For object interactions (examine, take, etc.): ONLY describe the specific object being interacted with, NOT the entire location.
        3. For NPC interactions (talk, chat): Focus only on the conversation and the NPC's appearance/reaction.
        4. Always maintain all the factual information from the original response.
        
        RESPONSE FORMAT REQUIREMENTS:
        - For movement/look commands: Use up to two short paragraphs with rich environmental details
        - For object interactions: Use ONLY ONE short paragraph (1-2 sentences) focused specifically on the object
        - For NPC interactions: One paragraph for NPC description/reaction, one for the content of their words
        - Add sensory details (sights, sounds, smells) but be extremely concise
        - Never exceed three sentences total for any response
        
        IMPORTANT: Never contradict or omit information from the original response. All items, enemies, exits, and game mechanics must be preserved exactly as they appear in the original.
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
            # Add detailed logging for debugging
            logger.info(f"[COMMAND FLOW] USER INPUT: '{user_input}'")
            
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
            logger.info(f"[COMMAND FLOW] GAME STATE: NPCs: {game_state.get('current_tile', {}).get('npcs', [])}") 
            
            # Convert natural language to game command with game state context
            game_command = await self._interpret_command(user_input, game_state)
            logger.info(f"[COMMAND FLOW] INTERPRETED COMMAND: '{game_command}'")
            
            # Execute the command and get the response
            logger.info(f"[COMMAND FLOW] SENDING COMMAND TO GAME: '{game_command}'")
            game_response = await self._send_command_to_game(game_command, game_id, access_token)
            logger.info(f"[COMMAND FLOW] GAME RESPONSE: '{game_response}'")
            
            # Enhance the response
            logger.info(f"[COMMAND FLOW] ENHANCING RESPONSE FOR: '{game_command}'")
            enhanced_response = await self._enhance_response(game_response, user_input, game_command)
            logger.info(f"[COMMAND FLOW] ENHANCED RESPONSE: '{enhanced_response}'")
            
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
            current_npcs = []  # Added explicit tracking of NPCs
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
                    
                    # Extract NPCs in the current location
                    if "npcs" in current_tile:
                        # Process NPCs, ensuring they are all strings
                        for npc in current_tile["npcs"]:
                            if isinstance(npc, str):
                                current_npcs.append(npc)
                            elif hasattr(npc, 'id'):
                                current_npcs.append(npc.id)
                            elif isinstance(npc, dict) and 'id' in npc:
                                current_npcs.append(npc['id'])
                            else:
                                # Log the unexpected NPC type
                                logger.warning(f"Unexpected NPC type: {type(npc)}, {npc}")
                                continue
                        logger.info(f"[INTERPRET] NPCs in current tile: {current_npcs}")
                    
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
                if "player" in game_state and "inventory" in game_state["player"]:
                    player_inventory = game_state["player"]["inventory"]
                elif "inventory" in game_state:
                    player_inventory = game_state["inventory"]
            
            # Check for NPC interaction intent
            lower_input = user_input.lower()
            logger.info(f"[INTERPRET] Processing user input: '{lower_input}'")
            
            # Special handling for NPC interactions
            # Check if the user is trying to talk to an NPC
            talk_keywords = ["talk", "speak", "chat", "converse", "ask", "talk to", "speak to", "talk with", "speak with"]
            is_talk_intent = False
            for keyword in talk_keywords:
                if keyword in lower_input:
                    is_talk_intent = True
                    logger.info(f"[INTERPRET] Detected talk keyword: '{keyword}' in input")
                    break
                    
            if is_talk_intent and current_npcs:
                logger.info(f"[INTERPRET] Detected potential talk intent: '{lower_input}', NPCs: {current_npcs}")
                # Try to extract the NPC name from the user input
                potential_npc = None
                
                # First check for exact NPC matches
                for npc in current_npcs:
                    if npc.lower() in lower_input:
                        potential_npc = npc
                        logger.info(f"[INTERPRET] Found exact NPC match: '{npc}'")
                        break
                
                # If no exact match, try to find partial matches or references
                if not potential_npc:
                    logger.info(f"[INTERPRET] No exact NPC match found, trying partial matches")
                    # Check for common terms like "scout", "guard", etc.
                    for npc in current_npcs:
                        # Extract key terms from NPC id
                        npc_terms = npc.lower().split('_')
                        logger.info(f"[INTERPRET] Checking NPC terms for '{npc}': {npc_terms}")
                        for term in npc_terms:
                            if term in lower_input and len(term) > 3:  # Only match significant terms
                                potential_npc = npc
                                logger.info(f"[INTERPRET] Found partial match: term '{term}' in NPC '{npc}'")
                                break
                        if potential_npc:
                            break
                
                # If we found a potential NPC, return the talk command
                if potential_npc:
                    logger.info(f"[INTERPRET] Detected talk intent with NPC: {potential_npc}")
                    return f"talk {potential_npc}"
                else:
                    # If we still couldn't find an NPC but the intent is to talk,
                    # and there's only one NPC present, assume that's the target
                    if len(current_npcs) == 1:
                        npc = current_npcs[0]
                        logger.info(f"[INTERPRET] Assuming talk intent with the only NPC present: {npc}")
                        return f"talk {npc}"
                    else:
                        logger.info(f"[INTERPRET] Could not identify an NPC target for talk command")
            
            # For simple, unambiguous commands, use pattern matching for efficiency
            
            # Check for direct direction commands
            directions = {"north": ["north", "n"], "south": ["south", "s"], 
                         "east": ["east", "e"], "west": ["west", "w"]}
            
            for direction, patterns in directions.items():
                for pattern in patterns:
                    if pattern == lower_input or f"go {pattern}" in lower_input or f"move {pattern}" in lower_input:
                        logger.info(f"[INTERPRET] Detected direction command: '{direction}'")
                        return direction
            
            # Check for inventory command
            if lower_input in ["inventory", "i", "check inventory", "check my inventory", "what am i carrying"]:
                logger.info(f"[INTERPRET] Detected inventory command")
                return "inventory"
            
            # For more complex commands, use the LLM with comprehensive context
            logger.info(f"[INTERPRET] Using LLM for complex command interpretation")
            context = f"""
            User input: {user_input}
            
            Current game state:
            """
            
            if tile_description:
                context += f"Current location description: {tile_description}\n"
            
            if terrain_type:
                context += f"Terrain type: {terrain_type}\n"
            
            if current_items:
                # Ensure all items are strings
                item_names = []
                for item in current_items:
                    if isinstance(item, str):
                        item_names.append(item)
                    elif hasattr(item, 'name'):
                        item_names.append(item.name)
                    elif isinstance(item, dict) and 'name' in item:
                        item_names.append(item['name'])
                    else:
                        # Skip any items that can't be converted to strings
                        continue
                
                if item_names:
                    context += f"Items visible: {', '.join(item_names)}\n"
            
            if current_enemies:
                # Ensure all enemies are strings
                enemy_names = []
                for enemy in current_enemies:
                    if isinstance(enemy, str):
                        enemy_names.append(enemy)
                    elif hasattr(enemy, 'name'):
                        enemy_names.append(enemy.name)
                    elif isinstance(enemy, dict) and 'name' in enemy:
                        enemy_names.append(enemy['name'])
                    else:
                        # Skip any enemies that can't be converted to strings
                        continue
                
                if enemy_names:
                    context += f"Enemies present: {', '.join(enemy_names)}\n"
            
            if current_npcs:
                context += f"NPCs present: {', '.join(current_npcs)}\n"
            
            if current_exits:
                context += f"Available exits: {', '.join(current_exits)}\n"
            
            if weather:
                context += f"Current weather: {weather}\n"
            
            if time_of_day:
                context += f"Time of day: {time_of_day}\n"
            
            if player_inventory:
                # Convert Item objects to strings if needed
                inventory_items = []
                for item in player_inventory:
                    if isinstance(item, str):
                        inventory_items.append(item)
                    elif hasattr(item, 'name'):
                        inventory_items.append(item.name)
                    elif isinstance(item, dict) and 'name' in item:
                        inventory_items.append(item['name'])
                    else:
                        # Log the unexpected item type
                        logger.warning(f"Unexpected item type in inventory: {type(item)}, {item}")
                        continue
                
                context += f"Items in inventory: {', '.join(inventory_items)}\n"
            else:
                context += "Inventory is empty.\n"
            
            # Use OpenAI for command interpretation with comprehensive context
            logger.info(f"[INTERPRET] Sending command to LLM for interpretation")
            response = await self.openai_client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": self.command_system_prompt},
                    {"role": "user", "content": context + f"\nWhat is the appropriate game command for: '{user_input}'?"}
                ],
                temperature=0.2,
                max_tokens=50
            )
            
            interpreted_command = response.choices[0].message.content.strip()
            logger.info(f"[INTERPRET] LLM interpreted command: '{interpreted_command}'")
            return interpreted_command
            
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
            logger.info(f"[SEND_COMMAND] Processing game command: '{command}'")
            # Handle attack commands with special care
            if command.startswith("attack "):
                target = command[7:].strip()  # Extract the target name
                logger.info(f"[SEND_COMMAND] Handling attack command for target: '{target}'")
                
                # First, check if the target is actually present in the current location
                look_response = await self._execute_direct_command("look", game_id, access_token)
                
                # Check if the target is mentioned in the look response
                if "Enemies present:" in look_response and target in look_response:
                    logger.info(f"[SEND_COMMAND] Target {target} found in the current location")
                    
                    # Try the attack command
                    attack_response = await self._execute_direct_command(command, game_id, access_token)
                    
                    # If we got a meaningful response, return it
                    if attack_response and len(attack_response.strip()) > 3:
                        logger.info(f"[SEND_COMMAND] Attack command successful")
                        return attack_response
                    
                    # If the response was empty or too short, provide a more helpful message
                    logger.info(f"[SEND_COMMAND] Attack command yielded empty response, providing fallback")
                    return f"You attempt to attack the {target}, but something seems off. The {target} might be too strong or not vulnerable to direct attacks right now."
                else:
                    logger.info(f"[SEND_COMMAND] Target {target} not found in the current location")
                    return f"You don't see any {target} here to attack."
            
            # Handle talk commands properly
            if command.startswith("talk "):
                npc_id = command[5:].strip()  # Extract the NPC ID
                logger.info(f"[SEND_COMMAND] Handling talk command for NPC: '{npc_id}'")
                
                # First, check if the NPC is actually present in the current location
                look_response = await self._execute_direct_command("look", game_id, access_token)
                
                # Check if the NPC is mentioned in the look response
                if "NPCs present:" in look_response and npc_id in look_response:
                    logger.info(f"[SEND_COMMAND] NPC {npc_id} found in the current location")
                    
                    # Execute the talk command
                    talk_response = await self._execute_direct_command(command, game_id, access_token)
                    
                    # If we got a meaningful response, return it
                    if talk_response and len(talk_response.strip()) > 3:
                        logger.info(f"[SEND_COMMAND] Talk command successful")
                        return talk_response
                    
                    # If the response was empty or too short, provide a more helpful message
                    logger.info(f"[SEND_COMMAND] Talk command yielded empty response, providing fallback")
                    return f"You approach the {npc_id}, but they don't seem responsive at the moment."
                else:
                    logger.info(f"[SEND_COMMAND] NPC {npc_id} not found in the current location")
                    return f"You don't see {npc_id} here to talk to."
            
            # Handle environmental roleplay items that aren't explicitly in the game state
            # but would naturally be present in the environment
            if command.startswith("take "):
                item = command[5:].strip()  # Extract the item name
                logger.info(f"[SEND_COMMAND] Handling take command for item: '{item}'")
                
                # First check if this is a regular item in the game
                # If it is, use the normal game command to take it
                regular_item_response = await self._execute_direct_command(command, game_id, access_token)
                if "You take" in regular_item_response or "added to your inventory" in regular_item_response:
                    logger.info(f"[SEND_COMMAND] Successfully took regular item: {item}")
                    return regular_item_response
                
                # Log that we're handling as a potential environmental item
                logger.info(f"[SEND_COMMAND] Regular take failed, handling as potential environmental item: {item}")
                
                # If we couldn't take it as a regular item, check if it's an environmental item
                # Get the current game state to check the environment
                game_data = await self.get_game_state(game_id, access_token)
                
                # Log the game state for debugging
                logger.info(f"[SEND_COMMAND] Processing potential environmental item: {item}")
                logger.info(f"[SEND_COMMAND] Game state keys: {list(game_data.keys())}")
                
                # First, try to get the current tile description from the look command
                # This is the most reliable way to get the current environment
                look_response = await self._execute_direct_command("look", game_id, access_token)
                
                # If we have a look response, check if this is a forest environment
                if look_response:
                    logger.info(f"[SEND_COMMAND] Got look response for environment check")
                    
                    # Check for forest/woods keywords in the look response
                    forest_keywords = ["forest", "woods", "trees", "ancient woods", "branches", "canopy"]
                    is_forest = any(keyword in look_response.lower() for keyword in forest_keywords)
                    
                    # Check if this is a forest item
                    forest_items = ["leaves", "twigs", "bark", "berries", "moss", "flowers", "herbs"]
                    
                    # If this is a forest environment and a forest item, handle it directly
                    if is_forest and item in forest_items:
                        logger.info(f"[SEND_COMMAND] Detected forest environment and forest item: {item}")
                        
                        # Try to add the item to inventory using our direct method
                        return await self._add_environmental_item_to_inventory(item, game_id, access_token)
                
                # If we didn't handle it directly, try the normal approach
                # Extract terrain type and description from game state
                terrain_type = ""
                description = look_response if look_response else ""
                
                # If we have a description from look, check for forest/woods keywords
                if description:
                    if any(keyword in description.lower() for keyword in ["forest", "woods", "trees", "ancient woods"]):
                        terrain_type = "forest"
                        logger.info(f"[SEND_COMMAND] Detected forest terrain from description")
                
                # If we couldn't get a description from look, try the game state
                if not description or not terrain_type:
                    # Check different possible structures in the game state
                    if "current_tile" in game_data:
                        current_tile = game_data["current_tile"]
                        if "terrain_type" in current_tile:
                            terrain_type = current_tile["terrain_type"]
                        if "description" in current_tile:
                            description = current_tile["description"]
                    elif "game_state" in game_data:
                        game_state = game_data["game_state"]
                        if "current_tile" in game_state:
                            current_tile = game_state["current_tile"]
                            if "terrain_type" in current_tile:
                                terrain_type = current_tile["terrain_type"]
                            if "description" in current_tile:
                                description = current_tile["description"]
                
                # Log the extracted information for debugging
                logger.info(f"[SEND_COMMAND] Extracted terrain_type: {terrain_type}, description: {description}")
                
                # Check if this is an environmental item
                if is_environmental_item(item, terrain_type, description):
                    logger.info(f"[SEND_COMMAND] Handling environmental item: {item}")
                    
                    # Use our helper function to update the inventory
                    async with httpx.AsyncClient() as client:
                        result = await update_inventory_with_item(
                            client, game_id, access_token, item, self.api_base_url
                        )
                        
                        return result["message"]
                
                # If we got here, it's not a valid item to take
                logger.info(f"[SEND_COMMAND] Item {item} not found, returning not found message")
                return f"There is no {item} here."
            
            # For non-environmental items or other commands, proceed with normal API call
            logger.info(f"[SEND_COMMAND] Executing standard command: '{command}'")
            return await self._execute_direct_command(command, game_id, access_token)
                    
        except Exception as e:
            logger.error(f"[SEND_COMMAND] Error sending command to game: {e}")
            return f"Error executing command: {str(e)}"
    
    async def _execute_direct_command(self, command: str, game_id: str, access_token: str) -> str:
        """
        Execute a command directly through the game API.
        
        Args:
            command: The game command to send
            game_id: The game instance ID
            access_token: The user's access token
            
        Returns:
            Game response string
        """
        try:
            logger.info(f"[EXECUTE] Executing direct command: '{command}'")
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
                
                if response.status_code == 200:
                    response_text = response.json()["response"]
                    logger.info(f"[EXECUTE] Direct command response: '{response_text}'")
                    return response_text
                else:
                    logger.error(f"[EXECUTE] Error from game API: {response.status_code} - {response.text}")
                    return f"Error executing command: {response.text}"
        except Exception as e:
            logger.error(f"[EXECUTE] Error executing direct command: {e}")
            return f"Error executing command: {str(e)}"
    
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
            logger.info(f"[ENHANCE] Processing response for command: '{game_command}'")
            logger.info(f"[ENHANCE] Original game response: '{game_response}'")
            
            # If the game response is empty or very short, return a more specific default message
            if not game_response or len(game_response.strip()) < 3:
                logger.info(f"[ENHANCE] Empty or very short game response detected")
                if "look" in game_command or "examine" in game_command:
                    logger.info(f"[ENHANCE] Returning default response for look command")
                    return "You see nothing special about that."
                elif "attack" in game_command:
                    logger.info(f"[ENHANCE] Returning default response for attack command")
                    return "You attack, but nothing happens. There may not be a valid target."
                elif "take" in game_command:
                    logger.info(f"[ENHANCE] Returning default response for take command")
                    return "You try to take something, but there's nothing there to grab."
                else:
                    logger.info(f"[ENHANCE] Returning generic default response")
                    return "Nothing happens. Perhaps try a different approach."
            
            # Determine the command type for better response formatting
            command_type = "location_description"  # Default
            
            # For movement commands or general look
            if game_command.startswith("move") or game_command == "look":
                command_type = "location_description"
            # For examining specific objects (not general look around)
            elif ("examine" in game_command or "look at" in game_command or "inspect" in game_command) and game_command != "look":
                command_type = "object_interaction"
            # For NPC interactions
            elif "talk" in game_command or "chat" in game_command or "speak" in game_command:
                command_type = "npc_interaction"
            # For inventory or item interactions
            elif "take" in game_command or "inventory" in game_command:
                command_type = "item_interaction"
            
            # Prepare context for the LLM
            context = f"""
            Response Type: {command_type}
            User input: {user_input}
            Game command: {game_command}
            Original game response: {game_response}
            """
            
            logger.info(f"[ENHANCE] Sending response to LLM for enhancement with type: {command_type}")
            # Use OpenAI for response enhancement
            response = await self.openai_client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": self.response_system_prompt},
                    {"role": "user", "content": context}
                ],
                temperature=0.5,
                max_tokens=200
            )
            
            enhanced_text = response.choices[0].message.content.strip()
            logger.info(f"[ENHANCE] LLM enhanced response: '{enhanced_text}'")
            return enhanced_text
            
        except Exception as e:
            logger.error(f"[ENHANCE] Error enhancing response: {e}")
            # Fall back to the original response
            return game_response
    
    async def get_game_state(self, game_id: str, access_token: str) -> Dict[str, Any]:
        """
        Get the current game state.
        
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
                
                if response.status_code == 200:
                    return response.json()
                else:
                    logger.error(f"Error getting game state: {response.status_code} - {response.text}")
                    return {}
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
    
    async def _add_environmental_item_to_inventory(self, item_name: str, game_id: str, access_token: str) -> str:
        """
        Add an environmental item directly to the player's inventory.
        This is a fallback method when the normal update_inventory_with_item fails.
        
        Args:
            item_name: The name of the item to add
            game_id: The game instance ID
            access_token: The user's access token
            
        Returns:
            Response message
        """
        try:
            # First, check the current inventory
            inventory_response = await self._execute_direct_command("inventory", game_id, access_token)
            logger.info(f"Current inventory: {inventory_response}")
            
            # Check if the player already has this item
            if item_name in inventory_response.lower():
                return f"You already have some {item_name} in your inventory."
            
            # Check if the inventory is full (arbitrary limit)
            # Count the number of items by splitting the inventory response
            if inventory_response.startswith("Inventory:"):
                items = inventory_response[len("Inventory:"):].strip().split(", ")
                if len(items) >= 20 and items[0]:  # Check if there are items and not just an empty string
                    return f"You gather some {item_name} from the surroundings, but your inventory is full."
            
            # Create a custom command to add the item to inventory
            # This is a hack, but it might work if the game supports it
            create_command = f"debug add_item {item_name}"
            create_response = await self._execute_direct_command(create_command, game_id, access_token)
            
            # Check if the command worked
            if "added to inventory" in create_response.lower() or "successfully" in create_response.lower():
                return f"You gather some {item_name} from the surroundings and add them to your inventory."
            
            # If that didn't work, try another approach
            # Try to use the game's internal command to create the item in the current location
            spawn_command = f"debug spawn_item {item_name}"
            spawn_response = await self._execute_direct_command(spawn_command, game_id, access_token)
            
            # Now try to take the item
            take_response = await self._execute_direct_command(f"take {item_name}", game_id, access_token)
            
            if "added to inventory" in take_response.lower() or "you take" in take_response.lower():
                return f"You gather some {item_name} from the surroundings and add them to your inventory."
            
            # If all else fails, return a generic message
            return f"You gather some {item_name} from the surroundings, but can't seem to find a place for them in your inventory."
            
        except Exception as e:
            logger.error(f"Error adding environmental item to inventory: {e}")
            return f"You gather some {item_name} from the surroundings, but something prevents you from keeping them." 