"""
Quest system for The Last Centaur.

This module implements FromSoftware-style quest lines with:
- Non-linear progression
- Hidden objectives and triggers
- Environmental storytelling
- Cryptic NPC dialogue that changes based on world state
- Multiple possible outcomes based on player choices
- Interconnected quest lines that affect each other
"""

from typing import Dict, List, Optional, Set, Tuple, Any
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime

from .models import StoryArea, EventType, GameEvent
from .player import Player
from .map_system import MapSystem

class QuestStatus(str, Enum):
    """Status of a quest in the game."""
    HIDDEN = "hidden"           # Quest exists but player hasn't discovered it
    DISCOVERED = "discovered"   # Player knows about quest but hasn't started
    ACTIVE = "active"           # Quest is in progress
    COMPLETED = "completed"     # Quest has been completed successfully
    FAILED = "failed"           # Quest has been failed permanently
    ALTERED = "altered"         # Quest has changed due to world state

class QuestTriggerType(str, Enum):
    """Types of triggers that can advance quest stages."""
    ITEM_ACQUIRED = "item_acquired"       # Player obtains a specific item
    AREA_VISITED = "area_visited"         # Player visits a specific area
    NPC_DIALOGUE = "npc_dialogue"         # Player talks to an NPC
    ENEMY_DEFEATED = "enemy_defeated"     # Player defeats a specific enemy
    TIME_PASSED = "time_passed"           # Game time reaches a threshold
    WORLD_STATE = "world_state"           # World reaches a specific state
    ITEM_USED = "item_used"               # Player uses a specific item
    ITEM_GIVEN = "item_given"             # Player gives an item to an NPC
    ENVIRONMENTAL = "environmental"       # Player interacts with environment
    QUEST_STATUS = "quest_status"         # Another quest reaches a status

@dataclass
class QuestTrigger:
    """A trigger that can advance a quest stage."""
    type: QuestTriggerType
    target: str                           # ID of the target (item, area, NPC, etc.)
    condition: Optional[str] = None       # Additional condition (e.g., "count > 3")
    hidden: bool = False                  # Whether this trigger is hidden from the player

@dataclass
class QuestStage:
    """A stage in a quest."""
    id: str
    description: str                      # Description shown to player
    hidden_description: str               # True nature of the stage (may be revealed later)
    triggers: List[QuestTrigger]          # Triggers to advance to next stage
    rewards: List[str] = field(default_factory=list)  # Items/status given when stage completes
    next_stages: List[str] = field(default_factory=list)  # Possible next stages (can branch)
    fail_conditions: List[QuestTrigger] = field(default_factory=list)  # Conditions that fail quest
    world_changes: List[Dict[str, Any]] = field(default_factory=list)  # Changes to make to world
    hint_dialogue: Dict[str, str] = field(default_factory=dict)  # NPC hints keyed by NPC ID

@dataclass
class Quest:
    """A quest in the game."""
    id: str
    name: str
    description: str
    hidden_description: str               # True nature of the quest (may be revealed later)
    initial_stage: str                    # ID of the first stage
    stages: Dict[str, QuestStage]         # All stages in this quest
    status: QuestStatus = QuestStatus.HIDDEN
    current_stage_id: Optional[str] = None
    discovery_triggers: List[QuestTrigger] = field(default_factory=list)  # How player discovers quest
    related_quests: List[str] = field(default_factory=list)  # Quests that interact with this one
    required_items: List[str] = field(default_factory=list)  # Items needed for this quest
    affected_npcs: List[str] = field(default_factory=list)  # NPCs whose dialogue changes
    lore_entries: List[str] = field(default_factory=list)  # Lore revealed by this quest
    
    def get_current_stage(self) -> Optional[QuestStage]:
        """Get the current stage of the quest."""
        if not self.current_stage_id:
            return None
        return self.stages.get(self.current_stage_id)

