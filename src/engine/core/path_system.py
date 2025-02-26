"""
Path System for The Last Centaur.

This module integrates the three paths (Warrior, Stealth, and Mystic) and provides
functionality for path selection, progression tracking, and path-specific gameplay.
"""

from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field
import random

from .models import PathType, StoryArea

# Import these directly to avoid circular imports
from .warrior_path import (
    create_warrior_quest, 
    WarriorProgression, 
    WARRIOR_ABILITIES, 
    calculate_warrior_damage, 
    can_use_warrior_ability
)
from .stealth_path import (
    create_stealth_quest, 
    StealthProgression, 
    StealthState, 
    STEALTH_ABILITIES, 
    calculate_stealth_damage, 
    can_use_stealth_ability
)
from .mystic_path import (
    create_mystic_quest, 
    MysticProgression, 
    MeditationState, 
    MYSTIC_ABILITIES, 
    calculate_spell_damage, 
    can_cast_spell
)

# Forward reference for type hints
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .quest_system import Quest, QuestSystem

@dataclass
class PathSelection:
    """Tracks a player's path selection and progress."""
    selected_path: Optional[PathType] = None
    warrior_progression: WarriorProgression = field(default_factory=WarriorProgression)
    stealth_progression: StealthProgression = field(default_factory=StealthProgression)
    mystic_progression: MysticProgression = field(default_factory=MysticProgression)
    stealth_state: StealthState = field(default_factory=StealthState)
    meditation_state: MeditationState = field(default_factory=MeditationState)
    path_quests: Dict[PathType, Any] = field(default_factory=dict)
    path_abilities_used: Dict[PathType, List[str]] = field(default_factory=lambda: {
        PathType.WARRIOR: [],
        PathType.STEALTH: [],
        PathType.MYSTIC: []
    })
    path_affinity: Dict[PathType, float] = field(default_factory=lambda: {
        PathType.WARRIOR: 0.0,
        PathType.STEALTH: 0.0,
        PathType.MYSTIC: 0.0
    })
    
    def select_path(self, path_type: PathType) -> str:
        """
        Select a path for the player.
        
        Args:
            path_type: The path to select
            
        Returns:
            A message describing the path selection
        """
        self.selected_path = path_type
        
        messages = {
            PathType.WARRIOR: "You have chosen the path of the Warrior. Your journey will be one of honor, strength, and direct confrontation.",
            PathType.STEALTH: "You have chosen the path of Stealth. Your journey will be one of shadows, cunning, and indirect approaches.",
            PathType.MYSTIC: "You have chosen the path of the Mystic. Your journey will be one of wisdom, magic, and understanding the deeper nature of reality."
        }
        
        return messages[path_type]
    
    def get_path_description(self, path_type: PathType) -> str:
        """
        Get a description of a path.
        
        Args:
            path_type: The path to describe
            
        Returns:
            A description of the path
        """
        descriptions = {
            PathType.WARRIOR: (
                "The Warrior path focuses on combat prowess and direct confrontation. "
                "Warriors gain strength from honorable victories and can wield powerful "
                "ancient weapons. This path is straightforward but challenging, requiring "
                "courage and determination."
            ),
            PathType.STEALTH: (
                "The Stealth path focuses on subterfuge, evasion, and indirect approaches. "
                "Those who follow this path learn to move unseen, strike from shadows, and "
                "bypass obstacles rather than confronting them directly. This path requires "
                "patience and careful planning."
            ),
            PathType.MYSTIC: (
                "The Mystic path focuses on magical abilities, wisdom, and understanding "
                "the deeper nature of reality. Mystics can cast powerful spells, see hidden "
                "truths, and commune with ancient forces. This path requires study and "
                "contemplation but offers great insight and power."
            )
        }
        
        return descriptions[path_type]
    
    def get_path_progress(self, path_type: Optional[PathType] = None) -> str:
        """
        Get a description of the player's progress along a path.
        
        Args:
            path_type: The path to check, or None for the selected path
            
        Returns:
            A description of the player's progress
        """
        if path_type is None:
            if self.selected_path is None:
                return "You have not yet chosen a path."
            path_type = self.selected_path
        
        if path_type == PathType.WARRIOR:
            progression = self.warrior_progression
            return (
                f"Warrior Path - Level {progression.level}\n"
                f"Experience: {progression.experience}\n"
                f"Honorable Kills: {progression.honorable_kills}\n"
                f"Abilities Unlocked: {', '.join(progression.abilities_unlocked) if progression.abilities_unlocked else 'None'}\n"
                f"Health Bonus: +{progression.max_health_bonus}\n"
                f"Stamina Bonus: +{progression.max_stamina_bonus}"
            )
        elif path_type == PathType.STEALTH:
            progression = self.stealth_progression
            return (
                f"Stealth Path - Level {progression.level}\n"
                f"Experience: {progression.experience}\n"
                f"Silent Kills: {progression.silent_kills}\n"
                f"Abilities Unlocked: {', '.join(progression.abilities_unlocked) if progression.abilities_unlocked else 'None'}\n"
                f"Detection Reduction: {progression.detection_reduction * 100:.1f}%"
            )
        elif path_type == PathType.MYSTIC:
            progression = self.mystic_progression
            return (
                f"Mystic Path - Level {progression.level}\n"
                f"Experience: {progression.experience}\n"
                f"Spells Learned: {', '.join(progression.spells_learned) if progression.spells_learned else 'None'}\n"
                f"Abilities Unlocked: {', '.join(progression.abilities_unlocked) if progression.abilities_unlocked else 'None'}\n"
                f"Max Mana: {progression.max_mana}\n"
                f"Mana Regeneration: {progression.mana_regen} per turn"
            )
        
        return "Unknown path type."
    
    def update_path_affinity(self, path_type: PathType, amount: float) -> None:
        """
        Update the player's affinity for a path.
        
        Args:
            path_type: The path to update
            amount: The amount to increase affinity by
        """
        self.path_affinity[path_type] += amount
    
    def get_suggested_path(self) -> Tuple[PathType, float]:
        """
        Get the path with the highest affinity.
        
        Returns:
            Tuple of (path type, affinity value)
        """
        if not any(self.path_affinity.values()):
            # If no affinities yet, return a random path
            return random.choice(list(PathType)), 0.0
        
        # Return the path with the highest affinity
        return max(self.path_affinity.items(), key=lambda x: x[1])
    
    def get_path_abilities(self, path_type: Optional[PathType] = None) -> Dict[str, Dict[str, Any]]:
        """
        Get the abilities for a path.
        
        Args:
            path_type: The path to check, or None for the selected path
            
        Returns:
            Dictionary of abilities
        """
        if path_type is None:
            if self.selected_path is None:
                return {}
            path_type = self.selected_path
        
        if path_type == PathType.WARRIOR:
            return WARRIOR_ABILITIES
        elif path_type == PathType.STEALTH:
            return STEALTH_ABILITIES
        elif path_type == PathType.MYSTIC:
            return MYSTIC_ABILITIES
        
        return {}
    
    def get_available_abilities(self, path_type: Optional[PathType] = None) -> Dict[str, Dict[str, Any]]:
        """
        Get the abilities available to the player for a path.
        
        Args:
            path_type: The path to check, or None for the selected path
            
        Returns:
            Dictionary of available abilities
        """
        if path_type is None:
            if self.selected_path is None:
                return {}
            path_type = self.selected_path
        
        all_abilities = self.get_path_abilities(path_type)
        
        if path_type == PathType.WARRIOR:
            progression = self.warrior_progression
            return {
                ability_id: ability_data
                for ability_id, ability_data in all_abilities.items()
                if ability_id in progression.abilities_unlocked
            }
        elif path_type == PathType.STEALTH:
            progression = self.stealth_progression
            return {
                ability_id: ability_data
                for ability_id, ability_data in all_abilities.items()
                if ability_id in progression.abilities_unlocked
            }
        elif path_type == PathType.MYSTIC:
            progression = self.mystic_progression
            return {
                ability_id: ability_data
                for ability_id, ability_data in all_abilities.items()
                if ability_id in progression.abilities_unlocked
            }
        
        return {}

