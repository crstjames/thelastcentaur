import random
from enum import Enum
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass

class WeatherType(Enum):
    CLEAR = "clear"
    CLOUDY = "cloudy"
    RAIN = "rain"
    STORM = "storm"
    FOG = "fog"
    MAGICAL_STORM = "magical_storm"
    SHADOW_MIST = "shadow_mist"
    BLOOD_MOON = "blood_moon"  # Rare event that empowers enemies

@dataclass
class WeatherEffect:
    name: str
    description: str
    combat_effects: Dict[str, float] = None  # Modifiers to combat stats
    stealth_effects: Dict[str, float] = None  # Modifiers to stealth mechanics
    mystic_effects: Dict[str, float] = None  # Modifiers to mystic abilities
    movement_penalty: float = 0.0  # Reduction in movement speed (0.0-1.0)
    visibility_reduction: float = 0.0  # Reduction in visibility (0.0-1.0)
    resource_drain: Dict[str, float] = None  # Additional resource drain rates
    special_encounters: List[str] = None  # Special encounters that can happen in this weather

class WeatherSystem:
    def __init__(self):
        self.current_weather = WeatherType.CLEAR
        self.weather_duration = 0  # How many more minutes this weather will last
        self.weather_intensity = 0.5  # 0.0-1.0 scale of intensity
        self.weather_effects = self._initialize_weather_effects()
        self.weather_transitions = self._initialize_weather_transitions()
        self.special_weather_chance = 0.05  # 5% chance of special weather per transition
        self.blood_moon_chance = 0.01  # 1% chance of blood moon at night
        self.last_weather_update = 0  # Game time of last update
        
    def _initialize_weather_effects(self) -> Dict[WeatherType, WeatherEffect]:
        """Initialize all possible weather effects."""
        effects = {
            WeatherType.CLEAR: WeatherEffect(
                name="Clear Skies",
                description="The sky is clear, allowing sunlight to illuminate the land.",
                combat_effects={"accuracy": 0.05},
                stealth_effects={"detection_rate": 0.1},  # Harder to hide in clear weather
                mystic_effects={"mana_regen": 0.1},  # Bonus to mana regeneration
                movement_penalty=0.0,
                visibility_reduction=0.0
            ),
            
            WeatherType.CLOUDY: WeatherEffect(
                name="Cloudy Skies",
                description="Clouds cover the sky, casting a gray pall over the land.",
                combat_effects={},
                stealth_effects={"detection_rate": -0.05},  # Slightly easier to hide
                mystic_effects={},
                movement_penalty=0.0,
                visibility_reduction=0.1
            ),
            
            WeatherType.RAIN: WeatherEffect(
                name="Rainfall",
                description="Rain falls steadily, soaking the ground and reducing visibility.",
                combat_effects={"accuracy": -0.1, "fire_damage": -0.2},
                stealth_effects={"detection_rate": -0.15, "sound_detection": -0.2},  # Rain masks sounds
                mystic_effects={"water_spell_power": 0.15, "fire_spell_power": -0.15},
                movement_penalty=0.1,
                visibility_reduction=0.2,
                resource_drain={"stamina": 0.01}  # Slight stamina drain from being wet
            ),
            
            WeatherType.STORM: WeatherEffect(
                name="Thunderstorm",
                description="Lightning flashes and thunder booms as rain pours down heavily.",
                combat_effects={"accuracy": -0.15, "fire_damage": -0.3, "lightning_damage": 0.2},
                stealth_effects={"detection_rate": -0.2, "sound_detection": -0.3},  # Storm masks sounds well
                mystic_effects={"water_spell_power": 0.2, "lightning_spell_power": 0.25, "fire_spell_power": -0.25},
                movement_penalty=0.2,
                visibility_reduction=0.3,
                resource_drain={"stamina": 0.02, "health": 0.01},  # Risk of lightning strikes
                special_encounters=["lightning_strike", "flooded_path"]
            ),
            
            WeatherType.FOG: WeatherEffect(
                name="Dense Fog",
                description="A thick fog blankets the area, making it difficult to see far ahead.",
                combat_effects={"accuracy": -0.2, "critical_chance": -0.1},
                stealth_effects={"detection_rate": -0.25, "visual_detection": -0.4},  # Great for stealth
                mystic_effects={"illusion_power": 0.2},
                movement_penalty=0.15,
                visibility_reduction=0.5,
                special_encounters=["lost_traveler", "ambush"]
            ),
            
            WeatherType.MAGICAL_STORM: WeatherEffect(
                name="Magical Storm",
                description="Arcane energies swirl through the air, causing reality to warp slightly.",
                combat_effects={"magical_resistance": -0.2, "magical_damage": 0.2},
                stealth_effects={"magical_detection": 0.3},  # Hard to hide from magical detection
                mystic_effects={"spell_power": 0.25, "mana_cost": -0.15, "wild_magic_chance": 0.2},
                movement_penalty=0.1,
                visibility_reduction=0.2,
                resource_drain={"mana": 0.03},  # Mana leaks in magical storms
                special_encounters=["mana_surge", "reality_tear", "arcane_creature"]
            ),
            
            WeatherType.SHADOW_MIST: WeatherEffect(
                name="Shadow Mist",
                description="Dark tendrils of mist curl around obstacles, seeming almost alive.",
                combat_effects={"physical_damage": -0.1, "shadow_damage": 0.2},
                stealth_effects={"stealth_bonus": 0.3, "shadow_affinity": 0.2},  # Excellent for stealth
                mystic_effects={"shadow_spell_power": 0.3, "light_spell_power": -0.2},
                movement_penalty=0.15,
                visibility_reduction=0.4,
                resource_drain={"mental_strain": 0.02},  # Shadow mist affects the mind
                special_encounters=["shadow_entity", "lost_memory", "whispers"]
            ),
            
            WeatherType.BLOOD_MOON: WeatherEffect(
                name="Blood Moon",
                description="The moon glows an ominous red, casting crimson light across the land. Ancient powers stir.",
                combat_effects={"enemy_damage": 0.3, "enemy_health": 0.2, "critical_damage": 0.2},
                stealth_effects={"enemy_detection": 0.3},  # Enemies more alert
                mystic_effects={"blood_magic_power": 0.4, "corruption_resistance": -0.2},
                movement_penalty=0.0,
                visibility_reduction=0.0,
                resource_drain={"mental_strain": 0.03},
                special_encounters=["blood_ritual", "ancient_awakening", "corrupted_wildlife"]
            )
        }
        return effects
    
    def _initialize_weather_transitions(self) -> Dict[WeatherType, Dict[WeatherType, float]]:
        """Initialize weather transition probabilities."""
        transitions = {
            WeatherType.CLEAR: {
                WeatherType.CLEAR: 0.7,
                WeatherType.CLOUDY: 0.3
            },
            WeatherType.CLOUDY: {
                WeatherType.CLEAR: 0.3,
                WeatherType.CLOUDY: 0.4,
                WeatherType.RAIN: 0.2,
                WeatherType.FOG: 0.1
            },
            WeatherType.RAIN: {
                WeatherType.CLOUDY: 0.4,
                WeatherType.RAIN: 0.4,
                WeatherType.STORM: 0.2
            },
            WeatherType.STORM: {
                WeatherType.RAIN: 0.6,
                WeatherType.STORM: 0.3,
                WeatherType.CLOUDY: 0.1
            },
            WeatherType.FOG: {
                WeatherType.FOG: 0.4,
                WeatherType.CLOUDY: 0.4,
                WeatherType.CLEAR: 0.2
            },
            WeatherType.MAGICAL_STORM: {
                WeatherType.MAGICAL_STORM: 0.3,
                WeatherType.CLOUDY: 0.3,
                WeatherType.CLEAR: 0.2,
                WeatherType.STORM: 0.2
            },
            WeatherType.SHADOW_MIST: {
                WeatherType.SHADOW_MIST: 0.3,
                WeatherType.FOG: 0.3,
                WeatherType.CLOUDY: 0.3,
                WeatherType.CLEAR: 0.1
            },
            WeatherType.BLOOD_MOON: {
                WeatherType.CLEAR: 0.5,
                WeatherType.CLOUDY: 0.3,
                WeatherType.SHADOW_MIST: 0.2
            }
        }
        return transitions
    
    def update_weather(self, game_time: int, time_of_day: str, area_type: str) -> Tuple[bool, str]:
        """
        Update weather based on time passed and location.
        Returns (weather_changed, description)
        """
        # Skip if not enough time has passed (update every 30 game minutes)
        minutes_passed = game_time - self.last_weather_update
        if minutes_passed < 30 and self.weather_duration > 0:
            self.weather_duration -= minutes_passed
            self.last_weather_update = game_time
            return False, ""
            
        self.last_weather_update = game_time
        
        # Check if current weather should end
        if self.weather_duration <= 0:
            return self._transition_weather(time_of_day, area_type)
        else:
            self.weather_duration -= minutes_passed
            # Occasionally change weather intensity
            if random.random() < 0.2:
                old_intensity = self.weather_intensity
                intensity_change = random.uniform(-0.2, 0.2)
                self.weather_intensity = max(0.1, min(1.0, self.weather_intensity + intensity_change))
                
                if abs(self.weather_intensity - old_intensity) > 0.15:
                    if self.weather_intensity > old_intensity:
                        return True, f"The {self.weather_effects[self.current_weather].name.lower()} intensifies."
                    else:
                        return True, f"The {self.weather_effects[self.current_weather].name.lower()} begins to subside."
            
            return False, ""
    
    def _transition_weather(self, time_of_day: str, area_type: str) -> Tuple[bool, str]:
        """Handle weather transitions based on time of day and area type."""
        old_weather = self.current_weather
        
        # Check for special weather events
        if time_of_day == "NIGHT" and random.random() < self.blood_moon_chance:
            self.current_weather = WeatherType.BLOOD_MOON
            self.weather_duration = random.randint(120, 240)  # 2-4 hours of blood moon
            self.weather_intensity = random.uniform(0.7, 1.0)  # Blood moons are always intense
            return True, "The moon turns blood red, casting an eerie crimson glow across the land. You feel a sense of dread as ancient powers stir."
        
        # Check for area-specific special weather
        if random.random() < self.special_weather_chance:
            if area_type == "MYSTIC" or area_type == "MAGICAL":
                self.current_weather = WeatherType.MAGICAL_STORM
                self.weather_duration = random.randint(60, 180)
                self.weather_intensity = random.uniform(0.5, 0.9)
                return True, "Arcane energies suddenly swirl around you as a magical storm forms. The air crackles with power."
            
            elif area_type == "SHADOW" or area_type == "STEALTH":
                self.current_weather = WeatherType.SHADOW_MIST
                self.weather_duration = random.randint(60, 180)
                self.weather_intensity = random.uniform(0.5, 0.9)
                return True, "Dark tendrils of mist begin to form, curling around obstacles and obscuring your vision. The shadows seem almost alive."
        
        # Normal weather transition based on probabilities
        transitions = self.weather_transitions[self.current_weather]
        weather_options = list(transitions.keys())
        probabilities = list(transitions.values())
        
        # Adjust probabilities based on time of day
        if time_of_day == "NIGHT":
            # More fog and clouds at night
            for i, option in enumerate(weather_options):
                if option == WeatherType.FOG:
                    probabilities[i] *= 1.5
                elif option == WeatherType.CLEAR:
                    probabilities[i] *= 0.7
        elif time_of_day == "DAWN" or time_of_day == "DUSK":
            # More fog at dawn/dusk
            for i, option in enumerate(weather_options):
                if option == WeatherType.FOG:
                    probabilities[i] *= 2.0
        
        # Normalize probabilities
        total = sum(probabilities)
        probabilities = [p/total for p in probabilities]
        
        # Select new weather
        self.current_weather = random.choices(weather_options, probabilities)[0]
        
        # Set duration and intensity
        self.weather_duration = random.randint(60, 240)  # 1-4 hours
        self.weather_intensity = random.uniform(0.3, 0.8)
        
        # Generate description if weather changed
        if old_weather != self.current_weather:
            if self.current_weather == WeatherType.CLEAR:
                return True, "The skies clear, allowing sunlight to illuminate the land."
            elif self.current_weather == WeatherType.CLOUDY:
                return True, "Clouds begin to gather overhead, casting a gray pall over the land."
            elif self.current_weather == WeatherType.RAIN:
                return True, "Rain begins to fall steadily, pattering on leaves and soaking the ground."
            elif self.current_weather == WeatherType.STORM:
                return True, "Dark storm clouds gather as thunder rumbles in the distance. A storm is brewing."
            elif self.current_weather == WeatherType.FOG:
                return True, "A thick fog begins to roll in, reducing visibility and muffling sounds."
        
        return False, ""
    
    def get_current_weather_effects(self) -> Dict[str, float]:
        """Get the effects of the current weather scaled by intensity."""
        if self.current_weather not in self.weather_effects:
            return {}
            
        effect = self.weather_effects[self.current_weather]
        result = {}
        
        # Scale effects by intensity
        if effect.combat_effects:
            for key, value in effect.combat_effects.items():
                result[f"combat_{key}"] = value * self.weather_intensity
                
        if effect.stealth_effects:
            for key, value in effect.stealth_effects.items():
                result[f"stealth_{key}"] = value * self.weather_intensity
                
        if effect.mystic_effects:
            for key, value in effect.mystic_effects.items():
                result[f"mystic_{key}"] = value * self.weather_intensity
                
        result["movement_penalty"] = effect.movement_penalty * self.weather_intensity
        result["visibility_reduction"] = effect.visibility_reduction * self.weather_intensity
        
        if effect.resource_drain:
            for key, value in effect.resource_drain.items():
                result[f"drain_{key}"] = value * self.weather_intensity
                
        return result
    
    def get_weather_description(self) -> str:
        """Get a description of the current weather based on intensity."""
        if self.current_weather not in self.weather_effects:
            return "The weather is unremarkable."
            
        effect = self.weather_effects[self.current_weather]
        
        intensity_desc = ""
        if self.weather_intensity < 0.3:
            intensity_desc = "mild "
        elif self.weather_intensity > 0.7:
            intensity_desc = "intense "
            
        return f"There is {intensity_desc}{effect.description}"
    
    def get_special_encounter(self) -> Optional[str]:
        """Check if a special weather-related encounter should occur."""
        if self.current_weather not in self.weather_effects:
            return None
            
        effect = self.weather_effects[self.current_weather]
        
        if not effect.special_encounters:
            return None
            
        # Chance based on intensity
        encounter_chance = 0.05 * self.weather_intensity
        
        if random.random() < encounter_chance:
            return random.choice(effect.special_encounters)
            
        return None 