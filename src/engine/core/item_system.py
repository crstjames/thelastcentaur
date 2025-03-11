"""
Item System for The Last Centaur game.

This module manages items, their properties, and interactions
including inventory management and item combinations.
"""

import logging
from typing import Dict, List, Optional, Set, Tuple, Any
import json
import os
from termcolor import colored

from src.engine.core.models import Item, ItemType, ElementType

logger = logging.getLogger(__name__)

class ItemManager:
    """Manages items and their interactions in the game."""
    
    def __init__(self):
        """Initialize the item manager."""
        self.items: Dict[str, Item] = {}
        self.combinations: Dict[Tuple[str, str], str] = {}
        self.sequence_puzzles: Dict[str, List[str]] = {}
        self.riddle_solutions: Dict[str, str] = {}
        
        # Initialize the item database
        self._initialize_items()
        self._initialize_combinations()
        self._initialize_sequence_puzzles()
        self._initialize_riddles()
        
        logger.info("Item Manager initialized")
        print(colored("Item Manager initialized", "green"))
    
    def _initialize_items(self):
        """Set up the initial item database."""
        # Basic items
        self.items["rusty_sword"] = Item(
            id="rusty_sword",
            name="Rusty Sword",
            description="An old, worn sword. Despite its age, it still feels balanced in your hand.",
            type=ItemType.WEAPON,
            properties={"damage": 5, "durability": 70}
        )
        
        self.items["leather_armor"] = Item(
            id="leather_armor",
            name="Leather Armor",
            description="Basic protection made of tanned hide. Provides minimal defense but won't slow you down.",
            type=ItemType.ARMOR,
            properties={"defense": 3, "weight": 2}
        )
        
        # Quest items
        self.items["mystic_crystal"] = Item(
            id="mystic_crystal",
            name="Mystic Crystal",
            description="A luminescent crystal that pulses with ethereal energy. It feels warm to the touch.",
            type=ItemType.QUEST,
            properties={"energy": 100, "glowing": True},
            elemental_type=ElementType.LIGHT
        )
        
        self.items["shadow_essence"] = Item(
            id="shadow_essence",
            name="Shadow Essence",
            description="A vial containing a swirling dark substance that seems to absorb light around it.",
            type=ItemType.QUEST,
            properties={"volatile": True},
            elemental_type=ElementType.SHADOW
        )
        
        self.items["ancient_medallion"] = Item(
            id="ancient_medallion",
            name="Ancient Medallion",
            description="A medallion etched with symbols of the centaur ancestors. It feels heavy with history.",
            type=ItemType.KEY,
            properties={"age": 1000, "inscribed": True}
        )
        
        # Craftable items
        self.items["crystal_fragment"] = Item(
            id="crystal_fragment",
            name="Crystal Fragment",
            description="A small piece of mystic crystal, still containing traces of power.",
            type=ItemType.CRAFTING,
            properties={"energy": 25},
            combinable_with=["shadow_essence"],
            combination_result="shadow_key",
            elemental_type=ElementType.LIGHT
        )
        
        self.items["metal_hilt"] = Item(
            id="metal_hilt",
            name="Metal Hilt",
            description="A finely crafted sword hilt without a blade.",
            type=ItemType.CRAFTING,
            properties={"craftsmanship": 7},
            combinable_with=["crystal_fragment"],
            combination_result="light_dagger"
        )
        
        # Combinable items results
        self.items["shadow_key"] = Item(
            id="shadow_key",
            name="Shadow Key",
            description="A key formed by merging crystal and shadow. It seems to phase in and out of reality.",
            type=ItemType.KEY,
            properties={"unlocks": "shadow_sanctuary"},
            elemental_type=ElementType.SHADOW
        )
        
        self.items["light_dagger"] = Item(
            id="light_dagger",
            name="Light Dagger",
            description="A dagger with a blade made of pure light energy.",
            type=ItemType.WEAPON,
            properties={"damage": 15, "light_damage": 10},
            elemental_type=ElementType.LIGHT
        )
        
        # Puzzle items
        self.items["honor_token"] = Item(
            id="honor_token",
            name="Honor Token",
            description="A token signifying your victory in honorable combat.",
            type=ItemType.QUEST,
            properties={"earned": True},
            combinable_with=["wisdom_token", "shadow_token"],
            combination_result="crown_of_dominion"
        )
        
        self.items["wisdom_token"] = Item(
            id="wisdom_token",
            name="Wisdom Token",
            description="A token representing knowledge gained through mystic study.",
            type=ItemType.QUEST,
            properties={"earned": True},
            combinable_with=["honor_token", "shadow_token"],
            combination_result="crown_of_dominion"
        )
        
        self.items["shadow_token"] = Item(
            id="shadow_token",
            name="Shadow Token",
            description="A token representing mastery over the shadows.",
            type=ItemType.QUEST,
            properties={"earned": True},
            combinable_with=["honor_token", "wisdom_token"],
            combination_result="crown_of_dominion"
        )
        
        self.items["crown_of_dominion"] = Item(
            id="crown_of_dominion",
            name="Crown of Dominion",
            description="A crown forged from the three tokens. It represents mastery of all paths.",
            type=ItemType.QUEST,
            properties={"complete": True, "power": 100}
        )
    
    def _initialize_combinations(self):
        """Set up the valid item combinations."""
        # Process all combinable items
        for item_id, item in self.items.items():
            if item.combinable_with and item.combination_result:
                for other_item_id in item.combinable_with:
                    self.combinations[(item_id, other_item_id)] = item.combination_result
                    self.combinations[(other_item_id, item_id)] = item.combination_result
        
        # Special three-item combination
        self.combinations[("honor_token", "wisdom_token", "shadow_token")] = "crown_of_dominion"
    
    def _initialize_sequence_puzzles(self):
        """Set up sequence-based puzzles."""
        # Crystal activation sequence
        self.sequence_puzzles["crystal_pond_ritual"] = [
            "touch north crystal",
            "touch east crystal", 
            "touch west crystal",
            "touch south crystal"
        ]
        
        # Temple door combination
        self.sequence_puzzles["temple_door"] = [
            "turn left dial",
            "turn middle dial",
            "turn left dial",
            "turn right dial"
        ]
        
        # Meditation sequence
        self.sequence_puzzles["meditation_circle"] = [
            "sit in center",
            "focus mind",
            "chant ancient verse",
            "release energy"
        ]
    
    def _initialize_riddles(self):
        """Set up riddle puzzles with their solutions."""
        self.riddle_solutions["guardian_riddle"] = "shadow"
        self.riddle_solutions["ancient_door_riddle"] = "reflection"
        self.riddle_solutions["elder_riddle"] = "time"
        self.riddle_solutions["crystal_cave_riddle"] = "light"
    
    def get_item(self, item_id: str) -> Optional[Item]:
        """Get an item by its ID.
        
        Args:
            item_id: The ID of the item to retrieve
            
        Returns:
            The item if found, None otherwise
        """
        return self.items.get(item_id)
    
    def get_item_by_name(self, name: str) -> Optional[Item]:
        """Get an item by its name.
        
        Args:
            name: The name of the item to retrieve
            
        Returns:
            The item if found, None otherwise
        """
        normalized_name = name.lower().replace(" ", "_")
        
        # Try direct match first
        if normalized_name in self.items:
            return self.items[normalized_name]
        
        # Try partial match
        for item_id, item in self.items.items():
            if normalized_name in item_id or normalized_name in item.name.lower():
                return item
                
        return None
    
    def combine_items(self, item1_id: str, item2_id: str) -> Optional[Item]:
        """Try to combine two items.
        
        Args:
            item1_id: The ID of the first item
            item2_id: The ID of the second item
            
        Returns:
            The resulting item if the combination is valid, None otherwise
        """
        # Check if the combination exists
        if (item1_id, item2_id) in self.combinations:
            result_id = self.combinations[(item1_id, item2_id)]
            logger.info(f"Combined {item1_id} and {item2_id} to create {result_id}")
            print(colored(f"You combine the items to create: {self.items[result_id].name}", "yellow"))
            return self.items[result_id]
        
        # Try the reverse combination
        if (item2_id, item1_id) in self.combinations:
            result_id = self.combinations[(item2_id, item1_id)]
            logger.info(f"Combined {item2_id} and {item1_id} to create {result_id}")
            print(colored(f"You combine the items to create: {self.items[result_id].name}", "yellow"))
            return self.items[result_id]
        
        logger.info(f"Failed to combine {item1_id} and {item2_id}")
        return None
    
    def combine_three_items(self, item1_id: str, item2_id: str, item3_id: str) -> Optional[Item]:
        """Try to combine three items.
        
        Args:
            item1_id: The ID of the first item
            item2_id: The ID of the second item
            item3_id: The ID of the third item
            
        Returns:
            The resulting item if the combination is valid, None otherwise
        """
        # Sort the items for consistent lookup
        items = sorted([item1_id, item2_id, item3_id])
        
        # Check if the combination exists
        combination = tuple(items)
        if combination in self.combinations:
            result_id = self.combinations[combination]
            logger.info(f"Combined {item1_id}, {item2_id}, and {item3_id} to create {result_id}")
            print(colored(f"You combine the three items to create: {self.items[result_id].name}", "cyan"))
            return self.items[result_id]
        
        logger.info(f"Failed to combine {item1_id}, {item2_id}, and {item3_id}")
        return None
    
    def check_sequence_puzzle(self, puzzle_id: str, actions: List[str]) -> bool:
        """Check if a sequence of actions solves a puzzle.
        
        Args:
            puzzle_id: The ID of the puzzle
            actions: The sequence of actions taken
            
        Returns:
            True if the sequence solves the puzzle, False otherwise
        """
        if puzzle_id not in self.sequence_puzzles:
            logger.warning(f"Unknown puzzle ID: {puzzle_id}")
            return False
            
        expected_sequence = self.sequence_puzzles[puzzle_id]
        
        # Check if the sequences match
        if len(actions) != len(expected_sequence):
            return False
            
        for i, action in enumerate(actions):
            if action.lower() != expected_sequence[i].lower():
                return False
                
        logger.info(f"Puzzle {puzzle_id} solved with correct sequence")
        print(colored(f"The puzzle activates as you complete the sequence!", "green"))
        return True
    
    def solve_riddle(self, riddle_id: str, answer: str) -> bool:
        """Check if an answer solves a riddle.
        
        Args:
            riddle_id: The ID of the riddle
            answer: The proposed answer
            
        Returns:
            True if the answer is correct, False otherwise
        """
        if riddle_id not in self.riddle_solutions:
            logger.warning(f"Unknown riddle ID: {riddle_id}")
            return False
            
        correct_answer = self.riddle_solutions[riddle_id]
        
        if answer.lower() == correct_answer.lower():
            logger.info(f"Riddle {riddle_id} solved correctly")
            print(colored("Your answer unlocks the riddle!", "green"))
            return True
            
        logger.info(f"Incorrect answer for riddle {riddle_id}: {answer}")
        return False
    
    def get_items_by_type(self, item_type: ItemType) -> List[Item]:
        """Get all items of a specific type.
        
        Args:
            item_type: The type of items to retrieve
            
        Returns:
            A list of items of the specified type
        """
        return [item for item in self.items.values() if item.type == item_type]
    
    def get_all_items(self) -> List[Item]:
        """Get all items in the database.
        
        Returns:
            A list of all items
        """
        return list(self.items.values())
    
    def add_item(self, item: Item):
        """Add an item to the database.
        
        Args:
            item: The item to add
        """
        self.items[item.id] = item
        logger.info(f"Added item to database: {item.name}")
        
        # Update combinations if necessary
        if item.combinable_with and item.combination_result:
            for other_item_id in item.combinable_with:
                self.combinations[(item.id, other_item_id)] = item.combination_result
                self.combinations[(other_item_id, item.id)] = item.combination_result 