class QuestSystem:
    """Manages quests and their progression."""
    
    def __init__(self, player: Player, map_system: MapSystem):
        self.player = player
        self.map_system = map_system
        self.quests: Dict[str, Quest] = {}
        self.active_quests: Set[str] = set()
        self.completed_quests: Set[str] = set()
        self.failed_quests: Set[str] = set()
        self.quest_events: List[GameEvent] = []
        self.discovered_lore: Set[str] = set()
        
        # Initialize quests
        self._initialize_quests()
    
    def _initialize_quests(self):
        """Initialize all quests in the game."""
        # Add the Hermit's Wisdom quest (Mystic path)
        hermit_quest = Quest(
            id="hermits_wisdom",
            name="The Hermit's Wisdom",
            description="Seek the ancient knowledge of the Hermit Druid.",
            hidden_description="The Hermit Druid holds secrets about the true nature of the Second Centaur.",
            initial_stage="find_hermit",
            stages={
                "find_hermit": QuestStage(
                    id="find_hermit",
                    description="Find the Hermit Druid in the western woods.",
                    hidden_description="The Hermit Druid is hiding from the Second Centaur's agents.",
                    triggers=[
                        QuestTrigger(
                            type=QuestTriggerType.NPC_DIALOGUE,
                            target="hermit_druid"
                        )
                    ],
                    next_stages=["retrieve_scroll"],
                    hint_dialogue={
                        "fallen_warrior": "I've heard whispers of an old druid who lives to the west. They say he knows things about our past that most have forgotten."
                    }
                ),
                "retrieve_scroll": QuestStage(
                    id="retrieve_scroll",
                    description="The Hermit Druid has asked you to retrieve an ancient scroll from his meditation spot.",
                    hidden_description="The scroll contains a ritual that can weaken the Second Centaur.",
                    triggers=[
                        QuestTrigger(
                            type=QuestTriggerType.ITEM_ACQUIRED,
                            target="ancient_scroll"
                        )
                    ],
                    next_stages=["return_scroll", "study_scroll"],
                    hint_dialogue={
                        "hermit_druid": "My meditation spot lies deeper in the grove. The scroll should still be there, unless... No, I'm sure it's safe."
                    }
                ),
                "study_scroll": QuestStage(
                    id="study_scroll",
                    description="Study the ancient scroll to learn its secrets.",
                    hidden_description="The scroll reveals the location of the Crystal Focus.",
                    triggers=[
                        QuestTrigger(
                            type=QuestTriggerType.ITEM_USED,
                            target="ancient_scroll"
                        )
                    ],
                    next_stages=["find_crystal"],
                    world_changes=[
                        {"type": "reveal_item", "item_id": "crystal_focus", "location": (3, 4)}
                    ]
                ),
                "return_scroll": QuestStage(
                    id="return_scroll",
                    description="Return the scroll to the Hermit Druid.",
                    hidden_description="The Hermit will reveal more about your quest if you return the scroll.",
                    triggers=[
                        QuestTrigger(
                            type=QuestTriggerType.ITEM_GIVEN,
                            target="ancient_scroll",
                            condition="recipient=hermit_druid"
                        )
                    ],
                    next_stages=["find_crystal"],
                    rewards=["hermit_blessing"],
                    hint_dialogue={
                        "hermit_druid": "You've found it! Now, let me show you what it means..."
                    }
                ),
                "find_crystal": QuestStage(
                    id="find_crystal",
                    description="Find the Crystal Focus in the Mystic Mountains.",
                    hidden_description="The Crystal Focus is needed to see through the Second Centaur's illusions.",
                    triggers=[
                        QuestTrigger(
                            type=QuestTriggerType.ITEM_ACQUIRED,
                            target="crystal_focus"
                        )
                    ],
                    next_stages=["crystal_caves"],
                    hint_dialogue={
                        "hermit_druid": "The Crystal Focus lies in the mountains to the north and west. It will reveal paths hidden to the naked eye."
                    }
                ),
                "crystal_caves": QuestStage(
                    id="crystal_caves",
                    description="Use the Crystal Focus to enter the Crystal Caves.",
                    hidden_description="The Crystal Caves contain the essence needed to challenge the Second Centaur.",
                    triggers=[
                        QuestTrigger(
                            type=QuestTriggerType.AREA_VISITED,
                            target="crystal_caves"
                        )
                    ],
                    next_stages=["defeat_guardian"],
                    world_changes=[
                        {"type": "unlock_area", "area": "crystal_caves"}
                    ]
                ),
                "defeat_guardian": QuestStage(
                    id="defeat_guardian",
                    description="Defeat the Crystal Guardian to obtain its essence.",
                    hidden_description="The Guardian's essence contains the power of the original centaur lords.",
                    triggers=[
                        QuestTrigger(
                            type=QuestTriggerType.ENEMY_DEFEATED,
                            target="crystal_guardian"
                        )
                    ],
                    next_stages=["complete_mystic_path"],
                    rewards=["guardian_essence"],
                    hint_dialogue={
                        "hermit_druid": "The Guardian will not yield easily, but its essence is crucial for your journey."
                    }
                ),
                "complete_mystic_path": QuestStage(
                    id="complete_mystic_path",
                    description="Use the knowledge and power you've gathered to confront the Second Centaur.",
                    hidden_description="The Mystic Path allows you to counter the Second Centaur's magical abilities.",
                    triggers=[
                        QuestTrigger(
                            type=QuestTriggerType.AREA_VISITED,
                            target="shadow_domain"
                        )
                    ],
                    next_stages=[],  # End of quest
                    world_changes=[
                        {"type": "unlock_area", "area": "shadow_domain"}
                    ]
                )
            },
            discovery_triggers=[
                QuestTrigger(
                    type=QuestTriggerType.AREA_VISITED,
                    target="awakening_woods"
                )
            ],
            related_quests=["warriors_honor", "shadows_embrace"],
            required_items=["ancient_scroll", "crystal_focus", "guardian_essence"],
            affected_npcs=["hermit_druid", "fallen_warrior"],
            lore_entries=["centaur_wars", "crystal_magic", "first_centaur"]
        )
        
        # Add the quest to the system
        self.quests["hermits_wisdom"] = hermit_quest
        
        # Add more quests here...
        # Warrior path quest
        # Stealth path quest
        # Side quests that can affect multiple paths
    
    def check_quest_triggers(self, trigger_type: QuestTriggerType, target: str, **kwargs) -> List[str]:
        """
        Check if any quest triggers are activated.
        Returns a list of messages about quest progression.
        """
        messages = []
        
        # Check for quest discovery triggers
        for quest_id, quest in self.quests.items():
            if quest.status == QuestStatus.HIDDEN:
                for discovery_trigger in quest.discovery_triggers:
                    if discovery_trigger.type == trigger_type and discovery_trigger.target == target:
                        # Check additional conditions if any
                        if discovery_trigger.condition:
                            # Evaluate condition (simplified for now)
                            if not self._evaluate_condition(discovery_trigger.condition, **kwargs):
                                continue
                        
                        # Discover the quest
                        quest.status = QuestStatus.DISCOVERED
                        self.quest_events.append(GameEvent(
                            event_type=EventType.DISCOVERY,
                            description=f"Discovered quest: {quest.name}",
                            location=self.player.get_current_position(),
                            details={"quest_id": quest_id}
                        ))
                        messages.append(f"New quest discovered: {quest.name}")
        
        # Check for quest stage progression
        for quest_id in self.active_quests:
            quest = self.quests.get(quest_id)
            if not quest or not quest.current_stage_id:
                continue
                
            current_stage = quest.get_current_stage()
            if not current_stage:
                continue
                
            for trigger in current_stage.triggers:
                if trigger.type == trigger_type and trigger.target == target:
                    # Check additional conditions if any
                    if trigger.condition:
                        # Evaluate condition (simplified for now)
                        if not self._evaluate_condition(trigger.condition, **kwargs):
                            continue
                    
                    # Advance to next stage (taking first available for now)
                    if current_stage.next_stages:
                        next_stage_id = current_stage.next_stages[0]
                        quest.current_stage_id = next_stage_id
                        next_stage = quest.stages.get(next_stage_id)
                        
                        # Apply rewards
                        for reward in current_stage.rewards:
                            if reward not in self.player.state.inventory:
                                self.player.state.inventory.append(reward)
                                messages.append(f"Received: {reward}")
                        
                        # Apply world changes
                        for change in current_stage.world_changes:
                            self._apply_world_change(change)
                        
                        # Record event
                        self.quest_events.append(GameEvent(
                            event_type=EventType.QUEST,
                            description=f"Advanced quest '{quest.name}' to stage: {next_stage_id}",
                            location=self.player.get_current_position(),
                            details={"quest_id": quest_id, "stage_id": next_stage_id}
                        ))
                        
                        messages.append(f"Quest updated: {quest.name}")
                        if next_stage:
                            messages.append(f"New objective: {next_stage.description}")
                        
                        # Check if this was the final stage
                        if not next_stage or not next_stage.next_stages:
                            quest.status = QuestStatus.COMPLETED
                            self.active_quests.remove(quest_id)
                            self.completed_quests.add(quest_id)
                            messages.append(f"Quest completed: {quest.name}")
        
        return messages
    
    def _evaluate_condition(self, condition: str, **kwargs) -> bool:
        """Evaluate a condition string with given parameters."""
        # Simple condition evaluation for now
        # In a real implementation, this would be more sophisticated
        if "=" in condition:
            key, value = condition.split("=")
            return kwargs.get(key.strip()) == value.strip()
        return False
    
    def _apply_world_change(self, change: Dict[str, Any]):
        """Apply a world change from a quest stage."""
        change_type = change.get("type")
        
        if change_type == "reveal_item":
            # Logic to make an item appear in the world
            item_id = change.get("item_id")
            location = change.get("location")
            if item_id and location:
                # Find the tile at this location and add the item
                if self.player.state.current_tile and tuple(self.player.state.current_tile.position) == tuple(location):
                    if item_id not in self.player.state.current_tile.items:
                        self.player.state.current_tile.items.append(item_id)
        
        elif change_type == "unlock_area":
            # Logic to unlock an area
            area = change.get("area")
            if area:
                # This would need to interact with the map system to unlock the area
                pass
        
        # Add more change types as needed
    
    def start_quest(self, quest_id: str) -> Tuple[bool, str]:
        """Start a quest if it's been discovered."""
        quest = self.quests.get(quest_id)
        if not quest:
            return False, f"Quest {quest_id} does not exist."
            
        if quest.status != QuestStatus.DISCOVERED:
            return False, f"Quest {quest.name} cannot be started right now."
            
        quest.status = QuestStatus.ACTIVE
        quest.current_stage_id = quest.initial_stage
        self.active_quests.add(quest_id)
        
        # Record event
        self.quest_events.append(GameEvent(
            event_type=EventType.QUEST,
            description=f"Started quest: {quest.name}",
            location=self.player.get_current_position(),
            details={"quest_id": quest_id}
        ))
        
        current_stage = quest.get_current_stage()
        if current_stage:
            return True, f"Started quest: {quest.name}\nObjective: {current_stage.description}"
        return True, f"Started quest: {quest.name}"
    
    def get_quest_status(self, quest_id: str) -> Tuple[bool, str]:
        """Get the status of a specific quest."""
        quest = self.quests.get(quest_id)
        if not quest:
            return False, f"Quest {quest_id} does not exist."
            
        if quest.status == QuestStatus.HIDDEN:
            return False, "You haven't discovered this quest yet."
            
        status_text = f"Quest: {quest.name}\nStatus: {quest.status.value}"
        
        if quest.status == QuestStatus.ACTIVE and quest.current_stage_id:
            current_stage = quest.get_current_stage()
            if current_stage:
                status_text += f"\nCurrent objective: {current_stage.description}"
                
        return True, status_text
    
    def get_active_quests(self) -> str:
        """Get a list of all active quests."""
        if not self.active_quests:
            return "You have no active quests."
            
        quest_list = []
        for quest_id in self.active_quests:
            quest = self.quests.get(quest_id)
            if quest and quest.current_stage_id:
                current_stage = quest.get_current_stage()
                if current_stage:
                    quest_list.append(f"- {quest.name}: {current_stage.description}")
                else:
                    quest_list.append(f"- {quest.name}")
        
        return "Active Quests:\n" + "\n".join(quest_list)
    
    def get_completed_quests(self) -> str:
        """Get a list of all completed quests."""
        if not self.completed_quests:
            return "You haven't completed any quests yet."
            
        quest_list = []
        for quest_id in self.completed_quests:
            quest = self.quests.get(quest_id)
            if quest:
                quest_list.append(f"- {quest.name}")
        
        return "Completed Quests:\n" + "\n".join(quest_list)
    
    def get_quest_hint(self, quest_id: str) -> Tuple[bool, str]:
        """Get a hint for the current stage of a quest."""
        quest = self.quests.get(quest_id)
        if not quest:
            return False, f"Quest {quest_id} does not exist."
            
        if quest.status != QuestStatus.ACTIVE or not quest.current_stage_id:
            return False, "This quest is not active."
            
        current_stage = quest.get_current_stage()
        if not current_stage:
            return False, "Cannot find the current stage of this quest."
            
        # Check if there are any NPCs in the current area that might have hints
        if self.player.state.current_tile and self.player.state.current_tile.npcs:
            for npc_id in self.player.state.current_tile.npcs:
                if npc_id in current_stage.hint_dialogue:
                    return True, f"{npc_id.replace('_', ' ').title()}: \"{current_stage.hint_dialogue[npc_id]}\""
        
        # Generic hint if no NPC-specific hints are available
        return True, "You should explore more of the world to find clues."
    
    def get_quest_log(self) -> str:
        """Get a complete log of all quests and their statuses."""
        log = []
        
        # Active quests
        active = self.get_active_quests()
        if active != "You have no active quests.":
            log.append(active)
        
        # Completed quests
        completed = self.get_completed_quests()
        if completed != "You haven't completed any quests yet.":
            log.append(completed)
        
        # Discovered but not started quests
        discovered = []
        for quest_id, quest in self.quests.items():
            if quest.status == QuestStatus.DISCOVERED and quest_id not in self.active_quests:
                discovered.append(f"- {quest.name}")
        
        if discovered:
            log.append("Available Quests:\n" + "\n".join(discovered))
        
        if not log:
            return "Your quest log is empty."
        
        return "\n\n".join(log) 