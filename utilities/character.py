"""
Character and Stats Management for Our Legacy
Centralized Character class and related logic
"""

import json
import uuid
from typing import Dict, List, Any, Optional

class Character:
    """Player character class"""

    def __init__(self,
                 name: str,
                 character_class: str,
                 classes_data: Optional[Dict] = None,
                 player_uuid: Optional[str] = None,
                 lang: Optional[Any] = None):
        self.name = name
        self.character_class = character_class
        self.uuid = player_uuid or str(uuid.uuid4())

        if lang is None:
            class MockLangCharacterAttr:
                def get(self, key, default=None, **kwargs):
                    return key
            self.lang = MockLangCharacterAttr()
        else:
            self.lang = lang

        # Rank system based on level
        self.rank = "F tier adventurer"
        self.level = 1
        self.experience = 0
        self.experience_to_next = 100
        self.class_data = {}
        self.level_up_bonuses = {}

        # Load class data if provided
        if classes_data and character_class in classes_data:
            self.class_data = classes_data[character_class]
            stats = self.class_data.get("base_stats", {})
            self.level_up_bonuses = self.class_data.get("level_up_bonuses", {})
        else:
            # Fallback defaults
            default_stats = {
                "hp": 100,
                "mp": 50,
                "attack": 10,
                "defense": 8,
                "speed": 10
            }
            stats = default_stats

        self.max_hp = stats.get("hp", 100)
        self.hp = self.max_hp
        self.max_mp = stats.get("mp", 50)
        self.mp = self.max_mp
        self.attack = stats.get("attack", 10)
        self.defense = stats.get("defense", 8)
        self.speed = stats.get("speed", 10)
        self.defending = False

        # Equipment slots
        self.equipment: Dict[str, Optional[str]] = {
            "weapon": None,
            "armor": None,
            "offhand": None,
            "accessory_1": None,
            "accessory_2": None,
            "accessory_3": None
        }

        # Legacy compatibility slots
        self.weapon = None
        self.armor = None
        self.offhand = None
        self.accessory = None

        # Inventory and gold
        self.inventory = []
        self.gold = 100
        self.companions: List[Dict[str, Any]] = []
        self.active_buffs: List[Dict[str, Any]] = []
        self.bosses_killed: Dict[str, str] = {}
        
        # Housing and Building
        self.housing_owned: List[str] = []
        self.comfort_points: int = 0
        self.building_slots: Dict[str, Optional[str]] = {
            "house_1": None, "house_2": None, "house_3": None,
            "decoration_1": None, "decoration_2": None, "decoration_3": None,
            "decoration_4": None, "decoration_5": None, "decoration_6": None,
            "decoration_7": None, "decoration_8": None, "decoration_9": None,
            "decoration_10": None, "fencing_1": None, "garden_1": None,
            "garden_2": None, "garden_3": None, "farm_1": None, "farm_2": None,
            "training_place_1": None, "training_place_2": None, "training_place_3": None,
        }
        self.farm_plots: Dict[str, List[Dict[str, Any]]] = {
            "farm_1": [],
            "farm_2": [],
        }

        # Time and Weather
        self.day = 1
        self.hour = 8.0
        self.max_hours = 24
        self.current_area = "starting_village"
        self.current_weather = "sunny"
        self.weather_data = {}
        self.times_data = {}

        # Stats tracking
        self.base_max_hp = self.max_hp
        self.base_max_mp = self.max_mp
        self.base_attack = self.attack
        self.base_defense = self.defense
        self.base_speed = self.speed

        self.active_pet: Optional[str] = None
        self.pets_owned: List[str] = []
        self.pets_data: Dict[str, Any] = {}
        self._load_pets_data()
        self._sync_equipment_slots()

    def _sync_equipment_slots(self):
        """Sync legacy equipment slots for compatibility"""
        self.weapon = self.equipment.get("weapon")
        self.armor = self.equipment.get("armor")
        self.accessory = self.equipment.get("accessory_1")
        self.offhand = self.equipment.get("offhand")

    def _update_equipment_slots(self):
        """Update legacy equipment slots when equipment dictionary changes"""
        self.weapon = self.equipment.get("weapon")
        self.armor = self.equipment.get("armor")
        self.accessory = self.equipment.get("accessory_1")
        self.offhand = self.equipment.get("offhand")

    def _load_pets_data(self):
        """Load pet data from data/pets.json"""
        try:
            with open('data/pets.json', 'r', encoding='utf-8') as f:
                self.pets_data = json.load(f)
        except Exception:
            self.pets_data = {}

    def get_pet_boost(self, stat: str) -> float:
        """Get the current pet's boost for a given stat, scaled by land comfort."""
        if not self.active_pet or self.active_pet not in self.pets_data:
            return 0.0

        pet = self.pets_data[self.active_pet]
        boosts = pet.get('boosts', {})
        base_boost = boosts.get(stat, 0.0)
        comfort_multiplier = 1.0 + (self.comfort_points / 1000.0)
        return base_boost * comfort_multiplier

    def is_alive(self) -> bool:
        """Check if character is alive"""
        return self.hp > 0

    def take_damage(self, damage: int) -> int:
        """Apply damage to character, return actual damage taken"""
        base_damage = max(1, damage - self.get_effective_defense())
        remaining = base_damage

        for b in list(self.active_buffs):
            mods = b.get('modifiers', {})
            if remaining <= 0:
                break
            if 'absorb_amount' in mods and mods.get('absorb_amount', 0) > 0:
                avail = mods.get('absorb_amount', 0)
                use = min(avail, remaining)
                remaining -= use
                mods['absorb_amount'] = avail - use
                if all((not isinstance(v, (int, float)) or v == 0) for v in mods.values()):
                    try:
                        self.active_buffs.remove(b)
                    except ValueError:
                        pass

        damage_taken = max(0, remaining)
        self.hp = max(0, self.hp - damage_taken)
        return damage_taken

    def heal(self, amount: int):
        """Heal character"""
        self.hp = min(self.max_hp, self.hp + amount)

    def gain_experience(self, exp: int):
        """Gain experience and level up if needed"""
        self.experience += exp
        while self.experience >= self.experience_to_next:
            self.level_up()

    def level_up(self):
        """Level up the character"""
        self.level += 1
        self.experience -= self.experience_to_next
        self.experience_to_next = int(self.experience_to_next * 1.5)

        if self.level_up_bonuses:
            self.max_hp += self.level_up_bonuses.get("hp", 0)
            self.max_mp += self.level_up_bonuses.get("mp", 0)
            self.attack += self.level_up_bonuses.get("attack", 0)
            self.defense += self.level_up_bonuses.get("defense", 0)
            self.speed += self.level_up_bonuses.get("speed", 0)
        self.hp = self.max_hp
        self._update_rank()

    def _update_rank(self):
        """Simple rank tiers based on level"""
        if self.level >= 100: self.rank = "SSR tier adventurer"
        elif self.level >= 90: self.rank = "SR tier adventurer"
        elif self.level >= 80: self.rank = "SSS tier adventurer"
        elif self.level >= 70: self.rank = "SS tier adventurer"
        elif self.level >= 50: self.rank = "S tier adventurer"
        elif self.level >= 30: self.rank = "A tier adventurer"
        elif self.level >= 20: self.rank = "B tier adventurer"
        elif self.level >= 15: self.rank = "C tier adventurer"
        elif self.level >= 10: self.rank = "D tier adventurer"
        elif self.level >= 5: self.rank = "E tier adventurer"
        else: self.rank = "F tier adventurer"

    def get_time_period(self) -> str:
        """Get current time period"""
        if not self.times_data:
            return "unknown"
        for period, data in self.times_data.items():
            if data['start_hour'] <= self.hour <= data['end_hour']:
                return period
        return "unknown"

    def get_time_description(self, language_manager: Any) -> str:
        """Get translated time description"""
        period = self.get_time_period()
        if period == "unknown":
            return "The passage of time is strange here..."
        period_data = self.times_data.get(period, {})
        return language_manager.get(period_data.get("description", ""))

    def get_weather_description(self, language_manager: Any) -> str:
        """Get translated weather description"""
        weather_info = self.weather_data.get(self.current_weather, {})
        desc_key = weather_info.get("description", f"weather_{self.current_weather}_desc")
        is_night = self.hour < 6 or self.hour >= 18
        if is_night:
            night_desc_key = f"{desc_key}_night"
            description = language_manager.get(night_desc_key)
            if description != night_desc_key:
                return description
        return language_manager.get(desc_key, self.current_weather.capitalize())

    def advance_time(self, minutes: float = 10.0):
        """Advance game time"""
        game_minutes = minutes / 2.0
        self.hour += game_minutes / 60.0
        while self.hour >= 24:
            self.hour -= 24
            self.day += 1

    def get_effective_attack(self) -> int:
        """Calculate attack with all bonuses"""
        bonus = sum(b.get('modifiers', {}).get('attack_bonus', 0) for b in self.active_buffs)
        pet_boost = self.get_pet_boost('attack')
        return int((self.attack + bonus) * (1.0 + pet_boost))

    def get_effective_defense(self) -> int:
        """Calculate defense with all bonuses"""
        bonus = sum(b.get('modifiers', {}).get('defense_bonus', 0) for b in self.active_buffs)
        pet_boost = self.get_pet_boost('defense')
        base_def = (self.defense + bonus) * (1.0 + pet_boost)
        return int(base_def * 1.5) if self.defending else int(base_def)

    def get_effective_speed(self) -> int:
        """Calculate speed with all bonuses"""
        bonus = sum(b.get('modifiers', {}).get('speed_bonus', 0) for b in self.active_buffs)
        pet_boost = self.get_pet_boost('speed')
        return int((self.speed + bonus) * (1.0 + pet_boost))
