"""
Puzzle System for The Last Centaur game.

This module manages puzzles throughout the game, including:
- Item combination puzzles
- Sequential action puzzles
- Environmental interaction puzzles
- Riddle/knowledge-based puzzles
"""

import logging
from typing import Dict, List, Optional, Set, Tuple, Any, Callable
from enum import Enum
import json
import os
from termcolor import colored

from src.engine.core.models import StoryArea, ItemType
from src.engine.core.item_system import ItemManager

logger = logging.getLogger(__name__)

class PuzzleType(Enum):
    """Types of puzzles in the game."""
    ITEM_COMBINATION = "item_combination"
    SEQUENCE = "sequence"
    ENVIRONMENTAL = "environmental"
    RIDDLE = "riddle"
    MULTI_STEP = "multi_step"

class PuzzleState(Enum):
    """Possible states of a puzzle."""
    UNDISCOVERED = "undiscovered"
    DISCOVERED = "discovered"
    IN_PROGRESS = "in_progress"
    SOLVED = "solved"
    FAILED = "failed"

class Puzzle:
    """Represents a puzzle in the game."""
    
    def __init__(
        self,
        id: str,
        name: str,
        description: str,
        puzzle_type: PuzzleType,
        area: StoryArea,
        hints: List[str],
        solution_items: Optional[List[str]] = None,
        solution_sequence: Optional[List[str]] = None,
        solution_answer: Optional[str] = None,
        reward_item: Optional[str] = None,
        reward_description: Optional[str] = None,
        prerequisite_puzzles: Optional[List[str]] = None,
        on_solve: Optional[Callable] = None
    ):
        """Initialize a puzzle.
        
        Args:
            id: Unique identifier for the puzzle
            name: Display name for the puzzle
            description: Description of the puzzle
            puzzle_type: Type of puzzle
            area: Area where the puzzle is located
            hints: List of hints for solving the puzzle
            solution_items: For item combination puzzles, the required items
            solution_sequence: For sequence puzzles, the required action sequence
            solution_answer: For riddle puzzles, the correct answer
            reward_item: Item ID granted for solving the puzzle
            reward_description: Description of what happens when the puzzle is solved
            prerequisite_puzzles: Puzzles that must be solved before this one
            on_solve: Function to call when the puzzle is solved
        """
        self.id = id
        self.name = name
        self.description = description
        self.puzzle_type = puzzle_type
        self.area = area
        self.hints = hints
        self.solution_items = solution_items or []
        self.solution_sequence = solution_sequence or []
        self.solution_answer = solution_answer
        self.reward_item = reward_item
        self.reward_description = reward_description or "You solved the puzzle!"
        self.prerequisite_puzzles = prerequisite_puzzles or []
        self.on_solve = on_solve
        self.state = PuzzleState.UNDISCOVERED
        self.progress: Dict[str, Any] = {}
        
        # For multi-step puzzles
        self.steps: List[Dict[str, Any]] = []
        self.current_step = 0

