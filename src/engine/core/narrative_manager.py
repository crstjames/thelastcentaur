"""
Narrative Manager for The Last Centaur game.

This module manages the narrative elements, story progression,
and storytelling aspects of the game experience.
"""

import logging
from typing import List, Dict, Optional, Any, Tuple, Set
from datetime import datetime

from termcolor import colored

from src.engine.core.models import (
    StoryArea, PathType, NarrativeEvent
)

logger = logging.getLogger(__name__)

# Story phases represent the overall narrative arc
STORY_PHASES = [
    "beginning",      # Starting in the Awakening Woods, learning the basics
    "revelation",     # Learning about the Shadow Centaur and your purpose
    "exploration",    # Exploring the world and gathering items
    "preparation",    # Preparing for the final confrontation
    "confrontation",  # The final battle with the Shadow Centaur
    "epilogue"        # After the final battle
]

# Character personalities and dialogue tones
CHARACTER_TRAITS = {
    "elder_sage": {
        "personality": "wise, patient, mysterious",
        "dialogue_style": "speaks in riddles and metaphors, references ancient wisdom",
        "topics": ["history of centaurs", "shadow threat", "balance of nature", "player's destiny"]
    },
    "warrior_mentor": {
        "personality": "gruff, direct, honorable",
        "dialogue_style": "concise instructions, occasional war stories, values action over words",
        "topics": ["combat training", "warrior code", "respecting strength", "battlefield stories"]
    },
    "mystic_guide": {
        "personality": "ethereal, contemplative, knowledgeable",
        "dialogue_style": "poetic, references natural forces, speaks of connections between things",
        "topics": ["magical energies", "crystal rituals", "meditation techniques", "cosmic balance"]
    },
    "shadow_messenger": {
        "personality": "cunning, deceptive, intimidating",
        "dialogue_style": "veiled threats, manipulative suggestions, cold and calculating",
        "topics": ["player's weaknesses", "inevitable defeat", "joining the shadow", "false promises"]
    },
    "forest_guardian": {
        "personality": "protective, ancient, connected to nature",
        "dialogue_style": "speaks slowly, uses natural metaphors, direct when threatened",
        "topics": ["forest protection", "natural balance", "ancient duties", "corruption spreading"]
    },
    "shadow_centaur": {
        "personality": "powerful, arrogant, twisted",
        "dialogue_style": "mocking, threatening, speaks of inevitability of darkness",
        "topics": ["domination plans", "player's insignificance", "past defeats", "dark powers"]
    }
}

# Rich area descriptions with sensory details and atmosphere
AREA_DESCRIPTIONS = {
    "awakening_woods": [
        "Ancient trees tower above, their branches forming a cathedral-like canopy. Dappled sunlight filters through, creating shifting patterns on the forest floor. The air is fresh with the scent of pine and wildflowers.",
        "Moss-covered stones form a natural path through the awakening woods. Birdsong echoes from the branches above, while small creatures rustle in the underbrush. The morning dew catches the light, making the forest glimmer.",
        "The Awakening Woods welcome you with a gentle breeze that carries whispers of ancient secrets. Towering trees stand like silent guardians, their roots twisting into the earth. Patches of wildflowers add splashes of color to the verdant scene."
    ],
    "warriors_camp": [
        "The camp bustles with activity. Training dummies bear the marks of countless strikes, while weapon racks hold an impressive array of blades. The smell of leather, steel, and woodsmoke fills the air.",
        "Warriors of various ages practice combat forms in the central clearing. The sound of steel striking steel rings out rhythmically. Banners depicting heroic centaurs flap in the breeze atop sturdy wooden posts.",
        "Tents of tough canvas form a circle around a central fire pit where veterans share tales of battles past. The ground is packed hard from countless hooves, and training equipment shows signs of dedicated use. A sense of discipline and purpose permeates the area."
    ],
    # Additional areas would be defined similarly
}

