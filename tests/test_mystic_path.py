"""
Test script for the Mystic Path in The Last Centaur.

This test follows the path of magical knowledge:
Start → Trials Path → Mystic Mountains → Crystal Caves → Shadow Domain
"""

import pytest
from src.engine.core.models import Direction, StoryArea
from src.engine.core.player import Player
from src.engine.core.map_system import MapSystem
from src.engine.core.command_parser import CommandParser

def test_mystic_path():
    """Test the complete Mystic Path through the game."""
    
    # Initialize game systems
    map_system = MapSystem()
    player = Player(map_system, player_id="test_mystic", player_name="Test Mystic")
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
    
    # Try going west (should fail - blocked path)
    result = execute("w")
    assert "blocked" in result.lower() or "cannot" in result.lower()
    
    # Defeat the wolf pack
    execute("defeat Wolf Pack")
    
    # Go west to meet the Hermit Druid
    result = execute("w")
    assert "Moved west" in result
    
    # Talk to the Hermit Druid and get the ancient_scroll
    result = execute("talk hermit_druid")
    assert "Ah, another proud centaur" in result
    execute("take ancient_scroll")
    
    # Look for the crystal_focus
    result = execute("look")
    if "crystal_focus" in result:
        execute("take crystal_focus")
    
    # Go east back to starting position
    execute("e")
    
    # Go north to Trials Path
    result = execute("n")
    assert "Moved north" in result
    result = execute("look")
    assert "crossroads where the three paths diverge" in result
    
    # Go west to Mystic Mountains
    result = execute("w")
    result = execute("look")
    assert "Jagged peaks pulse with ancient power" in result
    
    # Go to Crystal Outpost
    result = execute("w")
    result = execute("look")
    assert "former research post" in result
    
    # Defeat the Crystal Golem
    result = execute("look")
    if "Crystal Golem" in result:
        execute("defeat Crystal Golem")
    
    # Get the crystal_key
    result = execute("look")
    if "crystal_key" in result:
        execute("take crystal_key")
    
    # Go back to Mystic Mountains
    execute("e")
    
    # Head to Crystal Caves
    result = execute("n")
    result = execute("look")
    assert "vast network of crystal-lined caves" in result
    
    # Look for mystic_crystal
    if "mystic_crystal" in result:
        execute("take mystic_crystal")
    
    # Look for resonance_key
    if "resonance_key" in result:
        execute("take resonance_key")
    
    # Defeat Crystal Guardian
    result = execute("look")
    if "crystal_guardian" in result:
        execute("defeat crystal_guardian")
    
    # Get guardian_essence
    result = execute("look")
    if "guardian_essence" in result:
        execute("take guardian_essence")
    
    # Head to Shadow Domain
    result = execute("n")
    assert "Moved north" in result
    
    result = execute("look")
    assert "corrupted throne" in result
    
    # Face and defeat the Second Centaur
    result = execute("look")
    if "Second Centaur" in result:
        result = execute("defeat Second Centaur")
        assert "crown_of_dominion" in result
    
    # Verify inventory has key items
    result = execute("inventory")
    assert "ancient_scroll" in result
    assert "crystal_focus" in result
    assert "crystal_key" in result
    assert "mystic_crystal" in result
    assert "resonance_key" in result
    assert "guardian_essence" in result
    
    # Verify we're in the final area
    assert player.state.current_area == StoryArea.SHADOW_DOMAIN
    
    print("\nMystic Path Test Completed Successfully!")

if __name__ == "__main__":
    test_mystic_path()