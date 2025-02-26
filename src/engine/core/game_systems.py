"""
Core game systems for The Last Centaur.

This module implements various game systems including:
- Time progression
- Achievement tracking
- Title system
- Leaderboard functionality
"""

from enum import Enum
from typing import Dict, List, Optional, Set, Tuple, Any
from dataclasses import dataclass, field
import random
from datetime import datetime, timedelta

from .models import PathType

# Forward reference for type hints
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .quest_system import QuestSystem
    from .path_system import PathSystem
    from .discovery_system import DiscoverySystem

class TimeOfDay(str, Enum):
    """Different times of day that affect gameplay."""
    DAWN = "dawn"        # 5:00 - 6:59
    MORNING = "morning"  # 7:00 - 11:59
    NOON = "noon"        # 12:00 - 13:59
    AFTERNOON = "afternoon"  # 14:00 - 16:59
    EVENING = "evening"  # 17:00 - 19:59
    NIGHT = "night"      # 20:00 - 4:59

@dataclass
class GameTime:
    """Tracks the passage of time in the game."""
    days: int = 1
    hours: int = 8  # Start at 8:00 AM
    minutes: int = 0
    total_minutes: int = 0  # For easy time comparisons
    
    def add_minutes(self, minutes: int) -> None:
        """Add minutes to the current time."""
        self.minutes += minutes
        self.total_minutes += minutes
        
        while self.minutes >= 60:
            self.minutes -= 60
            self.hours += 1
        
        while self.hours >= 24:
            self.hours -= 24
            self.days += 1
    
    def get_time_of_day(self) -> TimeOfDay:
        """Get the current time of day."""
        hour = self.hours
        
        if 5 <= hour < 7:
            return TimeOfDay.DAWN
        elif 7 <= hour < 12:
            return TimeOfDay.MORNING
        elif 12 <= hour < 14:
            return TimeOfDay.NOON
        elif 14 <= hour < 17:
            return TimeOfDay.AFTERNOON
        elif 17 <= hour < 20:
            return TimeOfDay.EVENING
        else:
            return TimeOfDay.NIGHT
    
    def get_formatted_time(self) -> str:
        """Get a formatted string of the current time."""
        return f"Day {self.days}, {self.hours:02d}:{self.minutes:02d}"
    
    def get_time_description(self) -> str:
        """Get a descriptive string of the current time of day."""
        time_of_day = self.get_time_of_day()
        
        descriptions = {
            TimeOfDay.DAWN: "The dawn breaks over the horizon, painting the sky in soft hues.",
            TimeOfDay.MORNING: "The morning sun casts long shadows across the land.",
            TimeOfDay.NOON: "The sun reaches its zenith, bathing everything in bright light.",
            TimeOfDay.AFTERNOON: "The afternoon sun warms the air as shadows begin to lengthen.",
            TimeOfDay.EVENING: "The evening light bathes everything in golden hues.",
            TimeOfDay.NIGHT: "The land lies under a blanket of stars."
        }
        
        return descriptions[time_of_day]

class TimeSystem:
    """Manages the passage of time and its effects on the game world."""
    
    def __init__(self, map_system=None):
        self.time = GameTime()
        self.time_triggers: Dict[str, List[int]] = {}  # Events that occur at specific times
        self.day_count: int = 1
        self.last_rest_time: int = 0
        self.map_system = map_system  # Store reference to map system
    
    def advance_time(self, minutes: int) -> Dict[str, str]:
        """
        Advance time and return any triggered events.
        
        Args:
            minutes: Number of minutes to advance
            
        Returns:
            Dict of event descriptions that occurred during time advancement
        """
        old_time_of_day = self.time.get_time_of_day()
        self.time.add_minutes(minutes)
        new_time_of_day = self.time.get_time_of_day()
        
        events = {}
        
        # Check for time of day changes
        if old_time_of_day != new_time_of_day:
            events["time_change"] = f"The {new_time_of_day.value} arrives. {self.time.get_time_description()}"
            # Update map system with new time
            if self.map_system:
                self.map_system.update_time(new_time_of_day.value)
        
        # Check for day changes
        if self.time.days > self.day_count:
            self.day_count = self.time.days
            events["day_change"] = f"A new day dawns. Day {self.day_count} begins."
        
        return events
    
    def can_rest(self) -> Tuple[bool, str]:
        """Check if enough time has passed since last rest."""
        minutes_since_rest = self.time.total_minutes - self.last_rest_time
        if minutes_since_rest < 30:  # Must wait 30 minutes between rests
            return False, f"Must wait {30 - minutes_since_rest} more minutes to rest again."
        return True, ""
    
    def rest(self) -> Tuple[bool, str]:
        """Attempt to rest and recover stamina."""
        can_rest, message = self.can_rest()
        if not can_rest:
            return False, message
            
        self.last_rest_time = self.time.total_minutes
        self.advance_time(20)  # Resting takes 20 minutes
        return True, "You rest for 20 minutes."
    
    def get_time_multipliers(self) -> Dict[str, float]:
        """Get current time-based multipliers for various game mechanics."""
        time_of_day = self.time.get_time_of_day()
        
        multipliers = {
            "stealth": 1.0,
            "combat": 1.0,
            "stamina_recovery": 1.0,
            "magic": 1.0
        }
        
        # Adjust multipliers based on time of day
        if time_of_day == TimeOfDay.NIGHT:
            multipliers["stealth"] = 1.5  # Easier to sneak at night
            multipliers["magic"] = 1.2    # Magic is stronger at night
            multipliers["stamina_recovery"] = 0.8  # Harder to recover at night
        elif time_of_day == TimeOfDay.DAWN:
            multipliers["magic"] = 1.3     # Magic is stronger at dawn
            multipliers["combat"] = 1.2    # Warriors are stronger at dawn
        elif time_of_day == TimeOfDay.NOON:
            multipliers["stamina_recovery"] = 1.2  # Best recovery at noon
            multipliers["stealth"] = 0.8   # Harder to hide in bright light
        
        return multipliers 