class PuzzleSystem:
    """Manages puzzles and their interactions in the game."""
    
    def __init__(self, player, item_manager: ItemManager):
        """Initialize the puzzle system.
        
        Args:
            player: The player object
            item_manager: The item manager
        """
        self.player = player
        self.item_manager = item_manager
        self.puzzles: Dict[str, Puzzle] = {}
        self.active_sequence_actions: Dict[str, List[str]] = {}  # puzzle_id -> actions taken
        self.completed_puzzles: Set[str] = set()
        
        # Initialize the puzzle database
        self._initialize_puzzles()
        
        logger.info("Puzzle System initialized")
        print(colored("Puzzle System initialized", "green"))
    
    def _initialize_puzzles(self):
        """Set up the initial puzzle database."""
        # Item combination puzzles
        self.puzzles["shadow_key_creation"] = Puzzle(
            id="shadow_key_creation",
            name="Forging the Shadow Key",
            description="You need to combine the energies of light and shadow to create a key that can unlock the path forward.",
            puzzle_type=PuzzleType.ITEM_COMBINATION,
            area=StoryArea.CRYSTAL_POND,
            hints=[
                "The crystal fragment contains pure light energy.",
                "Shadow essence seems to be drawn to the light.",
                "Perhaps these opposing forces can be combined..."
            ],
            solution_items=["crystal_fragment", "shadow_essence"],
            reward_item="shadow_key",
            reward_description="The crystal fragment and shadow essence merge, swirling together into a key that seems to exist between realities."
        )
        
        # Sequential action puzzles
        self.puzzles["crystal_activation"] = Puzzle(
            id="crystal_activation",
            name="Crystal Pond Ritual",
            description="The ancient crystals surrounding the pond must be touched in a specific sequence to activate their power.",
            puzzle_type=PuzzleType.SEQUENCE,
            area=StoryArea.CRYSTAL_POND,
            hints=[
                "The crystals surround the pond in the four cardinal directions.",
                "An inscription nearby mentions 'following the sun's path'.",
                "The north crystal glows slightly brighter than the others."
            ],
            solution_sequence=[
                "touch north crystal",
                "touch east crystal", 
                "touch west crystal",
                "touch south crystal"
            ],
            reward_item="crystal_fragment",
            reward_description="As you complete the sequence, the crystals resonate with energy. A small fragment breaks off and falls into your hand."
        )
        
        # Environmental puzzles
        self.puzzles["temple_water_channels"] = Puzzle(
            id="temple_water_channels",
            name="Temple Water Channels",
            description="Ancient channels crisscross the temple floor. Water needs to flow to the central basin to reveal a hidden item.",
            puzzle_type=PuzzleType.ENVIRONMENTAL,
            area=StoryArea.FORGOTTEN_TEMPLE,
            hints=[
                "The stone blocks can be rotated to direct water flow.",
                "Water enters from the northern channel.",
                "The central basin has markings that suggest it should be filled."
            ],
            solution_sequence=[
                "rotate northwest block",
                "rotate center block",
                "rotate southeast block"
            ],
            reward_item="ancient_medallion",
            reward_description="Water rushes through the channels and fills the central basin. As it does, a hidden compartment opens, revealing an ancient medallion."
        )
        
        # Riddle puzzles
        self.puzzles["guardian_riddle"] = Puzzle(
            id="guardian_riddle",
            name="The Guardian's Riddle",
            description="A stone guardian blocks the path. It speaks a riddle that must be answered to proceed.",
            puzzle_type=PuzzleType.RIDDLE,
            area=StoryArea.GUARDIAN_OVERLOOK,
            hints=[
                "The guardian speaks of something that follows you always.",
                "It mentions that this thing is darkest when light is strongest.",
                "It refers to something that mimics your movements."
            ],
            solution_answer="shadow",
            reward_description="The guardian nods slowly and steps aside, revealing the path forward."
        )
        
        # Multi-step puzzle
        meditation_puzzle = Puzzle(
            id="meditation_ritual",
            name="The Meditation Ritual",
            description="An ancient ritual of meditation that requires multiple steps to unlock mystical energy.",
            puzzle_type=PuzzleType.MULTI_STEP,
            area=StoryArea.MEDITATION_CIRCLE,
            hints=[
                "The stone circle has markings indicating positions for meditation.",
                "Ancient texts mention a ritual to focus one's energy.",
                "The circle seems to respond to your presence and actions."
            ],
            reward_item="wisdom_token",
            reward_description="As you complete the ritual, mystical energy flows through you. A token materializes in the center of the circle."
        )
        
        # Add steps to the multi-step puzzle
        meditation_puzzle.steps = [
            {
                "description": "Find the center of the meditation circle and sit.",
                "action": "sit in center",
                "feedback": "You feel a subtle energy as you take your place in the center of the circle."
            },
            {
                "description": "Focus your mind and clear your thoughts.",
                "action": "focus mind",
                "feedback": "As your mind clears, the markings on the stones begin to glow faintly."
            },
            {
                "description": "Recite the ancient verse inscribed on the stones.",
                "action": "chant ancient verse",
                "feedback": "Your voice resonates with the circle, causing the glowing to intensify."
            },
            {
                "description": "Release your gathered energy into the circle.",
                "action": "release energy",
                "feedback": "The energy flows from you into the circle, creating a brilliant display of light."
            }
        ]
        
        self.puzzles["meditation_ritual"] = meditation_puzzle
        
        # Progression puzzle that requires other puzzles to be completed
        self.puzzles["crown_creation"] = Puzzle(
            id="crown_creation",
            name="Forging the Crown of Dominion",
            description="The three tokens of power must be combined to create the Crown of Dominion, which will allow you to confront the Shadow Centaur.",
            puzzle_type=PuzzleType.ITEM_COMBINATION,
            area=StoryArea.ANCIENT_SANCTUARY,
            hints=[
                "Each token represents mastery of a different path.",
                "The ancient altar seems designed to hold all three tokens.",
                "The prophecy speaks of 'three becoming one' to challenge the shadow."
            ],
            solution_items=["honor_token", "wisdom_token", "shadow_token"],
            reward_item="crown_of_dominion",
            reward_description="The three tokens rise into the air and merge in a flash of light, forming a crown that emanates power.",
            prerequisite_puzzles=["shadow_key_creation", "guardian_riddle", "meditation_ritual"]
        )
    
    def discover_puzzle(self, puzzle_id: str) -> Optional[Puzzle]:
        """Mark a puzzle as discovered by the player.
        
        Args:
            puzzle_id: The ID of the puzzle
            
        Returns:
            The puzzle if found, None otherwise
        """
        if puzzle_id not in self.puzzles:
            logger.warning(f"Unknown puzzle ID: {puzzle_id}")
            return None
            
        puzzle = self.puzzles[puzzle_id]
        
        if puzzle.state == PuzzleState.UNDISCOVERED:
            puzzle.state = PuzzleState.DISCOVERED
            logger.info(f"Puzzle discovered: {puzzle.name}")
            print(colored(f"You've discovered a puzzle: {puzzle.name}", "cyan"))
            
        return puzzle
    
    def get_puzzle(self, puzzle_id: str) -> Optional[Puzzle]:
        """Get a puzzle by its ID.
        
        Args:
            puzzle_id: The ID of the puzzle
            
        Returns:
            The puzzle if found, None otherwise
        """
        return self.puzzles.get(puzzle_id)
    
    def get_puzzles_in_area(self, area: StoryArea) -> List[Puzzle]:
        """Get all puzzles in a specific area.
        
        Args:
            area: The area to check
            
        Returns:
            List of puzzles in the area
        """
        return [p for p in self.puzzles.values() if p.area == area]
    
    def check_item_combination(self, item_ids: List[str]) -> Optional[Tuple[Puzzle, str]]:
        """Check if a combination of items solves any puzzles.
        
        Args:
            item_ids: The IDs of the items being combined
            
        Returns:
            Tuple of (puzzle, reward_item) if successful, None otherwise
        """
        for puzzle_id, puzzle in self.puzzles.items():
            if puzzle.puzzle_type != PuzzleType.ITEM_COMBINATION:
                continue
                
            if puzzle.state == PuzzleState.SOLVED:
                continue
                
            # Check if all prerequisite puzzles are solved
            if not self._check_prerequisites(puzzle):
                continue
                
            # Simple check - are all required items present?
            if sorted(puzzle.solution_items) == sorted(item_ids):
                if self._solve_puzzle(puzzle):
                    return (puzzle, puzzle.reward_item)
        
        return None
    
    def start_sequence_puzzle(self, puzzle_id: str) -> bool:
        """Start a sequence puzzle, resetting any previous progress.
        
        Args:
            puzzle_id: The ID of the puzzle to start
            
        Returns:
            True if the puzzle exists and was started, False otherwise
        """
        if puzzle_id not in self.puzzles:
            logger.warning(f"Unknown puzzle ID: {puzzle_id}")
            return False
            
        puzzle = self.puzzles[puzzle_id]
        
        if puzzle.puzzle_type != PuzzleType.SEQUENCE and puzzle.puzzle_type != PuzzleType.MULTI_STEP:
            logger.warning(f"Puzzle {puzzle_id} is not a sequence puzzle")
            return False
            
        if puzzle.state == PuzzleState.SOLVED:
            logger.info(f"Puzzle {puzzle_id} is already solved")
            return False
            
        # Check if all prerequisite puzzles are solved
        if not self._check_prerequisites(puzzle):
            logger.info(f"Prerequisite puzzles for {puzzle_id} not solved")
            return False
            
        # Reset the sequence
        self.active_sequence_actions[puzzle_id] = []
        puzzle.state = PuzzleState.IN_PROGRESS
        puzzle.current_step = 0
        
        logger.info(f"Started sequence puzzle: {puzzle.name}")
        print(colored(f"You begin working on: {puzzle.name}", "cyan"))
        
        return True
    
    def add_sequence_action(self, puzzle_id: str, action: str) -> Optional[str]:
        """Add an action to a sequence puzzle in progress.
        
        Args:
            puzzle_id: The ID of the puzzle
            action: The action taken
            
        Returns:
            Feedback message if the action was valid, None otherwise
        """
        if puzzle_id not in self.puzzles:
            logger.warning(f"Unknown puzzle ID: {puzzle_id}")
            return None
            
        puzzle = self.puzzles[puzzle_id]
        
        if puzzle.state != PuzzleState.IN_PROGRESS:
            if puzzle.state == PuzzleState.UNDISCOVERED:
                return "You haven't discovered this puzzle yet."
            elif puzzle.state == PuzzleState.SOLVED:
                return "This puzzle has already been solved."
            else:
                return "You need to start the puzzle first."
        
        # Initialize the sequence if needed
        if puzzle_id not in self.active_sequence_actions:
            self.active_sequence_actions[puzzle_id] = []
            
        # Add the action to the sequence
        self.active_sequence_actions[puzzle_id].append(action)
        
        # For multi-step puzzles, check each step as it's completed
        if puzzle.puzzle_type == PuzzleType.MULTI_STEP:
            if puzzle.current_step < len(puzzle.steps):
                expected_action = puzzle.steps[puzzle.current_step]["action"]
                if action.lower() == expected_action.lower():
                    feedback = puzzle.steps[puzzle.current_step]["feedback"]
                    puzzle.current_step += 1
                    
                    # If this was the last step, solve the puzzle
                    if puzzle.current_step >= len(puzzle.steps):
                        self._solve_puzzle(puzzle)
                        return puzzle.reward_description
                        
                    return feedback
                else:
                    # Wrong action, reset progress
                    puzzle.current_step = 0
                    self.active_sequence_actions[puzzle_id] = []
                    return "That doesn't seem right. The ritual resets."
            
        # For regular sequence puzzles, check if complete
        else:
            actions = self.active_sequence_actions[puzzle_id]
            solution = puzzle.solution_sequence
            
            # Check if the sequence matches so far
            for i, act in enumerate(actions):
                if i >= len(solution) or act.lower() != solution[i].lower():
                    # Wrong action, reset the sequence
                    self.active_sequence_actions[puzzle_id] = []
                    return "That doesn't seem right. The sequence resets."
            
            # If we've completed the sequence, solve the puzzle
            if len(actions) == len(solution):
                if self._solve_puzzle(puzzle):
                    return puzzle.reward_description
        
        # Sequence in progress but not completed
        return f"You {action}. Something seems to be happening..."
    
    def solve_riddle(self, puzzle_id: str, answer: str) -> bool:
        """Check if an answer solves a riddle puzzle.
        
        Args:
            puzzle_id: The ID of the riddle puzzle
            answer: The proposed answer
            
        Returns:
            True if the answer is correct and the puzzle is solved, False otherwise
        """
        if puzzle_id not in self.puzzles:
            logger.warning(f"Unknown puzzle ID: {puzzle_id}")
            return False
            
        puzzle = self.puzzles[puzzle_id]
        
        if puzzle.puzzle_type != PuzzleType.RIDDLE:
            logger.warning(f"Puzzle {puzzle_id} is not a riddle puzzle")
            return False
            
        if puzzle.state == PuzzleState.SOLVED:
            logger.info(f"Puzzle {puzzle_id} is already solved")
            return True
            
        # Check if all prerequisite puzzles are solved
        if not self._check_prerequisites(puzzle):
            logger.info(f"Prerequisite puzzles for {puzzle_id} not solved")
            return False
            
        # Check the answer
        if answer.lower() == puzzle.solution_answer.lower():
            if self._solve_puzzle(puzzle):
                return True
                
        return False
    
    def solve_environmental_puzzle(self, puzzle_id: str, environment_state: Dict[str, Any]) -> bool:
        """Check if the environment state solves an environmental puzzle.
        
        Args:
            puzzle_id: The ID of the puzzle
            environment_state: Dictionary representing the state of environment objects
            
        Returns:
            True if the puzzle is solved, False otherwise
        """
        if puzzle_id not in self.puzzles:
            logger.warning(f"Unknown puzzle ID: {puzzle_id}")
            return False
            
        puzzle = self.puzzles[puzzle_id]
        
        if puzzle.puzzle_type != PuzzleType.ENVIRONMENTAL:
            logger.warning(f"Puzzle {puzzle_id} is not an environmental puzzle")
            return False
            
        if puzzle.state == PuzzleState.SOLVED:
            logger.info(f"Puzzle {puzzle_id} is already solved")
            return True
            
        # Check if all prerequisite puzzles are solved
        if not self._check_prerequisites(puzzle):
            logger.info(f"Prerequisite puzzles for {puzzle_id} not solved")
            return False
            
        # This is a simplified check - in a real game, this would be more complex
        # and specific to each puzzle's requirements
        if "solution" in environment_state and environment_state["solution"]:
            if self._solve_puzzle(puzzle):
                return True
                
        return False
    
    def _check_prerequisites(self, puzzle: Puzzle) -> bool:
        """Check if all prerequisite puzzles for a puzzle have been solved.
        
        Args:
            puzzle: The puzzle to check
            
        Returns:
            True if all prerequisites are met, False otherwise
        """
        for prereq_id in puzzle.prerequisite_puzzles:
            if prereq_id not in self.completed_puzzles:
                return False
                
        return True
    
    def _solve_puzzle(self, puzzle: Puzzle) -> bool:
        """Mark a puzzle as solved and apply its rewards.
        
        Args:
            puzzle: The puzzle to solve
            
        Returns:
            True if successful, False otherwise
        """
        if puzzle.state == PuzzleState.SOLVED:
            return True
            
        puzzle.state = PuzzleState.SOLVED
        self.completed_puzzles.add(puzzle.id)
        
        logger.info(f"Puzzle solved: {puzzle.name}")
        print(colored(f"You solved the puzzle: {puzzle.name}!", "green"))
        
        # Award any reward item
        if puzzle.reward_item and puzzle.reward_item in self.item_manager.items:
            reward_item = self.item_manager.get_item(puzzle.reward_item)
            if reward_item:
                self.player.add_item(puzzle.reward_item)
                print(colored(f"You received: {reward_item.name}", "yellow"))
        
        # Execute any custom on_solve function
        if puzzle.on_solve:
            puzzle.on_solve()
        
        return True
    
    def get_hint(self, puzzle_id: str) -> Optional[str]:
        """Get a hint for a puzzle.
        
        Args:
            puzzle_id: The ID of the puzzle
            
        Returns:
            A hint if available, None otherwise
        """
        if puzzle_id not in self.puzzles:
            logger.warning(f"Unknown puzzle ID: {puzzle_id}")
            return None
            
        puzzle = self.puzzles[puzzle_id]
        
        if puzzle.state == PuzzleState.UNDISCOVERED:
            return None
            
        if not puzzle.hints:
            return "There are no hints available for this puzzle."
            
        # Get the next available hint
        hint_index = puzzle.progress.get("hint_index", 0)
        if hint_index >= len(puzzle.hints):
            hint_index = len(puzzle.hints) - 1
            
        hint = puzzle.hints[hint_index]
        
        # Update the hint index for progressive hints
        puzzle.progress["hint_index"] = hint_index + 1
        
        return hint
    
    def is_puzzle_solved(self, puzzle_id: str) -> bool:
        """Check if a puzzle has been solved.
        
        Args:
            puzzle_id: The ID of the puzzle
            
        Returns:
            True if the puzzle is solved, False otherwise
        """
        if puzzle_id not in self.puzzles:
            return False
            
        return self.puzzles[puzzle_id].state == PuzzleState.SOLVED 