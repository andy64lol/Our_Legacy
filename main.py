"""
Our Legacy - Text-Based CLI Fantasy RPG Game
A comprehensive exploration and grinding-driven RPG experience
"""

import json
import os
import random
import sys
import time
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import difflib
import signal
import traceback
import io
from utilities.settings import ModManager as UtilsModManager, get_setting, set_setting, DEFAULT_SETTINGS, get_settings_manager


class ModManager(UtilsModManager):
    """Manages mod loading and data merging"""

    def __init__(self):
        self.mods_dir = "mods"
        self.mods: Dict[str, Dict[str, Any]] = {}
        self.enabled_mods: List[str] = []
        self.settings_manager = get_settings_manager()
        self.settings = self.settings_manager.settings
        self.discover_mods()

    def load_settings(self):
        """Load settings using the global settings manager"""
        self.settings_manager.load_settings()
        self.settings = self.settings_manager.settings

    def save_settings(self):
        """Save settings using the global settings manager"""
        self.settings_manager.save_settings()

    def discover_mods(self):
        """Discover all mods in the mods directory"""
        self.mods = {}
        self.enabled_mods = []

        if not os.path.exists(self.mods_dir):
            return

        for entry in os.listdir(self.mods_dir):
            mod_path = os.path.join(self.mods_dir, entry)
            if os.path.isdir(mod_path):
                mod_json_path = os.path.join(mod_path, "mod.json")
                if os.path.exists(mod_json_path):
                    try:
                        with open(mod_json_path, 'r') as f:
                            mod_data = json.load(f)
                            mod_data['mod_path'] = mod_path
                            mod_data['folder_name'] = entry
                            self.mods[entry] = mod_data
                    except (json.JSONDecodeError, IOError):
                        print(self.lang.get("mod_load_error").format(entry=entry))

    def get_enabled_mods(self) -> List[str]:
        """Get list of enabled mod folder names"""
        if not self.settings.get("mods_enabled", True):
            return []

        disabled = set(self.settings.get("disabled_mods", []))
        return [name for name in self.mods.keys() if name not in disabled]

    def load_mod_data(self, data_type: str) -> Dict[str, Any]:
        """Load and merge data from all enabled mods for a specific data type"""
        merged_data = {}

        for mod_name in self.get_enabled_mods():
            mod = self.mods.get(mod_name)
            if not mod:
                continue

            mod_path = mod.get('mod_path', '')
            file_path = os.path.join(mod_path, data_type)

            if os.path.exists(file_path):
                try:
                    with open(file_path, 'r') as f:
                        mod_data = json.load(f)

                        # Add mod prefix to prevent conflicts
                        for key, value in mod_data.items():
                            # Check if key already exists in base data (for validation only)
                            # We still add it to allow mod-to-mod interaction
                            new_key = f"{mod_name}_{key}" if key in merged_data else key
                            merged_data[new_key] = value

                except (json.JSONDecodeError, IOError) as e:
                    print(
                        f"Warning: Failed to load {data_type} from mod {mod_name}: {e}"
                    )

        return merged_data

    def get_mod_list(self) -> List[Dict[str, Any]]:
        """Get list of all mods with their metadata and status"""
        mods_list = []
        enabled = self.get_enabled_mods()
        disabled = set(self.settings.get("disabled_mods", []))

        for name, mod in self.mods.items():
            mods_list.append({
                'folder_name':
                name,
                'name':
                mod.get('name', name),
                'description':
                mod.get('description', ''),
                'author':
                mod.get('author', 'Unknown'),
                'version':
                mod.get('version', '1.0'),
                'enabled':
                name in enabled and self.settings.get("mods_enabled", True),
                'mod_path':
                mod.get('mod_path', '')
            })

        return mods_list

    def toggle_mod(self, folder_name: str):
        """Toggle a mod's enabled state"""
        disabled = set(self.settings.get("disabled_mods", []))

        if folder_name in disabled:
            disabled.remove(folder_name)
            print(self.lang.get("mod_enabled_msg").format(folder_name=folder_name))
        else:
            disabled.add(folder_name)
            print(self.lang.get("mod_disabled_msg").format(folder_name=folder_name))

        self.settings["disabled_mods"] = list(disabled)
        self.save_settings()

    def toggle_mods_system(self):
        """Toggle the entire mods system on/off"""
        self.settings["mods_enabled"] = not self.settings.get(
            "mods_enabled", True)
        status = "enabled" if self.settings["mods_enabled"] else "disabled"
        print(self.lang.get("mod_system_status_msg").format(status=status))
        self.save_settings()
        return self.settings["mods_enabled"]


# Optional HTTP library for market API
try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    requests = None
    REQUESTS_AVAILABLE = False
    try:
        import urllib.request
        import urllib.parse
    except ImportError:
        pass

# Optional readline for tab-completion (best-effort)
try:
    import readline
except Exception:
    readline = None

# Global color toggle
COLORS_ENABLED = True


class Colors:
    """ANSI color codes for terminal output"""
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'
    GOLD = '\033[93m'
    ORANGE = '\033[38;5;208m'
    PURPLE = '\033[95m'
    DARK_GRAY = '\033[90m'
    LIGHT_GRAY = '\033[37m'
    GRAY = '\033[90m'  # Alias for DARK_GRAY

    # Rarity colors for items
    COMMON = '\033[37m'  # White
    UNCOMMON = '\033[92m'  # Green
    RARE = '\033[94m'  # Blue
    EPIC = '\033[95m'  # Magenta
    LEGENDARY = '\033[93m'  # Gold

    @staticmethod
    def _color(code: str) -> str:
        """Return color code if colors are enabled, otherwise empty string"""
        global COLORS_ENABLED
        if not COLORS_ENABLED:
            return ""
        return code

    @classmethod
    def wrap(cls, text: str, color_code: str) -> str:
        """Wrap text with color code and end with END code"""
        return f"{cls._color(color_code)}{text}{cls._color(cls.END)}"


def clear_screen():
    """Clear the terminal screen in a cross-platform way."""
    time.sleep(1)
    command = 'cls' if os.name == 'nt' else 'clear'
    os.system(command)


def create_progress_bar(current: int,
                        maximum: int,
                        width: int = 20,
                        color: str = Colors.GREEN) -> str:
    """Create a visual progress bar."""
    if maximum <= 0:
        return "[" + " " * width + "]"

    filled_width = int((current / maximum) * width)
    filled = "█" * filled_width
    empty = "░" * (width - filled_width)
    percentage = (current / maximum) * 100

    return f"[{Colors.wrap(filled, color)}{empty}] {percentage:.1f}%"


def create_boss_hp_bar(current: int,
                       maximum: int,
                       width: int = 40,
                       color: str = Colors.RED) -> str:
    """Create a wide, epic visual HP bar for bosses."""
    if maximum <= 0:
        return "[" + " " * width + "]"

    filled_width = int((current / maximum) * width)
    filled = "█" * filled_width
    empty = "░" * (width - filled_width)
    percentage = (current / maximum) * 100

    boss_label = Colors.wrap("BOSS HP", f"{Colors.BOLD}{Colors.RED}")
    bar = f"[{Colors.wrap(filled, color)}{empty}]"
    percent_text = Colors.wrap(f"{percentage:.1f}%", Colors.BOLD)
    return f"{boss_label} {bar} {percent_text} ({current}/{maximum})"


def create_hp_mp_bar(current: int,
                     maximum: int,
                     width: int = 15,
                     color: str = Colors.RED) -> str:
    """Create a visual HP/MP bar."""
    if maximum <= 0:
        return "[" + " " * width + "]"

    filled_width = int((current / maximum) * width)
    filled = "█" * filled_width
    empty = "░" * (width - filled_width)

    return f"[{Colors.wrap(filled, color)}{empty}] {current}/{maximum}"


def create_separator(char: str = "=", length: int = 60) -> str:
    """Create a visual separator line."""
    return char * length


def create_section_header(title: str, char: str = "=", width: int = 60) -> str:
    """Create a decorative section header."""
    padding = (width - len(title) - 2) // 2
    header_text = f"{char * padding} {title} {char * padding}"
    return Colors.wrap(header_text, f"{Colors.CYAN}{Colors.BOLD}")


def loading_indicator(message: str = "Loading"):
    """Display a loading indicator."""
    print(f"\n{Colors.wrap(message, Colors.YELLOW)}", end="", flush=True)
    for i in range(3):
        time.sleep(0.5)
        print(".", end="", flush=True)
    print()


def get_rarity_color(rarity: str) -> str:
    """Get the color for an item rarity."""
    rarity_colors = {
        "common": Colors.COMMON,
        "uncommon": Colors.UNCOMMON,
        "rare": Colors.RARE,
        "epic": Colors.EPIC,
        "legendary": Colors.LEGENDARY
    }
    return rarity_colors.get(rarity.lower(), Colors.WHITE)


def format_item_name(item_name: str, rarity: str = "common") -> str:
    """Format item name with rarity color."""
    color = get_rarity_color(rarity)
    return Colors.wrap(item_name, color)


def ask(prompt: str,
        valid_choices: Optional[List[str]] = None,
        allow_empty: bool = True,
        case_sensitive: bool = False,
        suggest: bool = True) -> str:
    """Prompt the user for input with optional validation and suggestions.

    - `valid_choices`: list of allowed responses (comparison controlled by `case_sensitive`).
    - `allow_empty`: if False, empty input will be rejected.
    - Returns the stripped input string.
    """
    while True:
        try:
            response = input(prompt)
        except EOFError:
            response = ''

        resp = response.strip()

        # Normalize for comparison if case-insensitive
        cmp_resp = resp if case_sensitive else resp.lower()
        # Ensure cmp_choices is always a list[str] for safe membership checks
        cmp_choices: List[str] = []
        if valid_choices:
            cmp_choices = [
                c if case_sensitive else c.lower() for c in valid_choices
            ]

        # Empty handling
        if not resp and allow_empty:
            clear_screen()
            return resp
        if not resp and not allow_empty:
            print(self.lang.get("input_empty_error"))
            continue

        # If no validation requested, accept
        if not valid_choices:
            clear_screen()
            return resp

        # Exact match
        if cmp_choices and cmp_resp in cmp_choices:
            clear_screen()
            return resp

        # If suggestions enabled, show closest matches
        if suggest and cmp_choices:
            close = difflib.get_close_matches(cmp_resp,
                                              cmp_choices,
                                              n=3,
                                              cutoff=0.4)
            if close:
                print(self.lang.get("invalid_input_suggestion").format(suggestions=', '.join(close)))
            else:
                print(
                    f"Invalid input. Allowed choices: {', '.join(cmp_choices)}"
                )
        else:
            # Fallback to showing valid choices if available
            print(
                f"Invalid input. Allowed choices: {', '.join(cmp_choices or [])}"
            )

        # Retry loop


def _make_completer(options: List[str]):
    """Return a simple readline completer for the provided options."""
    if not readline:
        return None

    opts = sorted(options)

    def completer(text, state):
        matches = [o for o in opts if o.startswith(text)]
        try:
            return matches[state]
        except IndexError:
            return None

    return completer


def enable_tab_completion(options: List[str]):
    """Enable tab-completion for a short period (best-effort)."""
    if not readline:
        return None
    completer = _make_completer(options)
    if completer:
        readline.set_completer(completer)
        readline.parse_and_bind('tab: complete')
        return completer
    return None


def disable_tab_completion(prev_completer):
    """Restore previous completer (if any)."""
    if not readline:
        return
    readline.set_completer(prev_completer)


# Market API URL and cooldown (set by Game class when game starts)
game_api = None

# Market API URL and cooldown
MARKET_API_URL = "https://our-legacy.vercel.app/api/market"
MARKET_COOLDOWN_MINUTES = 10