@dataclass
class Achievement:
    """Represents an achievement that can be earned by players."""
    id: str
    name: str
    description: str
    points: int
    
    def __str__(self) -> str:
        return f"{self.name} ({self.points} points): {self.description}"

class AchievementSystem:
    """Manages achievements for the game."""
    
    def __init__(self):
        """Initialize the achievement system."""
        self.achievements: Dict[str, Achievement] = {}
        self.player_achievements: Dict[str, Set[str]] = {}  # player_id -> set of achievement_ids
        self.title_system = None
        self.unlocked_achievements = set()  # Add this for test compatibility
    
    def register_title_system(self, title_system):
        """Register the title system for achievement notifications."""
        self.title_system = title_system
    
    def register_achievement(self, achievement_id: str, name: str, description: str, points: int) -> None:
        """
        Register a new achievement.
        
        Args:
            achievement_id: Unique identifier for the achievement
            name: Display name of the achievement
            description: Description of how to earn the achievement
            points: Points awarded for earning the achievement
        """
        self.achievements[achievement_id] = Achievement(achievement_id, name, description, points)
    
    def award_achievement(self, player_id: str, achievement_id: str) -> Tuple[bool, Optional[Achievement]]:
        """
        Award an achievement to a player.
        
        Args:
            player_id: ID of the player
            achievement_id: ID of the achievement to award
            
        Returns:
            Tuple of (success, achievement if awarded)
        """
        if achievement_id not in self.achievements:
            return False, None
        
        if player_id not in self.player_achievements:
            self.player_achievements[player_id] = set()
        
        if achievement_id in self.player_achievements[player_id]:
            return False, None
        
        self.player_achievements[player_id].add(achievement_id)
        achievement = self.achievements[achievement_id]
        
        # Notify title system of new achievement
        if self.title_system:
            self.title_system.check_titles(player_id, self.player_achievements[player_id])
        
        return True, achievement
    
    def get_player_achievements(self, player_id: str) -> List[Achievement]:
        """
        Get all achievements earned by a player.
        
        Args:
            player_id: ID of the player
            
        Returns:
            List of earned achievements
        """
        if player_id not in self.player_achievements:
            return []
        
        return [self.achievements[aid] for aid in self.player_achievements[player_id]]
    
    def get_player_achievement_points(self, player_id: str) -> int:
        """
        Get the total achievement points earned by a player.
        
        Args:
            player_id: ID of the player
            
        Returns:
            Total achievement points
        """
        achievements = self.get_player_achievements(player_id)
        return sum(a.points for a in achievements)
    
    def get_achievement(self, achievement_id: str) -> Optional[Achievement]:
        """
        Get an achievement by ID.
        
        Args:
            achievement_id: ID of the achievement
            
        Returns:
            Achievement if found, None otherwise
        """
        return self.achievements.get(achievement_id)
    
    def get_all_achievements(self) -> List[Achievement]:
        """
        Get all registered achievements.
        
        Returns:
            List of all achievements
        """
        return list(self.achievements.values())
    
    def has_achievement(self, player_id: str, achievement_id: str) -> bool:
        """
        Check if a player has earned an achievement.
        
        Args:
            player_id: ID of the player
            achievement_id: ID of the achievement
            
        Returns:
            True if the player has earned the achievement, False otherwise
        """
        if player_id not in self.player_achievements:
            return False
        
        return achievement_id in self.player_achievements[player_id]
    
    def unlock_achievement(self, achievement_id: str) -> bool:
        """
        Unlock an achievement for testing purposes.
        
        Args:
            achievement_id: ID of the achievement to unlock
            
        Returns:
            True if successful, False otherwise
        """
        if achievement_id in self.achievements:
            self.unlocked_achievements.add(achievement_id)
            return True
        return False
        
    def check_combat_achievement(self, player_id: str, enemy_type: str) -> Tuple[bool, Optional[str]]:
        """
        Check if a combat-related achievement should be awarded.
        
        Args:
            player_id: ID of the player
            enemy_type: Type of enemy defeated
            
        Returns:
            Tuple of (awarded, achievement_id if awarded)
        """
        return False, None

