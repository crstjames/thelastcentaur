"""
Test script for the Warrior Path in The Last Centaur.

This test follows the path of martial prowess:
Start → Trials Path → Ancient Ruins → Enchanted Valley → Shadow Domain
"""

import pytest
import sys
import os

# Add the src directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.engine.core.models import Direction, StoryArea
from src.engine.core.player import Player
from src.engine.core.map_system import MapSystem
from src.engine.core.command_parser import CommandParser

def test_warrior_path():
    """Test the complete Warrior Path through the game."""
    
    # Initialize game systems
    map_system = MapSystem()
    player = Player(map_system, player_id="test_warrior", player_name="Test Warrior")
    command_parser = CommandParser(player)
    
    # Helper function to execute commands and print results
    def execute(command: str) -> str:
        cmd = command_parser.parse_command(command)
        assert cmd is not None, f"Command '{command}' could not be parsed"
        result = command_parser.execute_command(cmd)
        print(f"\n> {command}")
        print(result)
        return result
    
    # Starting in Awakening Woods
    assert player.state.current_area == StoryArea.AWAKENING_WOODS
    
    # Look around starting area
    result = execute("look")
    assert "Ancient woods where you first awakened" in result
    assert "Wolf Pack" in result
    
    # Try going east (should fail - blocked path)
    result = execute("e")
    assert "Fallen Warrior" in result and "warrior_map" in result
    
    # Defeat the wolf pack
    execute("defeat Wolf Pack")
    
    # Go east to meet the Fallen Warrior
    result = execute("e")
    assert "Moved east" in result
    
    # Talk to the Fallen Warrior and get the warrior_map
    result = execute("talk fallen_warrior")
    assert "Strength alone won't save you" in result
    execute("take warrior_map")
    
    # Go west back to starting position
    execute("w")
    
    # Go north to Trials Path
    result = execute("n")
    assert "Moved north" in result
    result = execute("look")
    assert "crossroads where the three paths diverge" in result
    
    # Try going to Ancient Ruins
    result = execute("e")
    result = execute("look")
    assert "Crumbling ruins" in result
    
    # Find and take the ancient sword
    result = execute("look")
    if "ancient_sword" in result:
        execute("take ancient_sword")
    
    # Go east to Warrior's Armory
    result = execute("e")
    result = execute("look")
    assert "ancient armory" in result
    
    # Get the war_horn
    result = execute("look")
    if "war_horn" in result:
        execute("take war_horn")
    
    # Go west back to Ancient Ruins
    execute("w")
    
    # Defeat the Stone Guardian
    result = execute("look")
    if "Stone Guardian" in result:
        execute("defeat Stone Guardian")
    
    # Head to Enchanted Valley
    result = execute("n")
    result = execute("look")
    assert "valley of ancient battlefields" in result
    
    # Clear any enemies
    result = execute("look")
    if "Enemies present" in result:
        for enemy in result.split("Enemies present: ")[1].split("\n")[0].split(", "):
            execute(f"defeat {enemy}")
    
    # Face and defeat the Shadow Guardian
    result = execute("look")
    if "Shadow Guardian" in result:
        result = execute("defeat Shadow Guardian")
        assert "guardian_essence" in result
    
    # Take the guardian_essence
    result = execute("look")
    if "guardian_essence" in result:
        execute("take guardian_essence")
    
    # Final path to Shadow Domain
    result = execute("n")
    result = execute("look")
    assert "corrupted throne" in result
    
    # Face the Second Centaur
    result = execute("look")
    if "Second Centaur" in result:
        result = execute("defeat Second Centaur")
        assert "crown_of_dominion" in result
    
    # Verify inventory has key items
    result = execute("inventory")
    assert "warrior_map" in result
    assert "ancient_sword" in result
    assert "war_horn" in result
    assert "guardian_essence" in result
    
    # Verify we're in the final area
    result = execute("look")
    assert "corrupted throne" in result
    
    print("\nWarrior Path Test Completed Successfully!")

if __name__ == "__main__":
    test_warrior_path() 