class NarrativeManager:
    """Manages narrative and storytelling elements of the game."""
    
    def __init__(self, player):
        """Initialize the narrative manager.
        
        Args:
            player: The player object
        """
        self.player = player
        self.events: List[NarrativeEvent] = []
        self.completed_events: Set[str] = set()
        self.current_story_phase = "beginning"
        self.player_path: Optional[PathType] = None
        self.dialogue_history: Dict[str, List[Tuple[str, str]]] = {}  # character -> [(topic, response)]
        self.area_description_index: Dict[str, int] = {}  # area_id -> last description index
        
        # Initialize narrative events database
        self._initialize_narrative_events()
        
        # Log initialization
        logger.info("Narrative Manager initialized")
        print(colored("Narrative Manager initialized", "green"))
    
    def _initialize_narrative_events(self):
        """Set up the initial narrative events for the story."""
        # Beginning phase events
        self.events.append(NarrativeEvent(
            id="awakening",
            title="Awakening in the Forest",
            description="You awaken in a forest clearing, memories hazy but with a sense of purpose.",
            requirements={},
            consequences={"reveal_area": StoryArea.WARRIORS_CAMP},
            story_phase="beginning"
        ))
        
        self.events.append(NarrativeEvent(
            id="first_mentor_meeting",
            title="Meeting the Elder",
            description="An elderly centaur approaches, offering guidance on your journey.",
            requirements={"areas_visited": [StoryArea.AWAKENING_WOODS]},
            consequences={"dialogue_unlock": "elder_sage"},
            story_phase="beginning"
        ))
        
        # Revelation phase events
        self.events.append(NarrativeEvent(
            id="shadow_revelation",
            title="The Shadow Threat Revealed",
            description="You learn of the Shadow Centaur and the threat to the realm.",
            requirements={"completed_events": ["first_mentor_meeting"]},
            consequences={"story_phase": "revelation"},
            story_phase="revelation"
        ))
        
        # Exploration phase events
        self.events.append(NarrativeEvent(
            id="path_choice",
            title="Choosing Your Path",
            description="You must decide whether to follow the way of the Warrior, Mystic, or Stealth.",
            requirements={"story_phase": "revelation"},
            consequences={},
            story_phase="exploration"
        ))
        
        # Preparation phase events
        self.events.append(NarrativeEvent(
            id="final_preparation",
            title="Preparing for the Final Confrontation",
            description="With the necessary items collected, you prepare to face the Shadow Centaur.",
            requirements={
                "items": ["mystic_crystal", "shadow_key", "crown_of_dominion"],
                "areas_visited": [StoryArea.CRYSTAL_POND, StoryArea.SHADOW_DOMAIN, StoryArea.HONOR_SHRINE]
            },
            consequences={"story_phase": "preparation"},
            story_phase="preparation"
        ))
        
        # Confrontation phase events
        self.events.append(NarrativeEvent(
            id="final_confrontation",
            title="The Final Battle",
            description="You face the Shadow Centaur in a battle for the future of the realm.",
            requirements={"story_phase": "preparation"},
            consequences={"story_phase": "confrontation"},
            story_phase="confrontation"
        ))
        
        # Epilogue phase events
        self.events.append(NarrativeEvent(
            id="victory_aftermath",
            title="After the Shadow Falls",
            description="With the Shadow Centaur defeated, you contemplate your future.",
            requirements={"story_phase": "confrontation"},
            consequences={"story_phase": "epilogue"},
            story_phase="epilogue"
        ))
    
    def check_event_triggers(self) -> List[NarrativeEvent]:
        """Check if any narrative events should be triggered based on current state.
        
        Returns:
            List of triggered narrative events
        """
        triggered_events = []
        
        for event in self.events:
            if event.id in self.completed_events:
                continue
                
            if self._check_requirements(event.requirements):
                triggered_events.append(event)
                self.completed_events.add(event.id)
                self._apply_consequences(event.consequences)
                
                # Log the triggered event
                logger.info(f"Narrative event triggered: {event.title}")
                print(colored(f"Narrative event: {event.title}", "cyan"))
        
        return triggered_events
    
    def _check_requirements(self, requirements: Dict[str, Any]) -> bool:
        """Check if all requirements for an event are met.
        
        Args:
            requirements: Dictionary of requirements
            
        Returns:
            True if all requirements are met, False otherwise
        """
        if not requirements:
            return True
            
        # Check items in inventory
        if "items" in requirements:
            required_items = requirements["items"]
            if not all(item in self.player.inventory for item in required_items):
                return False
        
        # Check areas visited
        if "areas_visited" in requirements:
            required_areas = requirements["areas_visited"]
            visited_areas = self.player.visited_areas
            if not all(area in visited_areas for area in required_areas):
                return False
        
        # Check for completed events
        if "completed_events" in requirements:
            required_events = requirements["completed_events"]
            if not all(event in self.completed_events for event in required_events):
                return False
        
        # Check current story phase
        if "story_phase" in requirements:
            if self.current_story_phase != requirements["story_phase"]:
                return False
        
        # Add other requirement checks as needed
        
        return True
    
    def _apply_consequences(self, consequences: Dict[str, Any]):
        """Apply the consequences of a triggered event.
        
        Args:
            consequences: Dictionary of consequences to apply
        """
        if not consequences:
            return
            
        # Update story phase
        if "story_phase" in consequences:
            self.set_story_phase(consequences["story_phase"])
        
        # Reveal new areas
        if "reveal_area" in consequences:
            area = consequences["reveal_area"]
            # This would integrate with map system to make the area accessible
            logger.info(f"Area revealed: {area}")
            print(colored(f"New area discovered: {area}", "yellow"))
        
        # Unlock dialogue options
        if "dialogue_unlock" in consequences:
            character = consequences["dialogue_unlock"]
            logger.info(f"Dialogue unlocked for character: {character}")
            print(colored(f"You can now speak with: {character}", "yellow"))
        
        # Other consequences can be added as needed
    
    def get_area_description(self, area_id: str) -> str:
        """Get a rich description for an area.
        
        Args:
            area_id: Identifier for the area
            
        Returns:
            Descriptive text for the area
        """
        if area_id not in AREA_DESCRIPTIONS:
            return f"You find yourself in {area_id.replace('_', ' ')}."
            
        descriptions = AREA_DESCRIPTIONS[area_id]
        
        # Rotate through available descriptions for variety
        if area_id not in self.area_description_index:
            self.area_description_index[area_id] = 0
        else:
            self.area_description_index[area_id] = (self.area_description_index[area_id] + 1) % len(descriptions)
            
        return descriptions[self.area_description_index[area_id]]
    
    def get_character_dialogue(self, character_id: str, topic: str) -> str:
        """Get dialogue for a character on a specific topic.
        
        Args:
            character_id: Identifier for the character
            topic: The topic of conversation
            
        Returns:
            The character's response
        """
        if character_id not in CHARACTER_TRAITS:
            return f"{character_id.replace('_', ' ').title()} has nothing to say about that."
            
        character = CHARACTER_TRAITS[character_id]
        
        # Record dialogue history
        if character_id not in self.dialogue_history:
            self.dialogue_history[character_id] = []
        self.dialogue_history[character_id].append((topic, datetime.now().isoformat()))
        
        # Construct response based on character traits and story phase
        if topic.lower() in [t.lower() for t in character["topics"]]:
            personality = character["personality"].split(", ")[0]
            style = character["dialogue_style"].split(", ")[0]
            
            # Simple dialogue model - in a real implementation, this would be more sophisticated
            return f"The {character_id.replace('_', ' ')} {personality}ly speaks about {topic}, {style}."
        else:
            return f"The {character_id.replace('_', ' ')} has little to say about {topic}."
    
    def set_story_phase(self, phase: str):
        """Set the current story phase.
        
        Args:
            phase: The new story phase
        """
        if phase in STORY_PHASES:
            prev_phase = self.current_story_phase
            self.current_story_phase = phase
            logger.info(f"Story phase changed: {prev_phase} -> {phase}")
            print(colored(f"Story phase progressed to: {phase}", "magenta"))
        else:
            logger.warning(f"Attempted to set invalid story phase: {phase}")
    
    def get_story_phase(self) -> str:
        """Get the current story phase.
        
        Returns:
            The current story phase
        """
        return self.current_story_phase
    
    def set_player_path(self, path: PathType):
        """Set the player's chosen path.
        
        Args:
            path: The chosen path (Warrior, Mystic, or Stealth)
        """
        self.player_path = path
        logger.info(f"Player chose the {path.value} path")
        print(colored(f"You have chosen the path of the {path.value.title()}", "yellow"))
    
    def get_player_path(self) -> Optional[str]:
        """Get the player's chosen path.
        
        Returns:
            The player's chosen path or None if not yet chosen
        """
        return self.player_path.value if self.player_path else None
    
    def reset_player_path(self):
        """Reset the player's chosen path (for testing purposes)."""
        self.player_path = None
        logger.info("Player path reset") 