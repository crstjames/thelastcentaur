"""
Core game systems for The Last Centaur.

This module implements various game systems including:
- Time progression
- Achievement tracking
- Title system
- Leaderboard functionality
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Set, Tuple, Any

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

class AchievementType(str, Enum):
    """Types of achievements that can be unlocked."""
    EXPLORATION = "exploration"  # Map exploration achievements
    COMBAT = "combat"           # Combat-related achievements
    STORY = "story"            # Story progression achievements
    HIDDEN = "hidden"          # Secret achievements
    CHALLENGE = "challenge"    # Special challenge achievements

@dataclass
class Achievement:
    """Represents a single achievement that can be unlocked."""
    id: str
    name: str
    description: str
    type: AchievementType
    hidden: bool = False
    unlocked: bool = False
    unlock_date: Optional[datetime] = None

class AchievementSystem:
    """Manages the tracking and unlocking of achievements."""
    
    _instance = None
    _initialized = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(AchievementSystem, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not AchievementSystem._initialized:
            self.achievements: Dict[str, Achievement] = {
                "first_steps": Achievement(
                    id="first_steps",
                    name="First Steps",
                    description="Explore your first new area",
                    type=AchievementType.EXPLORATION
                ),
                "first_blood": Achievement(
                    id="first_blood",
                    name="First Blood",
                    description="Win your first combat encounter",
                    type=AchievementType.COMBAT
                ),
                "just_five_more": Achievement(
                    id="just_five_more",
                    name="Just Five More Minutes...",
                    description="???",  # Hidden achievement description
                    type=AchievementType.HIDDEN,
                    hidden=True
                ),
                # Add more achievements to reach 50 total
                "explorer": Achievement(
                    id="explorer",
                    name="Explorer",
                    description="Discover 10 new areas",
                    type=AchievementType.EXPLORATION
                ),
                "master_explorer": Achievement(
                    id="master_explorer",
                    name="Master Explorer",
                    description="Discover all areas",
                    type=AchievementType.EXPLORATION
                ),
                "warrior": Achievement(
                    id="warrior",
                    name="Warrior",
                    description="Win 10 combat encounters",
                    type=AchievementType.COMBAT
                ),
                "master_warrior": Achievement(
                    id="master_warrior",
                    name="Master Warrior",
                    description="Win 50 combat encounters",
                    type=AchievementType.COMBAT
                ),
                "survivor": Achievement(
                    id="survivor",
                    name="Survivor",
                    description="Survive for 7 days",
                    type=AchievementType.CHALLENGE
                ),
                "master_survivor": Achievement(
                    id="master_survivor",
                    name="Master Survivor",
                    description="Survive for 30 days",
                    type=AchievementType.CHALLENGE
                ),
                "collector": Achievement(
                    id="collector",
                    name="Collector",
                    description="Collect 10 unique items",
                    type=AchievementType.CHALLENGE
                ),
                "master_collector": Achievement(
                    id="master_collector",
                    name="Master Collector",
                    description="Collect all items",
                    type=AchievementType.CHALLENGE
                ),
                "storyteller": Achievement(
                    id="storyteller",
                    name="Storyteller",
                    description="Complete 10 story events",
                    type=AchievementType.STORY
                ),
                "master_storyteller": Achievement(
                    id="master_storyteller",
                    name="Master Storyteller",
                    description="Complete all story events",
                    type=AchievementType.STORY
                ),
                "night_owl": Achievement(
                    id="night_owl",
                    name="Night Owl",
                    description="???",
                    type=AchievementType.HIDDEN,
                    hidden=True
                ),
                "early_bird": Achievement(
                    id="early_bird",
                    name="Early Bird",
                    description="???",
                    type=AchievementType.HIDDEN,
                    hidden=True
                ),
                # ... Add more achievements to reach 50 total
            }
            self.total_achievements = 50  # Set total achievements to 50
            self.unlocked_achievements: Set[str] = set()
            AchievementSystem._initialized = True
    
    def unlock_achievement(self, achievement_id: str) -> Optional[str]:
        """
        Attempt to unlock an achievement.
        
        Args:
            achievement_id: The ID of the achievement to unlock
            
        Returns:
            Achievement notification message if newly unlocked, None if already unlocked
        """
        if achievement_id not in self.achievements:
            return None
            
        achievement = self.achievements[achievement_id]
        if achievement.unlocked:
            return None
            
        achievement.unlocked = True
        achievement.unlock_date = datetime.now()
        self.unlocked_achievements.add(achievement_id)
        
        return f"Achievement Unlocked: {achievement.name}!"
    
    def check_exploration_achievement(self, area_name: str) -> Optional[str]:
        """Check and award exploration-based achievements."""
        if not self.unlocked_achievements:  # First area explored
            return self.unlock_achievement("first_steps")
        return None
    
    def check_combat_achievement(self, enemy_name: str, victory: bool) -> Optional[str]:
        """Check and award combat-based achievements."""
        if victory and "first_blood" not in self.unlocked_achievements:
            return self.unlock_achievement("first_blood")
        return None
    
    def check_rest_achievement(self, rest_count: int) -> Optional[str]:
        """Check and award rest-based achievements."""
        if rest_count >= 10 and "just_five_more" not in self.unlocked_achievements:
            return self.unlock_achievement("just_five_more")
        return None
    
    def get_achievement_status(self) -> str:
        """Get a formatted string of achievement progress."""
        unlocked = len(self.unlocked_achievements)
        status = f"Achievements ({unlocked}/{self.total_achievements})\n\n"
        
        for achievement in self.achievements.values():
            if achievement.unlocked or not achievement.hidden:
                name = achievement.name
                desc = achievement.description if not achievement.hidden or achievement.unlocked else "???"
                unlocked_str = "✓" if achievement.unlocked else " "
                status += f"[{unlocked_str}] {name}: {desc}\n"
        
        return status.strip() 

class TitleType(str, Enum):
    """Types of titles that can be unlocked."""
    SPEED = "speed"       # Speed-related titles
    COMBAT = "combat"     # Combat-related titles
    STORY = "story"       # Story progression titles
    CHALLENGE = "challenge"  # Special challenge titles

@dataclass
class Title:
    """Represents a title that can be unlocked."""
    id: str
    name: str
    description: str
    type: TitleType
    unlocked: bool = False
    unlock_date: Optional[datetime] = None

class TitleSystem:
    """Manages the unlocking and selection of titles."""
    
    def __init__(self):
        self.titles: Dict[str, Title] = {
            "the_swift": Title(
                id="the_swift",
                name="The Swift",
                description="Complete the game in under 2 days",
                type=TitleType.SPEED
            ),
            "the_warrior": Title(
                id="the_warrior",
                name="The Warrior",
                description="Win 100 combat encounters",
                type=TitleType.COMBAT
            ),
            "the_survivor": Title(
                id="the_survivor",
                name="The Survivor",
                description="Survive for 100 days",
                type=TitleType.CHALLENGE
            ),
            "the_legend": Title(
                id="the_legend",
                name="The Legend",
                description="Complete all achievements",
                type=TitleType.CHALLENGE
            )
        }
        self.unlocked_titles: Set[str] = set()
        self.equipped_title: Optional[str] = None
    
    def unlock_title(self, title_id: str) -> Optional[str]:
        """
        Attempt to unlock a title.
        
        Args:
            title_id: The ID of the title to unlock
            
        Returns:
            Title notification message if newly unlocked, None if already unlocked
        """
        if title_id not in self.titles:
            return None
            
        title = self.titles[title_id]
        if title.unlocked:
            return None
            
        title.unlocked = True
        title.unlock_date = datetime.now()
        self.unlocked_titles.add(title_id)
        
        return f"Title Unlocked: {title.name}!"
    
    def equip_title(self, title_id: str) -> Tuple[bool, str]:
        """
        Attempt to equip a title.
        
        Args:
            title_id: The ID of the title to equip
            
        Returns:
            (success, message) tuple
        """
        if title_id not in self.titles:
            return False, f"Title '{title_id}' does not exist."
            
        title = self.titles[title_id]
        if not title.unlocked:
            return False, f"Title '{title.name}' is not unlocked yet."
            
        self.equipped_title = title_id
        return True, f"Title equipped: {title.name}"
    
    def get_title_status(self) -> str:
        """Get a formatted string of title progress."""
        if not self.unlocked_titles:
            return "No titles unlocked yet"
            
        status = []
        if self.equipped_title:
            equipped_title = self.titles[self.equipped_title]
            status.append(f"Current Title: {equipped_title.name}")
            status.append("")
            
        status.append("Available Titles:")
        for title in self.titles.values():
            if title.unlocked:
                equipped = " (Equipped)" if title.id == self.equipped_title else ""
                status.append(f"- {title.name}: {title.description}{equipped}")
                
        return "\n".join(status)
    
    def check_speed_title(self, days: int) -> Optional[str]:
        """Check and award speed-based titles."""
        if days <= 2 and "the_swift" not in self.unlocked_titles:
            return self.unlock_title("the_swift")
        return None
    
    def check_combat_title(self, combat_wins: int) -> Optional[str]:
        """Check and award combat-based titles."""
        if combat_wins >= 100 and "the_warrior" not in self.unlocked_titles:
            return self.unlock_title("the_warrior")
        return None
    
    def check_survival_title(self, days: int) -> Optional[str]:
        """Check and award survival-based titles."""
        if days >= 100 and "the_survivor" not in self.unlocked_titles:
            return self.unlock_title("the_survivor")
        return None
    
    def check_achievement_title(self, achievement_count: int, total_achievements: int) -> Optional[str]:
        """Check and award achievement-based titles."""
        if achievement_count == total_achievements and "the_legend" not in self.unlocked_titles:
            return self.unlock_title("the_legend")
        return None 

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
    
    def __init__(self):
        if not LeaderboardSystem._initialized:
            self.entries: List[LeaderboardEntry] = []
            self.path_types = ["warrior", "mystic", "stealth"]
            self.player_entries: Dict[str, List[LeaderboardEntry]] = {}  # Track entries by player_id
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