class MarketAPI:
    """API for accessing the Elite Market with 10-minute cooldown"""

    def __init__(self):
        self.cache = None
        self.last_fetch = None
        self.cooldown_minutes = MARKET_COOLDOWN_MINUTES

    def _is_cache_valid(self) -> bool:
        """Check if cache is still valid (within cooldown period)"""
        if not self.last_fetch or not self.cache:
            return False
        elapsed = datetime.now() - self.last_fetch
        return elapsed < timedelta(minutes=self.cooldown_minutes)

    def fetch_market_data(self,
                          force_refresh: bool = False
                          ) -> Optional[Dict[str, Any]]:
        """Fetch market data from the API with caching and cooldown"""
        # Check cache validity
        if not force_refresh and self._is_cache_valid():
            print(f"{Colors.CYAN}{self.lang.get('visiting_market')}{Colors.END}")
            return self.cache

        # Check cooldown
        if self.last_fetch and not self._is_cache_valid():
            remaining = timedelta(minutes=self.cooldown_minutes) - (
                datetime.now() - self.last_fetch)
            mins = int(remaining.total_seconds() // 60)
            secs = int(remaining.total_seconds() % 60)
            print(
                f"{Colors.YELLOW}Merchants have left and the market is closed! Please come back in {mins}m {secs}s{Colors.END}"
            )
            return None

        print(
            f"{Colors.CYAN}Checking if merchants are in the market...{Colors.END}"
        )

        # Try to fetch from API using requests
        if REQUESTS_AVAILABLE and requests is not None:
            try:
                response = requests.get(MARKET_API_URL, timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    self.cache = data
                    self.last_fetch = datetime.now()
                    print(f"{Colors.GREEN}{self.lang.get('market_open_msg')}{Colors.END}")
                    return data
                else:
                    print(
                        f"{Colors.RED}Failed to reach to the market: HTTP {response.status_code}{Colors.END}"
                    )
            except requests.exceptions.RequestException as e:
                print(f"{Colors.RED}{self.lang.get('network_error_msg').format(error=e)}{Colors.END}")
        else:
            # Fallback using urllib
            try:
                import urllib.request
                req = urllib.request.Request(MARKET_API_URL)
                with urllib.request.urlopen(req, timeout=10) as response:
                    data = json.loads(response.read().decode())
                    self.cache = data
                    self.last_fetch = datetime.now()
                    print(f"{Colors.GREEN}Market is open! {Colors.END}")
                    return data
            except Exception as e:
                print(f"{Colors.RED}Network error: {e}{Colors.END}")

        return None

    def get_cooldown_remaining(self) -> Optional[timedelta]:
        """Get remaining cooldown time"""
        if not self.last_fetch:
            return None
        elapsed = datetime.now() - self.last_fetch
        remaining = timedelta(minutes=self.cooldown_minutes) - elapsed
        if remaining.total_seconds() > 0:
            return remaining
        return None

    def get_all_items(self) -> List[Dict[str, Any]]:
        """Get all market items"""
        data = self.fetch_market_data()
        if data and data.get('ok'):
            return data.get('items', [])
        return []

    def filter_items(self,
                     item_type: Optional[str] = None,
                     rarity: Optional[str] = None,
                     class_req: Optional[str] = None,
                     max_price: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get filtered market items"""
        data = self.fetch_market_data()
        if not data or not data.get('ok'):
            return []

        items = data.get('items', [])

        filtered = []
        for item in items:
            if item_type and item.get('type', '').lower() != item_type.lower():
                continue
            if rarity and item.get('rarity', '').lower() != rarity.lower():
                continue
            if class_req:
                req = item.get('requirements') or {}
                if req.get('class', '').lower() != class_req.lower():
                    continue
            if max_price and item.get('marketPrice', 0) > max_price:
                continue
            filtered.append(item)

        return filtered

    def get_items_by_type(self) -> Dict[str, List[Dict[str, Any]]]:
        """Get items grouped by type"""
        data = self.fetch_market_data()
        if data and data.get('ok'):
            return data.get('itemsByType', {})
        return {}


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

        if lang is None:
            # Create a mock lang if None to avoid "get" on None errors
            class MockLang:

                def get(self, key, default=None):
                    return key

            self.lang = MockLang()
        else:
            self.lang = lang
        self.max_hp = stats.get("hp", 100)
        self.hp = self.max_hp
        self.max_mp = stats.get("mp", 50)
        self.mp = self.max_mp
        self.attack = stats.get("attack", 10)
        self.defense = stats.get("defense", 8)
        self.speed = stats.get("speed", 10)
        self.defending = False

        # Equipment slots (legacy compatibility)
        self.weapon = None
        self.armor = None
        self.offhand = None
        # Legacy single accessory points to accessory_1 for compatibility
        self.accessory = None

        # Inventory and gold
        self.inventory = []
        self.gold = 100  # Starting gold
        # Save base stats so equipment bonuses can be recalculated
        self.base_max_hp = self.max_hp
        self.base_max_mp = self.max_mp
        self.base_attack = self.attack
        self.base_defense = self.defense
        self.base_speed = self.speed

        # Equipped items are stored by slot name
        # Support 1 weapon, 1 armor, 1 offhand, 3 accessories, and companions
        self.equipment: Dict[str, Optional[str]] = {
            "weapon": None,
            "armor": None,
            "offhand": None,
            "accessory_1": None,
            "accessory_2": None,
            "accessory_3": None
        }

        # Companions (4 max) - now storing full companion data
        # Each companion is {id, name, equipment: {weapon, armor, accessory}, level}
        self.companions: List[Dict[str, Any]] = []

        self.hour = 8  # Start at 8 AM
        self.day = 1
        self.max_hours = 24
        self.current_area = "starting_village"
        self.current_weather = "sunny"
        self.weather_data = {}
        self.times_data = {}

        # Active temporary buffs/debuffs: list of {name, duration, modifiers}
        # modifiers is a dict like {"attack_bonus": 5, "defense_bonus": 2}
        self.active_buffs: List[Dict[str, Any]] = []

        # Track killed bosses for cooldown: {boss_name: timestamp_str}
        self.bosses_killed: Dict[str, str] = {}

        # Housing system: track owned housing items and comfort points
        self.housing_owned: List[str] = []  # List of housing item IDs owned
        self.comfort_points: int = 0  # Total comfort points from housing

        # Building slots: what's placed in each slot (None if empty)
        # Key format: "house_1", "house_2", "house_3", etc.
        self.building_slots: Dict[str, Optional[str]] = {
            "house_1": None,
            "house_2": None,
            "house_3": None,
            "decoration_1": None,
            "decoration_2": None,
            "decoration_3": None,
            "decoration_4": None,
            "decoration_5": None,
            "decoration_6": None,
            "decoration_7": None,
            "decoration_8": None,
            "decoration_9": None,
            "decoration_10": None,
            "fencing_1": None,
            "garden_1": None,
            "garden_2": None,
            "garden_3": None,
            "farm_1": None,
            "farm_2": None,
            "training_place_1": None,
            "training_place_2": None,
            "training_place_3": None,
        }

        # Farming system: track planted crops and their growth time
        # Format: {farm_slot_id: [{"crop": "wheat", "days_left": 3}, ...]}
        self.farm_plots: Dict[str, List[Dict[str, Any]]] = {
            "farm_1": [],
            "farm_2": [],
        }

        # Sync legacy equipment slots with new system for compatibility
        self._sync_equipment_slots()

    def _sync_equipment_slots(self):
        """Sync legacy equipment slots with new equipment dictionary for compatibility"""
        # This ensures backward compatibility with any code that might use the old slots
        self.weapon = self.equipment.get("weapon")
        self.armor = self.equipment.get("armor")
        # Map legacy single accessory to accessory_1
        self.accessory = self.equipment.get("accessory_1")
        self.offhand = self.equipment.get("offhand")

    def _update_equipment_slots(self):
        """Update legacy equipment slots when equipment dictionary changes"""
        self.weapon = self.equipment.get("weapon")
        self.armor = self.equipment.get("armor")
        self.accessory = self.equipment.get("accessory_1")
        self.offhand = self.equipment.get("offhand")

    def is_alive(self) -> bool:
        """Check if character is alive"""
        return self.hp > 0

    def take_damage(self, damage: int) -> int:
        """Apply damage to character, return actual damage taken"""
        # Use effective defense (includes buffs)
        base_damage = max(1, damage - self.get_effective_defense())

        remaining = base_damage

        # Consume any absorb shields from active buffs first
        for b in list(self.active_buffs):
            mods = b.get('modifiers', {})
            if remaining <= 0:
                break
            if 'absorb_amount' in mods and mods.get('absorb_amount', 0) > 0:
                avail = mods.get('absorb_amount', 0)
                use = min(avail, remaining)
                remaining -= use
                mods['absorb_amount'] = avail - use
                # remove buff if its modifiers are depleted
                if all((not isinstance(v, (int, float)) or v == 0)
                       for v in mods.values()):
                    try:
                        self.active_buffs.remove(b)
                    except ValueError:
                        pass

        # Any remaining damage applies to HP
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

        # Apply stat increases from class data
        if self.level_up_bonuses:
            self.max_hp += self.level_up_bonuses.get("hp", 0)
            self.max_mp += self.level_up_bonuses.get("mp", 0)
            self.attack += self.level_up_bonuses.get("attack", 0)
            self.defense += self.level_up_bonuses.get("defense", 0)
            self.speed += self.level_up_bonuses.get("speed", 0)
        self.hp = self.max_hp

        print(
            f"{Colors.GREEN}{Colors.BOLD}Level Up!{Colors.END} You are now level {self.level}!"
        )
        # Update rank when leveling
        self._update_rank()

    def _update_rank(self):
        """Simple rank tiers based on level"""
        if self.level >= 100:
            self.rank = "SSR tier adventurer"
        elif self.level >= 90:
            self.rank = "SR tier adventurer"
        elif self.level >= 80:
            self.rank = "SSS tier adventurer"
        elif self.level >= 70:
            self.rank = "SS tier adventurer"
        elif self.level >= 50:
            self.rank = "S tier adventurer"
        elif self.level >= 30:
            self.rank = "A tier adventurer"
        elif self.level >= 20:
            self.rank = "B tier adventurer"
        elif self.level >= 15:
            self.rank = "C tier adventurer"
        elif self.level >= 10:
            self.rank = "D tier adventurer"
        elif self.level >= 5:
            self.rank = "E tier adventurer"
        else:
            self.rank = "F tier adventurer"

    def get_time_period(self) -> str:
        """Get the current time period name based on the hour."""
        if not hasattr(self, 'times_data') or not self.times_data:
            return "unknown"
        for period, data in self.times_data.items():
            if data['start_hour'] <= self.hour <= data['end_hour']:
                return period
        return "unknown"

    def get_time_description(self, language_manager: Any) -> str:
        """Get the translated description of the current time."""
        period = self.get_time_period()
        if period == "unknown":
            return "The passage of time is strange here..."

        period_data = self.times_data.get(period, {})
        desc_key = period_data.get("description", "")
        return language_manager.get(desc_key)

    def get_weather_description(self, language_manager: Any) -> str:
        """Get the translated description of the current weather."""
        if not hasattr(self, 'current_weather') or not self.current_weather:
            self.current_weather = "sunny"  # Default

        weather_info = self.weather_data.get(self.current_weather, {})
        desc_key = weather_info.get("description", "")
        return language_manager.get(desc_key)

    def advance_time(self, hours: int = 1):
        """Advance the game time by a number of hours."""
        self.hour += hours
        while self.hour >= self.max_hours:
            self.hour -= self.max_hours
            self.day += 1
            # Randomly change weather each day
            self.update_weather()
            if self.lang:
                new_day_msg = self.lang.get("new_day_begins", day=str(self.day))
                print(f"\n{Colors.wrap(new_day_msg, Colors.YELLOW)}")

    def update_weather(self, area_id: Optional[str] = None):
        """Update weather based on area exclusivity and general availability."""
        if not hasattr(self, 'weather_data') or not self.weather_data:
            return

        target_area = area_id or getattr(self, 'current_area', None)

        # 1. Check if any weather is exclusive to THIS area
        exclusive_weather = None
        for w_id, w_info in self.weather_data.items():
            exclusives = w_info.get("areas_exclusives", [])
            if target_area in exclusives:
                exclusive_weather = w_id
                break

        if exclusive_weather:
            self.current_weather = exclusive_weather
            return

        # 2. Otherwise, pick from weathers that don't have area exclusives
        possible_weathers = []
        for w_id, w_info in self.weather_data.items():
            if not w_info.get("areas_exclusives"):
                possible_weathers.append(w_id)

        if possible_weathers:
            self.current_weather = random.choice(possible_weathers)
        else:
            self.current_weather = "sunny"  # Fallback

    def display_status(self):
        """Display character status and current world info"""
        if not self.lang:
            return

        print(create_section_header(self.lang.get("character_status", "CHARACTER STATUS")))
        print(f"{Colors.wrap(self.lang.get('name_label', 'Name:'), Colors.CYAN)} {self.name}")
        print(f"{Colors.wrap(self.lang.get('class_label', 'Class:'), Colors.CYAN)} {self.character_class}")
        print(f"{Colors.wrap(self.lang.get('level_label', 'Level:'), Colors.CYAN)} {self.level} ({self.rank})")
        
        # Dynamic Time and Day using translation keys
        time_str = self.lang.get("current_time", hour=str(self.hour).zfill(2))
        day_str = self.lang.get("current_day", day=str(self.day))
        print(f"{Colors.wrap(time_str, Colors.YELLOW)} | {Colors.wrap(day_str, Colors.YELLOW)}")
        
        print(f"{Colors.wrap(self.lang.get('hp_label', 'HP:'), Colors.RED)} {create_hp_mp_bar(self.hp, self.max_hp, color=Colors.RED)}")
        print(f"{Colors.wrap(self.lang.get('mp_label', 'MP:'), Colors.BLUE)} {create_hp_mp_bar(self.mp, self.max_mp, color=Colors.BLUE)}")
        print(f"{Colors.wrap(self.lang.get('exp_label', 'EXP:'), Colors.MAGENTA)} {create_progress_bar(self.experience, self.experience_to_next, color=Colors.MAGENTA)}")
        print(f"{Colors.wrap(self.lang.get('gold_label', 'Gold:'), Colors.GOLD)} {self.gold}g")
        
        # Display location and weather
        loc_str = self.lang.get("current_location", area=self.current_area)
        weather_str = self.lang.get(f"weather_{self.current_weather}", self.current_weather.capitalize())
        print(f"{Colors.wrap(loc_str, Colors.CYAN)} | {Colors.wrap(weather_str, Colors.CYAN)}")
        print(create_separator())

    def display_stats(self):
        """Display character statistics"""
        print(
            f"\n{Colors.CYAN}{Colors.BOLD}=== {self.name} - Level {self.level} {self.character_class} ({self.rank}) ==={Colors.END}"
        )
        # HP and MP with visual bars
        hp_bar = create_hp_mp_bar(self.hp,
                                  self.max_hp,
                                  width=20,
                                  color=Colors.RED)
        mp_bar = create_hp_mp_bar(self.mp,
                                  self.max_mp,
                                  width=20,
                                  color=Colors.BLUE)
        exp_bar = create_progress_bar(self.experience,
                                      self.experience_to_next,
                                      width=20,
                                      color=Colors.MAGENTA)

        print(f"HP:  {hp_bar}")
        print(f"MP:  {mp_bar}")
        print(f"Exp: {exp_bar}")

        # Stats with visual indicators
        print(f"\n{create_separator('-', 50)}")
        print(
            f"Attack:  {Colors.YELLOW}{Colors.BOLD}{self.attack}{Colors.END}")
        print(
            f"Defense: {Colors.YELLOW}{Colors.BOLD}{self.defense}{Colors.END}")
        print(f"Speed:   {Colors.YELLOW}{Colors.BOLD}{self.speed}{Colors.END}")
        print(f"Gold:    {Colors.GOLD}{Colors.BOLD}{self.gold}{Colors.END}")

        # Equipped items with better formatting
        print(f"\n{create_separator('-', 50)}")
        print(f"{Colors.CYAN}{Colors.BOLD}EQUIPPED ITEMS:{Colors.END}")
        for slot in ['weapon', 'armor', 'accessory']:
            item_name = self.equipment.get(slot, 'None')
            if item_name != 'None':
                print(f"  {slot.title():<10}: {item_name}")
            else:
                print(
                    f"  {slot.title():<10}: {Colors.DARK_GRAY}None{Colors.END}"
                )

        # Display companions if any
        if self.companions:
            print(f"\n{create_separator('-', 50)}")
            print(
                f"{Colors.CYAN}{Colors.BOLD}COMPANIONS ({len(self.companions)}/4):{Colors.END}"
            )
            for i, companion in enumerate(self.companions, 1):
                if isinstance(companion, dict):
                    comp_name = companion.get('name')
                    comp_level = companion.get('level', 1)
                    print(
                        f"  {i}. {Colors.CYAN}{comp_name}{Colors.END} (Level {comp_level})"
                    )
                else:
                    print(f"  {i}. {Colors.CYAN}{companion}{Colors.END}")

        # Active buffs
        if self.active_buffs:
            print(f"\n{create_separator('-', 50)}")
            print(f"{Colors.CYAN}{Colors.BOLD}ACTIVE BUFFS:{Colors.END}")
            for b in self.active_buffs:
                mods = ', '.join(f"{k}:{v}"
                                 for k, v in b.get('modifiers', {}).items())
                print(
                    f"  - {b.get('name')} ({b.get('duration')} turns): {mods}")

        print(f"{create_separator('=', 50)}")

    def update_stats_from_equipment(
            self,
            items_data: Dict[str, Any],
            companions_data: Optional[Dict[str, Any]] = None):
        """Recalculate stats from base stats plus any equipped item and companion bonuses."""
        # Start from base
        self.max_hp = self.base_max_hp
        self.max_mp = self.base_max_mp
        self.attack = self.base_attack
        self.defense = self.base_defense
        self.speed = self.base_speed

        # Apply bonuses from each equipped item
        for slot in ("weapon", "armor", "accessory"):
            item_name = self.equipment.get(slot)
            if not item_name:
                continue
            item = items_data.get(item_name, {})
            # Common bonus keys
            if item.get("attack_bonus"):
                self.attack += item.get("attack_bonus", 0)
            if item.get("defense_bonus"):
                self.defense += item.get("defense_bonus", 0)
            if item.get("speed_bonus"):
                self.speed += item.get("speed_bonus", 0)
            if item.get("mp_bonus"):
                self.max_mp += item.get("mp_bonus", 0)
            if item.get("defense_penalty"):
                self.defense -= item.get("defense_penalty", 0)
            if item.get("speed_penalty"):
                self.speed -= item.get("speed_penalty", 0)
            if item.get("attack_penalty"):
                self.attack -= item.get("attack_penalty", 0)
            if item.get("hp_bonus"):
                self.max_hp += item.get("hp_bonus", 0)

        # Apply companion bonuses if companions_data is provided
        if companions_data:
            bonuses = self.calculate_companion_bonuses(companions_data)
            self.attack += bonuses["attack"]
            self.defense += bonuses["defense"]
            self.speed += bonuses["speed"]
            self.max_hp += bonuses["max_hp"]
            self.max_mp += bonuses["max_mp"]

        # Clamp current HP/MP to new maxima
        self.hp = min(self.hp, self.max_hp)
        self.mp = min(self.mp, self.max_mp)

    # --- Buff helpers ---
    def get_total_buff_modifiers(self) -> Dict[str, int]:
        """Aggregate modifiers from active buffs"""
        totals = {}
        for b in self.active_buffs:
            for k, v in b.get('modifiers', {}).items():
                totals[k] = totals.get(k, 0) + v
        return totals

    def get_effective_attack(self) -> int:
        mods = self.get_total_buff_modifiers()
        return max(0, self.attack + mods.get('attack_bonus', 0))

    def get_effective_defense(self) -> int:
        mods = self.get_total_buff_modifiers()
        return max(0, self.defense + mods.get('defense_bonus', 0))

    def get_effective_speed(self) -> int:
        mods = self.get_total_buff_modifiers()
        return max(0, self.speed + mods.get('speed_bonus', 0))

    def get_effective_max_hp(self) -> int:
        mods = self.get_total_buff_modifiers()
        return max(1, self.max_hp + mods.get('hp_bonus', 0))

    def get_effective_max_mp(self) -> int:
        mods = self.get_total_buff_modifiers()
        return max(0, self.max_mp + mods.get('mp_bonus', 0))

    def apply_buff(self, name: str, duration: int, modifiers: Dict[str, int]):
        """Add a temporary buff/debuff"""
        self.active_buffs.append({
            "name": name,
            "duration": duration,
            "modifiers": modifiers
        })

    def tick_buffs(self):
        """Reduce buff durations by 1 and expire any that reach 0."""
        changed = False

        # First, apply per-turn modifiers (healing, mp regen, etc.)
        for b in list(self.active_buffs):
            mods = b.get('modifiers', {})
            # MP per turn
            if mods.get('mp_per_turn'):
                try:
                    self.mp = min(self.get_effective_max_mp(),
                                  self.mp + int(mods.get('mp_per_turn', 0)))
                except Exception:
                    pass
            # Heal per turn
            if mods.get('heal_per_turn'):
                try:
                    self.heal(int(mods.get('heal_per_turn', 0)))
                except Exception:
                    pass

        # Then reduce duration and remove expired buffs
        for b in list(self.active_buffs):
            b['duration'] -= 1
            if b['duration'] <= 0:
                try:
                    self.active_buffs.remove(b)
                except ValueError:
                    pass
                changed = True

        return changed

    def equip(self, item_name: str, items_data: Dict[str, Any]) -> bool:
        """Attempt to equip `item_name`. Returns True if equipped."""
        item = items_data.get(item_name)
        if not item:
            return False
        item_type = item.get("type")
        if item_type not in ("weapon", "armor", "accessory", "offhand"):
            return False

        # Check requirements (simple level/class checks)
        reqs = item.get("requirements", {})
        if reqs.get("level") and self.level < reqs.get("level", 0):
            return False
        if reqs.get("class") and reqs.get("class") != self.character_class:
            return False

        # Determine which slot to use
        if item_type == "accessory":
            # Find first available accessory slot
            for i in range(1, 4):
                slot = f"accessory_{i}"
                if self.equipment[slot] is None:
                    self.equipment[slot] = item_name
                    self._update_equipment_slots()
                    self.update_stats_from_equipment(items_data)
                    return True
            # If all slots full, ask which one to replace
            if self.lang is None:
                # Create a mock lang if None to avoid "get" on None errors
                class MockLang:

                    def get(self, key, default=None):
                        return key

                self.lang = MockLang()

            print(self.lang.get("all_accessory_slots_full"))
            for i in range(1, 4):
                slot = f"accessory_{i}"
                equipped = self.equipment[slot]
                print(f"{i}. Slot {i}: {equipped}")
            choice = input(
                "Enter slot (1-3) or press Enter to cancel: ").strip()
            if choice in ('1', '2', '3'):
                slot = f"accessory_{choice}"
                self.equipment[slot] = item_name
                self._update_equipment_slots()
                self.update_stats_from_equipment(items_data)
                return True
            return False
        else:
            # For weapon, armor, and offhand - single slot each
            self.equipment[item_type] = item_name
            self._update_equipment_slots()
            self.update_stats_from_equipment(items_data)
            return True

    def unequip(self, slot: str, items_data: Dict[str, Any]) -> Optional[str]:
        """Unequip an item from `slot`. Returns the item name if removed."""
        valid_slots = ("weapon", "armor", "offhand", "accessory_1",
                       "accessory_2", "accessory_3")
        if slot not in valid_slots:
            return None
        prev = self.equipment.get(slot)
        self.equipment[slot] = None
        self._update_equipment_slots()
        self.update_stats_from_equipment(items_data)
        return prev

    def calculate_companion_bonuses(
            self, companions_data: Dict[str, Any]) -> Dict[str, int]:
        """Calculate stat bonuses from all active companions."""
        bonuses = {
            "attack": 0,
            "defense": 0,
            "speed": 0,
            "max_hp": 0,
            "max_mp": 0,
            "healing": 0,
            "spell_power": 0
        }

        for companion in self.companions:
            # Companion can be just name (old format) or dict with equipment
            if isinstance(companion, str):
                # Legacy format: just the name
                comp_id = None
                comp_name = companion
            else:
                # New format: dict with id, name, equipment, level
                comp_id = companion.get('id')
                comp_name = companion.get('name')

            # Find companion data by name or id
            comp_data = None
            for cid, cdata in companions_data.items():
                if cdata.get('name') == comp_name or cid == comp_id:
                    comp_data = cdata
                    break

            if not comp_data:
                continue

            # Apply direct stat bonuses
            bonuses["attack"] += comp_data.get("attack_bonus", 0)
            bonuses["defense"] += comp_data.get("defense_bonus", 0)
            bonuses["speed"] += comp_data.get("speed_bonus", 0)
            bonuses["max_hp"] += comp_data.get("hp_bonus", 0)
            bonuses["max_mp"] += comp_data.get("mp_bonus", 0)
            bonuses["healing"] += comp_data.get("healing_bonus", 0)
            bonuses["spell_power"] += comp_data.get("spell_power_bonus", 0)

            # TODO: Apply equipment bonuses from companion's equipment dict
            if isinstance(companion, dict) and "equipment" in companion:
                # In future, equip items on companions and add their bonuses
                pass

        return bonuses

    def apply_companion_bonuses(self, companions_data: Dict[str, Any]):
        """Apply companion bonuses to character stats after recalculating from equipment."""
        bonuses = self.calculate_companion_bonuses(companions_data)

        self.attack += bonuses["attack"]
        self.defense += bonuses["defense"]
        self.speed += bonuses["speed"]
        self.max_hp += bonuses["max_hp"]
        self.max_mp += bonuses["max_mp"]

        # Cap current HP/MP to new max
        self.hp = min(self.hp, self.max_hp)
        self.mp = min(self.mp, self.max_mp)


class Enemy:
    """Enemy class"""

    def __init__(self, enemy_data: Dict):
        self.name = enemy_data["name"]
        self.max_hp = enemy_data["hp"]
        self.hp = enemy_data["hp"]
        self.attack = enemy_data["attack"]
        self.defense = enemy_data["defense"]
        self.speed = enemy_data["speed"]
        self.experience_reward = enemy_data["experience_reward"]
        self.gold_reward = enemy_data["gold_reward"]
        self.loot_table = enemy_data.get("loot_table", [])

    def is_alive(self) -> bool:
        """Check if enemy is alive"""
        return self.hp > 0

    def take_damage(self, damage: int) -> int:
        """Apply damage to enemy, return actual damage taken"""
        actual_damage = max(1, damage - self.defense)
        self.hp = max(0, self.hp - actual_damage)
        return actual_damage


class Boss(Enemy):
    """Boss enemy class with phases and special abilities"""

    def __init__(self,
                 boss_data: Dict,
                 dialogues_data: Optional[Dict[str, Any]] = None):
        super().__init__(boss_data)
        self.description = boss_data.get("description", "A powerful foe.")
        self.special_abilities = boss_data.get("special_abilities", [])
        self.phases = boss_data.get("phases", [])
        self.current_phase_index = -1
        self.mp = 100
        self.max_mp = 100
        self.cooldowns = {}
        self.dialogues_data = dialogues_data or {}
        self.boss_dialogues = boss_data.get("dialogues", {})

    def get_dialogue(self, dialogue_key: str) -> Optional[str]:
        """Get a dialogue string by key, looking up the reference in dialogues_data"""
        # Get the dialogue reference key from boss data
        dialogue_ref = self.boss_dialogues.get(dialogue_key)
        if not dialogue_ref:
            return None

        # Look up the actual dialogue text from dialogues_data
        return self.dialogues_data.get(dialogue_ref)

    def take_damage(self, damage: int) -> int:
        actual_damage = super().take_damage(damage)
        self.check_phase_transition()
        return actual_damage

    def check_phase_transition(self):
        hp_percent = self.hp / self.max_hp if self.max_hp > 0 else 0
        for i, phase in enumerate(self.phases):
            if hp_percent <= phase.get("hp_threshold",
                                       0) and i > self.current_phase_index:
                self.current_phase_index = i
                print(
                    f"\n{Colors.MAGENTA}{Colors.BOLD}PHASE TRANSITION: {phase.get('description')}{Colors.END}"
                )
                self.attack = int(self.attack *
                                  phase.get("attack_multiplier", 1.0))
                self.defense = int(self.defense *
                                   phase.get("defense_multiplier", 1.0))
                break


class LanguageManager:
    """Manages language loading and translation"""

    def __init__(self):
        self.config: Dict[str, Any] = {}
        self.translations: Dict[str, str] = {}
        # Get language from settings, fallback to 'en'
        self.current_language = get_setting("language", "en")
        self.load_config()
        self.load_translations()

    def load_config(self):
        """Load language configuration"""
        try:
            with open('data/languages/config.json', 'r') as f:
                self.config = json.load(f)
                # Ensure current_language matches settings
                self.current_language = get_setting("language", self.config.get('default_language', 'en'))
        except (FileNotFoundError, json.JSONDecodeError):
            # Fallback defaults
            self.config = {
                "default_language": "en",
                "available_languages": {
                    "en": "English",
                    "es": "Español",
                    "zh_simp": "简体中文"
                },
                "fallback_language": "en",
                "overwrite_save_files": True
            }

    def change_language(self, lang_code: str):
        """Change current language and save to settings"""
        if lang_code in self.config.get("available_languages", {}):
            self.current_language = lang_code
            set_setting("language", lang_code)
            self.load_translations()
            print(f"Language changed to: {self.config['available_languages'][lang_code]}")
            return True
        return False

    def load_translations(self):
        """Load translation strings for current language"""
        try:
            lang_file = f'data/languages/{self.current_language}.json'
            with open(lang_file, 'r') as f:
                self.translations = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            # Fallback to English if current language fails
            if self.current_language != 'en':
                try:
                    with open('data/languages/en.json', 'r') as f:
                        self.translations = json.load(f)
                except (FileNotFoundError, json.JSONDecodeError):
                    self.translations = {}

    def get(self, key: str, default: Optional[str] = None, **kwargs) -> str:
        """Get translated string with robust formatting and escape handling"""
        # Get translation, fallback to default or key if not found
        text = self.translations.get(key, default if default is not None else key)

        # Handle literal escape sequences found in JSON files
        text = text.replace("\\n", "\n").replace("\\033", "\033").replace(
            "\\x1b", "\x1b").replace("\\r", "\r")

        if kwargs:
            try:
                text = text.format(**kwargs)
            except (KeyError, ValueError, IndexError):
                # Fallback for missing placeholders in translation strings
                if key == "current_location" and "area" in kwargs and "{area}" not in text:
                    text = f"{text} {kwargs['area']}"
                elif key == "welcome_adventurer" and "name" in kwargs and "{name}" not in text:
                    text = f"{text} {kwargs['name']}"

        return text

    def should_overwrite_saves(self) -> bool:
        """Check if save files should be overwritten"""
        return self.config.get('overwrite_save_files', True)


class Game:
    """Main game class"""

    def __init__(self):
        self.player: Optional[Character] = None
        self.current_area = "starting_village"
        self.visited_areas: set = set()  # Track visited areas for cutscenes
        self.enemies_data: Dict[str, Any] = {}
        self.areas_data: Dict[str, Any] = {}
        self.items_data: Dict[str, Any] = {}
        self.missions_data: Dict[str, Any] = {}
        self.bosses_data: Dict[str, Any] = {}
        self.classes_data: Dict[str, Any] = {}
        self.spells_data: Dict[str, Any] = {}
        self.effects_data: Dict[str, Any] = {}
        self.companions_data: Dict[str, Any] = {}
        self.dialogues_data: Dict[str, Any] = {}
        self.dungeons_data: Dict[str, Any] = {}
        self.cutscenes_data: Dict[str, Any] = {}
        self.mission_progress: Dict[str, Any] = {
        }  # mission_id -> {current_count, target_count, completed, type}
        self.completed_missions: List[str] = []
        self.market_api: Optional[MarketAPI] = None
        self.crafting_data: Dict[str, Any] = {}
        self.weekly_challenges_data: Dict[str, Any] = {}
        self.housing_data: Dict[str, Any] = {}  # Housing items data
        self.shops_data: Dict[str, Any] = {}  # Shop data
        self.farming_data: Dict[str, Any] = {}  # Farming crops and foods data

        # Challenge tracking
        self.challenge_progress: Dict[str, int] = {
        }  # challenge_id -> progress count
        self.completed_challenges: List[str] = []

        # Dungeon state tracking
        self.current_dungeon: Optional[Dict[str, Any]] = None
        self.dungeon_progress: int = 0
        self.dungeon_rooms: List[Dict[str, Any]] = []
        self.dungeon_state: Dict[str, Any] = {}

        # Initialize ModManager
        self.mod_manager = ModManager()

        # Initialize Language Manager
        self.lang = LanguageManager()

        # Load game data
        self.load_game_data()
        self.load_config()

    def load_game_data(self):
        """Load all game data from JSON files and mods"""
        try:
            with open('data/enemies.json', 'r') as f:
                self.enemies_data = json.load(f)
            with open('data/areas.json', 'r') as f:
                self.areas_data = json.load(f)
            with open('data/items.json', 'r') as f:
                self.items_data = json.load(f)
            with open('data/missions.json', 'r') as f:
                self.missions_data = json.load(f)
            with open('data/bosses.json', 'r') as f:
                self.bosses_data = json.load(f)
            with open('data/classes.json', 'r') as f:
                self.classes_data = json.load(f)
            with open('data/spells.json', 'r') as f:
                self.spells_data = json.load(f)
            with open('data/effects.json', 'r') as f:
                self.effects_data = json.load(f)
            # Optional companions data
            try:
                with open('data/companions.json', 'r') as f:
                    self.companions_data = json.load(f)
            except FileNotFoundError:
                self.companions_data = {}

            # Optional crafting data
            try:
                with open('data/crafting.json', 'r') as f:
                    self.crafting_data = json.load(f)
            except FileNotFoundError:
                self.crafting_data = {}

            # Load dialogues data
            try:
                with open('data/dialogues.json', 'r') as f:
                    self.dialogues_data = json.load(f)
            except FileNotFoundError:
                self.dialogues_data = {}

            # Load cutscenes data
            try:
                with open('data/cutscenes.json', 'r') as f:
                    self.cutscenes_data = json.load(f)
            except FileNotFoundError:
                self.cutscenes_data = {}

            # Load weather and times data
            try:
                with open('data/weather.json', 'r') as f:
                    self.weather_data = json.load(f)
                with open('data/times.json', 'r') as f:
                    self.times_data = json.load(f)
            except FileNotFoundError:
                self.weather_data = {}
                self.times_data = {}

            # Apply mod data
            mod_enemies = self.mod_manager.load_mod_data("enemies.json")
            self.enemies_data.update(mod_enemies)

            mod_areas = self.mod_manager.load_mod_data("areas.json")
            self.areas_data.update(mod_areas)

            mod_items = self.mod_manager.load_mod_data("items.json")
            self.items_data.update(mod_items)

            mod_missions = self.mod_manager.load_mod_data("missions.json")
            self.missions_data.update(mod_missions)

            mod_bosses = self.mod_manager.load_mod_data("bosses.json")
            self.bosses_data.update(mod_bosses)

            mod_spells = self.mod_manager.load_mod_data("spells.json")
            self.spells_data.update(mod_spells)

            mod_effects = self.mod_manager.load_mod_data("effects.json")
            self.effects_data.update(mod_effects)

        except FileNotFoundError as e:
            print(f"Error loading game data: {e}")
            print(self.lang.get("ensure_data_files"))
            sys.exit(1)
        except Exception as e:
            print(f"Error loading game data: {e}")
            print(self.lang.get("ensure_data_files"))

        # Load dungeons data
        try:
            with open('data/dungeons.json', 'r') as f:
                self.dungeons_data = json.load(f)
        except FileNotFoundError:
            self.dungeons_data = {}

        # Load weekly challenges data
        try:
            with open('data/weekly_challenges.json', 'r') as f:
                self.weekly_challenges_data = json.load(f)
            # Initialize challenge progress
            for challenge in self.weekly_challenges_data.get('challenges', []):
                self.challenge_progress[challenge['id']] = 0
        except FileNotFoundError:
            self.weekly_challenges_data = {}

        # Load housing data
        try:
            with open('data/housing.json', 'r') as f:
                self.housing_data = json.load(f)
        except FileNotFoundError:
            self.housing_data = {}

        # Load weather data
        try:
            with open('data/weather.json', 'r') as f:
                self.weather_data = json.load(f)
        except FileNotFoundError:
            self.weather_data = {}

        # Load times data
        try:
            with open('data/times.json', 'r') as f:
                self.times_data = json.load(f)
        except FileNotFoundError:
            self.times_data = {}

        # Load shops data
        try:
            with open('data/shops.json', 'r') as f:
                self.shops_data = json.load(f)
        except FileNotFoundError:
            self.shops_data = {}

        # Load farming data
        try:
            with open('data/farming.json', 'r') as f:
                self.farming_data = json.load(f)
        except FileNotFoundError:
            self.farming_data = {}

        # Load mod data after base game data
        self._load_mod_data()

    def _load_mod_data(self):
        """Load and merge mod data into base game data"""
        # Discover available mods
        self.mod_manager.discover_mods()

        # Get enabled mods
        enabled_mods = self.mod_manager.get_enabled_mods()

        if not enabled_mods:
            return

        print(self.lang.get("nloading_mods"))

        # Load mod data for each data type
        mod_data_types = [('areas.json', 'areas_data'),
                          ('enemies.json', 'enemies_data'),
                          ('items.json', 'items_data'),
                          ('missions.json', 'missions_data'),
                          ('bosses.json', 'bosses_data'),
                          ('companions.json', 'companions_data'),
                          ('classes.json', 'classes_data'),
                          ('spells.json', 'spells_data'),
                          ('effects.json', 'effects_data'),
                          ('crafting.json', 'crafting_data'),
                          ('dungeons.json', 'dungeons_data'),
                          ('dialogues.json', 'dialogues_data'),
                          ('cutscenes.json', 'cutscenes_data'),
                          ('weekly_challenges.json', 'weekly_challenges_data'),
                          ('housing.json', 'housing_data'),
                          ('shops.json', 'shops_data'),
                          ('weather.json', 'weather_data'),
                          ('times.json', 'times_data')]

        for file_name, attr_name in mod_data_types:
            mod_data = self.mod_manager.load_mod_data(file_name)
            if mod_data:
                # Merge mod data into base data
                base_data = getattr(self, attr_name)

                # Special handling for dungeons: merge nested structures
                if file_name == 'dungeons.json':
                    if 'dungeons' in mod_data:
                        if 'dungeons' not in base_data:
                            base_data['dungeons'] = []
                        base_data['dungeons'].extend(mod_data['dungeons'])
                    if 'challenge_templates' in mod_data:
                        if 'challenge_templates' not in base_data:
                            base_data['challenge_templates'] = {}
                        base_data['challenge_templates'].update(
                            mod_data['challenge_templates'])
                    if 'chest_templates' in mod_data:
                        if 'chest_templates' not in base_data:
                            base_data['chest_templates'] = {}
                        base_data['chest_templates'].update(
                            mod_data['chest_templates'])
                # Special handling for weekly_challenges: merge nested challenge arrays
                elif file_name == 'weekly_challenges.json':
                    if 'challenges' in mod_data:
                        if 'challenges' not in base_data:
                            base_data['challenges'] = []
                        base_data['challenges'].extend(mod_data['challenges'])
                        # Initialize progress tracking for new challenges
                        for challenge in mod_data['challenges']:
                            self.challenge_progress[challenge['id']] = 0
                else:
                    # Standard merge for other data types
                    base_data.update(mod_data)

                print(
                    f"  Loaded {len(mod_data)} entries from mods for {file_name}"
                )

        print(self.lang.get("mod_loading_complete_1"))

    def load_config(self):
        """Load configuration - uses hardcoded defaults since config file is removed"""
        # Set global color toggle to True by default
        global COLORS_ENABLED
        COLORS_ENABLED = True

        # Initialize Market API
        self.market_api = MarketAPI()

    def play_cutscene(self, cutscene_id: str):
        """Play a cutscene by ID"""
        if cutscene_id not in self.cutscenes_data:
            print(f"Cutscene {cutscene_id} not found.")
            return

        cutscene = self.cutscenes_data[cutscene_id]
        self._play_cutscene_content(cutscene['content'])

    def _play_cutscene_content(self, content: Dict[str, Any]):
        """Recursively play cutscene content"""
        # Display text
        if 'text' in content:
            print(f"\n{Colors.CYAN}{content['text']}{Colors.END}")

        # Wait
        if 'wait' in content:
            wait_time = content['wait']
            for i in range(wait_time):
                print(".", end="", flush=True)
                time.sleep(1)
            print()

        # Handle choices
        if 'choice' in content:
            choices = content['choice']
            if choices:
                print(self.lang.get("nchoose_your_response"))
                choice_keys = list(choices.keys())
                for i, choice_key in enumerate(choice_keys, 1):
                    print(f"{i}. {choice_key}")

                # Allow skipping with Enter
                choice = ask("Your choice (or press Enter to skip): ").strip()
                if choice and choice.isdigit():
                    idx = int(choice) - 1
                    if 0 <= idx < len(choice_keys):
                        selected_choice = choice_keys[idx]
                        next_content = choices[selected_choice]
                        if isinstance(next_content, dict):
                            self._play_cutscene_content(next_content)
                # If no choice or invalid, continue without recursion

    def display_welcome(self) -> str:
        """Display welcome screen"""
        while True:
            clear_screen()
            print(f"{Colors.CYAN}{Colors.BOLD}")
            print("=" * 60)
            print(f"             {self.lang.get('game_title_display')}")
            print(f"       {self.lang.get('game_subtitle_display')}")
            print("=" * 60)
            print(f"{Colors.END}")
            print(self.lang.get("welcome_message"))
            print(
                "Choose your path wisely, for every decision shapes your destiny."
            )
            print()

            print(
                f"{Colors.BOLD}{Colors.CYAN}=== {self.lang.get('main_menu')} ==={Colors.END}"
            )
            print(f"{Colors.CYAN}1.{Colors.END} {self.lang.get('new_game')}")
            print(f"{Colors.CYAN}2.{Colors.END} {self.lang.get('load_game')}")
            print(f"{Colors.CYAN}3.{Colors.END} {self.lang.get('settings')}")
            print(f"{Colors.CYAN}4.{Colors.END} {self.lang.get('mods')}")
            print(f"{Colors.CYAN}5.{Colors.END} {self.lang.get('quit')}")
            print()

            choice = ask(f"{Colors.CYAN}Choose an option (1-5): {Colors.END}")
            if choice == "1":
                return "new_game"
            elif choice == "2":
                return "load_game"
            elif choice == "3":
                self.settings_welcome()
            elif choice == "4":
                self.mods_welcome()
            elif choice == "5":
                print(self.lang.get("thank_exit"))
                clear_screen()
                sys.exit(0)
            else:
                print(self.lang.get("invalid_choice"))

    def settings_welcome(self):
        """Settings menu available from welcome screen"""
        while True:
            clear_screen()
            print(self.lang.get("n_settings"))

            # Get current settings
            mods_enabled = self.mod_manager.settings.get("mods_enabled", True)

            print(
                f"\n1. Mod System: {'{Colors.GREEN}Enabled{Colors.END}' if mods_enabled else '{Colors.RED}Disabled{Colors.END}'}"
            )
            print(self.lang.get("mod_menu_goback"))

            choice = ask("\nChoose an option: ").strip()

            if choice == "1":
                # Toggle mods system
                self.mod_manager.toggle_mods_system()
                if self.mod_manager.settings.get("mods_enabled", True):
                    print(self.lang.get("mod_system_enabled_1"))
                else:
                    print(self.lang.get("03331mmod_system_disabled0330m"))
                print(
                    f"{Colors.YELLOW}Note: Changes take effect on game restart.{Colors.END}"
                )
                ask("\nPress Enter to continue...")
            elif choice == "2" or not choice:
                break
            else:
                print(self.lang.get("invalid_choice"))

    def mods_welcome(self):
        """Mods menu available from welcome screen"""
        while True:
            clear_screen()
            print(self.lang.get("n_mods"))

            # Refresh mod list
            self.mod_manager.discover_mods()
            mods_list = self.mod_manager.get_mod_list()

            if not mods_list:
                print(
                    f"\n{Colors.YELLOW}{self.lang.get('no_mods_found')}{Colors.END}"
                )
                print(self.lang.get("place_mods_instruction"))
                ask("\nPress Enter to go back...")
                break

            # Mod system status
            mods_system_enabled = self.mod_manager.settings.get(
                "mods_enabled", True)
            status_color = Colors.GREEN if mods_system_enabled else Colors.RED
            status_text = "Enabled" if mods_system_enabled else "Disabled"
            print(
                f"\nMod System Status: {status_color}{status_text}{Colors.END}"
            )

            print(
                f"\n{Colors.CYAN}Installed Mods ({len(mods_list)}):{Colors.END}"
            )

            for i, mod in enumerate(mods_list, 1):
                name = mod.get('name', mod.get('folder_name', 'Unknown'))
                description = mod.get('description', '')
                author = mod.get('author', 'Unknown')
                version = mod.get('version', '1.0')
                enabled = mod.get('enabled', False)

                status = f"{Colors.GREEN}[ENABLED]{Colors.END}" if enabled else f"{Colors.RED}[DISABLED]{Colors.END}"
                print(f"\n{i}. {Colors.BOLD}{name}{Colors.END} {status}")
                print(f"   Version: {version}")
                print(f"   Author: {author}")
                if description:
                    # Truncate long descriptions
                    desc = description[:100] + "..." if len(
                        description) > 100 else description
                    print(f"   {desc}")

            print(self.lang.get("noptions"))
            print(f"1-{len(mods_list)}. Toggle Mod")
            print(f"R. {self.lang.get('ui_refresh_mod_list')}")
            print(f"B. {self.lang.get('ui_back_to_main_menu')}")

            choice = ask("\nChoose an option: ").strip().upper()

            if choice == 'B' or not choice:
                break
            elif choice == 'R':
                # Refresh mods
                self.mod_manager.discover_mods()
                print(self.lang.get("mod_list_refreshed"))
                time.sleep(0.5)
            elif choice.isdigit():
                idx = int(choice) - 1
                if 0 <= idx < len(mods_list):
                    mod = mods_list[idx]
                    folder_name = mod.get('folder_name')
                    if isinstance(folder_name, str):
                        self.mod_manager.toggle_mod(folder_name)
                        print(
                            f"{Colors.YELLOW}Note: Changes take effect on game restart.{Colors.END}"
                        )
                        ask("\nPress Enter to continue...")
                else:
                    print(self.lang.get("invalid_mod_number"))
                    time.sleep(1)
            else:
                print(self.lang.get("invalid_choice"))
                time.sleep(1)

    def display_available_classes(self):
        """Display all available character classes from classes.json"""
        print(f"\n{self.lang.get('ui_choose_class')}")

        color_map = [
            Colors.RED, Colors.BLUE, Colors.GREEN, Colors.YELLOW,
            Colors.MAGENTA, Colors.CYAN, Colors.WHITE, Colors.GOLD
        ]

        for i, (class_name, class_data) in enumerate(self.classes_data.items(),
                                                     1):
            color = color_map[(i - 1) % len(color_map)]
            description = class_data.get("description",
                                         "No description available")
            print(f"{color}{i}. {class_name}{Colors.END} - {description}")

    def select_class(self) -> str:
        """Allow user to select a class from available options"""
        class_names = list(self.classes_data.keys())
        # Try to enable tab-completion for class names (best-effort)
        try:
            enable_tab_completion(class_names)
        except Exception:
            pass

        try:
            while True:
                prompt = f"Enter class choice (1-{len(class_names)}) or name: "
                choice = ask(prompt, allow_empty=False)
                if choice.isdigit():
                    choice_idx = int(choice) - 1
                    if 0 <= choice_idx < len(class_names):
                        return class_names[choice_idx]
                    else:
                        print(
                            f"Invalid choice. Please enter a number between 1 and {len(class_names)}."
                        )
                        continue

                # Try to match by name (case-insensitive)
                matches = [
                    cn for cn in class_names if cn.lower() == choice.lower()
                ]
                if matches:
                    return matches[0]

                # Try close matches
                close = difflib.get_close_matches(
                    choice.lower(), [cn.lower() for cn in class_names], n=1)
                if close:
                    # return the real-cased version
                    for cn in class_names:
                        if cn.lower() == close[0]:
                            return cn
                print(
                    "Invalid class name. Try again or use the numeric choice.")
        finally:
            # restore completer
            try:
                disable_tab_completion(None)
            except Exception:
                pass

    def create_character(self):
        """Create a new character"""
        print(
            f"{Colors.BOLD}{self.lang.get('character_creation')}{Colors.END}")
        print(self.lang.get("separator_30"))

        name = ask(self.lang.get("enter_name"))
        if not name:
            name = "Hero"

        # Use dynamic class selection instead of hardcoded options
        self.display_available_classes()

        character_class = self.select_class()

        self.player = Character(name,
                                character_class,
                                self.classes_data,
                                lang=self.lang)
        self.player.weather_data = getattr(self, 'weather_data', {})
        self.player.times_data = getattr(self, 'times_data', {})
        print(
            self.lang.get("welcome_adventurer",
                          name=name,
                          char_class=character_class))

        # Give starting items based on class data
        self.give_starting_items(character_class)

        if self.player:
            self.player.display_stats()

    def give_starting_items(self, character_class: str):
        """Grant starting items based on character class from classes.json"""
        if not self.player or character_class not in self.classes_data:
            return

        class_info = self.classes_data[character_class]
        items = class_info.get("starting_items", [])
        starting_gold = class_info.get("starting_gold", 100)

        for item in items:
            self.player.inventory.append(item)

        self.player.gold = starting_gold

        if items:
            print(
                f"{Colors.YELLOW}You received starting equipment:{Colors.END}")
            for item in items:
                print(f"  - {item}")

        # Auto-equip first weapon and armor if available
        for slot in ("weapon", "armor"):
            for item in items:
                item_type = self.items_data.get(item, {}).get("type")
                if item_type == slot:
                    self.player.equip(item, self.items_data)
                    print(f"{Colors.GREEN}Equipped: {item}{Colors.END}")
                    break

    def change_language_menu(self):
        """Menu to change the game language"""
        print(f"\n{Colors.CYAN}{Colors.BOLD}=== {self.lang.get('settings', 'SETTINGS')} ==={Colors.END}")
        available = self.lang.config.get("available_languages", {"en": "English"})
        
        langs = list(available.items())
        for i, (code, name) in enumerate(langs, 1):
            print(f"{Colors.CYAN}{i}.{Colors.END} {name}")
        
        print(f"{Colors.CYAN}{len(langs) + 1}.{Colors.END} {self.lang.get('back', 'Back')}")
        
        choice = ask(f"{Colors.CYAN}Choose a language: {Colors.END}")
        
        if choice.isdigit():
            idx = int(choice) - 1
            if 0 <= idx < len(langs):
                self.lang.change_language(langs[idx][0])
            elif idx == len(langs):
                return
        print(create_separator())

    def main_menu(self):
        """Display main menu"""
        # Advance time by 1 hour each menu loop to make it dynamic
        if self.player:
            self.player.advance_time(1)

        # Continuous mission check on every main menu return
        self.update_mission_progress('check', '')

        # Check level-based challenges
        if self.player:
            self.update_challenge_progress('level_reach', self.player.level)

        print(
            f"\n{Colors.BOLD}=== {self.lang.get('main_menu')} ==={Colors.END}")

        # Show current location
        area_data = self.areas_data.get(self.current_area, {})
        area_name = area_data.get('name', self.current_area)
        print(self.lang.get("current_location", area=area_name))

        # Display time and weather
        if hasattr(self, 'player') and self.player and self.lang:
            time_str = self.lang.get("current_time", hour=str(self.player.hour).zfill(2))
            day_str = self.lang.get("current_day", day=str(self.player.day))
            weather_str = self.lang.get(f"weather_{self.player.current_weather}", self.player.current_weather.capitalize())
            
            print(f"{Colors.YELLOW}{time_str} | {day_str}{Colors.END}")
            print(f"{Colors.CYAN}{weather_str}{Colors.END}")

        print(f"{Colors.CYAN}1.{Colors.END} {self.lang.get('explore')}")
        print(f"{Colors.CYAN}2.{Colors.END} {self.lang.get('view_character')}")
        print(f"{Colors.CYAN}3.{Colors.END} {self.lang.get('travel')}")
        print(f"{Colors.CYAN}4.{Colors.END} {self.lang.get('inventory')}")
        print(f"{Colors.CYAN}5.{Colors.END} {self.lang.get('missions')}")
        print(f"{Colors.CYAN}6.{Colors.END} {self.lang.get('fight_boss')}")
        print(f"{Colors.CYAN}7.{Colors.END} {self.lang.get('tavern')}")
        print(f"{Colors.CYAN}8.{Colors.END} {self.lang.get('shop')}")
        print(f"{Colors.CYAN}9.{Colors.END} {self.lang.get('alchemy')}")
        print(f"{Colors.CYAN}10.{Colors.END} {self.lang.get('elite_market')}")
        print(f"{Colors.CYAN}11.{Colors.END} {self.lang.get('rest')}")
        print(f"{Colors.CYAN}12.{Colors.END} {self.lang.get('companions')}")
        print(f"{Colors.CYAN}13.{Colors.END} {self.lang.get('dungeons')}")
        print(f"{Colors.CYAN}14.{Colors.END} {self.lang.get('challenges')}")
        print(f"{Colors.CYAN}15.{Colors.END} {self.lang.get('settings', 'Settings')}")

        # Show Build options only in your_land
        menu_max = "19"
        if self.current_area == "your_land":
            print(self.lang.get("16_furnish_home"))
            print(self.lang.get("17_build_structures"))
            print(self.lang.get("18_farm"))
            print(self.lang.get("19_training"))
            print(f"{Colors.CYAN}20.{Colors.END} {self.lang.get('save_game')}")
            print(f"{Colors.CYAN}21.{Colors.END} {self.lang.get('load_game')}")
            print(
                f"{Colors.CYAN}22.{Colors.END} {self.lang.get('claim_rewards')}"
            )
            print(f"{Colors.CYAN}23.{Colors.END} {self.lang.get('quit')}")
            menu_max = "23"
            choice = ask(
                f"{Colors.CYAN}Choose an option (1-{menu_max}): {Colors.END}",
                allow_empty=False)
        else:
            print(f"{Colors.CYAN}16.{Colors.END} {self.lang.get('save_game')}")
            print(f"{Colors.CYAN}17.{Colors.END} {self.lang.get('load_game')}")
            print(
                f"{Colors.CYAN}18.{Colors.END} {self.lang.get('claim_rewards')}"
            )
            print(f"{Colors.CYAN}19.{Colors.END} {self.lang.get('quit')}")
            menu_max = "19"
            choice = ask(
                f"{Colors.CYAN}Choose an option (1-{menu_max}): {Colors.END}",
                allow_empty=False)

        # Normalize textual shortcuts to numbers for backward compatibility
        shortcut_map = {
            'explore': '1',
            'e': '1',
            'view': '2',
            'v': '2',
            'travel': '3',
            't': '3',
            'inventory': '4',
            'i': '4',
            'missions': '5',
            'm': '5',
            'boss': '6',
            'tavern': '7',
            'shop': '8',
            's': '8',
            'alchemy': '9',
            'alc': '9',
            'craft': '9',
            'crafting': '9',
            'market': '10',
            'mkt': '10',
            'elite': '10',
            'rest': '11',
            'r': '11',
            'companions': '12',
            'comp': '12',
            'settings': '15',
            'lang': '15',
            'language': '15',
            'build_home': '16' if self.current_area == "your_land" else None,
            'furnish_home': '16' if self.current_area == "your_land" else None,
            'build_land': '17' if self.current_area == "your_land" else None,
            'build_structures':
            '17' if self.current_area == "your_land" else None,
            'land': '17' if self.current_area == "your_land" else None,
            'farm': '18' if self.current_area == "your_land" else None,
            'training': '19' if self.current_area == "your_land" else None,
            'train': '19' if self.current_area == "your_land" else None,
            'save': '20' if self.current_area == "your_land" else '16',
            'load': '21' if self.current_area == "your_land" else '17',
            'l': '21' if self.current_area == "your_land" else '17',
            'claim': '22' if self.current_area == "your_land" else '18',
            'c': '22' if self.current_area == "your_land" else '18',
            'quit': '23' if self.current_area == "your_land" else '19',
            'q': '23' if self.current_area == "your_land" else '19'
        }

        # Remove None values from shortcut map
        shortcut_map = {k: v for k, v in shortcut_map.items() if v is not None}

        normalized = choice.strip().lower()
        if normalized in shortcut_map:
            choice = shortcut_map[normalized]

        if choice == "1":
            self.explore()

        elif choice == "2":
            if self.player:
                self.player.display_stats()
            else:
                print(self.lang.get("no_character"))
        elif choice == "3":
            self.travel()

        elif choice == "4":
            self.view_inventory()

        elif choice == "5":
            self.view_missions()

        elif choice == "6":
            self.fight_boss_menu()

        elif choice == "7":
            self.visit_tavern()

        elif choice == "8":
            self.visit_shop()

        elif choice == "9":
            self.visit_alchemy()

        elif choice == "10":
            self.visit_market()

        elif choice == "11":
            self.rest()

        elif choice == "12":
            self.manage_companions()

        elif choice == "13":
            self.visit_dungeons()

        elif choice == "14":
            self.view_challenges()

        elif choice == "15":
            self.change_language_menu()

        elif choice == "16" and self.current_area == "your_land":
            # Furnish Home option only in your_land
            self.build_home()

        elif choice == "17" and self.current_area == "your_land":
            # Build Structures option only in your_land
            self.build_structures()

        elif choice == "18" and self.current_area == "your_land":
            # Farm option only in your_land
            self.farm()

        elif choice == "19" and self.current_area == "your_land":
            # Training option only in your_land
            self.training()

        elif choice == "16":
            # Save Game (when not in your_land)
            self.save_game()

        elif choice == "20" and self.current_area == "your_land":
            # Save Game (when in your_land)
            self.save_game()

        elif choice == "17":
            # Load Game (when not in your_land)
            self.load_game()

        elif choice == "21" and self.current_area == "your_land":
            # Load Game (when in your_land)
            self.load_game()

        elif choice == "18":
            # Claim Rewards (when not in your_land)
            self.claim_rewards()

        elif choice == "22" and self.current_area == "your_land":
            # Claim Rewards (when in your_land)
            self.claim_rewards()

        elif choice == "19":
            # Quit (when not in your_land)
            self.quit_game()

        elif choice == "23" and self.current_area == "your_land":
            # Quit (when in your_land)
            self.quit_game()

        elif choice == "21" and self.current_area == "your_land":
            # Quit (when in your_land)
            self.quit_game()

        else:
            print(self.lang.get("invalid_choice"))

    def fight_boss_menu(self):
        """Menu to select and fight a boss in the current area"""
        if not self.player:
            print(self.lang.get("no_character"))
            return

        area_data = self.areas_data.get(self.current_area, {})
        possible_bosses = area_data.get("possible_bosses", [])

        if not possible_bosses:
            print(
                f"There are no bosses in {area_data.get('name', self.current_area)}."
            )
            return

        print(
            f"\n{Colors.RED}{Colors.BOLD}=== BOSSES IN {area_data.get('name', self.current_area).upper()} ==={Colors.END}"
        )
        for i, boss_name in enumerate(possible_bosses, 1):
            boss_data = self.bosses_data.get(boss_name, {})
            status = ""
            if boss_name in self.player.bosses_killed:
                last_killed_str = self.player.bosses_killed[boss_name]
                try:
                    last_killed_dt = datetime.fromisoformat(last_killed_str)
                    diff = datetime.now() - last_killed_dt
                    if diff.total_seconds() < 28800:
                        status = f" {Colors.YELLOW}(Cooldown: {int((28800 - diff.total_seconds()) // 60)}m left){Colors.END}"
                except Exception:
                    pass
            print(f"{i}. {boss_data.get('name', boss_name)}{status}")

        choice = ask(
            f"Choose a boss (1-{len(possible_bosses)}) or Enter to cancel: ")
        if choice and choice.isdigit():
            idx = int(choice) - 1
            if 0 <= idx < len(possible_bosses):
                boss_name = possible_bosses[idx]

                # Cooldown check
                if boss_name in self.player.bosses_killed:
                    last_killed_str = self.player.bosses_killed[boss_name]
                    try:
                        last_killed_dt = datetime.fromisoformat(
                            last_killed_str)
                        if (datetime.now() -
                                last_killed_dt).total_seconds() < 28800:
                            print(
                                f"{boss_name} is still recovering. Try again later."
                            )
                            return
                    except Exception:
                        pass

                boss_data = self.bosses_data.get(boss_name)
                if boss_data:
                    boss = Boss(boss_data, self.dialogues_data)
                    print(
                        f"\n{Colors.RED}{Colors.BOLD}Challenge accepted!{Colors.END}"
                    )
                    # Print start dialogue if available
                    start_dialogue = boss.get_dialogue("on_start_battle")
                    if start_dialogue:
                        print(
                            f"\n{Colors.CYAN}{boss.name}:{Colors.END} {start_dialogue}"
                        )
                    self.battle(boss)
            else:
                print(self.lang.get("invalid_choice"))

    def explore(self):
        """Explore the current area"""
        if self.player:
            self.player.advance_time(1)  # Advance time on exploration
        if not self.player:
            print(self.lang.get('no_character_created'))
            return

        # Continuous mission check on every action
        self.update_mission_progress('check', '')

        area_data = self.areas_data.get(self.current_area, {})
        area_name = area_data.get("name", "Unknown Area")

        print(f"\n{Colors.CYAN}Exploring {area_name}...{Colors.END}")

        # Random encounter chance
        if random.random() < 0.7:  # 70% chance of encounter
            self.random_encounter()
        else:
            print(self.lang.get("explore_nothing_found"))

            # Small chance to find materials
            if random.random() < 0.4:  # 40% chance to find materials
                self._gather_materials()

            # Small chance to find gold
            if random.random() < 0.3:  # 30% chance to find gold
                found_gold = random.randint(5, 20)
                self.player.gold += found_gold
                print(f"{Colors.GOLD}You found {found_gold} gold!{Colors.END}")

    def random_encounter(self):
        """Handle random encounter with regular enemies"""
        if not self.player:
            return

        area_data = self.areas_data.get(self.current_area, {})
        possible_enemies = area_data.get("possible_enemies", [])

        if not possible_enemies:
            msg = self.lang.get("no_enemies_in_area")
            print(msg.replace("\\n", "\n").replace("\\033", "\033"))
            return

        # Regular enemy encounter
        enemy_name = random.choice(possible_enemies)
        enemy_data = self.enemies_data.get(enemy_name)

        if enemy_data:
            enemy = Enemy(enemy_data)
            msg = f"\nA wild {enemy.name} appears!"
            print(f"\n{Colors.wrap(msg, Colors.RED)}")
            self.battle(enemy)
        else:
            msg = self.lang.get("explore_no_enemies")
            print(msg.replace("\\n", "\n").replace("\\033", "\033"))

    def update_challenge_progress(self, challenge_type: str, value: int = 1):
        """Update challenge progress and check for completions"""
        if not self.player:
            return

        for challenge in self.weekly_challenges_data.get('challenges', []):
            if challenge['id'] in self.completed_challenges:
                continue

            if challenge['type'] == challenge_type:
                self.challenge_progress[challenge['id']] += value

                # Check if challenge is completed
                if self.challenge_progress[
                        challenge['id']] >= challenge['target']:
                    self.complete_challenge(challenge)

    def complete_challenge(self, challenge: Dict[str, Any]):
        """Complete a challenge and award rewards"""
        if not self.player:
            return

        challenge_id = challenge['id']
        self.completed_challenges.append(challenge_id)

        reward_exp = challenge.get('reward_exp', 0)
        reward_gold = challenge.get('reward_gold', 0)

        self.player.gain_experience(reward_exp)
        self.player.gold += reward_gold

        print(
            f"\n{Colors.CYAN}{Colors.BOLD}✓ Challenge Completed: {challenge['name']}!{Colors.END}"
        )
        print(f"  Reward: {reward_exp} EXP + {reward_gold} Gold")

    def view_challenges(self):
        """Display challenge status to player"""
        if not self.player:
            return

        print(
            f"\n{Colors.CYAN}{Colors.BOLD}=== WEEKLY CHALLENGES ==={Colors.END}"
        )

        for challenge in self.weekly_challenges_data.get('challenges', []):
            challenge_id = challenge['id']
            is_completed = challenge_id in self.completed_challenges
            progress = self.challenge_progress.get(challenge_id, 0)
            target = challenge['target']

            status = "✓" if is_completed else f"{progress}/{target}"
            completed_text = f"{Colors.GREEN}COMPLETED{Colors.END}" if is_completed else status

            print(f"\n{Colors.BOLD}{challenge['name']}{Colors.END}")
            print(f"  {challenge['description']}")
            print(f"  Status: {completed_text}")
            print(
                f"  Reward: {challenge['reward_exp']} EXP + {challenge['reward_gold']} Gold"
            )

    def battle(self, enemy: Enemy):
        """Handle turn-based battle"""
        if not self.player:
            return

        print(self.lang.get("n_battle"))
        print(f"VS {enemy.name}")

        # Track if player fled
        player_fled = False

        # Determine who goes first using effective speed (buffs apply)
        player_first = self.player.get_effective_speed() >= enemy.speed

        while self.player.is_alive() and enemy.is_alive():
            if player_first:
                if not self.player_turn(enemy):
                    player_fled = True
                    break
                # Companions may act after the player turn (each companion has a chance)
                if enemy.is_alive() and self.player.companions:
                    self.companions_act(enemy)
                if enemy.is_alive():
                    self.enemy_turn(enemy)
            else:
                self.enemy_turn(enemy)
                if self.player.is_alive():
                    if not self.player_turn(enemy):
                        player_fled = True
                        break
                    # Companions may act after the player turn (each companion has a chance)
                    if enemy.is_alive() and self.player.companions:
                        self.companions_act(enemy)

            # Display current HP/MP
            player_hp_bar = create_hp_mp_bar(self.player.hp,
                                             self.player.max_hp, 20,
                                             Colors.RED)
            player_mp_bar = create_hp_mp_bar(self.player.mp,
                                             self.player.max_mp, 20,
                                             Colors.BLUE)

            # Check for boss for special health bar
            if isinstance(enemy, Boss):
                enemy_hp_bar = create_boss_hp_bar(enemy.hp, enemy.max_hp)
            else:
                enemy_hp_bar = create_hp_mp_bar(enemy.hp, enemy.max_hp, 20,
                                                Colors.RED)

            print(f"\n{Colors.BOLD}{self.player.name}{Colors.END}")
            print(f"HP: {player_hp_bar} {self.player.hp}/{self.player.max_hp}")
            print(f"MP: {player_mp_bar} {self.player.mp}/{self.player.max_mp}")

            print(f"\n{Colors.BOLD}{enemy.name}{Colors.END}")
            if isinstance(enemy, Boss):
                print(enemy_hp_bar)
            else:
                print(f"HP: {enemy_hp_bar} {enemy.hp}/{enemy.max_hp}")

            # Tick buffs (reduce durations each round)
            if self.player.tick_buffs():
                # Recalculate stats if buffs expired
                self.player.update_stats_from_equipment(
                    self.items_data, self.companions_data)

        # Battle outcome
        if player_fled:
            print(self.lang.get("nyou_fled_from_the_battle"))
            # Optional: Add penalty for fleeing?
            return

        if self.player.is_alive():
            print(
                f"\n{Colors.GREEN}You defeated the {enemy.name}!{Colors.END}")

            # Record boss kill for cooldown
            if isinstance(enemy, Boss):
                self.player.bosses_killed[
                    enemy.name] = datetime.now().isoformat()

            # Rewards
            exp_reward = enemy.experience_reward
            gold_reward = enemy.gold_reward

            # Apply weather bonuses
            if self.player.current_weather == "sunny":
                exp_reward = int(exp_reward * 1.1)
                print(
                    f"{Colors.YELLOW}Sunny weather bonus: +10% EXP!{Colors.END}"
                )
            elif self.player.current_weather == "stormy":
                gold_reward = int(gold_reward * 1.2)
                print(
                    f"{Colors.CYAN}Stormy weather bonus: +20% Gold (hazardous conditions)!{Colors.END}"
                )

            print(
                f"Gained {Colors.MAGENTA}{exp_reward} experience{Colors.END}")
            print(f"Gained {Colors.GOLD}{gold_reward} gold{Colors.END}")

            self.player.gain_experience(exp_reward)
            self.player.gold += gold_reward

            # Update mission progress for kill
            self.update_mission_progress('kill', enemy.name)

            # Update challenge progress for kills
            self.update_challenge_progress('kill_count')

            # Loot drop
            if enemy.loot_table and random.random(
            ) < 0.5:  # 50% chance for loot
                loot = random.choice(enemy.loot_table)
                self.player.inventory.append(loot)
                print(f"{Colors.YELLOW}Loot acquired: {loot}!{Colors.END}")
                # Update mission progress for collection
                self.update_mission_progress('collect', loot)
            # Post-battle companion effects (e.g., post_battle_heal)
            if self.player.companions:
                for companion in self.player.companions:
                    if isinstance(companion, dict):
                        comp_id = companion.get('id')
                        comp_name = companion.get('name')
                    else:
                        comp_id = None
                        comp_name = companion

                    comp_data = None
                    for cid, cdata in self.companions_data.items():
                        if cdata.get('name') == comp_name or cid == comp_id:
                            comp_data = cdata
                            break

                    if not comp_data:
                        continue

                    if comp_data.get('post_battle_heal'):
                        amt = int(comp_data.get('post_battle_heal', 0))
                        if amt > 0:
                            self.player.heal(amt)
                            print(
                                f"{Colors.GREEN}{comp_data.get('name')} restores {amt} HP after battle!{Colors.END}"
                            )
        else:
            print(
                f"\n{Colors.RED}You were defeated by the {enemy.name}...{Colors.END}"
            )
            # Respawn penalty
            self.player.hp = self.player.max_hp // 2
            self.player.mp = self.player.max_mp // 2
            print(self.lang.get("respawn"))
            self.current_area = "starting_village"

    def player_turn(self, enemy: Enemy) -> bool:
        """Player's turn in battle. Returns False if player fled."""
        if not self.player:
            return True

        print(self.lang.get("nyour_turn"))
        print(f"1. {self.lang.get('attack')}")
        print(f"2. {self.lang.get('use_item')}")
        print(f"3. {self.lang.get('defend')}")
        print(f"4. {self.lang.get('flee')}")
        # Can only cast spells if weapon is magic-capable
        weapon_name: Optional[str] = self.player.equipment.get('weapon')
        weapon_data = self.items_data.get(weapon_name,
                                          {}) if weapon_name else {}
        can_cast = bool(weapon_data.get('magic_weapon'))
        if can_cast:
            print(f"5. {self.lang.get('cast_spell')}")

        choice = ask(
            "Choose action (1-5): " if can_cast else "Choose action (1-4): ")

        if choice == "1":
            damage = self.player.get_effective_attack()
            actual_damage = enemy.take_damage(damage)
            print(f"You attack for {actual_damage} damage!")
        elif choice == "2":
            self.use_item_in_battle()
        elif choice == "5" and can_cast:
            self.cast_spell(enemy, weapon_name)
        elif choice == "3":
            print(Colors.wrap(self.lang.get("you_defend"), Colors.BLUE))
            self.player.defending = True
        elif choice == "4":
            flee_chance = 0.7 if self.player.get_effective_speed(
            ) > enemy.speed else 0.4
            if random.random() < flee_chance:
                print(self.lang.get("you_successfully_fled"))
                return False
            else:
                print(self.lang.get("failed_to_flee"))
                return True
        else:
            print(self.lang.get("invalid_choice_turn_lost"))

        return True

    def companion_action(self, enemy: Enemy):
        """Companions help during battle with their own actions"""
        # Backwards-compatible wrapper: pick a random companion and delegate
        if not self.player or not self.player.companions:
            return
        companion = random.choice(self.player.companions)
        self.companion_action_for(companion, enemy)

    def companion_action_for(self, companion, enemy: Enemy):
        """Perform an action for a specific companion dict or name."""
        if not self.player:
            return

        # Get companion name (handle both old string format and new dict format)
        if isinstance(companion, dict):
            comp_name = companion.get('name')
            comp_id = companion.get('id')
        else:
            comp_name = companion
            comp_id = None

        # Find companion data
        comp_data = None
        for cid, cdata in self.companions_data.items():
            if cdata.get('name') == comp_name or cid == comp_id:
                comp_data = cdata
                break

        if not comp_data:
            return

        # Prefer using defined abilities; otherwise fallback to simple actions
        abilities = comp_data.get('abilities', [])
        used_ability = False

        for ability in abilities:
            # Chance of triggering ability (ability chance may be percent 0-100 or 0-1)
            chance = ability.get('chance')
            triggered = False
            if chance is None:
                triggered = True
            else:
                # Accept either 0-1 float or 0-100 int
                if isinstance(chance, float) and 0 <= chance <= 1:
                    triggered = random.random() < chance
                else:
                    try:
                        triggered = random.randint(1, 100) <= int(chance)
                    except Exception:
                        triggered = False

            if not triggered:
                continue

            used_ability = True
            atype = ability.get('type')

            if atype in ('attack_boost', 'rage', 'crit_boost'):
                # Immediate enhanced attack
                bonus = int(
                    ability.get('attack_bonus', 0)
                    or ability.get('crit_damage_bonus', 0) or 0)
                companion_damage = int(self.player.get_effective_attack() *
                                       0.6 + comp_data.get('attack_bonus', 0) +
                                       bonus)
                actual_damage = enemy.take_damage(companion_damage)
                print(
                    f"{Colors.CYAN}{comp_name} uses {ability.get('name')} for {actual_damage} damage!{Colors.END}"
                )

            elif atype == 'taunt':
                dur = int(ability.get('duration', 1))
                # Give a temporary defense buff and mark taunt (defensive)
                dbonus = int(
                    ability.get('defense_bonus',
                                comp_data.get('defense_bonus', 0)))
                self.player.apply_buff(ability.get('name'), dur,
                                       {'defense_bonus': dbonus})
                print(
                    f"{Colors.BLUE}{comp_name} uses {ability.get('name')} and draws enemy attention!{Colors.END}"
                )

            elif atype == 'heal':
                # immediate heal (chance already checked)
                heal_amt = int(
                    ability.get(
                        'healing',
                        ability.get('heal', comp_data.get('healing_bonus', 0))
                        or 0))
                self.player.heal(heal_amt)
                print(
                    f"{Colors.GREEN}{comp_name} uses {ability.get('name')} and heals you for {heal_amt} HP!{Colors.END}"
                )

            elif atype == 'mp_regen':
                dur = int(ability.get('duration', 3))
                mp_per = int(
                    ability.get('mp_per_turn', ability.get('mp_per_turn', 0)))
                if mp_per > 0:
                    self.player.apply_buff(ability.get('name'), dur,
                                           {'mp_per_turn': mp_per})
                    print(
                        f"{Colors.CYAN}{comp_name} grants {mp_per} MP/turn for {dur} turns!{Colors.END}"
                    )

            elif atype == 'spell_power':
                dur = int(ability.get('duration', 3))
                sp = int(ability.get('spell_power_bonus', 0))
                if sp:
                    self.player.apply_buff(ability.get('name'), dur,
                                           {'spell_power_bonus': sp})
                    print(
                        f"{Colors.CYAN}{comp_name} increases spell power by {sp} for {dur} turns!{Colors.END}"
                    )

            elif atype == 'party_buff':
                dur = int(ability.get('duration', 3))
                mods = {}
                for k in ('attack_bonus', 'defense_bonus', 'speed_bonus'):
                    if ability.get(k) is not None:
                        mods[k] = int(ability.get(k))
                if mods:
                    self.player.apply_buff(ability.get('name'), dur, mods)
                    print(
                        f"{Colors.CYAN}{comp_name} uses {ability.get('name')}, granting party buffs: {mods}!{Colors.END}"
                    )

            else:
                # Unknown ability: fallback to simple action
                pass

            # If an ability triggered, don't try multiple abilities this turn
            break

        if not used_ability:
            # Fallback random behavior
            action_type = random.choice(['attack', 'defend', 'heal'])

            if action_type == 'attack' and comp_data.get('attack_bonus',
                                                         0) > 0:
                companion_damage = int(self.player.get_effective_attack() *
                                       0.6 + comp_data.get('attack_bonus', 0))
                actual_damage = enemy.take_damage(companion_damage)
                print(
                    f"{Colors.CYAN}{comp_name} attacks for {actual_damage} damage!{Colors.END}"
                )

            elif action_type == 'heal' and comp_data.get('healing_bonus',
                                                         0) > 0:
                heal_amount = comp_data.get('healing_bonus', 0)
                self.player.heal(heal_amount)
                print(
                    f"{Colors.GREEN}{comp_name} heals you for {heal_amount} HP!{Colors.END}"
                )

            elif action_type == 'defend' and comp_data.get('defense_bonus',
                                                           0) > 0:
                print(
                    f"{Colors.BLUE}{comp_name} helps you defend, reducing incoming damage!{Colors.END}"
                )
                self.player.defending = True

    def companions_act(self, enemy: Enemy):
        """Each companion has a chance to act on their own each turn."""
        if not self.player:
            return
        for companion in list(self.player.companions):
            # Default 50% chance to take an action; stronger companions could have higher chance
            chance = 0.5
            # read optional field from companion definition
            if isinstance(companion, dict) and companion.get('action_chance'):
                chance = companion.get('action_chance') or 0.5

            if random.random() < chance:
                self.companion_action_for(companion, enemy)

    def enemy_turn(self, enemy: Enemy):
        """Enemy's turn in battle"""
        if not self.player:
            return

        # Handle boss special abilities if it's a boss
        if isinstance(enemy, Boss):
            # Reduce cooldowns
            for abil in enemy.cooldowns:
                if enemy.cooldowns[abil] > 0:
                    enemy.cooldowns[abil] -= 1

            # Try to use a special ability
            available_abilities = [
                a for a in enemy.special_abilities
                if enemy.cooldowns.get(a['name'], 0) == 0
                and enemy.mp >= a.get('mp_cost', 0)
            ]

            # Check phase-locked abilities
            current_phase = enemy.phases[
                enemy.
                current_phase_index] if enemy.current_phase_index >= 0 else {}
            unlocked = current_phase.get("special_abilities_unlocked", [])
            if unlocked:
                available_abilities = [
                    a for a in available_abilities if a['name'] in unlocked
                ]

            if available_abilities and random.random() < 0.4:
                ability = random.choice(available_abilities)
                print(
                    f"\n{Colors.RED}{enemy.name} uses {ability['name']}!{Colors.END}"
                )
                print(
                    f"{Colors.DARK_GRAY}{ability.get('description')}{Colors.END}"
                )

                # Pay costs
                enemy.mp -= ability.get('mp_cost', 0)
                enemy.cooldowns[ability['name']] = ability.get('cooldown', 0)

                # Execute effect
                if 'damage' in ability:
                    dmg = ability['damage']
                    if self.player.defending:
                        dmg //= 2
                    actual = self.player.take_damage(dmg)
                    print(f"It deals {actual} damage!")

                if 'stun_chance' in ability and random.random(
                ) < ability['stun_chance']:
                    print(
                        f"{Colors.YELLOW}You are stunned and skip your next turn!{Colors.END}"
                    )
                    self.player.apply_buff("Stunned", 1, {"speed_bonus": -999})

                if 'heal_amount' in ability:
                    heal = ability['heal_amount']
                    enemy.hp = min(enemy.max_hp, enemy.hp + heal)
                    print(f"{enemy.name} heals for {heal} HP!")

                return  # Skip regular attack if ability used

        damage = enemy.attack
        if self.player.defending:
            damage = damage // 2
            self.player.defending = False

        actual_damage = self.player.take_damage(damage)
        print(f"{enemy.name} attacks for {actual_damage} damage!")

        # Companion may help reduce damage based on defense bonus
        if self.player.companions:
            companion_defense_bonus = 0
            for companion in self.player.companions:
                if isinstance(companion, dict):
                    comp_name = companion.get('name')
                    comp_id = companion.get('id')
                else:
                    comp_name = companion
                    comp_id = None

                for cid, cdata in self.companions_data.items():
                    if cdata.get('name') == comp_name or cid == comp_id:
                        companion_defense_bonus += cdata.get(
                            'defense_bonus', 0)
                        break

            if companion_defense_bonus > 0:
                damage_reduction = int(companion_defense_bonus * 0.5)
                actual_damage = max(1, actual_damage - damage_reduction)
                # Companions mitigated some damage; heal back the mitigated amount
                self.player.heal(damage_reduction)
                print(
                    f"{Colors.BLUE}Companions mitigate {damage_reduction} damage!{Colors.END}"
                )

    def use_item_in_battle(self):
        """Use item during battle"""
        if not self.player:
            return

        consumables = [
            item for item in self.player.inventory if item in self.items_data
            and self.items_data[item].get("type") == "consumable"
        ]

        if not consumables:
            msg = self.lang.get("no_consumable_items")
            print(msg.replace("\\n", "\n").replace("\\033", "\033"))
            return

        msg = self.lang.get("available_consumables")
        print(msg.replace("\\n", "\n").replace("\\033", "\033"))
        for i, item in enumerate(consumables, 1):
            item_data = self.items_data[item]
            print(
                f"{i}. {item} - {item_data.get('description', 'Unknown effect')}"
            )

        try:
            choice = int(ask("Choose item (1-{}): ".format(
                len(consumables)))) - 1
            if 0 <= choice < len(consumables):
                item = consumables[choice]
                self.use_item(item)
                self.player.inventory.remove(item)
            else:
                print(self.lang.get("invalid_choice"))
        except ValueError:
            print(self.lang.get("invalid_input"))

    def cast_spell(self, enemy: Enemy, weapon_name: Optional[str] = None):
        """Cast a spell from the player's equipped magic weapon."""
        if not self.player:
            return

        # Handle case where no weapon is equipped
        if not weapon_name:
            print(self.lang.get("need_magic_weapon"))
            return

        # Gather spells allowed by the equipped weapon
        available = []
        for sname, sdata in self.spells_data.items():
            allowed = sdata.get('allowed_weapons', [])
            if weapon_name in allowed:
                available.append((sname, sdata))

        if not available:
            print(self.lang.get("no_spells_available"))
            return

        # Pagination for spells
        page = 0
        per_page = 10

        while True:
            clear_screen()
            total_pages = (len(available) + per_page - 1) // per_page
            if total_pages == 0:
                total_pages = 1
            start_idx = page * per_page
            end_idx = start_idx + per_page
            current_spells = available[start_idx:end_idx]

            print(
                f"\n{Colors.BOLD}=== SPELLS (Page {page + 1}/{total_pages}) ==={Colors.END}"
            )
            print(
                f"MP: {Colors.BLUE}{self.player.mp}/{self.player.max_mp}{Colors.END}\n"
            )

            for i, (sname, sdata) in enumerate(current_spells, 1):
                cost = sdata.get('mp_cost', 0)
                mp_color = Colors.BLUE if self.player.mp >= cost else Colors.RED
                print(
                    f"{i}. {Colors.CYAN}{sname}{Colors.END} - Cost: {mp_color}{cost} MP{Colors.END}"
                )
                print(f"   {sdata.get('description', '')}")

            print(self.lang.get("noptions_1"))
            if total_pages > 1:
                if page > 0:
                    print(f"P. {self.lang.get('ui_previous_page')}")
                if page < total_pages - 1:
                    print(f"N. {self.lang.get('ui_next_page')}")

            print(f"1-{len(current_spells)}. Cast Spell")
            print(f"B. {self.lang.get('back')}")

            choice = ask("\nChoose an option: ").upper()

            if choice == 'B' or not choice:
                return
            elif choice == 'N' and page < total_pages - 1:
                page += 1
            elif choice == 'P' and page > 0:
                page -= 1
            elif choice.isdigit():
                idx = int(choice) - 1
                if 0 <= idx < len(current_spells):
                    sname, sdata = current_spells[idx]
                    break
                else:
                    print(self.lang.get('invalid_selection'))
                    time.sleep(1)
            else:
                print(self.lang.get("invalid_choice"))
                time.sleep(1)

        cost = sdata.get('mp_cost', 0)
        if self.player.mp < cost:
            print(self.lang.get("not_enough_mp"))
            return

        # Pay cost
        self.player.mp -= cost

        if sdata.get('type') == 'damage':
            power = sdata.get('power', 0)
            damage = power + (self.player.get_effective_attack() // 2)
            actual = enemy.take_damage(damage)
            print(f"You cast {sname} for {actual} damage!")

            # Apply effects if any
            effects = sdata.get('effects', [])
            for effect_name in effects:
                effect_data = self.effects_data.get(effect_name, {})
                effect_type = effect_data.get('type', '')

                if effect_type == 'damage_over_time':
                    print(
                        f"{Colors.RED}{enemy.name} is afflicted with {effect_name}!{Colors.END}"
                    )
                elif effect_type == 'stun':
                    if random.random() < effect_data.get('chance', 0.5):
                        print(
                            f"{Colors.YELLOW}{enemy.name} is stunned!{Colors.END}"
                        )
                elif effect_type == 'mixed_effect':
                    if random.random() < effect_data.get('chance', 0.5):
                        print(
                            f"{Colors.CYAN}{enemy.name} is frozen!{Colors.END}"
                        )

        elif sdata.get('type') == 'heal':
            heal_amount = sdata.get('power', 0)
            old_hp = self.player.hp
            self.player.heal(heal_amount)
            print(f"You cast {sname} and healed {self.player.hp - old_hp} HP!")

            # Apply healing effects if any
            effects = sdata.get('effects', [])
            for effect_name in effects:
                effect_data = self.effects_data.get(effect_name, {})
                if effect_data.get('type') == 'healing_over_time':
                    print(
                        f"{Colors.GREEN}You are affected by regeneration!{Colors.END}"
                    )

        elif sdata.get('type') == 'buff':
            power = sdata.get('power', 0)
            effects = sdata.get('effects', [])

            for effect_name in effects:
                effect_data = self.effects_data.get(effect_name, {})
                effect_type = effect_data.get('type', '')

                # Collect numeric modifiers from effect_data (keys that end with _bonus or known keys)
                modifiers: Dict[str, int] = {}
                for k, v in effect_data.items():
                    if isinstance(v, (int, float)) and (
                            k.endswith('_bonus')
                            or k in ('hp_bonus', 'mp_bonus', 'absorb_amount',
                                     'critical_bonus')):
                        modifiers[k] = int(v)

                duration = int(
                    effect_data.get('duration', max(3, int(power or 3))))
                # Apply as temporary buff
                if modifiers:
                    self.player.apply_buff(effect_name, duration, modifiers)
                    print(
                        f"{Colors.GREEN}Applied buff: {effect_name} (+{', '.join(str(v) + ' ' + k for k, v in modifiers.items())}) for {duration} turns{Colors.END}"
                    )
                else:
                    # Non-numeric effects (like reconnaissance) still applied as a marker buff
                    self.player.apply_buff(effect_name, duration, {})
                    if effect_type == 'damage_absorb':
                        print(
                            f"{Colors.BLUE}You create a magical shield!{Colors.END}"
                        )
                    elif effect_type == 'reconnaissance':
                        print(
                            f"{Colors.CYAN}You can see enemy weaknesses!{Colors.END}"
                        )

        elif sdata.get('type') == 'debuff':
            power = sdata.get('power', 0)
            effects = sdata.get('effects', [])

            for effect_name in effects:
                effect_data = self.effects_data.get(effect_name, {})
                effect_type = effect_data.get('type', '')

                if effect_type == 'action_block':
                    if random.random() < effect_data.get('chance', 0.5):
                        print(
                            f"{Colors.YELLOW}{enemy.name} is stunned and cannot act!{Colors.END}"
                        )

                elif effect_type == 'accuracy_reduction':
                    print(
                        f"{Colors.RED}{enemy.name}'s accuracy is reduced!{Colors.END}"
                    )

                elif effect_type == 'speed_reduction':
                    print(
                        f"{Colors.YELLOW}{enemy.name} is slowed!{Colors.END}")

                elif effect_type == 'stat_reduction':
                    print(
                        f"{Colors.RED}{enemy.name}'s stats are cursed!{Colors.END}"
                    )

        else:
            print(f"Unknown spell type: {sdata.get('type')}")
            # Refund MP for unknown spell types
            self.player.mp += cost

        # Check for cast cutscene
        cast_cutscene = sdata.get('cast_cutscene')
        if cast_cutscene and cast_cutscene in self.cutscenes_data:
            self.play_cutscene(cast_cutscene)

    def use_item(self, item: str):
        """Use an item"""
        if not self.player:
            return

        item_data = self.items_data.get(item, {})
        item_type = item_data.get("type")

        if item_type == "consumable":
            if item_data.get("effect") == "heal":
                heal_amount = item_data.get("value", 0)
                old_hp = self.player.hp
                self.player.heal(heal_amount)
                print(f"Used {item}, healed {self.player.hp - old_hp} HP!")
            elif item_data.get("effect") == "mp_restore":
                mp_amount = item_data.get("value", 0)
                old_mp = self.player.mp
                self.player.mp = min(self.player.max_mp,
                                     self.player.mp + mp_amount)
                print(f"Used {item}, restored {self.player.mp - old_mp} MP!")

    def view_inventory(self):
        """View character inventory"""
        if not self.player:
            print(self.lang.get("no_character"))
            return

        print(self.lang.get("n_inventory"))
        print(f"Gold: {Colors.GOLD}{self.player.gold}{Colors.END}")

        if not self.player.inventory:
            print(self.lang.get('inventory_empty'))
            return

        # Group items by type
        items_by_type = {}
        for item in self.player.inventory:
            item_type = self.items_data.get(item, {}).get("type", "unknown")
            if item_type not in items_by_type:
                items_by_type[item_type] = []
            items_by_type[item_type].append(item)

        for item_type, items in items_by_type.items():
            print(f"\n{Colors.CYAN}{item_type.title()}:{Colors.END}")
            for item in items:
                item_data = self.items_data.get(item, {})
                print(f"  - {item}")
                if item_data.get("description"):
                    print(f"    {item_data['description']}")

        # Offer equip/unequip options for equipment items
        equipable = [
            it for it in self.player.inventory
            if self.items_data.get(it, {}).get('type') in ('weapon', 'armor',
                                                           'accessory',
                                                           'offhand')
        ]
        if equipable:
            print(self.lang.get("equipment_options"))
            print(self.lang.get("equip_from_inventory"))
            print(self.lang.get("unequip_slot"))
            choice = ask("Choose option (E/U) or press Enter to return: ")
            if choice.lower() == 'e':
                print(self.lang.get("equipable_items"))
                for i, item in enumerate(equipable, 1):
                    print(
                        f"{i}. {item} - {self.items_data.get(item, {}).get('description','')}"
                    )
                sel = ask(
                    f"Choose item to equip (1-{len(equipable)}) or press Enter: "
                )
                if sel and sel.isdigit():
                    idx = int(sel) - 1
                    if 0 <= idx < len(equipable):
                        item_name = equipable[idx]
                        ok = self.player.equip(item_name, self.items_data)
                        if ok:
                            print(f"Equipped {item_name}.")
                        else:
                            print(
                                f"Cannot equip {item_name} (requirements not met)."
                            )
            elif choice.lower() == 'u':
                print(self.lang.get("currently_equipped"))
                for slot in ('weapon', 'armor', 'offhand', 'accessory_1',
                             'accessory_2', 'accessory_3'):
                    print(
                        f"{slot.title()}: {self.player.equipment.get(slot, 'None')}"
                    )
                slot_choice = ask(
                    "Enter slot to unequip (weapon/armor/offhand/accessory_1/accessory_2/accessory_3) or press Enter: "
                )
                valid_slots = ('weapon', 'armor', 'offhand', 'accessory_1',
                               'accessory_2', 'accessory_3')
                if slot_choice in valid_slots:
                    removed = self.player.unequip(slot_choice, self.items_data)
                    if removed:
                        print(f"Unequipped {removed} from {slot_choice}.")
                    else:
                        print(self.lang.get("nothing_to_unequip"))

    def view_missions(self):
        """View and manage missions"""
        while True:
            clear_screen()
            print(create_section_header("MISSIONS"))

            # Active Missions
            active_missions = [
                mid for mid in self.mission_progress.keys()
                if not self.mission_progress[mid].get('completed', False)
            ]

            if active_missions:
                print(self.lang.get("n_active_missions"))
                for i, mid in enumerate(active_missions, 1):
                    mission = self.missions_data.get(mid, {})
                    progress = self.mission_progress[mid]

                    if progress['type'] == 'kill':
                        if 'current_counts' in progress:
                            lines = [
                                f"{t}: {progress['current_counts'].get(t,0)}/{c}"
                                for t, c in progress['target_counts'].items()
                            ]
                            status = ", ".join(lines)
                        else:
                            status = f"{progress['current_count']}/{progress['target_count']}"
                    else:
                        if 'current_counts' in progress:
                            lines = [
                                f"{t}: {progress['current_counts'].get(t,0)}/{c}"
                                for t, c in progress['target_counts'].items()
                            ]
                            status = ", ".join(lines)
                        else:
                            status = f"{progress['current_count']}/{progress['target_count']}"

                    print(f"{i}. {mission.get('name')} - {status}")
                    print(
                        f"   {Colors.DARK_GRAY}{mission.get('description')}{Colors.END}"
                    )

                print(f"\n{self.lang.get('options_available_cancel_back')}")
            else:
                print(self.lang.get("no_active_missions"))
                print(f"\n{self.lang.get('options_available_missions_back')}")

            choice = ask("\nChoose an option: ").upper()

            if choice == 'B':
                break
            elif choice == 'A':
                self.available_missions_menu()
            elif choice == 'C' and active_missions:
                idx_str = ask("Enter mission number to cancel: ")
                if idx_str.isdigit():
                    idx = int(idx_str) - 1
                    if 0 <= idx < len(active_missions):
                        m_id = active_missions[idx]
                        m_name = self.missions_data[m_id]['name']
                        confirm = ask(
                            f"Are you sure you want to cancel '{m_name}'? (y/n): "
                        ).lower()
                        if confirm == 'y':
                            del self.mission_progress[m_id]
                            print(f"Mission '{m_name}' cancelled.")
                            time.sleep(1)
                    else:
                        print(self.lang.get("invalid_mission_number"))
                        time.sleep(1)

    def available_missions_menu(self):
        """Menu for viewing and accepting available missions"""
        page = 0
        per_page = 10

        while True:
            clear_screen()
            print(create_section_header("AVAILABLE MISSIONS"))

            available_missions = [
                mid for mid in self.missions_data.keys()
                if mid not in self.mission_progress
                and mid not in self.completed_missions
            ]

            if not available_missions:
                print(self.lang.get("no_new_missions"))
                ask("\nPress Enter to go back...")
                break

            total_pages = (len(available_missions) + per_page - 1) // per_page
            start_idx = page * per_page
            end_idx = min(start_idx + per_page, len(available_missions))
            current_page_missions = available_missions[start_idx:end_idx]

            for i, mission_id in enumerate(current_page_missions, 1):
                mission = self.missions_data.get(mission_id, {})
                print(f"{i}. {Colors.BOLD}{mission.get('name')}{Colors.END}")
                print(f"   {mission.get('description')}")

                # Requirements
                reqs = []
                if mission.get('unlock_level'):
                    level_req = mission.get('unlock_level')
                    has_level = self.player.level >= level_req if self.player else False
                    color = Colors.GREEN if has_level else Colors.RED
                    reqs.append(f"Level {color}{level_req}{Colors.END}")
                if mission.get('prerequisites'):
                    for prereq_id in mission.get('prerequisites'):
                        prereq_name = self.missions_data.get(
                            prereq_id, {}).get('name', prereq_id)
                        color = Colors.GREEN if prereq_id in self.completed_missions else Colors.RED
                        reqs.append(
                            f"Requires: {color}{prereq_name}{Colors.END}")
                if reqs:
                    print(f"   Requirements: {', '.join(reqs)}")

            print(f"\nPage {page + 1}/{total_pages}")
            if total_pages > 1:
                if page > 0:
                    print(f"P. {self.lang.get('ui_previous_page')}")
                if page < total_pages - 1:
                    print(f"N. {self.lang.get('ui_next_page')}")

            if current_page_missions:
                print(f"1-{len(current_page_missions)}. Accept Mission")
            print(f"B. {self.lang.get('back')}")

            choice = ask("\nChoose an option: ").upper()

            if choice == 'B':
                break
            elif choice == 'N' and page < total_pages - 1:
                page += 1
            elif choice == 'P' and page > 0:
                page -= 1
            elif choice.isdigit():
                idx = int(choice) - 1
                if 0 <= idx < len(current_page_missions):
                    mission_id = current_page_missions[idx]
                    self.accept_mission(mission_id)
                else:
                    print(self.lang.get("invalid_mission_number"))
                    time.sleep(1)

    def accept_mission(self, mission_id: str):
        """Accept a mission"""
        if mission_id not in self.mission_progress:
            mission = self.missions_data.get(mission_id, {})

            # Initialize progress tracking for this mission
            if mission:
                mission_type = mission.get('type', 'kill')
                target_count = mission.get('target_count', 1)

                if mission_type == 'collect' and isinstance(
                        target_count, dict):
                    # For collect missions with multiple items
                    self.mission_progress[mission_id] = {
                        'current_counts': {
                            item: 0
                            for item in target_count.keys()
                        },
                        'target_counts': target_count,
                        'completed': False,
                        'type': mission_type
                    }
                else:
                    # For kill missions or single item collect missions
                    self.mission_progress[mission_id] = {
                        'current_count': 0,
                        'target_count': target_count,
                        'completed': False,
                        'type': mission_type
                    }

                print(f"Mission accepted: {mission.get('name', 'Unknown')}")

                # Check for accept cutscene
                accept_cutscene = mission.get('accept_cutscene')
                if accept_cutscene and accept_cutscene in self.cutscenes_data:
                    self.play_cutscene(accept_cutscene)

                time.sleep(1)
            else:
                print(self.lang.get("mission_data_not_found"))
                time.sleep(1)
        else:
            print(self.lang.get("mission_already_accepted"))
            time.sleep(1)

    def update_mission_progress(self,
                                update_type: str,
                                target: str,
                                count: int = 1):
        """Update mission progress for a specific target"""
        # Always check inventory-based collect missions
        if self.player:
            for mid, progress in self.mission_progress.items():
                if progress.get('completed', False):
                    continue
                mission = self.missions_data.get(mid, {})
                if progress['type'] == 'collect':
                    if 'current_counts' in progress:
                        for item in progress['target_counts'].keys():
                            inv_count = self.player.inventory.count(item)
                            progress['current_counts'][item] = inv_count

                        all_collected = all(
                            progress['current_counts'][item] >=
                            progress['target_counts'][item]
                            for item in progress['target_counts'])
                        if all_collected:
                            self.complete_mission(mid)
                    else:
                        target_item = mission.get('target', '')
                        inv_count = self.player.inventory.count(target_item)
                        progress['current_count'] = inv_count
                        if progress['current_count'] >= progress[
                                'target_count']:
                            self.complete_mission(mid)

        # Standard update logic for kills or specific increments
        for mid, progress in self.mission_progress.items():
            if progress.get('completed', False):
                continue

            mission = self.missions_data.get(mid, {})

            if progress['type'] == 'kill' and update_type == 'kill':
                target_enemy = mission.get('target', '').lower()
                if target_enemy == target.lower():
                    progress['current_count'] += count
                    print(
                        f"{Colors.CYAN}[Mission Progress] {mission.get('name')}: {progress['current_count']}/{progress['target_count']}{Colors.END}"
                    )

                    if progress['current_count'] >= progress['target_count']:
                        self.complete_mission(mid)

            elif progress['type'] == 'collect' and update_type == 'collect':
                # Handle collection missions
                if 'current_counts' in progress:
                    # Multi-item collection
                    if target in progress['current_counts']:
                        progress['current_counts'][target] += count
                        print(
                            f"{Colors.CYAN}[Mission Progress] {mission.get('name')} - {target}: {progress['current_counts'][target]}/{progress['target_counts'][target]}{Colors.END}"
                        )

                        # Check if all items are collected
                        all_collected = all(
                            progress['current_counts'][item] >=
                            progress['target_counts'][item]
                            for item in progress['target_counts'])
                        if all_collected:
                            self.complete_mission(mid)
                else:
                    # Single item collection
                    target_item = mission.get('target', '')
                    if target_item == target:
                        progress['current_count'] += count
                        print(
                            f"{Colors.CYAN}[Mission Progress] {mission.get('name')}: {progress['current_count']}/{progress['target_count']}{Colors.END}"
                        )

                        if progress['current_count'] >= progress[
                                'target_count']:
                            self.complete_mission(mid)

    def complete_mission(self, mission_id: str):
        """Mark a mission as completed and notify player"""
        if mission_id in self.mission_progress:
            self.mission_progress[mission_id]['completed'] = True
            mission = self.missions_data.get(mission_id, {})
            print(
                f"\n{Colors.GOLD}{Colors.BOLD}!!! MISSION COMPLETE: {mission.get('name')} !!!{Colors.END}"
            )
            print(
                f"{Colors.YELLOW}You can now claim your rewards from the menu.{Colors.END}"
            )

            # Check for complete cutscene
            complete_cutscene = mission.get('complete_cutscene')
            if complete_cutscene and complete_cutscene in self.cutscenes_data:
                self.play_cutscene(complete_cutscene)

            time.sleep(2)

    def claim_rewards(self):
        """Claim rewards for completed missions"""
        if not self.player:
            print(self.lang.get("no_character"))
            return

        completed_missions = [
            mid for mid, progress in self.mission_progress.items()
            if progress.get('completed', False)
        ]
        if not completed_missions:
            print(self.lang.get("no_completed_missions"))
            return

        print(self.lang.get("n_claim_rewards"))
        print(self.lang.get("completed_missions_header"))
        for i, mid in enumerate(completed_missions, 1):
            mission = self.missions_data.get(mid, {})
            reward = mission.get('reward', {})
            exp = reward.get('experience', 0)
            gold = reward.get('gold', 0)
            items = reward.get('items', [])
            print(
                f"{i}. {mission.get('name')} - Exp: {exp}, Gold: {gold}, Items: {', '.join(items) if items else 'None'}"
            )

        choice = ask(
            f"Claim rewards for mission (1-{len(completed_missions)}) or press Enter to cancel: "
        )
        if choice and choice.isdigit():
            idx = int(choice) - 1
            if 0 <= idx < len(completed_missions):
                mission_id = completed_missions[idx]
                mission = self.missions_data.get(mission_id, {})
                reward = mission.get('reward', {})

                # Apply rewards
                exp = reward.get('experience', 0)
                gold = reward.get('gold', 0)
                items = reward.get('items', [])

                self.player.gain_experience(exp)
                self.player.gold += gold
                for item in items:
                    self.player.inventory.append(item)

                # Remove from progress and add to completed
                del self.mission_progress[mission_id]
                self.completed_missions.append(mission_id)

                print(self.lang.get("nrewards_claimed"))
                print(f"Gained {Colors.MAGENTA}{exp} experience{Colors.END}")
                print(f"Gained {Colors.GOLD}{gold} gold{Colors.END}")
                if items:
                    print(f"Received items: {', '.join(items)}")
            else:
                print(self.lang.get("invalid_choice"))

    def visit_shop(self):
        """Visit the shop - displays items for sale in the current area"""
        if not self.player:
            print(self.lang.get("no_character"))
            return

        area_data = self.areas_data.get(self.current_area, {})
        area_shops = area_data.get("shops", [])

        # Add housing shop if in your_land
        available_shops = list(area_shops)
        if self.current_area == "your_land":
            available_shops.append("housing_shop")

        if not available_shops:
            print(
                f"\n{Colors.RED}There are no shops in {area_data.get('name', self.current_area)}.{Colors.END}"
            )
            return

        # If multiple shops, let player choose
        if len(available_shops) > 1:
            print(
                f"\n{Colors.BOLD}=== SHOPS IN {area_data.get('name', self.current_area).upper()} ==={Colors.END}"
            )
            print(f"Your gold: {Colors.GOLD}{self.player.gold}{Colors.END}\n")
            for i, shop_id in enumerate(available_shops, 1):
                if shop_id == "housing_shop":
                    shop_name = "Housing Shop"
                else:
                    shop_data = self.shops_data.get(shop_id, {})
                    shop_name = shop_data.get(
                        "name",
                        shop_id.replace("_", " ").title())
                print(f"{i}. {shop_name}")

            print(self.lang.get("leave_option"))
            choice = ask("Which shop would you like to visit? ")

            if choice == "0" or not choice.isdigit():
                return

            shop_idx = int(choice) - 1
            if 0 <= shop_idx < len(available_shops):
                selected_shop = available_shops[shop_idx]
            else:
                print(self.lang.get("invalid_choice"))
                return
        else:
            selected_shop = available_shops[0]

        # Now visit the selected shop
        if selected_shop == "housing_shop":
            self._visit_housing_shop_inline()
        else:
            self.visit_specific_shop(selected_shop)

    def _visit_housing_shop_inline(self):
        """Visit the housing shop in your_land to buy housing items"""
        if not self.player:
            print(self.lang.get("no_character"))
            return

        print(self.lang.get("n_housing_shop"))
        print(
            f"{Colors.YELLOW}Welcome to the Housing Shop! Build your dream home with these items.{Colors.END}"
        )
        print(f"\nYour gold: {Colors.GOLD}{self.player.gold}{Colors.END}")
        print(
            f"Comfort Points: {Colors.CYAN}{self.player.comfort_points}{Colors.END}"
        )
        print(
            f"Items owned: {Colors.MAGENTA}{len(self.player.housing_owned)}{Colors.END}"
        )

        # Get all housing items
        housing_items = list(self.housing_data.items())
        if not housing_items:
            print(self.lang.get("no_housing_items_available"))
            return

        page_size = 8
        current_page = 0

        while True:
            start = current_page * page_size
            end = start + page_size
            page_items = housing_items[start:end]

            if not page_items:
                print(self.lang.get("no_more_items"))
                break

            print(
                f"\n{Colors.CYAN}--- Page {current_page + 1} of {(len(housing_items) + page_size - 1) // page_size} ---{Colors.END}"
            )
            for i, (item_id, item_data) in enumerate(page_items, 1):
                name = item_data.get("name", item_id)
                price = item_data.get("price", 0)
                comfort = item_data.get("comfort_points", 0)
                desc = item_data.get("description", "")
                owned = "✓" if item_id in self.player.housing_owned else " "

                # Color price based on affordability
                price_color = Colors.GREEN if self.player.gold >= price else Colors.RED
                # Color owned indicator
                owned_color = Colors.GREEN if owned == "✓" else Colors.RED

                print(
                    f"\n{Colors.CYAN}{i}.{Colors.END} [{owned_color}{owned}{Colors.END}] {Colors.BOLD}{Colors.YELLOW}{name}{Colors.END}"
                )
                print(f"   {desc}")
                print(
                    f"   Price: {price_color}{price} gold{Colors.END} | Comfort: {Colors.CYAN}+{comfort}{Colors.END}"
                )

            print(self.lang.get("noptions_2"))
            print(
                f"{Colors.CYAN}1-{len(page_items)}.{Colors.END} Buy/Add Housing Item"
            )
            if len(housing_items) > page_size:
                print(self.lang.get("n_next_page"))
                print(self.lang.get("p_previous_page"))
            print(self.lang.get("b_furnishview_home"))
            print(self.lang.get("enter_leave_shop"))

            choice = ask("\nChoose action: ").strip().upper()

            if not choice:
                break
            elif choice == 'N' and len(housing_items) > page_size:
                if end < len(housing_items):
                    current_page += 1
            elif choice == 'P' and len(housing_items) > page_size:
                if current_page > 0:
                    current_page -= 1
            elif choice == 'B':
                self.build_home()
            elif choice.isdigit():
                item_idx = int(choice) - 1
                if 0 <= item_idx < len(page_items):
                    item_id, item_data = page_items[item_idx]
                    name = item_data.get("name", item_id)
                    price = item_data.get("price", 0)
                    comfort = item_data.get("comfort_points", 0)

                    # Check if already owned
                    if item_id in self.player.housing_owned:
                        # Option to buy another copy or view details
                        confirm = ask(
                            f"\n{Colors.YELLOW}You already own this. Buy another copy for {Colors.GOLD}{price} gold{Colors.YELLOW}? (y/n): {Colors.END}"
                        ).strip().lower()
                        if confirm != 'y':
                            continue

                    # Check if can afford
                    if self.player.gold >= price:
                        self.player.gold -= price
                        self.player.housing_owned.append(item_id)
                        self.player.comfort_points += comfort
                        print(
                            f"\n{Colors.GREEN}✓ Purchased {Colors.BOLD}{name}{Colors.END}{Colors.GREEN}!{Colors.END}"
                        )
                        print(
                            f"{Colors.CYAN}Comfort points: +{comfort} (Total: {self.player.comfort_points}){Colors.END}"
                        )
                    else:
                        print(
                            f"\n{Colors.RED}✗ Not enough gold! Need {Colors.BOLD}{price}{Colors.END}{Colors.RED}, have {self.player.gold}.{Colors.END}"
                        )
                else:
                    print(self.lang.get("invalid_selection_1"))

    def visit_specific_shop(self, shop_id):
        """Visit a specific shop by ID"""

        if not self.player:
            print(self.lang.get("no_character"))
            return

        shop_data = self.shops_data.get(shop_id, {})
        if not shop_data:
            print(f"Shop {shop_id} not found.")
            return

        self._visit_general_shop(shop_data)

    def build_home(self):
        """Build and manage structures on your land"""
        if not self.player:
            print(self.lang.get("no_character"))
            return

        if not self.player.housing_owned:
            print(
                f"{Colors.YELLOW}You haven't purchased any housing items yet! Visit the Housing Shop first.{Colors.END}"
            )
            input(self.lang.get("press_enter"))
            return

        while True:
            clear_screen()
            print(
                f"\n{Colors.BOLD}{Colors.CYAN}=== BUILD STRUCTURES ==={Colors.END}"
            )
            print(
                f"{Colors.YELLOW}Manage your buildings and customize your property{Colors.END}\n"
            )

            print(
                f"Comfort Points: {Colors.CYAN}{self.player.comfort_points}{Colors.END}\n"
            )

            # Display building categories
            building_types = {
                "house": {
                    "label": "House",
                    "slots": 3
                },
                "decoration": {
                    "label": "Decoration",
                    "slots": 10
                },
                "fencing": {
                    "label": "Fencing",
                    "slots": 1
                },
                "garden": {
                    "label": "Garden",
                    "slots": 3
                },
                "farm": {
                    "label": "Farm",
                    "slots": 2
                },
                "farming": {
                    "label": "Farming",
                    "slots": 2
                },
                "training_place": {
                    "label": "Training Place",
                    "slots": 3
                },
            }
            for b_type, info in building_types.items():
                print(f"{Colors.BOLD}{info['label']} Slots:{Colors.END}")
                for i in range(1, info["slots"] + 1):
                    slot = f"{b_type}_{i}"
                    item_id = self.player.building_slots.get(slot)
                    if item_id is not None and item_id in self.housing_data:
                        item = self.housing_data[item_id]
                        rarity_color = get_rarity_color(
                            item.get('rarity', 'common'))
                        print(
                            f"  {slot}: {rarity_color}{item.get('name', item_id)}{Colors.END}"
                        )
                    else:
                        print(f"  {slot}: {Colors.GRAY}Empty{Colors.END}")
                print()

            print(self.lang.get("options_1"))
            print(f"1. {self.lang.get('place_item_slot')}")
            print(f"2. {self.lang.get('remove_item_slot')}")
            print(f"3. {self.lang.get('view_home_status')}")
            print(f"B. {self.lang.get('back')}")

            choice = ask(
                f"\n{Colors.CYAN}Choose option: {Colors.END}").strip().upper()

            if choice == 'B':
                break
            elif choice == '1':
                self._place_housing_item()
            elif choice == '2':
                self.remove_housing_item()
            elif choice == '3':
                self.view_home_status()
            else:
                print(self.lang.get("invalid_choice_1"))
                time.sleep(1)

    def view_home_status(self):
        """View detailed home status and statistics"""
        if not self.player:
            return

        print(self.lang.get("n_home_details"))
        print(
            f"\nComfort Points: {Colors.CYAN}{self.player.comfort_points}{Colors.END}"
        )
        placed_items = [
            item_id for item_id in self.player.building_slots.values()
            if item_id is not None
        ]
        print(f"Total Items Placed: {len(placed_items)}")
        print(f"Unique Items Placed: {len(set(placed_items))}")

        # Calculate comfort distribution
        print(self.lang.get("nitem_breakdown"))
        item_comforts = {}
        for item_id in placed_items:
            item_data = self.housing_data.get(item_id, {})
            name = item_data.get("name", item_id)
            comfort = item_data.get("comfort_points", 0)

            if name not in item_comforts:
                item_comforts[name] = {"count": 0, "total_comfort": 0}
            item_comforts[name]["count"] += 1
            item_comforts[name]["total_comfort"] += comfort

        # Sort by total comfort contribution
        sorted_items = sorted(item_comforts.items(),
                              key=lambda x: x[1]["total_comfort"],
                              reverse=True)

        total_displayed = 0
        for name, info in sorted_items[:10]:  # Show top 10
            print(
                f"  {name}: x{info['count']} = +{info['total_comfort']} comfort"
            )
            total_displayed += 1

        if len(sorted_items) > 10:
            remaining_comfort = sum(info["total_comfort"]
                                    for _, info in sorted_items[10:])
            print(
                f"  ... and {len(sorted_items) - 10} more items (+{remaining_comfort} comfort)"
            )

        ask("\nPress Enter to continue...")

    def remove_housing_item(self):
        """Remove a housing item from a slot"""
        if not self.player:
            return
        occupied_slots = [
            slot for slot, item_id in self.player.building_slots.items()
            if item_id is not None
        ]

        if not occupied_slots:
            print(self.lang.get("no_items_to_remove"))
            return

        print(self.lang.get("nplaced_items"))
        for i, slot in enumerate(occupied_slots, 1):
            item_id = self.player.building_slots[slot]
            if item_id in self.housing_data:
                item = self.housing_data[item_id]
                rarity_color = get_rarity_color(item.get('rarity', 'common'))
                print(
                    f"{i}. {slot}: {rarity_color}{item.get('name', item_id)}{Colors.END}"
                )

        choice = ask(
            f"\nChoose item to remove (1-{len(occupied_slots)}) or press Enter to cancel: "
        ).strip()

        if not choice:
            return

        if not choice.isdigit():
            print(self.lang.get("invalid_choice"))
            return

        idx = int(choice) - 1
        if not (0 <= idx < len(occupied_slots)):
            print(self.lang.get("invalid_item_number"))
            return

        target_slot = occupied_slots[idx]
        item_id = self.player.building_slots[target_slot]

        # Remove the item
        self.player.building_slots[target_slot] = None

        # Update comfort
        if item_id is not None:
            item = self.housing_data.get(item_id)
        else:
            item = None
        if item:
            self.player.comfort_points -= item.get('comfort_points', 0)

        print(f"{Colors.YELLOW}Removed item from {target_slot}.{Colors.END}")
        input(self.lang.get("press_enter"))

    def _place_housing_item(self):
        """Place a housing item in a slot"""
        if not self.player:
            return
        if not self.player.housing_owned:
            print(self.lang.get("no_housing_items"))
            return

        print(self.lang.get("navailable_items"))
        for i, item_id in enumerate(self.player.housing_owned, 1):
            if item_id in self.housing_data:
                item = self.housing_data[item_id]
                rarity_color = get_rarity_color(item.get('rarity', 'common'))
                print(
                    f"{i}. {rarity_color}{item.get('name', item_id)}{Colors.END} ({item.get('type', 'misc')})"
                )

        choice = ask(
            f"\nChoose item (1-{len(self.player.housing_owned)}) or press Enter to cancel: "
        ).strip()

        if not choice:
            return

        if not choice.isdigit():
            print(self.lang.get("invalid_choice"))
            return

        idx = int(choice) - 1
        if not (0 <= idx < len(self.player.housing_owned)):
            print(self.lang.get("invalid_item_number"))
            return

        item_id = self.player.housing_owned[idx]
        item = self.housing_data.get(item_id)

        if not item:
            print(self.lang.get("item_data_not_found"))
            return

        item_type = item.get('type', 'decoration')

        # Find available slots for this item type
        available_slots = []
        if item_type == 'house':
            available_slots = [f"house_{i}" for i in range(1, 4)]
        elif item_type == 'decoration':
            available_slots = [f"decoration_{i}" for i in range(1, 11)]
        elif item_type == 'fencing':
            available_slots = ['fencing_1']
        elif item_type == 'garden':
            available_slots = [f"garden_{i}" for i in range(1, 4)]
        elif item_type == 'training_place':
            available_slots = [f"training_place_{i}" for i in range(1, 4)]
        elif item_type == 'farming':
            available_slots = [f"farm_{i}" for i in range(1, 3)]
        elif item_type == 'crafting':
            available_slots = ['crafting_1']
        elif item_type == 'storage':
            available_slots = ['storage_1']

        # Filter to slots that are empty
        empty_slots = [
            slot for slot in available_slots
            if self.player.building_slots.get(slot) is None
        ]

        if not empty_slots:
            print(f"No available slots for {item_type} items.")
            return

        print(f"\nAvailable slots for {item_type}:")
        for i, slot in enumerate(empty_slots, 1):
            print(f"{i}. {slot}")

        slot_choice = ask(
            f"\nChoose slot (1-{len(empty_slots)}) or press Enter to cancel: "
        ).strip()

        if not slot_choice:
            return

        if not slot_choice.isdigit():
            print(self.lang.get("invalid_choice"))
            return

        slot_idx = int(slot_choice) - 1
        if not (0 <= slot_idx < len(empty_slots)):
            print(self.lang.get("invalid_slot_number"))
            return

        target_slot = empty_slots[slot_idx]

        # Place the item
        self.player.building_slots[target_slot] = item_id

        # Update comfort
        if item:
            self.player.comfort_points += item.get('comfort_points', 0)

        print(
            f"{Colors.GREEN}Placed {item.get('name', item_id)} in {target_slot}!{Colors.END}"
        )
        input(self.lang.get("press_enter"))

    def build_structures(self):
        """Build and manage structures on your land"""
        if not self.player:
            print(self.lang.get("no_character"))
            return

        while True:
            clear_screen()
            print(
                f"\n{Colors.BOLD}{Colors.CYAN}=== BUILD STRUCTURES ==={Colors.END}"
            )
            print(
                f"{Colors.YELLOW}Manage your buildings and customize your property{Colors.END}\n"
            )

            # Display building categories
            building_types = {
                "house": {
                    "label": "House",
                    "slots": 3,
                    "max_owned": 0
                },
                "decoration": {
                    "label": "Decoration",
                    "slots": 10,
                    "max_owned": 0
                },
                "fencing": {
                    "label": "Fencing",
                    "slots": 1,
                    "max_owned": 0
                },
                "garden": {
                    "label": "Garden",
                    "slots": 3,
                    "max_owned": 0
                },
                "farm": {
                    "label": "Farm",
                    "slots": 2,
                    "max_owned": 0
                },
                "farming": {
                    "label": "Farming",
                    "slots": 2,
                    "max_owned": 0
                },
                "training_place": {
                    "label": "Training Place",
                    "slots": 3,
                    "max_owned": 0
                },
            }

            # Count occupied slots and available items for each type
            placed_items = {b_type: 0 for b_type in building_types}
            available_items = {b_type: [] for b_type in building_types}

            for slot_name, item_id in self.player.building_slots.items():
                if item_id:
                    # Extract type from slot name (e.g., "house_1" -> "house")
                    b_type = slot_name.rsplit('_', 1)[0]
                    if b_type in placed_items:
                        placed_items[b_type] += 1

            # Get available items from inventory
            for item_id in self.player.housing_owned:
                item_data = self.housing_data.get(item_id, {})
                item_type = item_data.get("type", "decoration")
                available_items[item_type].append({
                    "id": item_id,
                    "data": item_data
                })

            # Display building slots
            menu_idx = 1
            print(self.lang.get("building_slotsn"))

            for b_type, info in building_types.items():
                placed = placed_items.get(b_type, 0)
                max_slots = info["slots"]
                status_color = Colors.GREEN if placed > 0 else Colors.DARK_GRAY

                print(
                    f"{Colors.CYAN}{menu_idx}.{Colors.END} {Colors.BOLD}{info['label']}{Colors.END} [{status_color}{placed}/{max_slots}{Colors.END}]"
                )
                menu_idx += 1

            print(self.lang.get("nq_quit"))
            choice = ask(
                f"\n{Colors.CYAN}Choose a building type to manage: {Colors.END}"
            ).strip().upper()

            if choice == 'Q':
                break

            if choice.isdigit():
                idx = int(choice) - 1
                types_list = list(building_types.keys())
                if 0 <= idx < len(types_list):
                    self.manage_building_slots(
                        types_list[idx], building_types[types_list[idx]],
                        available_items[types_list[idx]])

    def manage_building_slots(self, b_type: str, b_info: Dict,
                              available_items: List[Dict]):
        """Manage slots for a specific building type"""
        if not self.player:
            print(self.lang.get("no_character"))
            return

        while True:
            clear_screen()
            print(
                f"\n{Colors.BOLD}{Colors.CYAN}=== {b_info['label'].upper()} SLOTS ==={Colors.END}"
            )
            print(
                f"{Colors.YELLOW}Manage your {b_info['label'].lower()} placements{Colors.END}\n"
            )

            max_slots = b_info["slots"]

            # Display all slots for this type
            print(self.lang.get("slots"))
            slot_list = []
            for i in range(1, max_slots + 1):
                slot_name = f"{b_type}_{i}"
                item_id = self.player.building_slots.get(slot_name)

                if item_id:
                    item_data = self.housing_data.get(item_id, {})
                    item_name = item_data.get("name", item_id)
                    item_price = item_data.get("price", 0)
                    swap_cost = int(item_price * 0.1)
                    print(
                        f"{Colors.CYAN}{i}.{Colors.END} [{Colors.GREEN}✓{Colors.END}] {Colors.BOLD}{Colors.YELLOW}{item_name}{Colors.END}"
                    )
                    print(
                        f"   Swap cost: {Colors.GOLD}{swap_cost} gold{Colors.END} (10% of {item_price})"
                    )
                else:
                    print(
                        f"{Colors.CYAN}{i}.{Colors.END} [{Colors.DARK_GRAY}-{Colors.END}] {Colors.DARK_GRAY}Empty{Colors.END}"
                    )

                slot_list.append(slot_name)

            print(
                f"\n{Colors.YELLOW}Available items in inventory: {len(available_items)}{Colors.END}"
            )

            for idx, item in enumerate(available_items[:3],
                                       1):  # Show first 3 available
                item_name = item["data"].get("name", item["id"])
                item_comfort = item["data"].get("comfort_points", 0)
                print(
                    f"  • {Colors.BOLD}{item_name}{Colors.END} (+{Colors.CYAN}{item_comfort}{Colors.END} comfort)"
                )

            if len(available_items) > 3:
                print(
                    f"  • {Colors.DARK_GRAY}... and {len(available_items) - 3} more items{Colors.END}"
                )

            print(f"\n{Colors.CYAN}1-{max_slots}.{Colors.END} Manage slot")
            print(self.lang.get("b_back_to_land_menu"))

            choice = ask(
                f"\n{Colors.CYAN}Choose action: {Colors.END}").strip().upper()

            if choice == 'B':
                break
            elif choice.isdigit():
                slot_idx = int(choice) - 1
                if 0 <= slot_idx < len(slot_list):
                    self.manage_slot(slot_list[slot_idx], available_items)

    def manage_slot(self, slot_name: str, available_items: List[Dict]):
        """Manage a specific building slot"""
        if not self.player:
            print(self.lang.get("no_character"))
            return

        current_item = self.player.building_slots.get(slot_name)

        while True:
            clear_screen()
            print(
                f"\n{Colors.BOLD}{Colors.CYAN}=== MANAGE {slot_name.upper()} ==={Colors.END}"
            )

            if current_item:
                current_data = self.housing_data.get(current_item, {})
                current_name = current_data.get("name", current_item)
                current_price = current_data.get("price", 0)
                swap_cost = int(current_price * 0.1)

                print(
                    f"{Colors.BOLD}Current item:{Colors.END} {Colors.YELLOW}{current_name}{Colors.END}"
                )
                print(
                    f"Swap cost: {Colors.GOLD}{swap_cost} gold{Colors.END}\n")
            else:
                print(self.lang.get("current_item_emptyn"))

            print(self.lang.get("available_items_to_placen"))

            for idx, item in enumerate(available_items, 1):
                item_id = item["id"]
                item_data = item["data"]
                item_name = item_data.get("name", item_id)
                item_comfort = item_data.get("comfort_points", 0)
                item_price = item_data.get("price", 0)
                swap_cost = int(item_price * 0.1)

                print(
                    f"{Colors.CYAN}{idx}.{Colors.END} {Colors.BOLD}{Colors.YELLOW}{item_name}{Colors.END}"
                )
                print(
                    f"   Comfort: {Colors.CYAN}+{item_comfort}{Colors.END} | Swap cost: {Colors.GOLD}{swap_cost}g{Colors.END}"
                )

            print(self.lang.get("nc_clear_this_slot"))
            print(self.lang.get("b_back"))

            choice = ask(
                f"\n{Colors.CYAN}Select item to place or action: {Colors.END}"
            ).strip().upper()

            if choice == 'B':
                break
            elif choice == 'C':
                if current_item:
                    self.player.building_slots[slot_name] = None
                    print(self.lang.get("n_slot_cleared"))
                    input(self.lang.get("press_enter"))
                    break
                else:
                    print(
                        f"\n{Colors.YELLOW}Slot is already empty.{Colors.END}")
                    input(self.lang.get("press_enter"))
            elif choice.isdigit():
                item_idx = int(choice) - 1
                if 0 <= item_idx < len(available_items):
                    selected_item = available_items[item_idx]

                    # Calculate cost
                    if current_item:
                        current_price = self.housing_data.get(
                            current_item, {}).get("price", 0)
                        swap_cost = int(current_price * 0.1)
                    else:
                        swap_cost = 0

                    # Check if player can afford
                    if self.player.gold >= swap_cost:
                        if swap_cost > 0:
                            self.player.gold -= swap_cost
                            print(
                                f"\n{Colors.GREEN}✓ Paid {Colors.GOLD}{swap_cost} gold{Colors.GREEN} to swap.{Colors.END}"
                            )

                        old_item = current_item
                        self.player.building_slots[slot_name] = selected_item[
                            "id"]

                        # Update comfort points
                        if old_item:
                            old_comfort = self.housing_data.get(
                                old_item, {}).get("comfort_points", 0)
                            self.player.comfort_points -= old_comfort

                        new_comfort = selected_item["data"].get(
                            "comfort_points", 0)
                        self.player.comfort_points += new_comfort

                        item_name = selected_item["data"].get(
                            "name", selected_item["id"])
                        print(
                            f"{Colors.GREEN}✓ Placed {Colors.BOLD}{item_name}{Colors.END}{Colors.GREEN} in {slot_name}!{Colors.END}"
                        )
                        print(
                            f"Total comfort: {Colors.CYAN}{self.player.comfort_points}{Colors.END}"
                        )
                        input(self.lang.get("press_enter"))
                        break
                    else:
                        needed = swap_cost - self.player.gold
                        print(
                            f"\n{Colors.RED}✗ Not enough gold! Need {needed} more.{Colors.END}"
                        )
                        input(self.lang.get("press_enter"))

    def farm(self):
        """Farm crops on your land"""
        if not self.player:
            print(self.lang.get("no_character"))
            return

        # Check if player has any farm buildings
        has_farm = any(
            self.player.building_slots.get(f"farm_{i}") is not None
            for i in range(1, 3))

        if not has_farm:
            print(
                f"\n{Colors.YELLOW}You need to build a farm first! Use the 'Build Structures' option.{Colors.END}"
            )
            input(self.lang.get("press_enter"))
            return

        while True:
            clear_screen()
            print(self.lang.get("n_farming"))
            print(
                f"{Colors.YELLOW}Tend to your crops and harvest your bounty{Colors.END}\n"
            )

            # Show available crops to plant
            crops_data = self.farming_data.get("crops", {})

            print(self.lang.get("available_crops_to_plantn"))
            crops_list = list(crops_data.items())
            for idx, (crop_id, crop_data) in enumerate(crops_list, 1):
                name = crop_data.get("name", crop_id)
                description = crop_data.get("description", "")
                growth_time = crop_data.get("growth_time", 0)
                harvest = crop_data.get("harvest_amount", 0)
                print(
                    f"{Colors.CYAN}{idx}.{Colors.END} {Colors.BOLD}{name}{Colors.END}"
                )
                print(f"   {description}")
                print(
                    f"   Growth: {Colors.YELLOW}{growth_time} days{Colors.END} | Harvest: {Colors.GREEN}+{harvest}{Colors.END}\n"
                )

            print(self.lang.get("farm_statusn"))

            # Show farm plot status
            for farm_idx in range(1, 3):
                farm_slot = f"farm_{farm_idx}"
                has_building = self.player.building_slots.get(
                    farm_slot) is not None

                if has_building:
                    print(
                        f"{Colors.GOLD}Farm Plot {farm_idx}:{Colors.END} {Colors.GREEN}✓ Active{Colors.END}"
                    )
                    plots = self.player.farm_plots.get(farm_slot, [])
                    if plots:
                        for plant_idx, plant in enumerate(plots, 1):
                            crop_name = self.farming_data.get("crops", {}).get(
                                plant.get("crop"),
                                {}).get("name", plant.get("crop"))
                            days_left = plant.get("days_left", 0)
                            if days_left > 0:
                                print(
                                    f"  {plant_idx}. {crop_name} - {Colors.YELLOW}{days_left} days{Colors.END} until ready"
                                )
                            else:
                                print(
                                    f"  {plant_idx}. {crop_name} - {Colors.GREEN}Ready to harvest!{Colors.END}"
                                )
                    else:
                        print(
                            f"  {Colors.GRAY}Empty - Ready to plant{Colors.END}"
                        )
                else:
                    print(
                        f"Farm Plot {farm_idx}: {Colors.DARK_GRAY}Not built{Colors.END}"
                    )
                print()

            print(
                f"{Colors.CYAN}1-{len(crops_list)}.{Colors.END} Plant a crop")
            print(self.lang.get("h_harvest_crops"))
            print(self.lang.get("v_view_inventory"))
            print(self.lang.get("b_back_1"))

            choice = ask(
                f"\n{Colors.CYAN}Choose action: {Colors.END}").strip().upper()

            if choice == 'B':
                break
            elif choice == 'H':
                self.harvest_crops()
            elif choice == 'V':
                self.view_farming_inventory()
            elif choice.isdigit():
                crop_idx = int(choice) - 1
                if 0 <= crop_idx < len(crops_list):
                    self.plant_crop(crops_list[crop_idx])

    def plant_crop(self, crop_tuple):
        """Plant a specific crop in an available farm plot"""
        if not self.player:
            return

        crop_id, crop_data = crop_tuple
        crop_name = crop_data.get("name", crop_id)
        growth_time = crop_data.get("growth_time", 0)

        # Select which farm to plant in
        clear_screen()
        print(
            f"\n{Colors.BOLD}{Colors.CYAN}=== PLANT {crop_name.upper()} ==={Colors.END}\n"
        )
        print(self.lang.get("select_farm_plot"))

        farm_choices = []
        for farm_idx in range(1, 3):
            farm_slot = f"farm_{farm_idx}"
            has_building = self.player.building_slots.get(
                farm_slot) is not None

            if has_building:
                plots = self.player.farm_plots.get(farm_slot, [])
                plant_count = len(plots)
                max_plots = self.farming_data.get("max_plots_per_farm", 3)

                print(
                    f"{len(farm_choices) + 1}. Farm Plot {farm_idx} - {Colors.GREEN}{plant_count}/{max_plots} plants{Colors.END}"
                )
                farm_choices.append(farm_slot)

        if not farm_choices:
            print(self.lang.get("no_active_farms_available"))
            input(self.lang.get("press_enter"))
            return

        choice = ask(
            f"\nChoose farm (1-{len(farm_choices)}) or press Enter to cancel: "
        ).strip()

        if choice and choice.isdigit():
            farm_choice_idx = int(choice) - 1
            if 0 <= farm_choice_idx < len(farm_choices):
                farm_slot = farm_choices[farm_choice_idx]

                # Add plant to farm
                if farm_slot not in self.player.farm_plots:
                    self.player.farm_plots[farm_slot] = []

                max_plots = self.farming_data.get("max_plots_per_farm", 3)
                if len(self.player.farm_plots[farm_slot]) < max_plots:
                    self.player.farm_plots[farm_slot].append({
                        "crop":
                        crop_id,
                        "days_left":
                        growth_time
                    })
                    print(
                        f"\n{Colors.GREEN}✓ Planted {crop_name} in {farm_slot}!{Colors.END}"
                    )
                    print(
                        f"It will be ready to harvest in {Colors.YELLOW}{growth_time} days{Colors.END}"
                    )
                else:
                    print(
                        f"\n{Colors.YELLOW}This farm plot is full! ({max_plots}/{max_plots} plants){Colors.END}"
                    )

                input(self.lang.get("press_enter"))

    def harvest_crops(self):
        """Harvest ready crops from farm plots"""
        if not self.player:
            return

        clear_screen()
        print(
            f"\n{Colors.BOLD}{Colors.CYAN}=== HARVEST CROPS ==={Colors.END}\n")

        harvested = False
        for farm_idx in range(1, 3):
            farm_slot = f"farm_{farm_idx}"
            plots = self.player.farm_plots.get(farm_slot, [])

            if not plots:
                continue

            crops_to_remove = []
            for plant_idx, plant in enumerate(plots):
                crop_id = plant.get("crop")
                days_left = plant.get("days_left", 0)

                if days_left <= 0:
                    crop_data = self.farming_data.get("crops",
                                                      {}).get(crop_id, {})
                    crop_name = crop_data.get("name", crop_id)
                    harvest_amount = crop_data.get("harvest_amount", 1)

                    # Add crops to inventory
                    for _ in range(harvest_amount):
                        self.player.inventory.append(crop_name)

                    print(
                        f"{Colors.GREEN}✓ Harvested {Colors.BOLD}{harvest_amount}x {crop_name}{Colors.END}{Colors.GREEN} from {farm_slot}!{Colors.END}"
                    )
                    crops_to_remove.append(plant_idx)
                    harvested = True

            # Remove harvested crops (in reverse to maintain indices)
            for idx in reversed(crops_to_remove):
                plots.pop(idx)

        if not harvested:
            print(
                f"{Colors.YELLOW}No crops are ready to harvest yet.{Colors.END}"
            )

        input(self.lang.get("press_enter"))

    def view_farming_inventory(self):
        """View crops in inventory"""
        if not self.player:
            return

        clear_screen()
        print(
            f"\n{Colors.BOLD}{Colors.CYAN}=== FARMING INVENTORY ==={Colors.END}\n"
        )

        crops_data = self.farming_data.get("crops", {})
        crop_names = {
            crop_data.get("name"): crop_id
            for crop_id, crop_data in crops_data.items()
        }

        # Count crops in inventory
        crop_counts = {}
        for item in self.player.inventory:
            if item in crop_names:
                crop_counts[item] = crop_counts.get(item, 0) + 1

        if crop_counts:
            print(self.lang.get("crops_in_inventoryn"))
            for crop_name, count in crop_counts.items():
                crop_id = crop_names[crop_name]
                crop_data = crops_data.get(crop_id, {})
                sell_price = crop_data.get("sell_price", 0)

                print(
                    f"{Colors.GREEN}✓{Colors.END} {Colors.BOLD}{crop_name}{Colors.END} x{count}"
                )
                print(
                    f"  Sell price: {Colors.GOLD}{sell_price}g{Colors.END} each | Total: {Colors.GOLD}{sell_price * count}g{Colors.END}\n"
                )

            print(self.lang.get("s_sell_crops"))
            print(self.lang.get("c_cook_crops_alchemy"))
            print(self.lang.get("b_back_2"))

            choice = ask(
                f"\n{Colors.CYAN}Choose action: {Colors.END}").strip().upper()

            if choice == 'S':
                self.sell_crops()
            elif choice == 'C':
                self.visit_alchemy()  # Reuse existing alchemy system
        else:
            print(
                f"{Colors.YELLOW}You have no crops in your inventory yet.{Colors.END}"
            )
            input(self.lang.get("press_enter"))

    def sell_crops(self):
        """Sell crops for gold"""
        if not self.player:
            return

        clear_screen()
        print(self.lang.get("n_sell_crops_n"))

        crops_data = self.farming_data.get("crops", {})
        crop_names = {
            crop_data.get("name"): crop_id
            for crop_id, crop_data in crops_data.items()
        }

        # Count crops
        crop_counts = {}
        for item in self.player.inventory:
            if item in crop_names:
                crop_counts[item] = crop_counts.get(item, 0) + 1

        total_gold = 0
        for crop_name, count in crop_counts.items():
            crop_id = crop_names[crop_name]
            crop_data = crops_data.get(crop_id, {})
            sell_price = crop_data.get("sell_price", 0)
            subtotal = sell_price * count
            total_gold += subtotal

            print(
                f"{crop_name} x{count}: {Colors.GOLD}{subtotal}g{Colors.END}")

            # Remove from inventory
            for _ in range(count):
                self.player.inventory.remove(crop_name)

        self.player.gold += total_gold
        print(
            f"\n{Colors.GREEN}✓ Sold all crops for {Colors.GOLD}{total_gold} gold{Colors.END}{Colors.GREEN}!{Colors.END}"
        )
        print(f"Total gold: {Colors.GOLD}{self.player.gold}{Colors.END}")
        input(self.lang.get("press_enter"))

    def training(self):
        """Training system for improving stats using training_place buildings"""
        if not self.player:
            print(self.lang.get("no_character"))
            return

        # Check if player has any training_place buildings
        has_training_place = any(
            self.player.building_slots.get(f"training_place_{i}") is not None
            for i in range(1, 4))

        if not has_training_place:
            print(
                f"\n{Colors.YELLOW}You need to build a Training Place first! Use the 'Build Structures' option.{Colors.END}"
            )
            input(self.lang.get("press_enter"))
            return

        # Calculate training effectiveness based on buildings
        training_bonus = self._calculate_training_effectiveness()

        while True:
            clear_screen()
            print(
                f"\n{Colors.BOLD}{Colors.CYAN}=== TRAINING GROUND ==={Colors.END}"
            )
            print(
                f"{Colors.YELLOW}Train to improve your stats! Each training session affects all your stats.{Colors.END}\n"
            )

            # Show training facility info
            self._display_training_facilities()

            print(self.lang.get("current_stats_1"))
            print(
                f"HP: {Colors.RED}{self.player.max_hp}{Colors.END} | MP: {Colors.BLUE}{self.player.max_mp}{Colors.END}"
            )
            print(
                f"Attack: {Colors.RED}{self.player.attack}{Colors.END} | Defense: {Colors.GREEN}{self.player.defense}{Colors.END} | Speed: {Colors.YELLOW}{self.player.speed}{Colors.END}\n"
            )

            print(self.lang.get("training_typesn"))
            print(self.lang.get("1_morning_training_1d4"))
            print(
                f"   {Colors.GREEN}4: +4%{Colors.END} | {Colors.YELLOW}3: +2%{Colors.END} | {Colors.RED}1-2: -1%{Colors.END}"
            )
            print()
            print(self.lang.get("2_calm_training_1d6"))
            print(
                f"   {Colors.GREEN}6: +13%{Colors.END} | {Colors.GREEN}5: +10%{Colors.END} | {Colors.YELLOW}4: +7%{Colors.END} | {Colors.YELLOW}3: +1%{Colors.END} | {Colors.RED}1-2: -3%{Colors.END}"
            )
            print()
            print(self.lang.get("3_normal_training_1d8"))
            print(
                f"   {Colors.GREEN}5-8: +10%{Colors.END} | {Colors.RED}1-3: -7%{Colors.END}"
            )
            print()
            print(self.lang.get("4_intense_training_1d20"))
            print(
                f"   {Colors.GREEN}16-20: +20%{Colors.END} | {Colors.GREEN}11-15: +15%{Colors.END} | {Colors.YELLOW}10: +10%{Colors.END} | {Colors.RED}5-9: -10%{Colors.END} | {Colors.RED}1-4: -20%{Colors.END}"
            )
            print()
            print(self.lang.get("b_back_3"))

            choice = ask(f"\n{Colors.CYAN}Choose training type: {Colors.END}"
                         ).strip().upper()

            if choice == 'B':
                break

            if choice in ['1', '2', '3', '4']:
                training_types = {
                    '1': ('Morning Training', 4, lambda roll: 4
                          if roll == 4 else 2 if roll == 3 else -1),
                    '2': ('Calm Training', 6, lambda roll: 13
                          if roll == 6 else 10 if roll == 5 else 7
                          if roll == 4 else 1 if roll == 3 else -3),
                    '3': ('Normal Training', 8, lambda roll: 10
                          if roll >= 4 else -7),
                    '4': ('Intense Training', 20, lambda roll: 20
                          if roll >= 16 else 15 if roll >= 11 else 10
                          if roll == 10 else -10 if roll >= 5 else -20)
                }

                name, dice_sides, calc_bonus = training_types[choice]

                # Roll the dice
                roll = random.randint(1, dice_sides)
                base_bonus_percent = calc_bonus(roll)

                # Apply training facility bonus
                final_bonus_percent = base_bonus_percent * training_bonus

                print(
                    f"\n{Colors.BOLD}{Colors.CYAN}=== {name.upper()} ==={Colors.END}"
                )
                print(
                    f"You rolled a {Colors.YELLOW}{roll}{Colors.END} on a d{dice_sides}!"
                )

                if training_bonus > 1.0:
                    bonus_description = f" (x{training_bonus:.1f} from facilities)"
                elif training_bonus < 1.0:
                    bonus_description = f" (x{training_bonus:.1f} from poor facilities)"
                else:
                    bonus_description = ""

                if final_bonus_percent > 0:
                    print(
                        f"{Colors.GREEN}Success!{Colors.END} All stats increase by {Colors.GREEN}+{final_bonus_percent:.1f}%{Colors.END}{bonus_description}"
                    )
                elif final_bonus_percent < 0:
                    print(
                        f"{Colors.RED}Training failed!{Colors.END} All stats decrease by {Colors.RED}{abs(final_bonus_percent):.1f}%{Colors.END}{bonus_description}"
                    )
                else:
                    print(self.lang.get("no_change_in_stats"))

                # Calculate stat changes
                old_stats = {
                    'max_hp': self.player.max_hp,
                    'max_mp': self.player.max_mp,
                    'attack': self.player.attack,
                    'defense': self.player.defense,
                    'speed': self.player.speed
                }

                # Apply percentage changes
                if final_bonus_percent != 0:
                    percent_multiplier = 1 + (final_bonus_percent / 100)

                    self.player.max_hp = max(
                        1, int(self.player.max_hp * percent_multiplier))
                    self.player.max_mp = max(
                        1, int(self.player.max_mp * percent_multiplier))
                    self.player.attack = max(
                        1, int(self.player.attack * percent_multiplier))
                    self.player.defense = max(
                        1, int(self.player.defense * percent_multiplier))
                    self.player.speed = max(
                        1, int(self.player.speed * percent_multiplier))

                    # Ensure current HP/MP don't exceed new maxes
                    self.player.hp = min(self.player.hp, self.player.max_hp)
                    self.player.mp = min(self.player.mp, self.player.max_mp)

                print(self.lang.get("nstat_changes"))
                print(
                    f"HP: {Colors.RED}{old_stats['max_hp']} → {self.player.max_hp}{Colors.END}"
                )
                print(
                    f"MP: {Colors.BLUE}{old_stats['max_mp']} → {self.player.max_mp}{Colors.END}"
                )
                print(
                    f"Attack: {Colors.RED}{old_stats['attack']} → {self.player.attack}{Colors.END}"
                )
                print(
                    f"Defense: {Colors.GREEN}{old_stats['defense']} → {self.player.defense}{Colors.END}"
                )
                print(
                    f"Speed: {Colors.YELLOW}{old_stats['speed']} → {self.player.speed}{Colors.END}"
                )

                input(self.lang.get('press_enter'))
            else:
                print(self.lang.get("invalid_choice_2"))
                time.sleep(1)

    def _calculate_training_effectiveness(self) -> float:
        """Calculate training effectiveness multiplier based on training facilities"""
        if not self.player:
            return 1.0

        total_comfort = 0
        facility_count = 0
        rarity_multipliers = {
            'common': 1.0,
            'uncommon': 1.2,
            'rare': 1.4,
            'epic': 1.6,
            'legendary': 1.8
        }

        # Check all training_place slots
        for i in range(1, 4):
            slot = f"training_place_{i}"
            building_id = self.player.building_slots.get(slot)

            if building_id and building_id in self.housing_data:
                building = self.housing_data[building_id]
                comfort = building.get('comfort_points', 0)
                rarity = building.get('rarity', 'common')

                # Apply rarity multiplier to comfort points
                rarity_mult = rarity_multipliers.get(rarity, 1.0)
                effective_comfort = comfort * rarity_mult

                total_comfort += effective_comfort
                facility_count += 1

        if facility_count == 0:
            return 1.0

        # Calculate average effective comfort
        avg_comfort = total_comfort / facility_count

        # Convert comfort to training multiplier
        # Base multiplier of 1.0, +0.1 per 10 comfort points
        base_multiplier = 1.0
        comfort_bonus = avg_comfort / 10 * 0.1

        return base_multiplier + comfort_bonus

    def _display_training_facilities(self):
        """Display information about the player's training facilities"""
        if not self.player:
            return

        print(self.lang.get("training_facilities_1"))

        facilities = []
        for i in range(1, 4):
            slot = f"training_place_{i}"
            building_id = self.player.building_slots.get(slot)

            if building_id and building_id in self.housing_data:
                building = self.housing_data[building_id]
                name = building.get('name', building_id)
                rarity = building.get('rarity', 'common')
                comfort = building.get('comfort_points', 0)

                # Color code by rarity
                rarity_colors = {
                    'common': Colors.GRAY,
                    'uncommon': Colors.GREEN,
                    'rare': Colors.BLUE,
                    'epic': Colors.MAGENTA,
                    'legendary': Colors.GOLD
                }

                color = rarity_colors.get(rarity, Colors.WHITE)
                facilities.append(
                    f"{color}{name} ({rarity}, {comfort} comfort){Colors.END}")

        if facilities:
            for facility in facilities:
                print(f"  • {facility}")

            effectiveness = self._calculate_training_effectiveness()
            if effectiveness > 1.0:
                print(
                    f"  {Colors.GREEN}Training Effectiveness: x{effectiveness:.1f} (better facilities = better results){Colors.END}"
                )
            elif effectiveness < 1.0:
                print(
                    f"  {Colors.YELLOW}Training Effectiveness: x{effectiveness:.1f} (upgrade facilities for better results){Colors.END}"
                )
            else:
                print(
                    f"  {Colors.GRAY}Training Effectiveness: x{effectiveness:.1f}{Colors.END}"
                )
        else:
            print(self.lang.get("no_training_facilities_built"))

        print()

    def visit_tavern(self):
        """Visit the tavern to hire companions."""
        if not self.player:
            print(self.lang.get("no_character"))
            return

        print(self.lang.get("n_tavern"))
        print(
            "Welcome to The Rusty Tankard. Here you can hire companions to join your party."
        )
        print(f"Your gold: {Colors.GOLD}{self.player.gold}{Colors.END}")

        companions = list(self.companions_data.items())
        if not companions:
            print(self.lang.get('no_companions_available'))
            return

        page_size = 6
        current_page = 0

        while True:
            start = current_page * page_size
            end = start + page_size
            page_items = companions[start:end]

            print(
                f"\n--- Page {current_page + 1} of {(len(companions) + page_size - 1) // page_size} ---"
            )
            for i, (cid, cdata) in enumerate(page_items, 1):
                price = cdata.get('price', '?')
                desc = cdata.get('description', '')
                print(
                    f"{i}. {cdata.get('name', cid)} - {Colors.GOLD}{price} gold{Colors.END}"
                )
                print(f"   {desc}")

            print(self.lang.get('ui_shortcuts_nav'))
            choice = ask(
                f"\nHire companion (1-{len(page_items)}) or press Enter to leave: "
            )

            if not choice:
                break
            elif choice.lower() == 'n':
                if end < len(companions):
                    current_page += 1
                else:
                    print(self.lang.get('ui_no_more_pages'))
            elif choice.lower() == 'p':
                if current_page > 0:
                    current_page -= 1
                else:
                    print(self.lang.get('ui_already_first_page'))
            elif choice.isdigit():
                idx = int(choice) - 1
                if 0 <= idx < len(page_items):
                    cid, cdata = page_items[idx]
                    price = cdata.get('price', 0)
                    if self.player.gold >= price:
                        if len(self.player.companions) >= 4:
                            print(
                                "You already have the maximum number of companions (4)."
                            )
                            continue
                        self.player.gold -= price
                        # Create companion data with equipment and level
                        companion_data = {
                            "id": cid,
                            "name": cdata.get('name', cid),
                            "level": 1,
                            "equipment": {
                                "weapon": None,
                                "armor": None,
                                "accessory": None
                            }
                        }
                        self.player.companions.append(companion_data)
                        print(
                            f"Hired {cdata.get('name', cid)} for {price} gold!"
                        )
                        # Recalculate stats with new companion bonus
                        self.player.update_stats_from_equipment(
                            self.items_data, self.companions_data)
                    else:
                        print(self.lang.get('not_enough_gold'))
                else:
                    print(self.lang.get("invalid_choice"))

    def visit_market(self):
        """Visit the Elite Market - browse and buy items from the API at 50% off"""
        if not self.player:
            print(self.lang.get("no_character"))
            return

        if not self.market_api:
            print(self.lang.get('market_api_not_available'))
            return

        print(
            f"\n{Colors.MAGENTA}{Colors.BOLD}=== ELITE MARKET ==={Colors.END}")
        print(self.lang.get('welcome_elite_market'))
        if self.player:
            print(f"\nYour gold: {Colors.GOLD}{self.player.gold}{Colors.END}")

        # Check cooldown
        remaining = self.market_api.get_cooldown_remaining()
        if remaining and remaining.total_seconds() > 0:
            mins = int(remaining.total_seconds() // 60)
            secs = int(remaining.total_seconds() % 60)
            print(
                f"\n{Colors.YELLOW}Market cooldown: {mins}m {secs}s remaining{Colors.END}"
            )

        # Fetch market data
        market_data = self.market_api.fetch_market_data()
        if not market_data or not market_data.get('ok'):
            print(
                f"\n{Colors.RED}{Colors.BOLD}Market is currently closed!{Colors.END}"
            )
            print(
                f"{Colors.YELLOW}Merchants have travelled to another distant far place!{Colors.END}"
            )
            print(
                f"{Colors.YELLOW}Please wait until the merchants arrive!{Colors.END}"
            )
            return

        items = self.market_api.get_all_items()
        if not items:
            print(self.lang.get('no_items_available_market'))
            return

        # Get filter options from player
        print(self.lang.get("n_browse_items"))
        print(self.lang.get('ui_filters_available'))
        print(self.lang.get('filter_all_items'))
        print(self.lang.get('filter_by_type_desc'))
        print(self.lang.get('filter_by_rarity_desc'))
        print(self.lang.get('filter_by_class_desc'))
        print(self.lang.get('filter_by_max_price_desc'))
        print(f"  R. {self.lang.get('filter_refresh_market')}")

        choice = ask("\nChoose filter (1-5, R) or press Enter to browse all: "
                     ).strip().upper()

        filtered_items = items

        if choice == '1' or not choice:
            pass  # All items
        elif choice == '2':
            print(
                "\nItem types: weapon, armor, consumable, accessory, material, offhand"
            )
            item_type = ask("Enter type: ").strip().lower()
            filtered_items = self.market_api.filter_items(item_type=item_type)
        elif choice == '3':
            print(f"\n{self.lang.get('rarities_list')}")
            rarity = ask("Enter rarity: ").strip().lower()
            filtered_items = self.market_api.filter_items(rarity=rarity)
        elif choice == '4':
            print(f"\n{self.lang.get('classes_list')}")
            class_req = ask("Enter class: ").strip()
            filtered_items = self.market_api.filter_items(class_req=class_req)
        elif choice == '5':
            try:
                max_price = int(ask("Enter max price: ").strip())
                filtered_items = self.market_api.filter_items(
                    max_price=max_price)
            except ValueError:
                print(self.lang.get('invalid_price_showing_all'))
        elif choice == 'R':
            filtered_items = self.market_api.get_all_items()
            # Force refresh
            self.market_api.fetch_market_data(force_refresh=True)
            filtered_items = self.market_api.get_all_items()

        if not filtered_items:
            print(self.lang.get('no_items_match_filters'))
            return

        # Sort by market price by default
        filtered_items = sorted(filtered_items,
                                key=lambda x: x.get('marketPrice', 0))

        # Paginate and display items
        page_size = 8
        current_page = 0

        while True:
            start = current_page * page_size
            end = start + page_size
            page_items = filtered_items[start:end]

            if not page_items:
                print(self.lang.get("no_more_items"))
                break

            print(
                f"\n--- Page {current_page + 1} of {(len(filtered_items) + page_size - 1) // page_size} ---"
            )

            for i, item in enumerate(page_items, 1):
                name = item.get('name', 'Unknown')
                item_type = item.get('type', 'unknown')
                rarity = item.get('rarity', 'common')
                original_price = item.get('originalPrice', 0)
                market_price = item.get('marketPrice', 0)
                desc = item.get('description',
                                '')[:60]  # Truncate long descriptions
                reqs = item.get('requirements')
                class_req = reqs.get('class') if reqs else None
                level_req = reqs.get('level', 1) if reqs else 1

                # Color by rarity
                rarity_color = get_rarity_color(rarity)
                price_color = Colors.GREEN if market_price <= self.player.gold else Colors.RED

                print(f"\n{i}. {rarity_color}{name}{Colors.END} ({item_type})")
                print(f"   {Colors.DARK_GRAY}{desc}{Colors.END}")
                print(
                    f"   {rarity_color}{rarity.title()}{Colors.END} | Level {level_req}"
                    + (f" | {Colors.CYAN}{class_req}{Colors.END}"
                       if class_req else ""))
                print(
                    f"   {price_color}{market_price}{Colors.END} gold (was {original_price})"
                )

            print(self.lang.get("noptions_3"))
            print(f"1-{len(page_items)}. Buy Item")
            if len(filtered_items) > page_size:
                print(f"N. {self.lang.get('ui_next_page')}")
                print(f"P. {self.lang.get('ui_previous_page')}")
            print(f"F. {self.lang.get('ui_filter_items')}")
            print(f"Enter. {self.lang.get('ui_return_to_main_menu')}")

            choice = ask("\nChoose action: ").strip().upper()

            if not choice:
                break
            elif choice == 'N' and len(filtered_items) > page_size:
                if end < len(filtered_items):
                    current_page += 1
            elif choice == 'P' and len(filtered_items) > page_size:
                if current_page > 0:
                    current_page -= 1
            elif choice == 'F':
                # Apply filter
                print(f"\n{self.lang.get('ui_refine_search')}")
                print(self.lang.get('filter_by_type'))
                print(self.lang.get('filter_by_rarity'))
                print(self.lang.get('filter_by_class'))
                print(self.lang.get('filter_by_max_price'))
                sub_choice = ask("Choose filter: ").strip()
                if sub_choice == '1':
                    item_type = ask("Enter type: ").strip().lower()
                    filtered_items = [
                        it for it in filtered_items
                        if it.get('type', '').lower() == item_type
                    ]
                elif sub_choice == '2':
                    rarity = ask("Enter rarity: ").strip().lower()
                    filtered_items = [
                        it for it in filtered_items
                        if it.get('rarity', '').lower() == rarity
                    ]
                elif sub_choice == '3':
                    class_req = ask("Enter class: ").strip()
                    filtered_items = [
                        it for it in filtered_items
                        if (it.get('requirements') or {}
                            ).get('class', '').lower() == class_req.lower()
                    ]
                elif sub_choice == '4':
                    try:
                        max_price = int(ask("Enter max price: ").strip())
                        filtered_items = [
                            it for it in filtered_items
                            if it.get('marketPrice', 0) <= max_price
                        ]
                    except ValueError:
                        pass
                current_page = 0
            elif choice.isdigit():
                item_idx = int(choice) - 1
                if 0 <= item_idx < len(page_items):
                    item = page_items[item_idx]
                    name = item.get('name', '')
                    market_price = item.get('marketPrice', 0)

                    if self.player.gold >= market_price:
                        self.player.gold -= market_price
                        self.player.inventory.append(name)
                        print(
                            f"\n{Colors.GREEN}Purchased {name} for {market_price} gold!{Colors.END}"
                        )
                        self.update_mission_progress('collect', name)
                    else:
                        print(
                            f"\n{Colors.RED}Not enough gold! Need {market_price}, have {self.player.gold}.{Colors.END}"
                        )
                else:
                    print(self.lang.get('invalid_selection'))

    def manage_companions(self):
        """Manage hired companions."""
        if not self.player:
            print(self.lang.get("no_character"))
            return

        while True:
            print(self.lang.get("n_companions"))
            print(f"Active companions: {len(self.player.companions)}/4")

            if not self.player.companions:
                print(
                    "You have no companions yet. Visit the tavern to hire some!"
                )
                return

            # Display active companions
            for i, companion in enumerate(self.player.companions, 1):
                if isinstance(companion, dict):
                    comp_name = companion.get('name')
                    comp_level = companion.get('level', 1)
                else:
                    comp_name = companion
                    comp_level = 1

                # Find companion data to show bonuses
                comp_data = None
                for cid, cdata in self.companions_data.items():
                    if cdata.get('name') == comp_name:
                        comp_data = cdata
                        break

                print(
                    f"\n{i}. {Colors.CYAN}{comp_name}{Colors.END} (Level {comp_level})"
                )
                if comp_data:
                    bonuses = []
                    if comp_data.get('attack_bonus'):
                        bonuses.append(f"+{comp_data.get('attack_bonus')} ATK")
                    if comp_data.get('defense_bonus'):
                        bonuses.append(
                            f"+{comp_data.get('defense_bonus')} DEF")
                    if comp_data.get('speed_bonus'):
                        bonuses.append(f"+{comp_data.get('speed_bonus')} SPD")
                    if comp_data.get('healing_bonus'):
                        bonuses.append(
                            f"+{comp_data.get('healing_bonus')} Healing")
                    if comp_data.get('mp_bonus'):
                        bonuses.append(f"+{comp_data.get('mp_bonus')} MP")

                    if bonuses:
                        print(f"   Bonuses: {', '.join(bonuses)}")
                    print(f"   {comp_data.get('description', '')}")

            print(f"\n{self.lang.get('ui_options')}")
            print(self.lang.get('ui_dismiss_companion'))
            print(self.lang.get('ui_equip_companion'))
            print(self.lang.get('ui_enter_return'))

            choice = ask("Choose action: ").strip().lower()

            if not choice:
                break
            elif choice == 'd':
                # Dismiss companion
                if self.player.companions:
                    try:
                        idx = int(
                            ask(f"Dismiss which companion (1-{len(self.player.companions)})? "
                                )) - 1
                        if 0 <= idx < len(self.player.companions):
                            dismissed = self.player.companions.pop(idx)
                            if isinstance(dismissed, dict):
                                print(
                                    f"{Colors.RED}Dismissed {dismissed.get('name')}.{Colors.END}"
                                )
                            else:
                                print(
                                    f"{Colors.RED}Dismissed {dismissed}.{Colors.END}"
                                )
                            # Recalculate stats after dismissal
                            self.player.update_stats_from_equipment(
                                self.items_data, self.companions_data)
                        else:
                            print(self.lang.get('invalid_selection'))
                    except ValueError:
                        print(self.lang.get('invalid_input'))
            elif choice == 'e':
                # Equip item on companion
                print(self.lang.get('ui_companion_equip_soon'))
                # TODO: Implement companion equipment
            else:
                print(self.lang.get("invalid_choice"))

    def travel(self):
        """Travel to connected areas from the current area."""
        if not self.player:
            print(self.lang.get("no_character"))
            return

        current = self.current_area
        area_data = self.areas_data.get(current, {})
        connections = area_data.get("connections", [])

        print(self.lang.get("n_travel"))
        print(f"Current location: {area_data.get('name', current)}")
        if not connections:
            print(self.lang.get('no_connected_areas'))
            return

        print(self.lang.get('ui_connected_areas'))
        for i, aid in enumerate(connections, 1):
            a = self.areas_data.get(aid, {})
            print(f"{i}. {a.get('name', aid)} - {a.get('description','')}")

        choice = ask(
            f"Travel to (1-{len(connections)}) or press Enter to cancel: ")
        if choice and choice.isdigit():
            idx = int(choice) - 1
            if 0 <= idx < len(connections):
                new_area = connections[idx]
                self.current_area = new_area
                self.player.update_weather(new_area)
                print(
                    f"Traveling to {self.areas_data.get(new_area, {}).get('name', new_area)}..."
                )

                # Check for area cutscene
                area_data = self.areas_data.get(new_area, {})
                cutscene_id = area_data.get('first_time_enter_cutscene')
                if cutscene_id and cutscene_id in self.cutscenes_data:
                    cutscene = self.cutscenes_data[cutscene_id]
                    is_iterable = cutscene.get('iterable', False)
                    if is_iterable or new_area not in self.visited_areas:
                        self.play_cutscene(cutscene_id)
                        if not is_iterable:
                            self.visited_areas.add(new_area)

                # small chance encounter on travel
                if random.random() < 0.3:
                    self.random_encounter()

    def shop_sell(self):
        """Sell items from the player's inventory to the shop."""
        if not self.player:
            return

        sellable = [it for it in self.player.inventory]
        if not sellable:
            print(self.lang.get('you_have_nothing_sell'))
            return

        print(f"\n{self.lang.get('ui_your_inventory')}")
        for i, item in enumerate(sellable, 1):
            equip_marker = ''
            for slot, eq in self.player.equipment.items():
                if eq == item:
                    equip_marker = ' (equipped)'
            price = self.items_data.get(item, {}).get('price', 0)
            sell_price = price // 2 if price else 0
            print(f"{i}. {item}{equip_marker} - Sell for {sell_price} gold")

        choice = ask(
            f"Choose item to sell (1-{len(sellable)}) or press Enter to cancel: "
        )
        if not choice or not choice.isdigit():
            return
        idx = int(choice) - 1
        if not (0 <= idx < len(sellable)):
            print(self.lang.get('invalid_selection'))
            return

        item = sellable[idx]
        # Prevent selling equipped items
        if item in self.player.equipment.values():
            print(self.lang.get('unequip_before_selling'))
            return

        price = self.items_data.get(item, {}).get('price', 0)
        sell_price = price // 2 if price else 0
        self.player.inventory.remove(item)
        self.player.gold += sell_price
        print(f"Sold {item} for {sell_price} gold.")

    def rest(self):
        """Rest in a safe area to recover HP and MP for gold."""
        if not self.player:
            print(self.lang.get("no_character"))
            return

        area_data = self.areas_data.get(self.current_area, {})
        area_name = area_data.get("name", "Unknown Area")
        can_rest = area_data.get("can_rest", False)
        rest_cost = area_data.get("rest_cost", 0)

        if not can_rest:
            print(
                f"\n{Colors.RED}You cannot rest in {area_name}. It's too dangerous!{Colors.END}"
            )
            return

        print(
            f"\n{Colors.CYAN}=== REST IN {area_name.upper()} ==={Colors.END}")
        print(f"Rest Cost: {Colors.GOLD}{rest_cost} gold{Colors.END}")
        print(
            f"Current HP: {Colors.RED}{self.player.hp}/{self.player.max_hp}{Colors.END}"
        )
        print(
            f"Current MP: {Colors.BLUE}{self.player.mp}/{self.player.max_mp}{Colors.END}"
        )

        if self.player.gold < rest_cost:
            print(
                f"\n{Colors.RED}You don't have enough gold to rest! Need {rest_cost}, have {self.player.gold}.{Colors.END}"
            )
            return

        choice = ask(f"Rest for {rest_cost} gold? (y/n): ")
        if choice.lower() != 'y':
            print(self.lang.get('decide_not_rest'))
            return

        # Deduct gold and restore HP/MP
        self.player.gold -= rest_cost
        old_hp = self.player.hp
        old_mp = self.player.mp
        self.player.hp = self.player.max_hp
        self.player.mp = self.player.max_mp

        print(
            f"\n{Colors.GREEN}You rest and recover your strength...{Colors.END}"
        )
        print(
            f"HP restored: {old_hp} → {Colors.GREEN}{self.player.hp}{Colors.END}"
        )
        print(
            f"MP restored: {old_mp} → {Colors.GREEN}{self.player.mp}{Colors.END}"
        )
        print(f"Gold remaining: {Colors.GOLD}{self.player.gold}{Colors.END}")

    def save_game(self, filename_prefix: str = ""):
        """Save the game with an optional filename prefix (keeps backward compatible signature)."""
        if not self.player:
            print(self.lang.get('no_character_save'))
            return

        save_data = {
            "player": {
                "name": self.player.name,
                "uuid": self.player.uuid,
                "character_class": self.player.character_class,
                "level": self.player.level,
                "experience": self.player.experience,
                "experience_to_next": self.player.experience_to_next,
                "max_hp": self.player.max_hp,
                "hp": self.player.hp,
                "max_mp": self.player.max_mp,
                "mp": self.player.mp,
                "attack": self.player.attack,
                "defense": self.player.defense,
                "speed": self.player.speed,
                "inventory": self.player.inventory,
                "gold": self.player.gold,
                "equipment": self.player.equipment,
                "companions": self.player.companions,
                "base_stats": {
                    "base_max_hp": self.player.base_max_hp,
                    "base_max_mp": self.player.base_max_mp,
                    "base_attack": self.player.base_attack,
                    "base_defense": self.player.base_defense,
                    "base_speed": self.player.base_speed
                },
                "class_data": self.player.class_data,
                "rank": self.player.rank,
                "active_buffs": self.player.active_buffs,
                "housing_owned": getattr(self.player, 'housing_owned', []),
                "comfort_points": getattr(self.player, 'comfort_points', 0),
                "building_slots": getattr(self.player, 'building_slots', {}),
                "farm_plots": getattr(self.player, 'farm_plots', {}),
                "hour": getattr(self.player, 'hour', 8),
                "day": getattr(self.player, 'day', 1),
                "current_weather": getattr(self.player, 'current_weather',
                                           "sunny")
            },
            "current_area": self.current_area,
            "visited_areas": list(self.visited_areas),
            "mission_progress": self.mission_progress,
            "completed_missions": self.completed_missions,
            "save_version": "3.1",
            "save_time": datetime.now().isoformat(),
            "bosses_killed": getattr(self.player, 'bosses_killed', {}),
            "hour": getattr(self.player, 'hour', 8),
            "day": getattr(self.player, 'day', 1),
            "current_weather": getattr(self.player, 'current_weather', "sunny")
        }

        saves_dir = "data/saves"
        os.makedirs(saves_dir, exist_ok=True)

        safe_prefix = filename_prefix or ""
        # sanitize prefix to avoid accidental path chars
        safe_prefix = safe_prefix.replace('/', '_')

        # Check if overwrite by UUID is enabled
        overwrite_by_uuid = self.mod_manager.settings.get(
            "overwrite_save_by_uuid", False)
        if overwrite_by_uuid and not filename_prefix:
            # Find existing save file with same UUID
            existing_save = None
            for f in os.listdir(saves_dir):
                if f.endswith(
                        '.json'
                ) and f"{self.player.uuid[:8]}" in f and not f.startswith(
                        'err_save'):
                    existing_save = f
                    break

            if existing_save:
                filename = os.path.join(saves_dir, existing_save)
            else:
                # No existing save found, create new one with timestamp
                timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
                filename = f"{saves_dir}/{safe_prefix}{self.player.name}_{self.player.uuid[:8]}_save_{timestamp}_{self.player.character_class}_{self.player.level}.json"
        else:
            # Default behavior: create new save with timestamp
            timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            filename = f"{saves_dir}/{safe_prefix}{self.player.name}_{self.player.uuid[:8]}_save_{timestamp}_{self.player.character_class}_{self.player.level}.json"

        with open(filename, 'w') as f:
            json.dump(save_data, f, indent=2)

        print(f"Game saved successfully: {filename}")

    def load_game(self):
        """Load a saved game with enhanced equipment handling and backward compatibility"""
        saves_dir = "data/saves"
        if not os.path.exists(saves_dir):
            print(self.lang.get('no_save_files'))
            return

        save_files = [f for f in os.listdir(saves_dir) if f.endswith('.json')]
        if not save_files:
            print(self.lang.get('no_save_files'))
            return

        print(self.lang.get('available_save_files'))
        for i, save_file in enumerate(save_files, 1):
            character_name = save_file.replace('_save.json', '')
            print(f"{i}. {character_name}")

        choice = ask(
            f"Load save (1-{len(save_files)}) or press Enter to cancel: ")
        if choice and choice.isdigit():
            save_index = int(choice) - 1
            if 0 <= save_index < len(save_files):
                save_file = save_files[save_index]
                filename = os.path.join(str(saves_dir), save_file)

                try:
                    with open(filename, 'r') as f:
                        save_data = json.load(f)

                    # Check save version for compatibility
                    save_version = save_data.get("save_version", "1.0")

                    # Recreate player
                    player_data = save_data["player"]
                    player_uuid = player_data.get("uuid")
                    self.player = Character(player_data["name"],
                                            player_data["character_class"],
                                            self.classes_data,
                                            player_uuid=player_uuid)

                    # Restore stats
                    self.player.level = player_data["level"]
                    self.player.experience = player_data["experience"]
                    self.player.experience_to_next = player_data[
                        "experience_to_next"]
                    self.player.max_hp = player_data["max_hp"]
                    self.player.hp = player_data["hp"]
                    self.player.max_mp = player_data["max_mp"]
                    self.player.mp = player_data["mp"]
                    self.player.attack = player_data["attack"]
                    self.player.defense = player_data["defense"]
                    self.player.speed = player_data["speed"]
                    self.player.inventory = player_data["inventory"]
                    self.player.gold = player_data["gold"]
                    # Restore rank and active buffs if present
                    self.player.rank = player_data.get("rank",
                                                       self.player.rank)
                    self.player.active_buffs = player_data.get(
                        "active_buffs", self.player.active_buffs)

                    # NEW: Load companions with backward compatibility
                    self.player.companions = player_data.get("companions", [])

                    # NEW: Load housing data with backward compatibility
                    self.player.housing_owned = player_data.get(
                        "housing_owned", [])
                    self.player.comfort_points = player_data.get(
                        "comfort_points", 0)
                    self.player.building_slots = player_data.get(
                        "building_slots", {})
                    self.player.farm_plots = player_data.get(
                        "farm_plots", {
                            "farm_1": [],
                            "farm_2": []
                        })

                    # NEW: Enhanced equipment loading with validation
                    self._load_equipment_data(player_data, save_version)

                    self.current_area = save_data["current_area"]
                    self.visited_areas = set(save_data.get(
                        "visited_areas", []))

                    # Mission system load with backward compatibility
                    self.mission_progress = save_data.get(
                        "mission_progress", {})
                    self.completed_missions = save_data.get(
                        "completed_missions", [])

                    # Load boss kill cooldowns
                    if self.player:
                        self.player.bosses_killed = save_data.get(
                            "bosses_killed", {})
                        # Check both top-level and player-level for backward compatibility
                        self.player.hour = save_data.get(
                            "hour", player_data.get("hour", 8))
                        self.player.day = save_data.get(
                            "day", player_data.get("day", 1))
                        self.player.current_weather = save_data.get(
                            "current_weather",
                            player_data.get("current_weather", "sunny"))

                    # Backward compatibility for old saves using current_missions
                    if not self.mission_progress and "current_missions" in save_data:
                        for mid in save_data["current_missions"]:
                            mission = self.missions_data.get(mid)
                            if mission:
                                mission_type = mission.get('type', 'kill')
                                target_count = mission.get('target_count', 1)
                                if mission_type == 'collect' and isinstance(
                                        target_count, dict):
                                    self.mission_progress[mid] = {
                                        'current_counts': {
                                            item: 0
                                            for item in target_count.keys()
                                        },
                                        'target_counts': target_count,
                                        'completed': False,
                                        'type': mission_type
                                    }
                                else:
                                    self.mission_progress[mid] = {
                                        'current_count': 0,
                                        'target_count': target_count,
                                        'completed': False,
                                        'type': mission_type
                                    }

                    # Recalculate stats with equipment and companions
                    if self.player:
                        # Ensure rank matches loaded level
                        try:
                            self.player._update_rank()
                        except Exception:
                            pass
                        self.player.update_stats_from_equipment(
                            self.items_data, self.companions_data)
                        print(
                            f"Game loaded successfully! Welcome back, {self.player.name}!"
                        )
                        self.player.display_stats()

                except Exception as e:
                    print(f"Error loading save file: {e}")

    def _load_equipment_data(self, player_data: Dict, save_version: str):
        """Load and validate equipment data with backward compatibility"""
        if not self.player:
            return

        # NEW: Handle enhanced save format (v2.0+)
        if save_version >= "2.0":
            # Load equipment if present
            equipment: Dict[str, Optional[str]] = player_data.get(
                "equipment", {
                    "weapon": None,
                    "armor": None,
                    "accessory": None
                })
            self.player.equipment = equipment

            # Load base stats if present for equipment recalculation
            base_stats = player_data.get("base_stats", {})
            if base_stats:
                self.player.base_max_hp = base_stats.get(
                    "base_max_hp", self.player.base_max_hp)
                self.player.base_max_mp = base_stats.get(
                    "base_max_mp", self.player.base_max_mp)
                self.player.base_attack = base_stats.get(
                    "base_attack", self.player.base_attack)
                self.player.base_defense = base_stats.get(
                    "base_defense", self.player.base_defense)
                self.player.base_speed = base_stats.get(
                    "base_speed", self.player.base_speed)

            # Load class data if present
            class_data = player_data.get("class_data", {})
            if class_data:
                self.player.class_data = class_data
                self.player.level_up_bonuses = class_data.get(
                    "level_up_bonuses", {})

            # Validate equipped items exist and meet requirements
            self._validate_and_fix_equipment()

            # Recalculate stats from equipment
            self.player.update_stats_from_equipment(self.items_data)

        else:
            # OLD: Backward compatibility for v1.0 saves
            print(
                f"{Colors.YELLOW}Loading legacy save (v{save_version}). Equipment may not be restored.{Colors.END}"
            )

            # Try to find equipment in inventory for old saves
            equipment: Dict[str, Optional[str]] = {
                "weapon": None,
                "armor": None,
                "accessory": None
            }

            # Heuristic: look for likely equipped items in inventory
            for item in player_data.get("inventory", []):
                item_data = self.items_data.get(item, {})
                item_type = item_data.get("type")

                if item_type == "weapon" and not equipment["weapon"]:
                    equipment["weapon"] = item
                elif item_type == "armor" and not equipment["armor"]:
                    equipment["armor"] = item
                elif item_type == "accessory" and not equipment["accessory"]:
                    equipment["accessory"] = item

            self.player.equipment = equipment
            self._validate_and_fix_equipment()
            self.player.update_stats_from_equipment(self.items_data)

    def _validate_and_fix_equipment(self):
        """Validate equipped items and auto-unequip invalid ones"""
        if not self.player:
            return

        invalid_items = []

        for slot in ("weapon", "armor", "accessory"):
            item_name = self.player.equipment.get(slot)
            if not item_name:
                continue

            # Check if item still exists in game data
            if item_name not in self.items_data:
                invalid_items.append(
                    (slot, item_name, "Item no longer exists"))
                self.player.equipment[slot] = None
                continue

            item_data = self.items_data[item_name]

            # Check if item type matches slot
            if item_data.get("type") != slot:
                invalid_items.append((slot, item_name, "Item type mismatch"))
                self.player.equipment[slot] = None
                continue

            # Check requirements
            requirements = item_data.get("requirements", {})
            if requirements:
                level_req = requirements.get("level", 0)
                class_req = requirements.get("class")

                if self.player.level < level_req:
                    invalid_items.append(
                        (slot, item_name, f"Level {level_req} required"))
                    self.player.equipment[slot] = None
                    continue

                if class_req and class_req != self.player.character_class:
                    invalid_items.append(
                        (slot, item_name, f"{class_req} class required"))
                    self.player.equipment[slot] = None
                    continue

        # Report any items that were auto-unequipped
        if invalid_items:
            print(
                f"\n{Colors.YELLOW}Some equipped items were invalid and have been unequipped:{Colors.END}"
            )
            for slot, item_name, reason in invalid_items:
                print(f"  - {slot.title()}: {item_name} ({reason})")
            print(
                f"{Colors.YELLOW}Please check your inventory and re-equip valid items.{Colors.END}"
            )

    def save_on_error(self,
                      exc_info=None,
                      filename_prefix="err_save_unstable_"):
        """Attempt to save the current game state and write a traceback log when an error occurs."""
        try:
            # Build a safe player name for filenames
            pname = (self.player.name if self.player
                     and getattr(self.player, 'name', None) else 'unknown')
            # Try to save using the standard save function with prefix
            try:
                self.save_game(filename_prefix)
            except Exception as se:
                print(f"Error while saving game on error: {se}")

            # Write traceback log
            try:
                saves_dir = "data/saves"
                os.makedirs(saves_dir, exist_ok=True)
                ts = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
                safe_prefix = (filename_prefix or '').replace('/', '_')
                logname = f"{saves_dir}/{safe_prefix}{pname}_error_{ts}.log"
                if exc_info is None:
                    exc_info = sys.exc_info()
                # exc_info may be a tuple (etype, value, tb) or an exception instance
                # Ensure exc_info is a 3-tuple (etype, value, tb)
                if not (isinstance(exc_info, tuple) and len(exc_info) == 3):
                    exc_info = sys.exc_info()

                et, ev, tbobj = exc_info
                buf = io.StringIO()
                traceback.print_exception(et, ev, tbobj, file=buf)
                tb = buf.getvalue()
                with open(logname, 'w') as lf:
                    lf.write(tb)
                print(f"Error traceback written to: {logname}")
            except Exception as le:
                print(f"Failed to write error log: {le}")
        except Exception as e:
            print(f"Unexpected failure during save_on_error: {e}")

    def quit_game(self):
        """Quit the game"""
        print(f"\n{self.lang.get('ui_have_you_saved')}")
        response = input(">>> ").strip().lower()
        if response == "no":
            clear_screen()
            print(self.lang.get('ui_saving_progress'))
            self.save_game()
            print(self.lang.get('ui_progress_saved'))
        print(self.lang.get('ui_thank_you_playing'))
        print(self.lang.get('ui_legacy_remembered'))
        sys.exit(0)

    def _gather_materials(self):
        """Gather materials based on current area's difficulty and theme."""
        if not self.player:
            return

        area_data = self.areas_data.get(self.current_area, {})
        difficulty = area_data.get('difficulty', 1)

        # Define material pools by difficulty tier
        # Tier 1: Basic materials (difficulty 1-2)
        tier1_materials = [
            "Herb", "Spring Water", "Leather", "Leather Strip", "Hardwood",
            "Stone Block", "Coal", "Iron Ore", "Goblin Ear", "Wolf Fang",
            "Bone Fragment"
        ]

        # Tier 2: Uncommon materials (difficulty 3)
        tier2_materials = [
            "Mana Herb", "Gold Nugget", "Steel Ingot", "Orc Tooth",
            "Serpent Tail", "Crystal Shard", "Venom Sac", "Swamp Scale",
            "Ancient Relic", "Wind Elemental Essence", "Demon Blood"
        ]

        # Tier 3: Rare materials (difficulty 4)
        tier3_materials = [
            "Dark Crystal", "Ice Crystal", "Void Crystal", "Shadow Essence",
            "Fire Essence", "Ice Essence", "Starlight Shard",
            "Eternal Essence", "Poison Crystal", "Lightning Crystal"
        ]

        # Tier 4: Legendary materials (difficulty 5-6)
        tier4_materials = [
            "Dragon Scale", "Dragon Bone", "Phoenix Feather", "Fire Gem",
            "Soul Fragment", "Demon Heart", "Golem Core",
            "Storm Elemental Core", "Zephyr's Scale", "Wind Dragon's Heart",
            "Eternal Feather", "Dragon Heart", "Void Heart"
        ]

        # Select materials based on difficulty
        available_materials = []
        if difficulty <= 2:
            available_materials = tier1_materials.copy()
            if random.random() < 0.3:  # 30% chance for tier 2
                available_materials.extend(tier2_materials)
        elif difficulty == 3:
            available_materials = tier1_materials + tier2_materials
            if random.random() < 0.4:  # 40% chance for tier 3
                available_materials.extend(tier3_materials)
        elif difficulty == 4:
            available_materials = tier2_materials + tier3_materials
            if random.random() < 0.3:  # 30% chance for tier 4
                available_materials.extend(tier4_materials)
        else:  # difficulty 5-6
            available_materials = tier3_materials + tier4_materials
            if random.random() < 0.2:  # 20% chance for tier 2
                available_materials.extend(tier2_materials)

        # Filter to only materials that actually exist in items_data
        valid_materials = [
            m for m in available_materials if m in self.items_data
        ]

        if not valid_materials:
            return

        # Gather 1-3 random materials
        num_materials = random.randint(1, 3)
        gathered = {}

        for _ in range(num_materials):
            material = random.choice(valid_materials)
            quantity = random.randint(1, 3)
            gathered[material] = gathered.get(material, 0) + quantity

        # Add gathered materials to inventory
        found_text = []
        for material, qty in gathered.items():
            for _ in range(qty):
                self.player.inventory.append(material)

            # Get material info for display
            item_data = self.items_data.get(material, {})
            rarity = item_data.get('rarity', 'common')
            color = get_rarity_color(rarity)
            found_text.append(f"{color}{qty}x {material}{Colors.END}")

        # Display gathered materials
        print(self.lang.get("nyou_found_materials"))
        for text in found_text:
            print(f"  - {text}")

        # Update mission progress for collected materials
        for material in gathered.keys():
            self.update_mission_progress('collect', material)

    def visit_dungeons(self):
        """Visit the dungeon menu to select and enter dungeons"""
        if not self.player:
            print(self.lang.get("no_character"))
            return

        print(self.lang.get("n_dungeons"))
        print(self.lang.get('ui_dungeon_portal'))

        # Check if player is in a dungeon
        if self.current_dungeon:
            print(
                f"\n{Colors.YELLOW}You are currently in: {self.current_dungeon['name']}{Colors.END}"
            )
            print(
                f"Progress: Room {self.dungeon_progress + 1}/{len(self.dungeon_rooms)}"
            )

            choice = ask("Continue dungeon (C) or Exit (E)? ").strip().upper()
            if choice == 'C':
                self.continue_dungeon()
            elif choice == 'E':
                self.exit_dungeon()
            return

        # Show available dungeons (filter by allowed_areas)
        all_dungeons = self.dungeons_data.get('dungeons', [])
        if not all_dungeons:
            print(self.lang.get('ui_no_dungeons'))
            return

        # Filter dungeons by allowed_areas for current location
        dungeons = []
        for dungeon in all_dungeons:
            allowed_areas = dungeon.get('allowed_areas', [])
            if not allowed_areas or self.current_area in allowed_areas:
                dungeons.append(dungeon)

        if not dungeons:
            print(
                f"\n{Colors.YELLOW}No dungeons available in {self.current_area}.{Colors.END}"
            )
            print(self.lang.get('ui_travel_find_dungeons'))
            return

        print(
            f"\n{Colors.CYAN}Available Dungeons in {self.current_area}:{Colors.END}"
        )
        for i, dungeon in enumerate(dungeons, 1):
            name = dungeon['name']
            difficulty = dungeon['difficulty']
            rooms = dungeon['rooms']
            desc = dungeon['description']

            # Check if player meets minimum level requirement
            min_level = difficulty[0] * 5  # Rough level requirement
            level_ok = self.player.level >= min_level

            status = f"{Colors.GREEN}Available{Colors.END}" if level_ok else f"{Colors.RED}Level {min_level}+ required{Colors.END}"

            print(
                f"{i}. {Colors.BOLD}{name}{Colors.END} (Difficulty {difficulty[0]}-{difficulty[1]}, {rooms} rooms)"
            )
            print(f"   {desc}")
            print(f"   Status: {status}")

        choice = ask(
            f"\nChoose dungeon (1-{len(dungeons)}) or press Enter to cancel: ")
        if choice and choice.isdigit():
            idx = int(choice) - 1
            if 0 <= idx < len(dungeons):
                dungeon = dungeons[idx]
                min_level = dungeon['difficulty'][0] * 5
                if self.player.level >= min_level:
                    self.enter_dungeon(dungeon)
                    clear_screen()
                else:
                    print(
                        f"You need to be at least level {min_level} to enter this dungeon."
                    )
            else:
                print(self.lang.get("invalid_choice"))

    def enter_dungeon(self, dungeon: Dict[str, Any]):
        """Enter a dungeon and generate rooms"""
        print(
            f"\n{Colors.MAGENTA}{Colors.BOLD}Entering {dungeon['name']}!{Colors.END}"
        )
        print(dungeon['description'])

        # Set dungeon state
        self.current_dungeon = dungeon
        self.dungeon_progress = 0
        self.dungeon_state = {
            'start_time': datetime.now().isoformat(),
            'total_rooms': dungeon['rooms'],
            'current_room': 0
        }

        # Generate dungeon rooms based on weights
        self.generate_dungeon_rooms(dungeon)

        # Start with first room
        self.continue_dungeon()

    def generate_dungeon_rooms(self, dungeon: Dict[str, Any]):
        """Generate dungeon rooms based on room weights"""
        room_weights = dungeon.get('room_weights', {})
        total_rooms = dungeon.get('rooms', 5)

        self.dungeon_rooms = []

        # Validate room_weights
        if not room_weights or sum(room_weights.values()) == 0:
            # Default room weights if none provided or sum is zero
            room_weights = {
                'battle': 40,
                'question': 20,
                'chest': 15,
                'empty': 15,
                'trap_chest': 5,
                'multi_choice': 5
            }

        if total_rooms <= 0:
            total_rooms = 5

        # Create weighted room list
        room_types = []
        weights = []

        for room_type, weight in room_weights.items():
            room_types.append(room_type)
            weights.append(weight)

        # Generate rooms
        for i in range(total_rooms):
            # Last room is always boss room
            if i == total_rooms - 1:
                room_type = 'boss'
            else:
                room_type = random.choices(room_types, weights=weights, k=1)[0]

            room_data = {
                'type': room_type,
                'room_number': i + 1,
                'difficulty': dungeon.get('difficulty', [1, 3])[0] +
                (i * 0.5)  # Scale difficulty
            }

            self.dungeon_rooms.append(room_data)

    def continue_dungeon(self):
        """Continue through the current dungeon"""
        if not self.current_dungeon or not self.dungeon_rooms:
            print(self.lang.get('ui_no_active_dungeon'))
            return

        # Loop through rooms until dungeon is complete
        while self.current_dungeon and self.dungeon_progress < len(
                self.dungeon_rooms):
            # Get current room
            room = self.dungeon_rooms[self.dungeon_progress]

            print(
                f"\n{Colors.CYAN}{Colors.BOLD}=== Room {room['room_number']} ==={Colors.END}"
            )

            # Handle room based on type
            room_type = room['type']
            if room_type == 'question':
                self.handle_question_room(room)
            elif room_type == 'battle':
                self.handle_battle_room(room)
            elif room_type == 'chest':
                self.handle_chest_room(room)
            elif room_type == 'trap_chest':
                self.handle_trap_chest_room(room)
            elif room_type == 'multi_choice':
                self.handle_multi_choice_room(room)
            elif room_type == 'empty':
                self.handle_empty_room(room)
            elif room_type == 'boss':
                self.handle_boss_room(room)

            # Check if player died during room
            if not self.player or not self.player.is_alive():
                return

        # Dungeon complete
        if self.current_dungeon and self.dungeon_progress >= len(
                self.dungeon_rooms):
            self.complete_dungeon()

    def handle_question_room(self, room: Dict[str, Any]):
        """Handle a question/riddle room"""
        if not self.player:
            return
        print(self.lang.get('ui_mystical_pedestal'))

        # Get random question from challenge templates
        challenge_templates = self.dungeons_data.get('challenge_templates', {})
        question_template = challenge_templates.get('question', {})

        if not question_template or not question_template.get('types'):
            print(self.lang.get('ui_no_questions'))
            self.advance_room()
            return

        question_data = random.choice(question_template['types'])

        print(self.lang.get("nriddle"))
        print(question_data['question'])

        # Show hints if available
        if question_data.get('hints'):
            print(
                f"\n{Colors.DARK_GRAY}Hints available (type 'hint' to see them){Colors.END}"
            )

        time_limit = question_data.get('time_limit', 60)
        start_time = time.time()
        answered_correctly = False
        attempts = 0
        max_attempts = question_data.get('max_attempts', 3)

        while attempts < max_attempts:
            answer = ask(
                f"Your answer ({max_attempts - attempts} tries left, or type 'leave'): "
            ).strip().lower()

            if answer == 'leave':
                print(self.lang.get('ui_give_up_riddle'))
                break

            if answer == 'hint' and question_data.get('hints'):
                print(self.lang.get("nhints"))
                for i, hint in enumerate(question_data['hints'], 1):
                    print(f"{i}. {hint}")
                continue

            # Check time limit
            elapsed = time.time() - start_time
            if elapsed > time_limit:
                print(self.lang.get("times_up"))
                break

            # Check answer
            correct_answer = question_data.get('answer', '').lower()
            if answer == correct_answer:
                print(self.lang.get("correct"))
                answered_correctly = True

                # Give rewards
                reward = question_data.get('success_reward', {})
                if reward.get('gold') and self.player:
                    self.player.gold += reward['gold']
                    print(f"You gained {reward['gold']} gold!")
                if reward.get('experience') and self.player:
                    self.player.gain_experience(reward['experience'])
                    print(f"You gained {reward['experience']} experience!")
                break
            else:
                attempts += 1
                print(self.lang.get("incorrect"))

                # Show close matches
                close = difflib.get_close_matches(answer, [correct_answer],
                                                  n=1,
                                                  cutoff=0.6)
                if close:
                    print(
                        f"{Colors.YELLOW}Close, but not quite right.{Colors.END}"
                    )
                else:
                    print(
                        f"{Colors.YELLOW}Try again or ask for a hint.{Colors.END}"
                    )

        # Handle outcome
        if answered_correctly:
            self.advance_room()
        else:
            # Failed - take damage
            damage = question_data.get('failure_damage', 15)
            if self.player:
                actual_damage = self.player.take_damage(damage)
                print(
                    f"You took {actual_damage} damage from the failed riddle!")

                if self.player.is_alive():
                    self.advance_room()
                else:
                    self.dungeon_death()
            else:
                self.advance_room()

    def handle_battle_room(self, room: Dict[str, Any]):
        """Handle a battle room with enemies"""
        if not self.player:
            print(self.lang.get('ui_no_player_battle'))
            self.advance_room()
            return

        if not hasattr(self,
                       'enemies_data') or not self.enemies_data or not hasattr(
                           self, 'areas_data') or not self.areas_data:
            print(self.lang.get('ui_game_data_missing'))
            self.advance_room()
            return

        print(self.lang.get('ui_combat_approaching'))

        # Generate enemies based on difficulty
        difficulty = room.get('difficulty', 1)
        enemy_count = random.randint(1, max(1, int(difficulty)))

        # Get enemies from current area or fallback with valid enemy checks
        area_enemies = self.areas_data.get(self.current_area,
                                           {}).get('possible_enemies', [])
        if not area_enemies:
            # Only use fallback enemies that actually exist in enemies_data
            fallback_enemies = ['goblin', 'orc', 'skeleton']
            area_enemies = [
                e for e in fallback_enemies if e in self.enemies_data
            ]
            # If still no valid enemies, use all available enemies from enemies_data
            if not area_enemies:
                area_enemies = list(self.enemies_data.keys()
                                    )[:5]  # Use first 5 enemies as last resort

        enemies = []
        for _ in range(enemy_count):
            if not area_enemies:
                break
            enemy_name = random.choice(area_enemies)
            enemy_data = self.enemies_data.get(enemy_name)
            if enemy_data and all(k in enemy_data for k in [
                    'name', 'hp', 'attack', 'defense', 'speed',
                    'experience_reward', 'gold_reward'
            ]):
                # Scale enemy stats by difficulty
                scaled_data = enemy_data.copy()
                scaled_data['hp'] = int(scaled_data['hp'] *
                                        (0.8 + difficulty * 0.2))
                scaled_data['attack'] = int(scaled_data['attack'] *
                                            (0.8 + difficulty * 0.2))
                scaled_data['defense'] = int(scaled_data['defense'] *
                                             (0.8 + difficulty * 0.2))

                enemy = Enemy(scaled_data)
                enemies.append(enemy)

        # Handle case where no valid enemies were found
        if not enemies:
            print(
                f"{Colors.YELLOW}No enemies found! You proceed safely.{Colors.END}"
            )
            self.advance_room()
            return

        print(f"You encounter {len(enemies)} enemy(ies)!")

        # Battle each enemy
        for i, enemy in enumerate(enemies):
            if enemy is None:  # skip None enemies
                continue
            if self.player is None or not self.player.is_alive():
                break

            if len(enemies) > 1:
                print(
                    f"\n{Colors.RED}Enemy {i+1} of {len(enemies)}:{Colors.END}"
                )

            self.battle(enemy)

        if self.player and self.player.is_alive():
            print(self.lang.get("you_cleared_the_battle_room"))
            self.advance_room()
        else:
            self.dungeon_death()

    def handle_chest_room(self, room: Dict[str, Any]):
        """Handle a treasure chest room"""
        if not self.player:
            print(self.lang.get('ui_no_player_chest'))
            self.advance_room()
            return
        print(self.lang.get('ui_chest_center_room'))

        # Determine chest quality based on difficulty
        difficulty = room.get('difficulty', 1)
        if difficulty >= 8:
            chest_type = 'legendary'
        elif difficulty >= 5:
            chest_type = 'large'
        elif difficulty >= 3:
            chest_type = 'medium'
        else:
            chest_type = 'small'

        chest_templates = self.dungeons_data.get('chest_templates', {})
        chest_data = chest_templates.get(chest_type,
                                         chest_templates.get('small', {}))

        print(f"It's a {chest_data.get('name', 'chest')}!")

        # Generate rewards
        gold_min, gold_max = chest_data.get('gold_range', [50, 150])
        gold_reward = random.randint(gold_min, gold_max)

        item_count_min, item_count_max = chest_data.get(
            'item_count_range', [1, 2])
        item_count = random.randint(item_count_min, item_count_max)

        exp_reward = chest_data.get('experience', 100)

        # Give rewards
        self.player.gold += gold_reward
        self.player.gain_experience(exp_reward)

        print(f"\n{Colors.GOLD}You found {gold_reward} gold!{Colors.END}")
        print(
            f"{Colors.MAGENTA}You gained {exp_reward} experience!{Colors.END}")

        # Generate items
        item_rarities = chest_data.get('item_rarity', ['common'])
        guaranteed_legendary = chest_data.get('guaranteed_legendary', False)

        items_found = []

        # Handle guaranteed legendary items
        if guaranteed_legendary:
            count = guaranteed_legendary if isinstance(guaranteed_legendary,
                                                       int) else 1
            legendary_items = [
                item for item in self.items_data.values()
                if item.get('rarity') == 'legendary'
            ]
            if legendary_items:
                for _ in range(min(count, len(legendary_items))):
                    item = random.choice(legendary_items)
                    items_found.append(item['name'])
                    self.player.inventory.append(item['name'])
                    self.update_mission_progress('collect', item['name'])
            else:
                # No legendary items available, add bonus gold instead
                bonus_gold = 100 * count
                self.player.gold += bonus_gold
                print(
                    f"{Colors.YELLOW}No legendary items found! Added {bonus_gold} bonus gold instead.{Colors.END}"
                )

        # Generate random items - with safety checks for empty item lists
        for _ in range(item_count - len(items_found)):
            rarity = random.choice(item_rarities)
            possible_items = [
                item for item in self.items_data.values()
                if item.get('rarity') == rarity
            ]

            if possible_items:
                item = random.choice(possible_items)
                items_found.append(item['name'])
                self.player.inventory.append(item['name'])
                self.update_mission_progress('collect', item['name'])
            else:
                # No items of this rarity, add bonus gold instead
                bonus_gold = random.randint(25, 75)
                self.player.gold += bonus_gold
                print(
                    f"{Colors.DARK_GRAY}No items of {rarity} rarity found. Added {bonus_gold} gold instead.{Colors.END}"
                )

        if items_found:
            print(self.lang.get("items_found"))
            for item in items_found:
                item_data = self.items_data.get(item, {})
                color = get_rarity_color(item_data.get('rarity', 'common'))
                print(f"  - {color}{item}{Colors.END}")

        self.advance_room()

    def handle_trap_chest_room(self, room: Dict[str, Any]):
        """Handle a trapped chest room"""
        if not self.player:
            print(self.lang.get('ui_no_player_trap'))
            self.advance_room()
            return
        print(self.lang.get('ui_suspicious_chest'))

        choice = ask("Open the chest (O) or leave it (L)? ").strip().upper()

        if choice == 'L':
            print(self.lang.get('ui_leave_chest_alone'))
            self.advance_room()
            return

        # Roll for trap
        trap_chance = 0.7  # 70% chance of trap
        if random.random() < trap_chance:
            print(self.lang.get("trap_triggered"))

            # Get random trap
            trap_templates = self.dungeons_data.get('challenge_templates',
                                                    {}).get('trap', {})
            trap_types = trap_templates.get('types', [])

            if trap_types:
                trap = random.choice(trap_types)
                print(trap['description'])

                # Roll d20 for trap avoidance
                roll = random.randint(1, 20)
                threshold = trap_templates.get('success_threshold', 10)

                # Apply difficulty modifier
                difficulty_mod = trap.get('difficulty', 'normal')
                mod_data = trap_templates.get('difficulty_modifiers',
                                              {}).get(difficulty_mod, {})
                threshold += mod_data.get('threshold',
                                          0) - 10  # Adjust threshold

                print(f"You roll a {roll} (need {threshold}+ to succeed)")

                if roll >= threshold:
                    print(
                        f"{Colors.GREEN}You successfully avoid the trap!{Colors.END}"
                    )

                    # Success reward
                    reward = trap_templates.get('success_reward', {})
                    if reward.get('gold'):
                        self.player.gold += reward['gold']
                        print(f"You found {reward['gold']} gold in the chest!")
                    if reward.get('experience'):
                        self.player.gain_experience(reward['experience'])
                        print(f"You gained {reward['experience']} experience!")

    def handle_multi_choice_room(self, room: Dict[str, Any]):
        """Handle a multiple choice decision room"""
        if not self.player:
            print(self.lang.get('ui_no_player_multichoice'))
            self.advance_room()
            return
        print(self.lang.get('ui_crossroads_paths'))

        # Get random selection challenge
        challenge_templates = self.dungeons_data.get('challenge_templates', {})
        selection_template = challenge_templates.get('selection', {})

        if not selection_template.get('types'):
            print(self.lang.get('ui_paths_safe'))
            self.advance_room()
            return

        challenge = random.choice(selection_template['types'])

        print(self.lang.get("ndecision"))
        print(challenge['question'])

        options = challenge.get('options', [])
        for i, option in enumerate(options, 1):
            print(f"{i}. {option['text']}")

        time_limit = challenge.get('time_limit', 30)
        start_time = time.time()

        choice = ask(f"Your choice (1-{len(options)}): ").strip()

        # Check time limit
        elapsed = time.time() - start_time
        if elapsed > time_limit:
            print(self.lang.get("you_took_too_long_to_decide"))
            # Random bad outcome
            bad_options = [
                opt for opt in options if not opt.get('correct', False)
            ]
            if bad_options:
                outcome = random.choice(bad_options)
            else:
                outcome = options[0]
        elif choice.isdigit() and 1 <= int(choice) <= len(options):
            outcome = options[int(choice) - 1]
        else:
            print(self.lang.get("invalid_choice"))
            return

        print(f"\n{outcome['reason']}")

        if outcome.get('correct', False):
            # Success reward
            reward = challenge.get('success_reward', {})
            if self.player:
                if reward.get('gold'):
                    self.player.gold += reward['gold']
                    print(f"You gained {reward['gold']} gold!")
                if reward.get('experience'):
                    self.player.gain_experience(reward['experience'])
                    print(f"You gained {reward['experience']} experience!")
        else:
            # Failure penalty
            if self.player:
                damage = challenge.get('failure_damage', 10)
                actual_damage = self.player.take_damage(damage)
                print(f"You took {actual_damage} damage!")

                if not self.player.is_alive():
                    self.dungeon_death()
                    return

        self.advance_room()

    def handle_empty_room(self, room: Dict[str, Any]):
        """Handle an empty room"""
        print(self.lang.get('ui_room_empty'))

        # Small chance for hidden treasure or encounter
        if random.random() < 0.3:  # 30% chance
            if random.random() < 0.5:
                # Hidden treasure
                if self.player:
                    gold_found = random.randint(10, 50)
                    self.player.gold += gold_found
                    print(
                        f"{Colors.GOLD}You found {gold_found} gold hidden in the room!{Colors.END}"
                    )
            else:
                # Random encounter
                print(self.lang.get('ui_hear_noise'))
                time.sleep(1)
                self.random_encounter()
                if self.player and not self.player.is_alive():
                    self.dungeon_death()
                    return
        else:
            print(self.lang.get('ui_nothing_interest'))

        self.advance_room()

    def handle_boss_room(self, room: Dict[str, Any]):
        """Handle the boss room"""
        dungeon = self.current_dungeon
        if dungeon:
            boss_id = dungeon.get('boss_id')
        else:
            boss_id = None

        if boss_id and boss_id in self.bosses_data:
            boss_data = self.bosses_data[boss_id]
            boss = Boss(boss_data, self.dialogues_data)

            print(self.lang.get("nboss_battle"))
            print(f"You face {boss.name}!")
            print(boss.description)

            # Print start dialogue if available
            start_dialogue = boss.get_dialogue("on_start_battle")
            if start_dialogue:
                print(
                    f"\n{Colors.CYAN}{boss.name}:{Colors.END} {start_dialogue}"
                )

            self.battle(boss)

            if self.player and self.player.is_alive():
                print(self.lang.get("nvictory"))
                print(f"You defeated {boss.name}!")

                # Boss rewards
                exp_reward = boss.experience_reward * 2  # Double XP for bosses
                gold_reward = boss.gold_reward * 2

                self.player.gain_experience(exp_reward)
                self.player.gold += gold_reward

                print(
                    f"Gained {Colors.MAGENTA}{exp_reward} experience{Colors.END}"
                )
                print(f"Gained {Colors.GOLD}{gold_reward} gold{Colors.END}")

                # Boss loot
                if boss.loot_table:
                    loot = random.choice(boss.loot_table)
                    self.player.inventory.append(loot)
                    print(f"{Colors.YELLOW}Boss loot: {loot}!{Colors.END}")
                    self.update_mission_progress('collect', loot)

                self.complete_dungeon()
            else:
                self.dungeon_death()
        else:
            # Boss not found - try to find a suitable replacement or generate a generic boss
            print(
                f"{Colors.YELLOW}Boss data not found. A powerful enemy appears!{Colors.END}"
            )

            # Try to use dungeon completion rewards as a "boss substitute"
            dungeon = self.current_dungeon
            if dungeon:
                completion_reward = dungeon.get('completion_reward', {})
                exp_reward = completion_reward.get('experience',
                                                   500) // 2  # Half reward
                gold_reward = completion_reward.get('gold', 300) // 2

                if self.player:
                    self.player.gain_experience(exp_reward)
                    self.player.gold += gold_reward

                    print(self.lang.get('ui_defeated_guardian'))
                    print(
                        f"Gained {Colors.MAGENTA}{exp_reward} experience{Colors.END}"
                    )
                    print(
                        f"Gained {Colors.GOLD}{gold_reward} gold{Colors.END}")

                    # Give a random item from completion reward if available
                    items = completion_reward.get('items', [])
                    if items:
                        loot = random.choice(items)
                        self.player.inventory.append(loot)
                        print(
                            f"{Colors.YELLOW}Special item: {loot}!{Colors.END}"
                        )

            self.complete_dungeon()

    def advance_room(self):
        """Advance to the next room"""
        self.dungeon_progress += 1
        if self.dungeon_progress < len(self.dungeon_rooms):
            self.dungeon_state['current_room'] = self.dungeon_progress

        if self.dungeon_progress >= len(self.dungeon_rooms):
            self.complete_dungeon()
        else:
            print(self.lang.get("nmoving_to_the_next_room"))
            time.sleep(1)
            clear_screen()

    def complete_dungeon(self):
        """Complete the current dungeon"""
        if not self.current_dungeon:
            return

        dungeon = self.current_dungeon
        print(self.lang.get("ndungeon_complete"))
        print(f"You successfully cleared {dungeon['name']}!")

        # Calculate completion time
        start_time_str = self.dungeon_state.get('start_time')
        if start_time_str:
            try:
                start_time = datetime.fromisoformat(start_time_str)
            except (ValueError, TypeError):
                start_time = datetime.now()
        else:
            start_time = datetime.now()
        end_time = datetime.now()
        duration = end_time - start_time

        print(
            f"Completion time: {duration.seconds // 60}m {duration.seconds % 60}s"
        )

        # Update challenge for dungeon completion
        self.update_challenge_progress('dungeon_complete')

        # Give completion rewards
        completion_reward = dungeon.get('completion_reward', {})
        if completion_reward and self.player:
            print(
                f"\n{Colors.GOLD}{Colors.BOLD}Completion Rewards:{Colors.END}")

            # Gold reward
            gold_reward = completion_reward.get('gold', 0)
            if gold_reward > 0:
                self.player.gold += gold_reward
                print(f"  {Colors.GOLD}+{gold_reward} gold{Colors.END}")

            # Experience reward
            exp_reward = completion_reward.get('experience', 0)
            if exp_reward > 0:
                self.player.gain_experience(exp_reward)
                print(
                    f"  {Colors.MAGENTA}+{exp_reward} experience{Colors.END}")

            # Item rewards
            items = completion_reward.get('items', [])
            if items:
                print(self.lang.get("items_received"))
                for item_name in items:
                    self.player.inventory.append(item_name)
                    item_data = self.items_data.get(item_name, {})
                    color = get_rarity_color(item_data.get('rarity', 'common'))
                    print(f"    - {color}{item_name}{Colors.END}")
                    self.update_mission_progress('collect', item_name)

        # Clear dungeon state
        self.current_dungeon = None
        self.dungeon_progress = 0
        self.dungeon_rooms = []
        self.dungeon_state = {}

    def exit_dungeon(self):
        """Exit the current dungeon"""
        if not self.player:
            return

        # Check for none here
        if self.current_dungeon is not None:
            print(
                f"\n{Colors.YELLOW}Exiting {self.current_dungeon['name']}...{Colors.END}"
            )
        else:
            print(self.lang.get("nexiting_dungeon"))

        # Optional: penalty for early exit
        if self.dungeon_progress > 0 and self.player:
            penalty_gold = min(self.player.gold // 10,
                               100)  # 10% of gold or 100 max
            if penalty_gold > 0:
                self.player.gold -= penalty_gold
                print(
                    f"{Colors.RED}Exit penalty: Lost {penalty_gold} gold{Colors.END}"
                )

        # Clear dungeon state
        self.current_dungeon = None
        self.dungeon_progress = 0
        self.dungeon_rooms = []
        self.dungeon_state = {}

    def dungeon_death(self):
        """Handle death in dungeon"""
        if not self.player:
            return
        print(
            f"\n{Colors.RED}{Colors.BOLD}You have fallen in the dungeon!{Colors.END}"
        )
        print(
            f"\n{Colors.RED}{Colors.BOLD}You have fallen in the dungeon!{Colors.END}"
        )

        if self.player:
            # Death penalty
            self.player.hp = self.player.max_hp // 2
            self.player.mp = self.player.max_mp // 2

            # Lose some gold
            gold_loss = min(self.player.gold // 5,
                            200)  # 20% of gold or 200 max
            self.player.gold -= gold_loss
            print(f"You lost {gold_loss} gold to the dungeon spirits.")

        # Return to starting village
        self.current_area = "starting_village"
        print(self.lang.get("respawn"))

        # Clear dungeon state
        self.current_dungeon = None
        self.dungeon_progress = 0
        self.dungeon_rooms = []
        self.dungeon_state = {}

    def visit_alchemy(self):
        """Visit the Alchemy workshop to craft items"""
        if not self.player:
            print(self.lang.get("no_character"))
            return

        if not self.crafting_data or not self.crafting_data.get('recipes'):
            print(self.lang.get('ui_no_crafting_recipes'))
            return

        print(
            f"\n{Colors.MAGENTA}{Colors.BOLD}=== ALCHEMY WORKSHOP ==={Colors.END}"
        )
        print(
            "Welcome to the Alchemy Workshop! Here you can craft potions, elixirs, and items."
        )
        print(f"\nYour gold: {Colors.GOLD}{self.player.gold}{Colors.END}")

        # Display available materials from inventory
        self._display_crafting_materials()

        while True:
            clear_screen()
            print(self.lang.get("n_alchemy_workshop"))
            print(
                "Categories: [P]otions, [E]lixirs, [E]ntchantments, [U]tility, [A]ll"
            )
            print(self.lang.get('ui_craft_item'))

            choice = ask("\nChoose an option: ").strip().upper()

            if choice == 'B' or not choice:
                break
            elif choice == 'P':
                self._display_recipes_by_category('Potions')
            elif choice == 'E':
                # Ask which type of E (Elixirs or Enchantments)
                print(self.lang.get('ui_elixirs_enchantments'))
                sub = ask("Choose (E/N): ").strip().upper()
                if sub == 'E':
                    self._display_recipes_by_category('Elixirs')
                elif sub == 'N':
                    self._display_recipes_by_category('Enchantments')
            elif choice == 'U':
                self._display_recipes_by_category('Utility')
            elif choice == 'A':
                self._display_all_recipes()
            elif choice == 'C':
                self._craft_item()
            elif choice == 'M':
                self._display_crafting_materials()
            else:
                print(self.lang.get("invalid_choice"))

    def _display_crafting_materials(self):
        """Display materials available in player's inventory"""
        if not self.player:
            return

        print(self.lang.get("n_your_materials"))

        # Get all material categories
        material_categories = self.crafting_data.get('material_categories', {})

        # Collect all possible materials
        all_materials = set()
        for materials in material_categories.values():
            all_materials.update(materials)

        # Count materials in inventory
        material_counts = {}
        for item in self.player.inventory:
            if item in all_materials:
                material_counts[item] = material_counts.get(item, 0) + 1

        if not material_counts:
            print(self.lang.get('ui_no_crafting_materials'))
            print(
                "Materials can be found as drops from enemies or purchased from shops."
            )
            return

        print(f"{'Material':<25} {'Quantity':<10}")
        print("-" * 35)
        for material, count in sorted(material_counts.items()):
            print(f"{material:<25} {count:<10}")

    def _display_recipes_by_category(self, category: str):
        """Display recipes filtered by category"""
        if not self.crafting_data:
            return

        recipes = self.crafting_data.get('recipes', {})
        category_recipes = [(rid, rdata) for rid, rdata in recipes.items()
                            if rdata.get('category') == category]

        if not category_recipes:
            print(f"\nNo recipes found in category: {category}")
            return

        print(f"\n{Colors.BOLD}=== {category.upper()} ==={Colors.END}")
        for i, (rid, rdata) in enumerate(category_recipes, 1):
            name = rdata.get('name', rid)
            rarity = rdata.get('rarity', 'common')
            rarity_color = get_rarity_color(rarity)
            print(f"{i}. {rarity_color}{name}{Colors.END}")

    def _display_all_recipes(self):
        """Display all available recipes"""
        if not self.crafting_data:
            return

        recipes = self.crafting_data.get('recipes', {})
        if not recipes:
            print(f"\n{self.lang.get('ui_no_recipes_available')}")
            return

        page_size = 10
        recipe_list = list(recipes.items())
        current_page = 0

        while True:
            start = current_page * page_size
            end = start + page_size
            page_items = recipe_list[start:end]

            print(self.lang.get("n_all_recipes"))
            for i, (rid, rdata) in enumerate(page_items, 1):
                name = rdata.get('name', rid)
                category = rdata.get('category', 'Unknown')
                rarity = rdata.get('rarity', 'common')
                rarity_color = get_rarity_color(rarity)
                print(
                    f"{start + i}. {rarity_color}{name}{Colors.END} ({category})"
                )

            total_pages = (len(recipe_list) + page_size - 1) // page_size
            print(f"\nPage {current_page + 1}/{total_pages}")

            if total_pages > 1:
                if current_page > 0:
                    print(f"P. {self.lang.get('ui_previous_page')}")
                if current_page < total_pages - 1:
                    print(f"N. {self.lang.get('ui_next_page')}")
            print(f"C. {self.lang.get('ui_craft_option')}")
            print(f"B. {self.lang.get('back')}")

            choice = ask("\nChoose an option: ").strip().upper()

            if choice == 'B':
                break
            elif choice == 'N' and current_page < total_pages - 1:
                current_page += 1
            elif choice == 'P' and current_page > 0:
                current_page -= 1
            elif choice == 'C':
                self._craft_item()
            else:
                print(self.lang.get("invalid_choice"))

    def _craft_item(self):
        """Craft an item using materials from inventory"""
        if not self.player or not self.crafting_data:
            print(self.lang.get('ui_cannot_craft'))
            return

        recipes = self.crafting_data.get('recipes', {})

        # Show all recipes for selection
        print(self.lang.get("n_craft_item"))
        recipe_names = list(recipes.keys())

        for i, rid in enumerate(recipe_names, 1):
            rdata = recipes[rid]
            name = rdata.get('name', rid)
            rarity = rdata.get('rarity', 'common')
            rarity_color = get_rarity_color(rarity)
            print(f"{i}. {rarity_color}{name}{Colors.END}")

        choice = ask(
            f"\nChoose recipe (1-{len(recipe_names)}) or press Enter to cancel: "
        ).strip()

        if not choice:
            return

        if not choice.isdigit():
            print(self.lang.get("invalid_choice"))
            return

        idx = int(choice) - 1
        if not (0 <= idx < len(recipe_names)):
            print(self.lang.get('invalid_recipe_number'))
            return

        recipe_id = recipe_names[idx]
        recipe = recipes[recipe_id]

        # Check skill requirement
        skill_req = recipe.get('skill_requirement', 1)
        if self.player.level < skill_req:
            print(
                f"\n{Colors.RED}You need at least level {skill_req} to craft this item.{Colors.END}"
            )
            return

        # Get materials required
        materials_needed = recipe.get('materials', {})

        # Check if player has materials
        missing_materials = []
        for material, quantity in materials_needed.items():
            in_inventory = self.player.inventory.count(material)
            if in_inventory < quantity:
                missing_materials.append(
                    f"{material} (need {quantity}, have {in_inventory})")

        if missing_materials:
            print(self.lang.get("nmissing_materials"))
            for m in missing_materials:
                print(f"  - {m}")
            print(f"\n{self.lang.get('ui_gather_more_materials')}")
            return

        # Show craft confirmation
        output_items = recipe.get('output', {})
        print(self.lang.get("n_craft_confirmation"))
        print(f"Recipe: {recipe.get('name')}")
        print(
            f"Output: {', '.join(f'{qty}x {item}' for item, qty in output_items.items())}"
        )
        print(f"\n{self.lang.get('ui_materials_consume')}")
        for material, quantity in materials_needed.items():
            print(f"  - {quantity}x {material}")

        confirm = ask("\nCraft this item? (y/n): ").strip().lower()
        if confirm != 'y':
            print(self.lang.get('ui_crafting_cancelled'))
            return

        # Consume materials
        for material, quantity in materials_needed.items():
            for _ in range(quantity):
                self.player.inventory.remove(material)

        # Add crafted items to inventory
        for item, quantity in output_items.items():
            for _ in range(quantity):
                self.player.inventory.append(item)
                self.update_mission_progress('collect', item)

        print(
            f"\n{Colors.GREEN}Successfully crafted {recipe.get('name')}!{Colors.END}"
        )
        for item, quantity in output_items.items():
            print(f"  Received: {quantity}x {item}")

    def _visit_general_shop(self, shop_data):
        """Visit a general shop (not housing)"""
        if not self.player:
            print(self.lang.get("no_character"))
            return

        shop_name = shop_data.get("name", "Shop")
        welcome_msg = shop_data.get("welcome_message",
                                    f"Welcome to {shop_name}!")
        items = shop_data.get("items", [])
        max_buy = shop_data.get("max_buy", 99)

        print(f"\n{Colors.BOLD}=== {shop_name.upper()} ==={Colors.END}")
        print(welcome_msg)
        print(f"Your gold: {Colors.GOLD}{self.player.gold}{Colors.END}")

        if not items:
            print(self.lang.get('ui_shop_no_items'))
            return

        # Group items by type for better display
        item_details = []
        for item_id in items:
            if item_id in self.items_data:
                item = self.items_data[item_id]
                item_details.append({
                    'id': item_id,
                    'name': item.get('name', item_id),
                    'type': item.get('type', 'misc'),
                    'rarity': item.get('rarity', 'common'),
                    'price': item.get('price', 0),
                    'description': item.get('description', '')
                })

        if not item_details:
            print(self.lang.get('ui_no_valid_items_shop'))
            return

        page_size = 8
        current_page = 0

        while True:
            start = current_page * page_size
            end = start + page_size
            page_items = item_details[start:end]

            print(f"\n--- Items (Page {current_page + 1}) ---")
            for i, item in enumerate(page_items, 1):
                rarity_color = get_rarity_color(item['rarity'])
                owned_count = self.player.inventory.count(item['id'])
                can_buy_more = owned_count < max_buy

                status = ""
                if not can_buy_more:
                    status = f" {Colors.RED}(Max owned: {max_buy}){Colors.END}"
                elif owned_count > 0:
                    status = f" {Colors.YELLOW}(Owned: {owned_count}){Colors.END}"

                print(
                    f"{start + i}. {rarity_color}{item['name']}{Colors.END} - {Colors.GOLD}{item['price']}g{Colors.END}{status}"
                )
                print(f"   {item['description']}")

            total_pages = (len(item_details) + page_size - 1) // page_size
            print(f"\nPage {current_page + 1}/{total_pages}")

            if total_pages > 1:
                if current_page > 0:
                    print(f"P. {self.lang.get('ui_previous_page')}")
                if current_page < total_pages - 1:
                    print(f"N. {self.lang.get('ui_next_page')}")
            print(f"B. {self.lang.get('back')}")

            choice = ask("\nChoose item to buy or option: ").strip().upper()

            if choice == 'B':
                break
            elif choice == 'N' and current_page < total_pages - 1:
                current_page += 1
            elif choice == 'P' and current_page > 0:
                current_page -= 1
            elif choice.isdigit():
                item_idx = int(choice) - 1
                if 0 <= item_idx < len(item_details):
                    item = item_details[item_idx]
                    owned_count = self.player.inventory.count(item['id'])

                    if owned_count >= max_buy:
                        print(
                            f"{Colors.RED}You already own the maximum amount ({max_buy}) of this item.{Colors.END}"
                        )
                        continue

                    if self.player.gold >= item['price']:
                        self.player.gold -= item['price']
                        self.player.inventory.append(item['id'])
                        print(
                            f"{Colors.GREEN}Purchased {item['name']} for {item['price']} gold!{Colors.END}"
                        )
                        self.update_mission_progress('collect', item['id'])
                    else:
                        print(
                            f"{Colors.RED}Not enough gold! Need {item['price']}, have {self.player.gold}.{Colors.END}"
                        )
                else:
                    print(self.lang.get("invalid_item_number"))
            else:
                print(self.lang.get("invalid_choice"))
        """Build structures - alias for build_home for now"""
        self.build_home()

    def run(self):
        """Main game loop"""
        choice = self.display_welcome()

        if choice == "new_game":
            self.create_character()
        elif choice == "load_game":
            self.load_game()
            if not self.player:
                print(self.lang.get('ui_no_game_loaded'))
                self.create_character()

        # Main game loop
        while True:
            self.main_menu()


def main():
    """Main entry point"""
    game = Game()

    # Setup global handlers for Ctrl+C and uncaught exceptions so we can save before exit
    try:
        # SIGINT handler
        def _handle_sigint(signum, frame):
            print(
                "\nReceived interrupt (SIGINT). Attempting to save before exit..."
            )
            try:
                game.save_on_error(filename_prefix="err_save_unstable_")
            finally:
                sys.exit(1)

        signal.signal(signal.SIGINT, _handle_sigint)

        # Unhandled exception hook
        def _handle_exception(exc_type, exc_value, exc_tb):
            print(
                "Unhandled exception occurred. Attempting to save game before exiting..."
            )
            try:
                game.save_on_error((exc_type, exc_value, exc_tb),
                                   filename_prefix="err_save_unstable_")
            except Exception:
                pass
            # Print the traceback to stderr then exit
            traceback.print_exception(exc_type, exc_value, exc_tb)
            sys.exit(1)

        sys.excepthook = _handle_exception
    except Exception:
        # If handler setup fails, continue without it
        pass

    game.run()


if __name__ == "__main__":
    clear_screen()
    main()