class PathSystem:
    """Manages the path system for the game."""
    
    def __init__(self, quest_system=None):
        """
        Initialize the path system.
        
        Args:
            quest_system: The quest system to use
        """
        self.quest_system = quest_system
        self.path_selection = PathSelection()
        if quest_system is not None:
            self._initialize_path_quests()
    
    def _initialize_path_quests(self) -> None:
        """Initialize the quests for each path."""
        # Create the quests
        warrior_quest = create_warrior_quest()
        stealth_quest = create_stealth_quest()
        mystic_quest = create_mystic_quest()
        
        # Store them in the path selection
        self.path_selection.path_quests = {
            PathType.WARRIOR: warrior_quest,
            PathType.STEALTH: stealth_quest,
            PathType.MYSTIC: mystic_quest
        }
        
        # Add them to the quest system
        if self.quest_system is not None:
            self.quest_system.add_quest(warrior_quest)
            self.quest_system.add_quest(stealth_quest)
            self.quest_system.add_quest(mystic_quest)
    
    def select_path(self, path_type: PathType) -> str:
        """
        Select a path for the player.
        
        Args:
            path_type: The path to select
            
        Returns:
            A message describing the path selection
        """
        message = self.path_selection.select_path(path_type)
        
        # Start the quest for this path
        quest_id = {
            PathType.WARRIOR: "warriors_honor",
            PathType.STEALTH: "shadows_embrace",
            PathType.MYSTIC: "hermits_wisdom"
        }[path_type]
        
        if self.quest_system is not None:
            success, quest_message = self.quest_system.start_quest(quest_id)
            return f"{message}\n\n{quest_message if success else ''}"
        
        return message
    
    def get_path_description(self, path_type: PathType) -> str:
        """
        Get a description of a path.
        
        Args:
            path_type: The path to describe
            
        Returns:
            A description of the path
        """
        return self.path_selection.get_path_description(path_type)
    
    def get_path_progress(self, path_type: Optional[PathType] = None) -> str:
        """
        Get a description of the player's progress along a path.
        
        Args:
            path_type: The path to check, or None for the selected path
            
        Returns:
            A description of the player's progress
        """
        return self.path_selection.get_path_progress(path_type)
    
    def record_combat_action(self, action_type: str, target_type: str, success: bool) -> None:
        """
        Record a combat action to update path affinities.
        
        Args:
            action_type: The type of action (attack, defend, etc.)
            target_type: The type of target (enemy, environment, etc.)
            success: Whether the action was successful
        """
        # Update path affinities based on combat actions
        if action_type == "direct_attack" and success:
            self.path_selection.update_path_affinity(PathType.WARRIOR, 0.1)
        elif action_type == "stealth_attack" and success:
            self.path_selection.update_path_affinity(PathType.STEALTH, 0.1)
        elif action_type == "spell_cast" and success:
            self.path_selection.update_path_affinity(PathType.MYSTIC, 0.1)
    
    def record_exploration_action(self, action_type: str, area_type: str) -> None:
        """
        Record an exploration action to update path affinities.
        
        Args:
            action_type: The type of action (search, examine, etc.)
            area_type: The type of area being explored
        """
        # Update path affinities based on exploration actions
        if action_type == "search_for_enemies":
            self.path_selection.update_path_affinity(PathType.WARRIOR, 0.05)
        elif action_type == "search_for_hidden":
            self.path_selection.update_path_affinity(PathType.STEALTH, 0.05)
        elif action_type == "search_for_knowledge":
            self.path_selection.update_path_affinity(PathType.MYSTIC, 0.05)
    
    def record_dialogue_choice(self, npc_id: str, choice_type: str) -> None:
        """
        Record a dialogue choice to update path affinities.
        
        Args:
            npc_id: The ID of the NPC being talked to
            choice_type: The type of dialogue choice made
        """
        # Update path affinities based on dialogue choices
        if choice_type == "aggressive":
            self.path_selection.update_path_affinity(PathType.WARRIOR, 0.05)
        elif choice_type == "deceptive":
            self.path_selection.update_path_affinity(PathType.STEALTH, 0.05)
        elif choice_type == "inquisitive":
            self.path_selection.update_path_affinity(PathType.MYSTIC, 0.05)
    
    def get_suggested_path(self) -> Tuple[PathType, str]:
        """
        Get the path with the highest affinity and a description.
        
        Returns:
            Tuple of (path type, description)
        """
        path_type, affinity = self.path_selection.get_suggested_path()
        
        descriptions = {
            PathType.WARRIOR: (
                "Your actions suggest you might be well-suited to the Warrior path. "
                "You seem to prefer direct confrontation and honorable combat."
            ),
            PathType.STEALTH: (
                "Your actions suggest you might be well-suited to the Stealth path. "
                "You seem to prefer subtlety, cunning, and avoiding unnecessary confrontation."
            ),
            PathType.MYSTIC: (
                "Your actions suggest you might be well-suited to the Mystic path. "
                "You seem to prefer seeking knowledge and understanding the deeper nature of things."
            )
        }
        
        return path_type, descriptions[path_type]
    
    def gain_path_experience(self, amount: int) -> Tuple[int, List[str]]:
        """
        Gain experience for the selected path.
        
        Args:
            amount: The amount of experience to gain
            
        Returns:
            Tuple of (levels gained, newly unlocked abilities)
        """
        if self.path_selection.selected_path is None:
            return 0, []
        
        path_type = self.path_selection.selected_path
        
        if path_type == PathType.WARRIOR:
            return self.path_selection.warrior_progression.gain_experience(amount)
        elif path_type == PathType.STEALTH:
            return self.path_selection.stealth_progression.gain_experience(amount)
        elif path_type == PathType.MYSTIC:
            return self.path_selection.mystic_progression.gain_experience(amount)
        
        return 0, []
    
    def calculate_damage(self, base_damage: int, weapon_damage: int, **kwargs) -> int:
        """
        Calculate damage based on the selected path.
        
        Args:
            base_damage: Base damage value
            weapon_damage: Weapon damage value
            **kwargs: Additional arguments for specific path calculations
            
        Returns:
            Final damage value
        """
        if self.path_selection.selected_path is None:
            return base_damage + weapon_damage
        
        path_type = self.path_selection.selected_path
        
        if path_type == PathType.WARRIOR:
            return calculate_warrior_damage(
                base_damage, 
                self.path_selection.warrior_progression.level, 
                weapon_damage,
                kwargs.get("is_honorable_strike", False),
                kwargs.get("target_is_corrupted", False)
            )
        elif path_type == PathType.STEALTH:
            return calculate_stealth_damage(
                base_damage,
                self.path_selection.stealth_progression.level,
                weapon_damage,
                kwargs.get("is_silent_strike", False),
                kwargs.get("target_is_unaware", False)
            )
        elif path_type == PathType.MYSTIC:
            return calculate_spell_damage(
                base_damage,
                self.path_selection.mystic_progression.level,
                kwargs.get("focus_power", 0),
                kwargs.get("target_is_corrupted", False)
            )
        
        return base_damage + weapon_damage
    
    def can_use_ability(self, ability_id: str, **kwargs) -> Tuple[bool, str]:
        """
        Check if the player can use an ability.
        
        Args:
            ability_id: The ID of the ability to check
            **kwargs: Additional arguments for specific path checks
            
        Returns:
            Tuple of (can use ability, reason if cannot)
        """
        if self.path_selection.selected_path is None:
            return False, "You have not selected a path."
        
        path_type = self.path_selection.selected_path
        
        if path_type == PathType.WARRIOR:
            return can_use_warrior_ability(
                ability_id,
                self.path_selection.warrior_progression.level,
                kwargs.get("player_items", []),
                kwargs.get("player_stamina", 0)
            )
        elif path_type == PathType.STEALTH:
            return can_use_stealth_ability(
                ability_id,
                self.path_selection.stealth_progression.level,
                kwargs.get("player_items", []),
                kwargs.get("player_stamina", 0),
                self.path_selection.stealth_state
            )
        elif path_type == PathType.MYSTIC:
            return can_cast_spell(
                ability_id,
                self.path_selection.mystic_progression.level,
                kwargs.get("player_items", []),
                kwargs.get("player_mana", 0),
                self.path_selection.meditation_state
            )
        
        return False, "Unknown path type."
    
    def use_ability(self, ability_id: str, **kwargs) -> Tuple[bool, str, Dict[str, Any]]:
        """
        Use an ability.
        
        Args:
            ability_id: The ID of the ability to use
            **kwargs: Additional arguments for specific abilities
            
        Returns:
            Tuple of (success, message, effects)
        """
        can_use, reason = self.can_use_ability(ability_id, **kwargs)
        
        if not can_use:
            return False, reason, {}
        
        path_type = self.path_selection.selected_path
        
        # Record that this ability was used
        if path_type and ability_id not in self.path_selection.path_abilities_used[path_type]:
            self.path_selection.path_abilities_used[path_type].append(ability_id)
        
        # Get the ability data
        abilities = self.path_selection.get_path_abilities(path_type)
        ability = abilities.get(ability_id, {})
        
        # Apply cooldown
        if path_type == PathType.STEALTH:
            self.path_selection.stealth_state.cooldowns[ability_id] = ability.get("cooldown", 1)
        
        # Return success and effects
        return True, f"You use {ability.get('name', ability_id)}.", {
            "name": ability.get("name", ability_id),
            "description": ability.get("description", ""),
            "damage": self.calculate_damage(
                kwargs.get("base_damage", 0),
                kwargs.get("weapon_damage", 0),
                **{f"is_{ability_id}": True, **kwargs}
            ) if "damage" in kwargs else None,
            "duration": ability.get("duration", 1),
            "effect": ability.get("effect", {})
        }
    
    def update_stealth_state(self, **kwargs) -> None:
        """
        Update the player's stealth state.
        
        Args:
            **kwargs: Arguments for stealth state update
        """
        self.path_selection.stealth_state.update_detection(
            kwargs.get("light_level", 0.5),
            kwargs.get("movement_speed", 0.0),
            kwargs.get("carrying_weight", 0.0),
            kwargs.get("in_combat", False)
        )
        
        # Apply item effects
        self.path_selection.stealth_state.apply_stealth_item_effects(
            kwargs.get("player_items", [])
        )
        
        # Update cooldowns
        self.path_selection.stealth_state.update_cooldowns()
    
    def update_meditation_state(self, **kwargs) -> Tuple[float, bool]:
        """
        Update the player's meditation state.
        
        Args:
            **kwargs: Arguments for meditation state update
            
        Returns:
            Tuple of (mana restored, whether gained insight)
        """
        if kwargs.get("start_meditation", False):
            self.path_selection.meditation_state.start_meditation(
                self.path_selection.mystic_progression.level
            )
            return 0.0, False
        elif kwargs.get("end_meditation", False):
            self.path_selection.meditation_state.end_meditation()
            return 0.0, False
        elif self.path_selection.meditation_state.is_meditating:
            return self.path_selection.meditation_state.continue_meditation()
        
        return 0.0, False
    
    def get_path_status(self) -> Dict[str, Any]:
        """
        Get the status of all paths.
        
        Returns:
            Dictionary with path status information
        """
        return {
            "selected_path": self.path_selection.selected_path,
            "warrior": {
                "level": self.path_selection.warrior_progression.level,
                "experience": self.path_selection.warrior_progression.experience,
                "abilities": len(self.path_selection.warrior_progression.abilities_unlocked),
                "affinity": self.path_selection.path_affinity[PathType.WARRIOR]
            },
            "stealth": {
                "level": self.path_selection.stealth_progression.level,
                "experience": self.path_selection.stealth_progression.experience,
                "abilities": len(self.path_selection.stealth_progression.abilities_unlocked),
                "affinity": self.path_selection.path_affinity[PathType.STEALTH],
                "is_hidden": self.path_selection.stealth_state.is_hidden
            },
            "mystic": {
                "level": self.path_selection.mystic_progression.level,
                "experience": self.path_selection.mystic_progression.experience,
                "abilities": len(self.path_selection.mystic_progression.abilities_unlocked),
                "affinity": self.path_selection.path_affinity[PathType.MYSTIC],
                "is_meditating": self.path_selection.meditation_state.is_meditating
            }
        } 