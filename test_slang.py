#!/usr/bin/env python3
"""
Test script for The Last Centaur LLM interface with slang expressions.

This script tests how well the LLM interface can interpret various slang expressions
and convert them to valid game commands.
"""

import os
import asyncio
from dotenv import load_dotenv
from termcolor import colored
from src.game.llm_interface import LLMInterface

# Load environment variables
load_dotenv()

# Test slang expressions and their expected interpretations
SLANG_TESTS = [
    # Movement slang
    "Let's bounce to the north",
    "Imma head north",
    "Yo, let's roll outta here to the east",
    "Bounce to the west side",
    "Scoot over south",
    
    # Look/examine slang
    "Peep that chest over there",
    "Yo, check out that weird tree",
    "What's the 411 on this place?",
    "Scope the surroundings",
    "Gimme the deets on this room",
    
    # Inventory slang
    "What's in my stash?",
    "Lemme see my gear",
    "What am I packin'?",
    "Show me the goods I'm carrying",
    "What's in my pockets, precious?",
    
    # Take/get slang
    "Yoink that sword",
    "Snag that potion",
    "Gimme that gold",
    "Five-finger discount on that necklace",
    "Swipe the map",
    
    # Combat slang
    "Let's throw hands with that wolf",
    "Square up against the goblin",
    "Catch these hooves, troll!",
    "Mess up that orc",
    "Throw down with the bandit",
    
    # Talk slang
    "Holla at that merchant",
    "Spit some game to the innkeeper",
    "Drop a line to that guard",
    "Shoot the breeze with the old man",
    "Rap with the wizard",
    
    # Drop item slang
    "Drop this useless sword",
    "Toss away the empty bottle",
    "Ditch the broken shield",
    "I don't need this map anymore",
    "Get rid of these old boots"
]

async def test_slang_interpretation():
    """Test the LLM interface's ability to interpret slang expressions."""
    print(colored("=== Testing LLM Interface with Slang Expressions ===", "magenta", attrs=["bold"]))
    print(colored("This test will show how the LLM interprets various slang expressions.", "magenta"))
    print()
    
    # Initialize the LLM interface
    llm_interface = LLMInterface(api_base_url="http://localhost:8003/api/v1")
    
    # Test each slang expression
    for i, slang in enumerate(SLANG_TESTS, 1):
        print(colored(f"Test {i}/{len(SLANG_TESTS)}: ", "yellow"), end="")
        print(colored(f'"{slang}"', "cyan"))
        
        try:
            # Interpret the slang expression
            command = await llm_interface._interpret_command(slang)
            print(colored(f"Interpreted as: ", "green"), end="")
            print(colored(f'"{command}"', "white"))
            print()
            
            # Add a small delay to avoid rate limiting
            await asyncio.sleep(0.5)
            
        except Exception as e:
            print(colored(f"Error: {str(e)}", "red"))
            print()
    
    print(colored("=== Test Complete ===", "magenta"))

if __name__ == "__main__":
    asyncio.run(test_slang_interpretation()) 