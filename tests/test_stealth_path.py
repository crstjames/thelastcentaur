"""
Test script for the Stealth Path in The Last Centaur.

This test follows the path of cunning and deception:
Start → Trials Path → Twilight Glade → Forgotten Grove → Shadow Domain

The stealth path is the most intricate, requiring careful timing and
discovery of hidden paths and items.
"""

import pytest
from src.engine.core.models import Direction, StoryArea
from src.engine.core.player import Player
from src.engine.core.map_system import MapSystem
from src.engine.core.command_parser import CommandParser

def test_stealth_path():
    """Test the complete Stealth Path through the game."""
    
    # Initialize game systems
    map_system = MapSystem()
    player = Player(map_system, player_id="test_stealth", player_name="Test Stealth")
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
    
    # Must defeat the wolf pack to proceed
    execute("defeat Wolf Pack")
    
    # First, we need to find the Shadow Scout
    # They only appear after examining the surroundings carefully
    result = execute("look")
    result = execute("look north")
    result = execute("look east")
    result = execute("look west")
    
    # Move north to Trials Path
    result = execute("n")
    assert "Moved north" in result
    result = execute("look")
    assert "crossroads where the three paths diverge" in result
    
    # The Shadow Scout is here, but only reveals themselves after careful observation
    result = execute("look")
    result = execute("look north")
    result = execute("look east")
    result = execute("look west")
    
    # Now we can talk to them
    result = execute("talk shadow_scout")
    assert "Not all victories require bloodshed" in result
    
    # Get the shadow_key
    result = execute("look")
    if "shadow_key" in result:
        execute("take shadow_key")
    
    # The path to Twilight Glade is hidden
    # Must look in specific directions to reveal it
    result = execute("look north")
    result = execute("look")
    
    # Now we can move to Twilight Glade
    result = execute("n")
    result = execute("look")
    assert "small clearing where twilight seems to linger" in result
    
    # Defeat the shadow hound
    result = execute("look")
    if "Shadow Hound" in result:
        execute("defeat Shadow Hound")
    
    # Get the shadow essence fragment
    result = execute("look")
    if "shadow_essence_fragment" in result:
        execute("take shadow_essence_fragment")
    
    # The path to Forgotten Grove requires specific timing
    # Must look around in a specific sequence
    result = execute("look")
    result = execute("look north")
    result = execute("look east")
    result = execute("look west")
    result = execute("look north")
    
    # Now we can enter Forgotten Grove
    result = execute("n")
    result = execute("look")
    assert "mysterious grove where shadows move with purpose" in result
    
    # Defeat the shadow stalker
    result = execute("look")
    if "Shadow Stalker" in result:
        execute("defeat Shadow Stalker")
    
    # Get the stealth_cloak
    result = execute("look")
    if "stealth_cloak" in result:
        execute("take stealth_cloak")
    
    # Must find and defeat the Phantom Assassin
    # They only appear after specific sequence
    result = execute("look")
    result = execute("look north")
    result = execute("look east")
    result = execute("look west")
    result = execute("look")
    
    # Now the Phantom Assassin appears
    if "Phantom Assassin" in result:
        execute("defeat Phantom Assassin")
    
    # Get the phantom_dagger and shadow_essence
    result = execute("look")
    if "phantom_dagger" in result:
        execute("take phantom_dagger")
    if "shadow_essence" in result:
        execute("take shadow_essence")
    
    # With both shadow essences combined, we can slip through reality
    # The shadow_essence_fragment from Twilight Glade combines with the shadow_essence
    # to create a powerful stealth effect
    
    # Enter the Shadow Domain through the hidden path
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
    assert "shadow_key" in result
    assert "stealth_cloak" in result
    assert "phantom_dagger" in result
    assert "shadow_essence" in result
    assert "shadow_essence_fragment" in result
    
    # Verify we're in the final area
    assert player.state.current_area == StoryArea.SHADOW_DOMAIN
    
    print("\nStealth Path Test Completed Successfully!")

if __name__ == "__main__":
    test_stealth_path() 