@dataclass
class Title:
    """Represents a title that can be earned by players."""
    id: str
    name: str
    required_achievements: List[str]
    
    def __str__(self) -> str:
        return self.name

class TitleSystem:
    """Manages titles for the game."""
    
    def __init__(self):
        """Initialize the title system."""
        self.titles: Dict[str, Title] = {}
        self.player_titles: Dict[str, Set[str]] = {}  # player_id -> set of title_ids
        self.player_active_title: Dict[str, str] = {}  # player_id -> active title_id
        self.equipped_title = None  # Currently equipped title ID for single-player mode
        self.unlocked_titles = set()  # Set of unlocked title IDs for single-player mode
    
    def register_title(self, title_id: str, name: str, required_achievements: List[str]) -> None:
        """
        Register a new title.
        
        Args:
            title_id: Unique identifier for the title
            name: Display name of the title
            required_achievements: List of achievement IDs required to earn the title
        """
        self.titles[title_id] = Title(title_id, name, required_achievements)
    
    def check_titles(self, player_id: str, player_achievements: Set[str]) -> List[Title]:
        """
        Check if a player has earned any new titles.
        
        Args:
            player_id: ID of the player
            player_achievements: Set of achievement IDs earned by the player
            
        Returns:
            List of newly earned titles
        """
        if player_id not in self.player_titles:
            self.player_titles[player_id] = set()
        
        newly_earned = []
        
        for title_id, title in self.titles.items():
            if title_id in self.player_titles[player_id]:
                continue
            
            if all(aid in player_achievements for aid in title.required_achievements):
                self.player_titles[player_id].add(title_id)
                newly_earned.append(title)
                
                # If this is the player's first title, make it active
                if player_id not in self.player_active_title:
                    self.player_active_title[player_id] = title_id
        
        return newly_earned
    
    def set_active_title(self, player_id: str, title_id: str) -> bool:
        """
        Set a player's active title.
        
        Args:
            player_id: ID of the player
            title_id: ID of the title to set as active
            
        Returns:
            True if successful, False otherwise
        """
        if player_id not in self.player_titles or title_id not in self.player_titles[player_id]:
            return False
        
        self.player_active_title[player_id] = title_id
        
        # For single-player mode compatibility, also update equipped_title
        self.equipped_title = title_id
        
        return True
    
    def get_active_title(self, player_id: str) -> Optional[Title]:
        """
        Get a player's active title.
        
        Args:
            player_id: ID of the player
            
        Returns:
            Active title if set, None otherwise
        """
        if player_id not in self.player_active_title:
            return None
        
        title_id = self.player_active_title[player_id]
        return self.titles.get(title_id)
    
    def get_player_titles(self, player_id: str) -> List[Title]:
        """
        Get all titles earned by a player.
        
        Args:
            player_id: ID of the player
            
        Returns:
            List of earned titles
        """
        if player_id not in self.player_titles:
            return []
        
        return [self.titles[tid] for tid in self.player_titles[player_id]]
    
    def get_title(self, title_id: str) -> Optional[Title]:
        """
        Get a title by ID.
        
        Args:
            title_id: ID of the title
            
        Returns:
            Title if found, None otherwise
        """
        return self.titles.get(title_id)
    
    def get_all_titles(self) -> List[Title]:
        """
        Get all registered titles.
        
        Returns:
            List of all titles
        """
        return list(self.titles.values())
    
    def has_title(self, player_id: str, title_id: str) -> bool:
        """
        Check if a player has earned a title.
        
        Args:
            player_id: ID of the player
            title_id: ID of the title
            
        Returns:
            True if the player has earned the title, False otherwise
        """
        if player_id not in self.player_titles:
            return False
        
        return title_id in self.player_titles[player_id]
    
    def get_title_status(self, player_id: str) -> str:
        """
        Get a formatted string of the player's title status.
        
        Args:
            player_id: ID of the player
            
        Returns:
            Formatted string of title status
        """
        titles = self.get_player_titles(player_id)
        if not titles:
            return "No titles unlocked yet"
            
        active_title = self.get_active_title(player_id)
        active_title_str = f"Active title: {active_title.name}" if active_title else "No active title"
        
        title_list = "\n".join([f"- {title.name}" for title in titles])
        return f"{active_title_str}\n\nUnlocked titles:\n{title_list}"
    
    def unlock_title(self, title_id: str) -> str:
        """
        Unlock a specific title for the player.
        
        Args:
            title_id: The ID of the title to unlock
            
        Returns:
            A message about the title being unlocked
        """
        if title_id not in self.titles:
            return f"Title '{title_id}' does not exist."
            
        # For test compatibility, use the equipped_title attribute
        if not hasattr(self, 'player_titles'):
            self.player_titles = {}
            
        # Use a default player_id for backward compatibility
        player_id = "default_player"
        
        if player_id not in self.player_titles:
            self.player_titles[player_id] = set()
            
        # Add the title to the player's titles
        self.player_titles[player_id].add(title_id)
        
        # Also add to unlocked_titles for single-player mode
        self.unlocked_titles.add(title_id)
        
        # If this is the player's first title, make it active
        if player_id not in self.player_active_title:
            self.player_active_title[player_id] = title_id
            self.equipped_title = title_id  # Also update equipped_title
            
        title = self.titles[title_id]
        return f"You have earned the title: {title.name}!"

