"""
Test script for a Complete Player Journey in The Last Centaur.

This test verifies the complete gameplay experience:
1. Starting as a novice in the Awakening Woods
2. Exploring the map and discovering key locations
3. Gathering essential items and solving puzzles
4. Engaging in combat with progressively tougher enemies
5. Reaching and defeating the Shadow Centaur in the final battle
6. Experiencing key narrative moments and character growth

This is an end-to-end test that simulates a full playthrough.
"""

import pytest
import sys
import os
from typing import Dict, List, Set, Tuple

# Add the src directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.engine.core.models import Direction, StoryArea, ItemType, EnemyType
from src.engine.core.player import Player
from src.engine.core.map_system import MapManager
from src.engine.core.command_parser import CommandParser
from src.engine.core.combat_system import CombatSystem


def test_complete_journey():
    """Test a complete journey through the game, start to finish."""
    
    # Initialize game systems
    map_system = MapManager()
    player = Player(map_system, player_id="test_journey", player_name="Hero")
    command_parser = CommandParser(player)
    combat_system = CombatSystem()
    
    # Helper function to execute commands
    def execute(command: str) -> str:
        """Execute a command and return the response."""
        response = command_parser.parse_command(command)
        print(f"\n> {command}")
        print(response)
        return response
    
    # PHASE 1: BEGINNING - Awakening Woods
    print("\n=== PHASE 1: BEGINNING ===")
    assert map_system.get_current_area() == StoryArea.AWAKENING_WOODS
    
    # First exploration
    initial_look = execute("look")
    assert "forest clearing" in initial_look.lower()
    assert "pouch" in initial_look.lower()
    assert "rusty sword" in initial_look.lower()
    
    # Collect first items
    take_pouch = execute("take pouch")
    assert "You pick up the leather pouch" in take_pouch
    
    take_sword = execute("take rusty sword")
    assert "You pull the rusty sword from the stump" in take_sword
    
    # Check inventory
    inventory = execute("inventory")
    assert "leather pouch" in inventory.lower()
    assert "rusty sword" in inventory.lower()
    
    # Move to Warrior's Camp
    go_east = execute("go east")
    assert "Warriors Camp" in go_east
    
    # PHASE 2: WARRIOR PATH EXPLORATION
    print("\n=== PHASE 2: WARRIOR PATH EXPLORATION ===")
    
    # Talk to the warrior
    talk_warrior = execute("talk to warrior")
    assert "strength" in talk_warrior.lower()
    assert "training" in talk_warrior.lower()
    
    # Begin training
    train = execute("train with warrior")
    assert "basic combat techniques" in train.lower()
    
    # Receive warrior's token
    complete_training = execute("complete training")
    assert "warrior's emblem" in complete_training.lower()
    
    # Check updated inventory
    inventory = execute("inventory")
    assert "warrior's emblem" in inventory.lower()
    
    # First combat encounter
    encounter = execute("go north")
    assert "training dummy" in encounter.lower()
    
    # Fight training dummy
    fight = execute("attack dummy")
    assert "You attack the training dummy" in fight
    assert "You've learned the basics of combat" in fight
    
    # Progress to Honor Shrine
    go_east = execute("go east")
    assert "Honor Shrine" in go_east
    
    # Get honor blade
    examine_shrine = execute("examine shrine")
    assert "ancient blade" in examine_shrine.lower()
    
    take_blade = execute("take honor blade")
    assert "honor blade" in take_blade.lower()
    
    # PHASE 3: FIRST REAL COMBAT
    print("\n=== PHASE 3: FIRST REAL COMBAT ===")
    
    # Return to camp and head to trials
    execute("go west")
    execute("go south")
    go_west = execute("go west")
    assert "Trials Path" in go_west
    
    # Encounter wolf pack
    wolf_encounter = execute("go west")
    assert "wolf pack" in wolf_encounter.lower()
    
    # Begin combat
    combat_start = execute("ready weapon")
    assert "combat" in combat_start.lower()
    
    # Use combat commands
    attack = execute("attack with honor blade")
    assert "strike" in attack.lower()
    
    # Dodge enemy attack
    dodge = execute("dodge")
    assert "evade" in dodge.lower()
    
    # Use special attack
    special = execute("use warrior's fury")
    assert "powerful strike" in special.lower()
    
    # Defeat the wolves
    victory = execute("continue combat")
    assert "defeated" in victory.lower()
    
    # Collect reward
    loot = execute("search wolves")
    assert "wolf fang" in loot.lower()
    
    # PHASE 4: PUZZLE SOLVING
    print("\n=== PHASE 4: PUZZLE SOLVING ===")
    
    # Head to Crystal Pond
    execute("go east")
    execute("go north")
    pond = execute("go east")
    assert "Crystal Pond" in pond
    
    # Observe the area
    look_pond = execute("look")
    assert "shimmering water" in look_pond.lower()
    assert "strange patterns" in look_pond.lower()
    
    # Examine the patterns
    patterns = execute("examine patterns")
    assert "symbols" in patterns.lower()
    
    # Use wolf fang as a tool
    use_fang = execute("use wolf fang on patterns")
    assert "scrape away" in use_fang.lower()
    assert "reveals" in use_fang.lower()
    
    # Solve the pond puzzle
    solve_puzzle = execute("touch crystal in sequence")
    assert "glow with energy" in solve_puzzle.lower()
    assert "crystal fragment" in solve_puzzle.lower()
    
    # Collect the fragment
    take_fragment = execute("take crystal fragment")
    assert "crystal fragment" in take_fragment
    
    # PHASE 5: MYSTIC PATH EXPLORATION
    print("\n=== PHASE 5: MYSTIC PATH EXPLORATION ===")
    
    # Travel to Mystic Mountains
    execute("go west")
    go_west = execute("go west")
    assert "Mystic Mountains" in go_west
    
    # Meet the mystic
    talk_mystic = execute("talk to mystic")
    assert "wisdom" in talk_mystic.lower()
    assert "crystal" in talk_mystic.lower()
    
    # Learn about the crystals
    ask_crystal = execute("ask about crystal fragments")
    assert "three fragments" in ask_crystal.lower()
    assert "meditation circle" in ask_crystal.lower()
    
    # Go to Meditation Circle
    execute("go east")
    execute("go east")
    circle = execute("go east")
    assert "Meditation Circle" in circle
    
    # Perform the ritual
    meditate = execute("meditate")
    assert "clear your mind" in meditate.lower()
    
    light_incense = execute("light incense")
    assert "sweet aroma" in light_incense.lower()
    
    place_fragment = execute("place crystal fragment")
    assert "begins to glow" in place_fragment.lower()
    assert "reveals another fragment" in place_fragment.lower()
    
    # Collect second fragment
    take_fragment = execute("take second crystal fragment")
    assert "second crystal fragment" in take_fragment
    
    # PHASE 6: SHADOW PATH AND TOUGHER COMBAT
    print("\n=== PHASE 6: SHADOW PATH AND TOUGHER COMBAT ===")
    
    # Travel to Shadow Domain
    execute("go west")
    execute("go south")
    execute("go west")
    shadow = execute("go south")
    assert "Shadow Domain" in shadow
    
    # Face shadow creatures
    encounter = execute("look")
    assert "shadow creatures" in encounter.lower()
    
    combat = execute("approach creatures")
    assert "prepare for battle" in combat.lower()
    
    # Tougher combat using advanced techniques
    elemental = execute("use fire element")
    assert "flames" in elemental.lower()
    
    special_combo = execute("combine honor blade with fire")
    assert "blazing strike" in special_combo.lower()
    
    # Defeat creatures
    victory = execute("finish combat")
    assert "dissolve into mist" in victory.lower()
    assert "shadow essence" in victory.lower()
    
    # Collect shadow item
    take_essence = execute("collect shadow essence")
    assert "shadow essence" in take_essence
    
    # Find the final crystal fragment
    search = execute("search area")
    assert "hidden alcove" in search.lower()
    
    alcove = execute("examine alcove")
    assert "final crystal fragment" in alcove.lower()
    
    take_fragment = execute("take final crystal fragment")
    assert "final crystal fragment" in take_fragment
    
    # PHASE 7: CRAFTING THE KEY ITEM
    print("\n=== PHASE 7: CRAFTING THE KEY ITEM ===")
    
    # Return to Mystic Mountains
    execute("go north")
    execute("go west")
    execute("go west")
    
    # Speak to Mystic about fragments
    show_fragments = execute("show crystal fragments to mystic")
    assert "complete set" in show_fragments.lower()
    assert "combine them" in show_fragments.lower()
    
    # Combine fragments
    combine = execute("combine crystal fragments")
    assert "mystic crystal" in combine.lower()
    assert "powerful artifact" in combine.lower()
    
    # Get information about the final challenge
    ask_final = execute("ask about shadow centaur")
    assert "ancient sanctuary" in ask_final.lower()
    assert "prepare yourself" in ask_final.lower()
    
    # PHASE 8: UNLOCKING THE FINAL AREA
    print("\n=== PHASE 8: UNLOCKING THE FINAL AREA ===")
    
    # Travel to Forgotten Temple
    execute("go west")
    execute("go south")
    execute("go west")
    execute("go south")
    temple = execute("go south")
    assert "Forgotten Temple" in temple
    
    # Find the keyhole
    examine_temple = execute("examine temple doors")
    assert "keyhole" in examine_temple.lower()
    assert "crystal shaped" in examine_temple.lower()
    
    # Use the mystic crystal
    use_crystal = execute("use mystic crystal on keyhole")
    assert "doors begin to open" in use_crystal.lower()
    assert "path to the Guardian Overlook" in use_crystal.lower()
    
    # Enter Guardian Overlook
    enter = execute("enter doorway")
    assert "Guardian Overlook" in enter
    
    # Final guardian battle
    guardian = execute("approach guardian")
    assert "ancient guardian" in guardian.lower()
    assert "final test" in guardian.lower()
    
    # Defeat the guardian using all skills
    tough_battle = execute("battle guardian")
    assert "difficult battle" in tough_battle.lower()
    
    use_skills = execute("use all elements")
    assert "combine your skills" in use_skills.lower()
    
    victory = execute("defeat guardian")
    assert "guardian falls" in victory.lower()
    assert "crown of dominion" in victory.lower()
    
    # Collect the final item
    take_crown = execute("take crown of dominion")
    assert "crown of dominion" in take_crown
    
    # Unlock path to Ancient Sanctuary
    unlock_path = execute("use crown on altar")
    assert "gateway opens" in unlock_path.lower()
    assert "Ancient Sanctuary revealed" in unlock_path.lower()
    
    # PHASE 9: FINAL CONFRONTATION
    print("\n=== PHASE 9: FINAL CONFRONTATION ===")
    
    # Enter final area
    sanctuary = execute("enter gateway")
    assert "Ancient Sanctuary" in sanctuary
    assert "shadow centaur" in sanctuary.lower()
    
    # Confront the Shadow Centaur
    confront = execute("approach shadow centaur")
    assert "dark mirror of yourself" in confront.lower()
    assert "reclaim what was lost" in confront.lower()
    
    # Final dialogue
    speak = execute("speak to shadow centaur")
    assert "transformation" in speak.lower()
    assert "final test" in speak.lower()
    
    # Final battle
    final_battle = execute("begin ritual combat")
    assert "shadow centaur charges" in final_battle.lower()
    
    # Use all collected skills and items
    use_crystal = execute("channel mystic crystal")
    assert "energy surges" in use_crystal.lower()
    
    use_blade = execute("strike with honor blade")
    assert "penetrates the darkness" in use_blade.lower()
    
    use_essence = execute("unleash shadow essence")
    assert "control the shadows" in use_essence.lower()
    
    use_crown = execute("wear crown of dominion")
    assert "true potential" in use_crown.lower()
    
    # Final victory
    victory = execute("complete the transformation")
    assert "shadow and light merge" in victory.lower()
    assert "centaur's power" in victory.lower()
    assert "transformation complete" in victory.lower()
    
    # PHASE 10: EPILOGUE
    print("\n=== PHASE 10: EPILOGUE ===")
    
    # Final scene
    epilogue = execute("look")
    assert "transformed" in epilogue.lower()
    assert "centaur" in epilogue.lower()
    assert "heritage reclaimed" in epilogue.lower()
    
    # Game completion
    complete = execute("reflect on journey")
    assert "completed" in complete.lower()
    assert "last centaur" in complete.lower()
    
    print("\nComplete journey test successful!") 