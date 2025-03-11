"""
Test script for the Narrative System in The Last Centaur.

This test verifies that narrative elements progress appropriately:
1. Key story moments are presented
2. Area descriptions are rich and engaging
3. Character interactions convey personality
4. Story progression affects the world state
5. Narrative adapts to player choices
"""

import pytest
import sys
import os

# Add the src directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.engine.core.models import Direction, StoryArea, NarrativeEvent
from src.engine.core.player import Player
from src.engine.core.map_system import MapManager
from src.engine.core.command_parser import CommandParser
from src.engine.core.narrative_manager import NarrativeManager


class TestNarrativeSystem:
    """Test suite for narrative elements and story progression."""
    
    @pytest.fixture
    def game_setup(self):
        """Set up the game systems for testing narrative elements."""
        # Initialize game systems
        map_system = MapManager()
        player = Player(map_system, player_id="test_narrative", player_name="Test Protagonist")
        command_parser = CommandParser(player)
        narrative_manager = NarrativeManager(player)
        
        # Helper function to execute commands
        def execute(command: str) -> str:
            """Execute a command and return the response."""
            response = command_parser.parse_command(command)
            print(f"\n> {command}")
            print(response)
            return response
            
        return map_system, player, command_parser, execute, narrative_manager
    
    def test_area_descriptions(self, game_setup):
        """Test that area descriptions are rich and engaging."""
        map_system, _, _, execute, _ = game_setup
        
        # Check key areas for richness of description
        areas_to_test = [
            (StoryArea.AWAKENING_WOODS, ["ancient", "forest", "mystery"]),
            (StoryArea.SHADOW_DOMAIN, ["dark", "shadows", "foreboding"]),
            (StoryArea.CRYSTAL_POND, ["shimmering", "reflection", "magical"]),
            (StoryArea.ANCIENT_SANCTUARY, ["sacred", "power", "ancient"])
        ]
        
        for area, expected_terms in areas_to_test:
            map_system.set_current_area(area)
            description = execute("look")
            
            # Check that description is sufficiently detailed
            assert len(description.split()) >= 20, f"Description for {area} is too short"
            
            # Check for evocative terms
            for term in expected_terms:
                assert term in description.lower(), f"'{term}' not found in {area} description"
            
            # Check for unique character in each area's description
            assert description != execute("look"), "Area descriptions should have some variability"

    def test_character_interactions(self, game_setup):
        """Test that NPCs have distinct personalities in dialogue."""
        map_system, _, _, execute, _ = game_setup
        
        # Test conversation with the Mystic Guide
        map_system.set_current_area(StoryArea.MYSTIC_MOUNTAINS)
        talk_response = execute("talk to mystic")
        
        # Check personality markers
        assert "wisdom" in talk_response.lower()
        assert len(talk_response) >= 100, "Dialogue is too brief"
        
        # Test getting different responses for different questions
        question1 = execute("ask mystic about crystal")
        question2 = execute("ask mystic about shadow")
        assert question1 != question2, "Different questions should yield different responses"
        
        # Test Warrior NPC
        map_system.set_current_area(StoryArea.WARRIORS_CAMP)
        warrior_talk = execute("talk to warrior")
        assert "honor" in warrior_talk.lower() or "strength" in warrior_talk.lower()
        assert warrior_talk != talk_response, "Different NPCs should have different dialogue styles"

    def test_major_story_beats(self, game_setup):
        """Test that key story events occur in the right sequence."""
        map_system, player, _, execute, narrative_manager = game_setup
        
        # Starting point - narrative should be in initial state
        assert narrative_manager.get_story_phase() == "beginning"
        
        # Trigger first major story beat - discovering the truth about the centaurs
        map_system.set_current_area(StoryArea.FORGOTTEN_TEMPLE)
        reading_response = execute("read ancient tablet")
        assert "centaurs" in reading_response.lower()
        assert "transformation" in reading_response.lower()
        assert narrative_manager.get_story_phase() == "revelation"
        
        # Verify story change affects dialogue
        map_system.set_current_area(StoryArea.MYSTIC_MOUNTAINS)
        mystic_after = execute("talk to mystic")
        assert "now that you know the truth" in mystic_after.lower()

        # Encounter with Shadow Messenger
        map_system.set_current_area(StoryArea.SHADOW_DOMAIN)
        encounter = execute("look")
        assert "dark figure" in encounter.lower()
        confront = execute("approach figure")
        assert "messenger" in confront.lower()
        assert "Shadow Centaur awaits" in confront.lower()
        assert narrative_manager.get_story_phase() == "confrontation"

    def test_narrative_adaptation(self, game_setup):
        """Test that narrative adapts to player choices."""
        map_system, player, _, execute, narrative_manager = game_setup
        
        # Setup - player makes a key choice
        map_system.set_current_area(StoryArea.TRIALS_PATH)
        
        # Choose warrior path
        warrior_choice = execute("follow warrior teachings")
        assert "path of strength" in warrior_choice.lower()
        assert narrative_manager.get_player_path() == "warrior"
        
        # Verify world changes based on choice
        map_system.set_current_area(StoryArea.TRAINING_GROUNDS)
        training_response = execute("look")
        assert "recognized as a warrior" in training_response.lower()
        
        # Reset and try different path
        narrative_manager.reset_player_path()
        map_system.set_current_area(StoryArea.TRIALS_PATH)
        
        # Choose mystic path
        mystic_choice = execute("follow mystic teachings")
        assert "path of wisdom" in mystic_choice.lower()
        assert narrative_manager.get_player_path() == "mystic"
        
        # Verify different outcome
        map_system.set_current_area(StoryArea.MYSTIC_MOUNTAINS)
        mystic_response = execute("look")
        assert "welcomed as an initiate" in mystic_response.lower()

    def test_environmental_storytelling(self, game_setup):
        """Test that the environment tells parts of the story."""
        map_system, player, _, execute, _ = game_setup
        
        # Check that examining objects reveals story elements
        map_system.set_current_area(StoryArea.CRYSTAL_POND)
        examine_response = execute("examine ancient carving")
        assert "history" in examine_response.lower()
        assert "centaurs" in examine_response.lower()
        
        # Another area should have connected but different story elements
        map_system.set_current_area(StoryArea.FORGOTTEN_TEMPLE)
        temple_examine = execute("examine wall mural")
        assert "shadow" in temple_examine.lower()
        assert temple_examine != examine_response
        
        # Items should also contain story elements
        player.add_item_to_inventory("ancient_journal")
        journal_response = execute("read ancient_journal")
        assert "transformation" in journal_response.lower()
        assert "last of their kind" in journal_response.lower()

    def test_final_confrontation_narrative(self, game_setup):
        """Test the narrative elements of the final confrontation."""
        map_system, player, _, execute, narrative_manager = game_setup
        
        # Set up for final confrontation
        map_system.set_current_area(StoryArea.ANCIENT_SANCTUARY)
        narrative_manager.set_story_phase("final_confrontation")
        
        # Prepare player for final battle
        player.add_item_to_inventory("shadow_key")
        player.add_item_to_inventory("shadow_essence")
        player.add_item_to_inventory("crown_of_dominion")
        
        # Final approach
        approach = execute("approach altar")
        assert "shadow begins to coalesce" in approach.lower()
        assert "dark mirror of yourself" in approach.lower()
        
        # Dialogue with Shadow Centaur
        talk = execute("speak to shadow centaur")
        assert "lost heritage" in talk.lower()
        assert "reclaim" in talk.lower()
        
        # Final choice setup
        choice_setup = execute("ready weapon")
        assert "destiny" in choice_setup.lower()
        assert "choice" in choice_setup.lower() 