@dataclass
class LeaderboardEntry:
    """Represents a single leaderboard entry."""
    player_id: str
    player_name: str
    completion_time: str
    achievements: int
    path_type: str
    date: datetime = field(default_factory=datetime.now)

class LeaderboardSystem:
    """Manages the game's leaderboard system."""
    
    _instance = None
    _initialized = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(LeaderboardSystem, cls).__new__(cls)
        return cls._instance
    
    def __init__(self, db_pool=None):
        if not LeaderboardSystem._initialized:
            self.entries: List[LeaderboardEntry] = []
            self.path_types = ["warrior", "mystic", "stealth"]
            self.player_entries: Dict[str, List[LeaderboardEntry]] = {}  # Track entries by player_id
            self.db_pool = db_pool
            LeaderboardSystem._initialized = True
    
    def clear(self) -> None:
        """Clear all entries from the leaderboard. Used for testing."""
        self.entries = []
        self.player_entries = {}
    
    def add_entry(self, entry: LeaderboardEntry) -> None:
        """Add a new entry to the leaderboard."""
        # Validate path type
        if entry.path_type.lower() not in [p.lower() for p in self.path_types]:
            raise ValueError(f"Invalid path type: {entry.path_type}")
            
        # Normalize path type to lowercase
        entry.path_type = entry.path_type.lower()
        
        # Ensure achievements count is an integer
        entry.achievements = int(entry.achievements)
        
        # Update existing entry if it has more achievements
        if entry.player_id in self.player_entries:
            existing_entries = self.player_entries[entry.player_id]
            for existing in existing_entries:
                if existing.achievements < entry.achievements:
                    # Remove the old entry with fewer achievements
                    self.entries.remove(existing)
                    existing_entries.remove(existing)
                    break
        
        self.entries.append(entry)
        
        # Track entry by player_id
        if entry.player_id not in self.player_entries:
            self.player_entries[entry.player_id] = []
        self.player_entries[entry.player_id].append(entry)
        
        # Sort entries by completion time
        self.entries.sort(key=lambda e: datetime.strptime(e.completion_time, "Day %d, %H:%M"))
    
    def get_player_entries(self, player_id: str) -> List[LeaderboardEntry]:
        """Get all entries for a specific player."""
        return self.player_entries.get(player_id, [])
    
    def get_player_best_time(self, player_id: str, path_type: Optional[str] = None) -> Optional[str]:
        """Get a player's best completion time, optionally filtered by path type."""
        entries = self.player_entries.get(player_id, [])
        if path_type:
            entries = [e for e in entries if e.path_type == path_type]
        
        if not entries:
            return None
            
        return min(entries, key=lambda e: e.completion_time).completion_time
    
    def get_player_ranking(self, player_id: str, category: str = "fastest") -> Optional[int]:
        """
        Get a player's ranking in a specific category.
        
        Args:
            player_id: The player's ID
            category: The ranking category (fastest, achievements)
            
        Returns:
            The player's rank (1-based) or None if not ranked
        """
        if not self.entries:
            return None
            
        if category == "achievements":
            # Sort by achievements in descending order
            sorted_entries = sorted(
                self.entries,
                key=lambda x: (x.achievements, -x.date.timestamp()),
                reverse=True
            )
        else:  # fastest completion
            # Sort by completion time (days, hours, minutes)
            sorted_entries = sorted(
                self.entries,
                key=lambda x: (
                    int(x.completion_time.split(",")[0].split()[1]),  # Days
                    int(x.completion_time.split(",")[1].strip().split(":")[0]),  # Hours
                    int(x.completion_time.split(",")[1].strip().split(":")[1])  # Minutes
                )
            )
        
        # Find player's position
        for i, entry in enumerate(sorted_entries, 1):
            if entry.player_id == player_id:
                return i
        
        return None
    
    def get_leaderboard(self, category: Optional[str] = None) -> str:
        """
        Get the leaderboard for a specific category.
        
        Args:
            category: Optional category to filter by (fastest, achievements, or path type)
            
        Returns:
            Formatted leaderboard string
        """
        if not self.entries:
            return "No entries yet"
            
        if category == "fastest":
            # Sort by completion time
            sorted_entries = sorted(self.entries, 
                                 key=lambda e: datetime.strptime(e.completion_time, "Day %d, %H:%M"))
            header = "Fastest Completions"
            entries = [
                f"{i+1}. {e.player_name} - {e.completion_time}"
                for i, e in enumerate(sorted_entries[:10])
            ]
            
        elif category == "achievements":
            # Get the latest entry for each player
            player_entries = {}
            for entry in self.entries:
                if entry.player_id not in player_entries or \
                   entry.achievements > player_entries[entry.player_id].achievements:
                    player_entries[entry.player_id] = entry
            
            # Sort by achievement count
            sorted_entries = sorted(
                player_entries.values(),
                key=lambda e: (e.achievements, -e.date.timestamp()),
                reverse=True
            )
            
            header = "Most Achievements"
            entries = [
                f"{i+1}. {e.player_name} - {e.achievements} achievements"
                for i, e in enumerate(sorted_entries[:10])
            ]
            
        elif category in self.path_types:
            # Filter by path type and sort by completion time
            path_entries = [e for e in self.entries if e.path_type.lower() == category.lower()]
            if not path_entries:
                return f"{category.title()} Path Rankings\nNo entries yet"
                
            sorted_entries = sorted(path_entries, 
                                 key=lambda e: datetime.strptime(e.completion_time, "Day %d, %H:%M"))
            header = f"{category.title()} Path Rankings"
            entries = [
                f"{i+1}. {e.player_name} - {e.completion_time}"
                for i, e in enumerate(sorted_entries[:10])
            ]
            
        else:
            # Default to overall rankings
            sorted_entries = sorted(self.entries, 
                                 key=lambda e: datetime.strptime(e.completion_time, "Day %d, %H:%M"))
            header = "Overall Rankings"
            entries = [
                f"{i+1}. {e.player_name} - {e.completion_time} ({e.path_type})"
                for i, e in enumerate(sorted_entries[:10])
            ]
        
        if not entries:
            return f"{header}\nNo entries yet"
            
        return f"{header}\n\n" + "\n".join(entries)
    
    def get_path_records(self, path_type: str) -> Dict[str, str]:
        """Get the records for a specific path type."""
        path_entries = [e for e in self.entries if e.path_type == path_type]
        if not path_entries:
            return {}
            
        fastest = min(path_entries, key=lambda e: e.completion_time)
        most_achievements = max(path_entries, key=lambda e: e.achievements)
        
        return {
            "fastest_time": f"{fastest.player_name} - {fastest.completion_time}",
            "most_achievements": f"{most_achievements.player_name} - {most_achievements.achievements} achievements"
        }
    
    def get_global_stats(self) -> Dict[str, Any]:
        """Get global leaderboard statistics."""
        if not self.entries:
            return {
                "total_entries": 0,
                "total_players": 0,
                "path_distribution": {}
            }
            
        unique_players = len(set(e.player_id for e in self.entries))
        path_counts = {}
        for path in self.path_types:
            path_counts[path] = len([e for e in self.entries if e.path_type == path])
            
        return {
            "total_entries": len(self.entries),
            "total_players": unique_players,
            "path_distribution": path_counts,
            "average_achievements": sum(e.achievements for e in self.entries) / len(self.entries)
        } 

class GameSystems:
    """Core game systems for The Last Centaur."""
    
    def __init__(self, db_pool=None):
        """Initialize game systems."""
        self.game_time = GameTime()
        self.achievement_system = AchievementSystem()
        self.title_system = TitleSystem()
        self.leaderboard = LeaderboardSystem(db_pool)
        
        # Import here to avoid circular imports
        from .quest_system import QuestSystem
        from .path_system import PathSystem
        from .discovery_system import DiscoverySystem
        
        self.quest_system = QuestSystem()
        self.path_system = PathSystem(self.quest_system)
        self.discovery_system = DiscoverySystem()
        
        # Register other systems with each other as needed
        self.achievement_system.register_title_system(self.title_system)
        
        # Initialize systems
        self._initialize_systems()
        
        # Add resource depletion tracking
        self.resource_depletion = {
            "hunger": 0.0,  # 0.0-1.0, affects stamina regen
            "fatigue": 0.0,  # 0.0-1.0, affects health regen
            "mental_strain": 0.0,  # 0.0-1.0, affects mana regen
            "last_meal_time": 0,  # Game time when last ate
            "last_rest_time": 0,  # Game time when last rested properly
            "last_meditation_time": 0  # Game time when last meditated
        }
    
    def _initialize_systems(self):
        """Initialize all game systems."""
        self._initialize_achievements()
        self._initialize_titles()
        # Initialize other systems as needed
    
    def _initialize_achievements(self):
        """Initialize the achievement system with predefined achievements."""
        # Path-specific achievements
        self.achievement_system.register_achievement(
            "warrior_path_chosen",
            "Path of the Warrior",
            "Choose the Warrior path",
            10
        )
        self.achievement_system.register_achievement(
            "stealth_path_chosen",
            "Path of Shadows",
            "Choose the Stealth path",
            10
        )
        self.achievement_system.register_achievement(
            "mystic_path_chosen",
            "Path of Wisdom",
            "Choose the Mystic path",
            10
        )
        
        # Warrior achievements
        self.achievement_system.register_achievement(
            "warrior_honorable_victory",
            "Honorable Victory",
            "Defeat an enemy in honorable combat",
            15
        )
        self.achievement_system.register_achievement(
            "warrior_champion",
            "Champion",
            "Reach level 5 on the Warrior path",
            30
        )
        
        # Stealth achievements
        self.achievement_system.register_achievement(
            "stealth_unseen",
            "Unseen",
            "Complete an area without being detected",
            20
        )
        self.achievement_system.register_achievement(
            "stealth_shadow_master",
            "Shadow Master",
            "Reach level 5 on the Stealth path",
            30
        )
        
        # Mystic achievements
        self.achievement_system.register_achievement(
            "mystic_spell_master",
            "Spell Master",
            "Learn 5 different spells",
            25
        )
        self.achievement_system.register_achievement(
            "mystic_enlightened",
            "Enlightened",
            "Reach level 5 on the Mystic path",
            30
        )
        
        # General achievements
        self.achievement_system.register_achievement(
            "explorer",
            "Explorer",
            "Discover 10 different locations",
            20
        )
        self.achievement_system.register_achievement(
            "collector",
            "Collector",
            "Collect 15 different items",
            25
        )
        self.achievement_system.register_achievement(
            "quest_master",
            "Quest Master",
            "Complete 5 quests",
            30
        )
    
    def _initialize_titles(self):
        """Initialize the title system with predefined titles."""
        # Path-specific titles
        self.title_system.register_title(
            "warrior_novice",
            "Warrior Novice",
            ["warrior_path_chosen"]
        )
        self.title_system.register_title(
            "warrior_adept",
            "Warrior Adept",
            ["warrior_path_chosen", "warrior_honorable_victory"]
        )
        self.title_system.register_title(
            "warrior_master",
            "Warrior Master",
            ["warrior_path_chosen", "warrior_champion"]
        )
        
        self.title_system.register_title(
            "stealth_novice",
            "Shadow Novice",
            ["stealth_path_chosen"]
        )
        self.title_system.register_title(
            "stealth_adept",
            "Shadow Adept",
            ["stealth_path_chosen", "stealth_unseen"]
        )
        self.title_system.register_title(
            "stealth_master",
            "Shadow Master",
            ["stealth_path_chosen", "stealth_shadow_master"]
        )
        
        self.title_system.register_title(
            "mystic_novice",
            "Mystic Novice",
            ["mystic_path_chosen"]
        )
        self.title_system.register_title(
            "mystic_adept",
            "Mystic Adept",
            ["mystic_path_chosen", "mystic_spell_master"]
        )
        self.title_system.register_title(
            "mystic_master",
            "Mystic Master",
            ["mystic_path_chosen", "mystic_enlightened"]
        )
        
        # General titles
        self.title_system.register_title(
            "adventurer",
            "Adventurer",
            ["explorer"]
        )
        self.title_system.register_title(
            "treasure_hunter",
            "Treasure Hunter",
            ["collector"]
        )
        self.title_system.register_title(
            "hero",
            "Hero",
            ["quest_master"]
        )
        
        # Special titles requiring multiple achievements
        self.title_system.register_title(
            "champion_of_the_realm",
            "Champion of the Realm",
            ["warrior_champion", "explorer", "quest_master"]
        )
        self.title_system.register_title(
            "master_of_shadows",
            "Master of Shadows",
            ["stealth_shadow_master", "stealth_unseen", "quest_master"]
        )
        self.title_system.register_title(
            "archmage",
            "Archmage",
            ["mystic_enlightened", "mystic_spell_master", "quest_master"]
        )
        
        # Legendary title
        self.title_system.register_title(
            "the_last_centaur",
            "The Last Centaur",
            ["warrior_champion", "stealth_shadow_master", "mystic_enlightened", "explorer", "collector", "quest_master"]
        )
    
    def select_path(self, player_id: str, path_type: PathType) -> str:
        """
        Select a path for the player.
        
        Args:
            player_id: The ID of the player
            path_type: The path to select
            
        Returns:
            A message describing the path selection
        """
        return self.path_system.select_path(path_type)
    
    def get_path_description(self, path_type: PathType) -> str:
        """
        Get a description of a path.
        
        Args:
            path_type: The path to describe
            
        Returns:
            A description of the path
        """
        return self.path_system.get_path_description(path_type)
    
    def get_path_progress(self, path_type: Optional[PathType] = None) -> str:
        """
        Get a description of the player's progress along a path.
        
        Args:
            path_type: The path to check, or None for the selected path
            
        Returns:
            A description of the player's progress
        """
        return self.path_system.get_path_progress(path_type)
    
    def record_combat_action(self, action_type: str, target_type: str, success: bool) -> None:
        """
        Record a combat action to update path affinities.
        
        Args:
            action_type: The type of action (attack, defend, etc.)
            target_type: The type of target (enemy, environment, etc.)
            success: Whether the action was successful
        """
        self.path_system.record_combat_action(action_type, target_type, success)
    
    def record_exploration_action(self, action_type: str, area_type: str) -> None:
        """
        Record an exploration action to update path affinities.
        
        Args:
            action_type: The type of action (search, examine, etc.)
            area_type: The type of area being explored
        """
        self.path_system.record_exploration_action(action_type, area_type)
    
    def record_dialogue_choice(self, npc_id: str, choice_type: str) -> None:
        """
        Record a dialogue choice to update path affinities.
        
        Args:
            npc_id: The ID of the NPC being talked to
            choice_type: The type of dialogue choice made
        """
        self.path_system.record_dialogue_choice(npc_id, choice_type)
    
    def get_suggested_path(self) -> Tuple[PathType, str]:
        """
        Get the path with the highest affinity and a description.
        
        Returns:
            Tuple of (path type, description)
        """
        return self.path_system.get_suggested_path()
    
    def gain_path_experience(self, amount: int) -> Tuple[int, List[str]]:
        """
        Gain experience for the selected path.
        
        Args:
            amount: The amount of experience to gain
            
        Returns:
            Tuple of (levels gained, newly unlocked abilities)
        """
        return self.path_system.gain_path_experience(amount)
    
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
        return self.path_system.calculate_damage(base_damage, weapon_damage, **kwargs)
    
    def can_use_ability(self, ability_id: str, **kwargs) -> Tuple[bool, str]:
        """
        Check if the player can use an ability.
        
        Args:
            ability_id: The ID of the ability to check
            **kwargs: Additional arguments for specific path checks
            
        Returns:
            Tuple of (can use ability, reason if cannot)
        """
        return self.path_system.can_use_ability(ability_id, **kwargs)
    
    def use_ability(self, ability_id: str, **kwargs) -> Tuple[bool, str, Dict[str, Any]]:
        """
        Use an ability.
        
        Args:
            ability_id: The ID of the ability to use
            **kwargs: Additional arguments for specific abilities
            
        Returns:
            Tuple of (success, message, effects)
        """
        return self.path_system.use_ability(ability_id, **kwargs)
    
    def update_stealth_state(self, **kwargs) -> None:
        """
        Update the player's stealth state.
        
        Args:
            **kwargs: Arguments for stealth state update
        """
        self.path_system.update_stealth_state(**kwargs)
    
    def update_meditation_state(self, **kwargs) -> Tuple[float, bool]:
        """
        Update the player's meditation state.
        
        Args:
            **kwargs: Arguments for meditation state update
            
        Returns:
            Tuple of (mana restored, whether gained insight)
        """
        return self.path_system.update_meditation_state(**kwargs)
    
    def get_path_status(self) -> Dict[str, Any]:
        """
        Get the status of all paths.
        
        Returns:
            Dictionary with path status information
        """
        return self.path_system.get_path_status()
    
    def update_resource_depletion(self, minutes_passed: int) -> Dict[str, str]:
        """Update resource depletion based on time passed and return status messages."""
        messages = {}
        
        # Increase hunger over time (faster during physical activity)
        base_hunger_rate = 0.01 * (minutes_passed / 60)  # Base rate per hour
        if hasattr(self, 'last_combat_time') and (self.game_time.total_minutes - self.last_combat_time) < 30:
            # Combat in the last 30 minutes increases hunger
            base_hunger_rate *= 1.5
        
        self.resource_depletion["hunger"] = min(1.0, self.resource_depletion["hunger"] + base_hunger_rate)
        
        # Increase fatigue over time (faster during night or combat)
        base_fatigue_rate = 0.005 * (minutes_passed / 60)  # Base rate per hour
        if self.game_time.get_time_of_day() == TimeOfDay.NIGHT:
            base_fatigue_rate *= 1.3  # Fatigue increases faster at night
        if hasattr(self, 'last_combat_time') and (self.game_time.total_minutes - self.last_combat_time) < 30:
            base_fatigue_rate *= 2.0  # Combat greatly increases fatigue
            
        self.resource_depletion["fatigue"] = min(1.0, self.resource_depletion["fatigue"] + base_fatigue_rate)
        
        # Increase mental strain over time (faster when using abilities)
        base_strain_rate = 0.003 * (minutes_passed / 60)  # Base rate per hour
        if hasattr(self, 'last_ability_time') and (self.game_time.total_minutes - self.last_ability_time) < 30:
            base_strain_rate *= 1.8  # Using abilities increases mental strain
            
        self.resource_depletion["mental_strain"] = min(1.0, self.resource_depletion["mental_strain"] + base_strain_rate)
        
        # Generate messages based on depletion levels
        if self.resource_depletion["hunger"] > 0.7 and self.resource_depletion["hunger"] <= 0.85:
            messages["hunger"] = "Your stomach growls. You should find food soon."
        elif self.resource_depletion["hunger"] > 0.85:
            messages["hunger"] = "You're starving. Your stamina regeneration is severely reduced."
            
        if self.resource_depletion["fatigue"] > 0.7 and self.resource_depletion["fatigue"] <= 0.85:
            messages["fatigue"] = "You feel tired. Rest would do you good."
        elif self.resource_depletion["fatigue"] > 0.85:
            messages["fatigue"] = "Exhaustion weighs on you. Your health regeneration is severely reduced."
            
        if self.resource_depletion["mental_strain"] > 0.7 and self.resource_depletion["mental_strain"] <= 0.85:
            messages["mental_strain"] = "Your mind feels foggy. Meditation would help clear it."
        elif self.resource_depletion["mental_strain"] > 0.85:
            messages["mental_strain"] = "Mental fatigue clouds your thoughts. Your mana regeneration is severely reduced."
            
        return messages
    
    def consume_food(self, food_item: str) -> Tuple[bool, str]:
        """Consume food to reduce hunger."""
        # Check if the item is actually food
        food_items = {
            "ration": {"hunger_reduction": 0.3, "description": "A basic travel ration."},
            "fresh_fruit": {"hunger_reduction": 0.2, "description": "Sweet and refreshing."},
            "cooked_meat": {"hunger_reduction": 0.5, "description": "Hearty and filling."},
            "mystic_herb": {"hunger_reduction": 0.1, "mental_strain_reduction": 0.2, "description": "A rare herb with restorative properties."},
            "warrior_brew": {"hunger_reduction": 0.2, "stamina_boost": 20, "description": "A strong drink favored by warriors."},
            "shadow_berry": {"hunger_reduction": 0.2, "stealth_boost": 0.1, "description": "A dark berry that helps you blend with shadows."}
        }
        
        if food_item not in food_items:
            return False, f"{food_item} is not edible."
        
        food_data = food_items[food_item]
        self.resource_depletion["hunger"] = max(0.0, self.resource_depletion["hunger"] - food_data["hunger_reduction"])
        self.resource_depletion["last_meal_time"] = self.game_time.total_minutes
        
        result_message = f"You consume the {food_item}. {food_data['description']}"
        
        # Apply additional effects
        if "mental_strain_reduction" in food_data:
            self.resource_depletion["mental_strain"] = max(0.0, self.resource_depletion["mental_strain"] - food_data["mental_strain_reduction"])
            result_message += " You feel your mind clearing."
            
        if "stamina_boost" in food_data:
            # This would need to be passed to the player object
            result_message += " You feel a surge of energy."
            
        if "stealth_boost" in food_data:
            # This would need to be passed to the stealth state
            result_message += " You feel more attuned to the shadows."
            
        return True, result_message
    
    def get_resource_penalties(self) -> Dict[str, float]:
        """Get penalties to resource regeneration based on depletion levels."""
        penalties = {
            "health_regen": 1.0,
            "stamina_regen": 1.0,
            "mana_regen": 1.0
        }
        
        # Apply hunger penalty to stamina regeneration
        if self.resource_depletion["hunger"] > 0.5:
            # Linear penalty from 0% at 0.5 hunger to 90% at 1.0 hunger
            hunger_penalty = min(0.9, (self.resource_depletion["hunger"] - 0.5) * 1.8)
            penalties["stamina_regen"] *= (1.0 - hunger_penalty)
            
        # Apply fatigue penalty to health regeneration
        if self.resource_depletion["fatigue"] > 0.5:
            # Linear penalty from 0% at 0.5 fatigue to 80% at 1.0 fatigue
            fatigue_penalty = min(0.8, (self.resource_depletion["fatigue"] - 0.5) * 1.6)
            penalties["health_regen"] *= (1.0 - fatigue_penalty)
            
        # Apply mental strain penalty to mana regeneration
        if self.resource_depletion["mental_strain"] > 0.5:
            # Linear penalty from 0% at 0.5 strain to 85% at 1.0 strain
            strain_penalty = min(0.85, (self.resource_depletion["mental_strain"] - 0.5) * 1.7)
            penalties["mana_regen"] *= (1.0 - strain_penalty)
            
        return penalties 
    
    def process_environmental_interaction(self, player: Any, interaction_type: str, 
                                        interaction_text: str) -> Tuple[str, Optional[Dict[str, Any]]]:
        """
        Process a player's interaction with the environment.
        
        Args:
            player: The player object
            interaction_type: The type of interaction (examine, touch, etc.)
            interaction_text: The text describing the interaction
            
        Returns:
            Tuple of (response text, optional effects)
        """
        return self.discovery_system.process_interaction(player, interaction_type, interaction_text)
    
    def enhance_tile_description(self, tile: Any) -> str:
        """
        Enhance a tile's description with environmental changes.
        
        Args:
            tile: The tile to enhance
            
        Returns:
            Enhanced description
        """
        return self.discovery_system.enhance_tile_description(tile)
    
    def get_discovery_stats(self) -> Dict[str, Any]:
        """
        Get statistics about discoveries.
        
        Returns:
            Dictionary with discovery statistics
        """
        return self.discovery_system.get_discovery_stats() 