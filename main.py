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
import subprocess
import tempfile

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
        return code if COLORS_ENABLED else ""


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

    return f"[{color}{filled}{Colors.END}{empty}] {percentage:.1f}%"


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

    return f"{Colors.BOLD}{Colors.RED}BOSS HP{Colors.END} [{color}{filled}{Colors.END}{empty}] {Colors.BOLD}{percentage:.1f}%{Colors.END} ({current}/{maximum})"


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

    return f"[{color}{filled}{Colors.END}{empty}] {current}/{maximum}"


def create_separator(char: str = "=", length: int = 60) -> str:
    """Create a visual separator line."""
    return char * length


def create_section_header(title: str, char: str = "=", width: int = 60) -> str:
    """Create a decorative section header."""
    padding = (width - len(title) - 2) // 2
    return f"{Colors.CYAN}{Colors.BOLD}{char * padding} {title} {char * padding}{Colors.END}"


def loading_indicator(message: str = "Loading"):
    """Display a loading indicator."""
    print(f"\n{Colors.YELLOW}{message}{Colors.END}", end="", flush=True)
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
    return f"{color}{item_name}{Colors.END}"


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
            print("Input cannot be empty. Please try again.")
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
                print(f"Invalid input. Did you mean: {', '.join(close)} ?")
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

# Check for Node.js availability for scripting
NODE_AVAILABLE = None


def _check_node_available():
    """Check if Node.js is available in the system"""
    global NODE_AVAILABLE
    if NODE_AVAILABLE is not None:
        return NODE_AVAILABLE
    try:
        result = subprocess.run(['node', '--version'],
                               capture_output=True,
                               text=True,
                               timeout=5)
        if result.returncode == 0:
            NODE_AVAILABLE = True
            print(f"{Colors.GREEN}Node.js detected: {result.stdout.strip()}{Colors.END}")
        else:
            NODE_AVAILABLE = False
    except (FileNotFoundError, subprocess.TimeoutExpired, Exception) as e:
        NODE_AVAILABLE = False
    return NODE_AVAILABLE


class ScriptingEngine:
    """JavaScript scripting engine using Node.js for game scripting functionality"""

    def __init__(self):
        self.scripting_enabled = False
        self.activities_file = 'scripts/activities.json'
        self.current_activities = []
        self._init_context()
        self._load_game_state_to_activities()

    def _load_game_state_to_activities(self):
        """Load current game state into activities.json for script access"""
        try:
            # Read current activities.json or create default structure
            data = {
                'version': '2.0',
                'last_updated': None,
                'activities': [],
                'player': {
                    'uuid': '',
                    'name': '',
                    'class': '',
                    'health': 100,
                    'maxHealth': 100,
                    'mp': 50,
                    'maxMP': 50,
                    'level': 1,
                    'exp': 0,
                    'gold': 100,
                    'inventory': [],
                    'companions': [],
                    'equipped': {
                        'weapon': None,
                        'offhand': None,
                        'armor': None,
                        'accessory': None
                    },
                    'lastItemConsumed': None,
                    'lastItemObtained': None
                },
                'location': {
                    'id': 'starting_village',
                    'name': 'Starting Village',
                    'connections': [],
                    'canRest': True,
                    'restCost': 10,
                    'difficulty': 1
                },
                'enemy': {
                    'id': '',
                    'name': '',
                    'isBoss': False,
                    'hp': 0,
                    'maxHp': 0
                },
                'battle': {
                    'active': False,
                    'enemyId': None,
                    'bossId': None
                },
                'missions': {
                    'finished': [],
                    'ongoing': [],
                    'notAccepted': []
                },
                'system': {
                    'latestSave': None
                },
                'effects': []
            }
            
            # Try to load existing file
            if os.path.exists(self.activities_file):
                with open(self.activities_file, 'r') as f:
                    existing = json.load(f)
                    # Merge with existing data
                    if existing.get('version') == '2.0':
                        data = existing
            
            # Write back to file
            with open(self.activities_file, 'w') as f:
                json.dump(data, f, indent=2)
                
            print(f"{Colors.CYAN}Activities file initialized{Colors.END}")
            
        except Exception as e:
            print(f"{Colors.YELLOW}Warning: Could not initialize activities: {e}{Colors.END}")
    
    def sync_game_state_to_activities(self, game_instance=None):
        """Sync current game state to activities.json for script access"""
        try:
            # Load existing data
            data = {
                'version': '2.0',
                'last_updated': None,
                'activities': [],
                'player': {
                    'uuid': '',
                    'name': '',
                    'class': '',
                    'health': 100,
                    'maxHealth': 100,
                    'mp': 50,
                    'maxMP': 50,
                    'level': 1,
                    'exp': 0,
                    'gold': 100,
                    'inventory': [],
                    'companions': [],
                    'equipped': {
                        'weapon': None,
                        'offhand': None,
                        'armor': None,
                        'accessory': None
                    },
                    'lastItemConsumed': None,
                    'lastItemObtained': None
                },
                'location': {
                    'id': 'starting_village',
                    'name': 'Starting Village',
                    'connections': [],
                    'canRest': True,
                    'restCost': 10,
                    'difficulty': 1
                },
                'enemy': {
                    'id': '',
                    'name': '',
                    'isBoss': False,
                    'hp': 0,
                    'maxHp': 0
                },
                'battle': {
                    'active': False,
                    'enemyId': None,
                    'bossId': None
                },
                'missions': {
                    'finished': [],
                    'ongoing': [],
                    'notAccepted': []
                },
                'system': {
                    'latestSave': None
                },
                'effects': []
            }
            
            # Try to load existing file
            if os.path.exists(self.activities_file):
                with open(self.activities_file, 'r') as f:
                    existing = json.load(f)
                    if existing.get('version') == '2.0':
                        data = existing
            
            # Update with current game state if game instance provided and has player
            if game_instance and hasattr(game_instance, 'player') and game_instance.player:
                data['player'] = {
                    'uuid': game_instance.player.uuid,
                    'name': game_instance.player.name,
                    'class': game_instance.player.character_class,
                    'health': game_instance.player.hp,
                    'maxHealth': game_instance.player.max_hp,
                    'mp': game_instance.player.mp,
                    'maxMP': game_instance.player.max_mp,
                    'level': game_instance.player.level,
                    'exp': game_instance.player.experience,
                    'gold': game_instance.player.gold,
                    'inventory': game_instance.player.inventory,
                    'companions': game_instance.player.companions,
                    'equipped': game_instance.player.equipment,
                    'lastItemConsumed': None,
                    'lastItemObtained': None
                }
            
            # Update with current location
            if game_instance and hasattr(game_instance, 'current_area'):
                area_data = game_instance.areas_data.get(game_instance.current_area, {})
                data['location'] = {
                    'id': game_instance.current_area,
                    'name': area_data.get('name', game_instance.current_area),
                    'connections': area_data.get('connections', []),
                    'canRest': area_data.get('can_rest', False),
                    'restCost': area_data.get('rest_cost', 10),
                    'difficulty': area_data.get('difficulty', 1)
                }
            
            # Update missions state
            if game_instance:
                data['missions'] = {
                    'finished': game_instance.completed_missions if hasattr(game_instance, 'completed_missions') else [],
                    'ongoing': list(game_instance.mission_progress.keys()) if hasattr(game_instance, 'mission_progress') else [],
                    'notAccepted': []
                }
            
            # Write back to file
            with open(self.activities_file, 'w') as f:
                json.dump(data, f, indent=2)
                
        except Exception as e:
            print(f"{Colors.YELLOW}Warning: Could not sync game state to activities: {e}{Colors.END}")
    
    def sync_activities_from_file(self):
        """Sync activities from activities.json back to Python state after script execution"""
        try:
            if os.path.exists(self.activities_file):
                with open(self.activities_file, 'r') as f:
                    data = json.load(f)
                    self.current_activities = data.get('activities', [])
                    
                print(f"{Colors.CYAN}Activities synced from file ({len(self.current_activities)} items){Colors.END}")
                return True
        except Exception as e:
            print(f"{Colors.YELLOW}Warning: Could not sync activities from file: {e}{Colors.END}")
        return False

    def _init_context(self):
        """Initialize the scripting context using Node.js"""
        if not _check_node_available():
            print(f"{Colors.YELLOW}Node.js not available. Scripting disabled.{Colors.END}")
            return

        try:
            # Test Node.js can execute
            result = subprocess.run(['node', '-e', 'console.log("test")'],
                                   capture_output=True,
                                   text=True,
                                   timeout=5)
            if result.returncode != 0:
                print(f"{Colors.YELLOW}Node.js test failed. Scripting disabled.{Colors.END}")
                return

            self.scripting_enabled = True
            print(f"{Colors.GREEN}Scripting engine initialized successfully.{Colors.END}")

        except Exception as e:
            print(f"{Colors.RED}Failed to initialize scripting engine: {e}{Colors.END}")
            self.scripting_enabled = False

    def execute_script(self, script_code: str) -> bool:
        """Execute JavaScript code using Node.js"""
        if not self.scripting_enabled:
            return False

        try:
            # Create a temporary file with the script
            with tempfile.NamedTemporaryFile(mode='w', suffix='.js', delete=False) as f:
                # Write the API first
                api_file = 'scripts/scripting_API.js'
                if os.path.exists(api_file):
                    with open(api_file, 'r') as api_f:
                        f.write(api_f.read())
                        f.write('\n')

                # Write the user script
                f.write('\n// User script\n')
                f.write(script_code)
                f.write('\n')

                temp_path = f.name

            # Execute with Node.js
            result = subprocess.run(['node', temp_path],
                                   capture_output=True,
                                   text=True,
                                   timeout=30)

            # Clean up temp file
            try:
                os.unlink(temp_path)
            except Exception:
                pass

            # Print any output
            if result.stdout.strip():
                for line in result.stdout.strip().split('\n'):
                    print(f"{Colors.CYAN}[Script] {line}{Colors.END}")

            # Check for errors
            if result.returncode != 0:
                if result.stderr.strip():
                    print(f"{Colors.RED}Script error: {result.stderr}{Colors.END}")
                return False

            return True

        except subprocess.TimeoutExpired:
            print(f"{Colors.RED}Script execution timed out{Colors.END}")
            return False
        except Exception as e:
            print(f"{Colors.RED}Script execution error: {e}{Colors.END}")
            return False

    def execute_file(self, filepath: str) -> bool:
        """Execute a JavaScript file using Node.js"""
        if not os.path.exists(filepath):
            return False

        if not self.scripting_enabled:
            return False

        try:
            # Execute with Node.js
            result = subprocess.run(['node', filepath],
                                   capture_output=True,
                                   text=True,
                                   timeout=30)

            # Print any output
            if result.stdout.strip():
                for line in result.stdout.strip().split('\n'):
                    print(f"{Colors.CYAN}[Script] {line}{Colors.END}")

            # Check for errors
            if result.returncode != 0:
                if result.stderr.strip():
                    print(f"{Colors.RED}Script error: {result.stderr}{Colors.END}")
                return False

            return True

        except subprocess.TimeoutExpired:
            print(f"{Colors.RED}Script execution timed out{Colors.END}")
            return False
        except Exception as e:
            print(f"{Colors.RED}Error executing script file {filepath}: {e}{Colors.END}")
            return False
    
    def load_activities(self) -> List[Dict]:
        """Load activities from the activities file"""
        try:
            if os.path.exists(self.activities_file):
                with open(self.activities_file, 'r') as f:
                    data = json.load(f)
                    self.current_activities = data.get('activities', [])
                    return self.current_activities
        except Exception as e:
            print(f"{Colors.RED}Error loading activities: {e}{Colors.END}")
        return []
    
    def save_activities(self):
        """Save activities to the activities file"""
        try:
            data = {
                'activities': self.current_activities,
                'last_updated': datetime.now().isoformat(),
                'scripting_enabled': self.scripting_enabled,
                'version': '1.0'
            }
            with open(self.activities_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"{Colors.RED}Error saving activities: {e}{Colors.END}")
    
    def add_activity(self, activity_type: str, details: Optional[Dict] = None):
        """Add an activity to the tracking list"""
        activity: Dict[str, Any] = {
            'type': activity_type,
            'timestamp': datetime.now().isoformat()
        }
        if details:
            activity['details'] = details
        
        self.current_activities.append(activity)
        
        # Keep only last 1000 activities to prevent file bloat
        if len(self.current_activities) > 1000:
            self.current_activities = self.current_activities[-1000:]
    
    def clear_activities(self):
        """Clear all activities"""
        self.current_activities = []
        self.save_activities()
    
    def get_activities(self) -> List[Dict]:
        """Get all recorded activities"""
        return self.current_activities
    
    def execute_scripts_from_config(self, game_instance=None):
        """Execute all scripts listed in scripts/scripts.json"""
        scripts_config = 'scripts/scripts.json'

        if not os.path.exists(scripts_config):
            return

        # Sync game state to activities.json before executing scripts
        self.sync_game_state_to_activities(game_instance)

        try:
            with open(scripts_config, 'r') as f:
                config = json.load(f)

            if isinstance(config, list):
                scripts = config
            elif isinstance(config, dict) and config.get('scripts'):
                scripts = config['scripts']
            else:
                return

            for script_name in scripts:
                script_path = f"scripts/{script_name}.js"
                if os.path.exists(script_path):
                    print(f"{Colors.CYAN}Executing script: {script_name}{Colors.END}")
                    self.execute_file(script_path)
                    self.add_activity('script_executed', {'script': script_name})
            
            # Sync activities back from file after script execution
            self.sync_activities_from_file()
            
            # Sync game state again to capture any changes made by scripts
            self.sync_game_state_to_activities(game_instance)
            
        except Exception as e:
            print(f"{Colors.RED}Error executing scripts from config: {e}{Colors.END}")
    
    def reload_api(self):
        """Reload the scripting API"""
        self._init_context()
    
    def is_enabled(self) -> bool:
        """Check if scripting is enabled"""
        return self.scripting_enabled


# Global scripting engine instance
scripting_engine = ScriptingEngine()


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

    def fetch_market_data(self, force_refresh: bool = False) -> Optional[Dict[str, Any]]:
        """Fetch market data from the API with caching and cooldown"""
        # Check cache validity
        if not force_refresh and self._is_cache_valid():
            print(f"{Colors.CYAN}Visiting the market...{Colors.END}")
            return self.cache

        # Check cooldown
        if self.last_fetch and not self._is_cache_valid():
            remaining = timedelta(minutes=self.cooldown_minutes) - (datetime.now() - self.last_fetch)
            mins = int(remaining.total_seconds() // 60)
            secs = int(remaining.total_seconds() % 60)
            print(
                f"{Colors.YELLOW}Merchants have left and the market is closed! Please come back in {mins}m {secs}s{Colors.END}"
            )
            return None

        print(f"{Colors.CYAN}Checking if merchants are in the market...{Colors.END}")

        # Try to fetch from API using requests
        if REQUESTS_AVAILABLE and requests is not None:
            try:
                response = requests.get(MARKET_API_URL, timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    self.cache = data
                    self.last_fetch = datetime.now()
                    print(f"{Colors.GREEN}Market is open!{Colors.END}")
                    return data
                else:
                    print(f"{Colors.RED}Failed to reach to the market: HTTP {response.status_code}{Colors.END}")
            except requests.exceptions.RequestException as e:
                print(f"{Colors.RED}Network error: {e}{Colors.END}")
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
                 player_uuid: Optional[str] = None):
        self.name = name
        self.character_class = character_class
        self.uuid = player_uuid or str(uuid.uuid4())
        # Rank system based on level
        self.rank = "Novice"
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

        # Battle state
        self.defending = False

        # Active temporary buffs/debuffs: list of {name, duration, modifiers}
        # modifiers is a dict like {"attack_bonus": 5, "defense_bonus": 2}
        self.active_buffs: List[Dict[str, Any]] = []

        # Track killed bosses for cooldown: {boss_name: timestamp_str}
        self.bosses_killed: Dict[str, str] = {}

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
            self.mp = self.max_mp

        print(
            f"{Colors.GREEN}{Colors.BOLD}Level Up!{Colors.END} You are now level {self.level}!"
        )
        # Update rank when leveling
        self._update_rank()

    def _update_rank(self):
        """Simple rank tiers based on level"""
        if self.level >= 30:
            self.rank = "Legend"
        elif self.level >= 20:
            self.rank = "Champion"
        elif self.level >= 15:
            self.rank = "Elite"
        elif self.level >= 10:
            self.rank = "Veteran"
        elif self.level >= 5:
            self.rank = "Adept"
        else:
            self.rank = "Novice"

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
            print("All accessory slots are full. Replace one?")
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

    def __init__(self, boss_data: Dict):
        super().__init__(boss_data)
        self.description = boss_data.get("description", "A powerful foe.")
        self.special_abilities = boss_data.get("special_abilities", [])
        self.phases = boss_data.get("phases", [])
        self.current_phase_index = -1
        self.mp = 100
        self.max_mp = 100
        self.cooldowns = {}

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


class Game:
    """Main game class"""

    def __init__(self):
        self.player: Optional[Character] = None
        self.current_area = "starting_village"
        self.enemies_data: Dict[str, Any] = {}
        self.areas_data: Dict[str, Any] = {}
        self.items_data: Dict[str, Any] = {}
        self.missions_data: Dict[str, Any] = {}
        self.bosses_data: Dict[str, Any] = {}
        self.classes_data: Dict[str, Any] = {}
        self.spells_data: Dict[str, Any] = {}
        self.effects_data: Dict[str, Any] = {}
        self.companions_data: Dict[str, Any] = {}
        self.mission_progress: Dict[str, Any] = {
        }  # mission_id -> {current_count, target_count, completed, type}
        self.completed_missions: List[str] = []
        self.config: Dict[str, Any] = {}
        self.market_api: Optional[MarketAPI] = None
        self.crafting_data: Dict[str, Any] = {}

        # Load game data
        self.load_game_data()
        self.load_config()

    def load_game_data(self):
        """Load all game data from JSON files"""
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
        except FileNotFoundError as e:
            print(f"Error loading game data: {e}")
            print("Please ensure all data files exist in the data/ directory.")
            sys.exit(1)

    def load_config(self):
        """Load configuration from config.json"""
        try:
            with open('data/config.json', 'r') as f:
                self.config = json.load(f)
        except FileNotFoundError:
            # Default config if file doesn't exist
            self.config = {
                'auto_load_scripts': True,
                'scripts_enabled': True,
                'autosave_enabled': True,
                'autosave_interval': 5,
                'colors_enabled': True
            }
            self.scripting_enabled = False
        except json.JSONDecodeError:
            print("Warning: config.json is invalid JSON. Using defaults.")
            self.scripting_enabled = False

        # Set global color toggle
        global COLORS_ENABLED
        COLORS_ENABLED = self.config.get('colors_enabled', True)

        # Initialize Market API
        self.market_api = MarketAPI()

    def display_welcome(self) -> str:
        """Display welcome screen"""
        while True:
            clear_screen()
            print(f"{Colors.CYAN}{Colors.BOLD}")
            print("=" * 60)
            print("             OUR LEGACY")
            print("       Text-Based CLI Fantasy RPG")
            print("=" * 60)
            print(f"{Colors.END}")
            print("Welcome, adventurer! Your legacy awaits...")
            print(
                "Choose your path wisely, for every decision shapes your destiny."
            )
            print()

            print(f"{Colors.BOLD}=== MAIN MENU ==={Colors.END}")
            print("1. New Game")
            print("2. Load Game")
            print("3. Configurations")
            print("4. Quit")
            print()

            choice = ask("Choose an option (1-4): ")
            if choice == "1":
                return "new_game"
            elif choice == "2":
                return "load_game"
            elif choice == "3":
                self.configurations_menu()
            elif choice == "4":
                print("Thank you for playing Our Legacy!")
                clear_screen()
                sys.exit(0)
            else:
                print("Invalid choice. Please enter 1, 2, 3, or 4.")

    def configurations_menu(self):
        """Display and allow toggling of configuration settings"""
        while True:
            clear_screen()
            print(f"{Colors.BOLD}=== CONFIGURATIONS ==={Colors.END}")

            # Scripts Enabled
            scripts_enabled = self.config.get('scripts_enabled', True)
            scripts_color = Colors.GREEN if scripts_enabled else Colors.RED
            scripts_status = "Enabled" if scripts_enabled else "Disabled"
            print(
                f"1. Scripts Enabled: {scripts_color}{scripts_status}{Colors.END}"
            )

            # Autosave Enabled
            autosave_enabled = self.config.get('autosave_enabled', True)
            autosave_color = Colors.GREEN if autosave_enabled else Colors.RED
            autosave_status = "Enabled" if autosave_enabled else "Disabled"
            print(
                f"2. Autosave Enabled: {autosave_color}{autosave_status}{Colors.END}"
            )

            # Auto Load Scripts
            auto_load = self.config.get('auto_load_scripts', True)
            auto_load_color = Colors.GREEN if auto_load else Colors.RED
            auto_load_status = "Enabled" if auto_load else "Disabled"
            print(
                f"3. Auto Load Scripts: {auto_load_color}{auto_load_status}{Colors.END}"
            )

            # Colors Enabled
            colors_enabled = self.config.get('colors_enabled', True)
            colors_color = Colors.GREEN if colors_enabled else Colors.RED
            colors_status = "Enabled" if colors_enabled else "Disabled"
            print(
                f"4. Colors Enabled: {colors_color}{colors_status}{Colors.END}"
            )

            print("5. Back to Main Menu")

            choice = ask("Choose an option (1-5): ")
            if choice == "1":
                # Toggle scripts_enabled
                self.config['scripts_enabled'] = not scripts_enabled
                print(
                    f"Scripts Enabled set to: {'Enabled' if self.config['scripts_enabled'] else 'Disabled'}"
                )
                self.save_config()
            elif choice == "2":
                # Toggle autosave_enabled
                self.config['autosave_enabled'] = not autosave_enabled
                print(
                    f"Autosave Enabled set to: {'Enabled' if self.config['autosave_enabled'] else 'Disabled'}"
                )
                self.save_config()
            elif choice == "3":
                # Toggle auto_load_scripts
                self.config['auto_load_scripts'] = not auto_load
                print(
                    f"Auto Load Scripts set to: {'Enabled' if self.config['auto_load_scripts'] else 'Disabled'}"
                )
                self.save_config()
            elif choice == "4":
                # Toggle colors_enabled
                self.config['colors_enabled'] = not colors_enabled
                global COLORS_ENABLED
                COLORS_ENABLED = self.config['colors_enabled']
                print(
                    f"Colors Enabled set to: {'Enabled' if self.config['colors_enabled'] else 'Disabled'}"
                )
                self.save_config()
            elif choice == "5":
                break
            else:
                print("Invalid choice. Please enter 1, 2, 3, 4, or 5.")
            time.sleep(1)  # Brief pause

    def save_config(self):
        """Save the current config to config.json"""
        try:
            with open('data/config.json', 'w') as f:
                json.dump(self.config, f, indent=2)
            print("Configuration saved.")
        except Exception as e:
            print(f"Error saving config: {e}")

    def display_available_classes(self):
        """Display all available character classes from classes.json"""
        print("\nChoose your class:")

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
        print(f"{Colors.BOLD}Character Creation{Colors.END}")
        print("-" * 30)

        name = ask("Enter your character's name: ")
        if not name:
            name = "Hero"

        # Use dynamic class selection instead of hardcoded options
        self.display_available_classes()

        character_class = self.select_class()

        self.player = Character(name, character_class, self.classes_data)
        print(
            f"\n{Colors.GREEN}Welcome, {name} the {character_class}!{Colors.END}"
        )

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

    def main_menu(self):
        """Display main menu"""
        # Continuous mission check on every main menu return
        self.update_mission_progress('check', '')

        print(f"\n{Colors.BOLD}=== MAIN MENU ==={Colors.END}")
        print("1. Explore")
        print("2. View Character")
        print("3. Travel")
        print("4. Inventory")
        print("5. Missions")
        print("6. Fight Boss")
        print("7. Tavern")
        print("8. Shop")
        print("9. Alchemy")
        print("10. Elite Market")
        print("11. Rest")
        print("12. Companions")
        print("13. Save Game")
        print("14. Load Game")
        print("15. Claim Rewards")
        print("16. Quit")
        choice = ask("Choose an option (1-16): ", allow_empty=False)

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
            'save': '13',
            'load': '14',
            'l': '14',
            'claim': '15',
            'c': '15',
            'quit': '16',
            'q': '16'
        }

        normalized = choice.strip().lower()
        if normalized in shortcut_map:
            choice = shortcut_map[normalized]

        if choice == "1":
            self.explore()
            # Execute scripts after user action
            if self.config.get('auto_load_scripts', True) and self.config.get('scripts_enabled', True):
                scripting_engine.execute_scripts_from_config(self)
        elif choice == "2":
            if self.player:
                self.player.display_stats()
                if self.config.get('auto_load_scripts', True) and self.config.get('scripts_enabled', True):
                    scripting_engine.execute_scripts_from_config(self)
            else:
                print("No character created yet.")
        elif choice == "3":
            self.travel()
            if self.config.get('auto_load_scripts', True) and self.config.get('scripts_enabled', True):
                scripting_engine.execute_scripts_from_config(self)
        elif choice == "4":
            self.view_inventory()
            if self.config.get('auto_load_scripts', True) and self.config.get('scripts_enabled', True):
                scripting_engine.execute_scripts_from_config(self)           
        elif choice == "5":
            self.view_missions()
            if self.config.get('auto_load_scripts', True) and self.config.get('scripts_enabled', True):
                scripting_engine.execute_scripts_from_config(self)
        elif choice == "6":
            self.fight_boss_menu()
            if self.config.get('auto_load_scripts', True) and self.config.get('scripts_enabled', True):
                scripting_engine.execute_scripts_from_config(self)            
        elif choice == "7":
            self.visit_tavern()
            if self.config.get('auto_load_scripts', True) and self.config.get('scripts_enabled', True):
                scripting_engine.execute_scripts_from_config(self)
        elif choice == "8":
            self.visit_shop()
            if self.config.get('auto_load_scripts', True) and self.config.get('scripts_enabled', True):
                scripting_engine.execute_scripts_from_config(self)
        elif choice == "9":
            self.visit_alchemy()
            if self.config.get('auto_load_scripts', True) and self.config.get('scripts_enabled', True):
                scripting_engine.execute_scripts_from_config(self)
        elif choice == "10":
            self.visit_market()
            if self.config.get('auto_load_scripts', True) and self.config.get('scripts_enabled', True):
                scripting_engine.execute_scripts_from_config(self)
        elif choice == "11":
            self.rest()
            if self.config.get('auto_load_scripts', True) and self.config.get('scripts_enabled', True):
                scripting_engine.execute_scripts_from_config(self)
        elif choice == "12":
            self.manage_companions()
            if self.config.get('auto_load_scripts', True) and self.config.get('scripts_enabled', True):
                scripting_engine.execute_scripts_from_config(self)
        elif choice == "13":
            self.save_game()
            if self.config.get('auto_load_scripts', True) and self.config.get('scripts_enabled', True):
                scripting_engine.execute_scripts_from_config(self)
        elif choice == "14":
            self.load_game()
            if self.config.get('auto_load_scripts', True) and self.config.get('scripts_enabled', True):
                scripting_engine.execute_scripts_from_config(self)
        elif choice == "15":
            self.claim_rewards()
            if self.config.get('auto_load_scripts', True) and self.config.get('scripts_enabled', True):
                scripting_engine.execute_scripts_from_config(self)
        elif choice == "16":
            self.quit_game()
            if self.config.get('auto_load_scripts', True) and self.config.get('scripts_enabled', True):
                scripting_engine.execute_scripts_from_config(self)
        else:
            print("Invalid choice. Please try again.")
            if self.config.get('auto_load_scripts', True) and self.config.get('scripts_enabled', True):
                scripting_engine.execute_scripts_from_config(self)

    def fight_boss_menu(self):
        """Menu to select and fight a boss in the current area"""
        if not self.player:
            print("No character created yet.")
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
                    boss = Boss(boss_data)
                    print(
                        f"\n{Colors.RED}{Colors.BOLD}Challenge accepted!{Colors.END}"
                    )
                    self.battle(boss)
            else:
                print("Invalid choice.")

    def explore(self):
        """Explore the current area"""
        if not self.player:
            print("No character created yet. Please create a character first.")
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
            print("You explore the area but find nothing of interest.")

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
            print("No enemies found in this area.")
            return

        # Regular enemy encounter
        enemy_name = random.choice(possible_enemies)
        enemy_data = self.enemies_data.get(enemy_name)

        if enemy_data:
            enemy = Enemy(enemy_data)
            print(f"\n{Colors.RED}A wild {enemy.name} appears!{Colors.END}")
            self.battle(enemy)
        else:
            print("You explore the area but find no enemies.")

    def battle(self, enemy: Enemy):
        """Handle turn-based battle"""
        if not self.player:
            return

        print(f"\n{Colors.BOLD}=== BATTLE ==={Colors.END}")
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
            print(f"\n{Colors.YELLOW}You fled from the battle!{Colors.END}")
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

            print(
                f"Gained {Colors.MAGENTA}{exp_reward} experience{Colors.END}")
            print(f"Gained {Colors.GOLD}{gold_reward} gold{Colors.END}")

            self.player.gain_experience(exp_reward)
            self.player.gold += gold_reward

            # Update mission progress for kill
            self.update_mission_progress('kill', enemy.name)

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
            print("You respawn at the starting village.")
            self.current_area = "starting_village"

    def player_turn(self, enemy: Enemy) -> bool:
        """Player's turn in battle. Returns False if player fled."""
        if not self.player:
            return True

        print(f"\n{Colors.BOLD}Your turn!{Colors.END}")
        print("1. Attack")
        print("2. Use Item")
        print("3. Defend")
        print("4. Flee")
        # Can only cast spells if weapon is magic-capable
        weapon_name: Optional[str] = self.player.equipment.get('weapon')
        weapon_data = self.items_data.get(weapon_name,
                                          {}) if weapon_name else {}
        can_cast = bool(weapon_data.get('magic_weapon'))
        if can_cast:
            print("5. Cast Spell")

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
            print("You defend, reducing incoming damage by half!")
            self.player.defending = True
        elif choice == "4":
            flee_chance = 0.7 if self.player.get_effective_speed(
            ) > enemy.speed else 0.4
            if random.random() < flee_chance:
                print("You successfully fled from battle!")
                return False
            else:
                print("Failed to flee!")
                return True
        else:
            print("Invalid choice. You lose your turn!")

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
            print("No consumable items available!")
            return

        print("Available consumables:")
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
                print("Invalid choice!")
        except ValueError:
            print("Invalid input!")

    def cast_spell(self, enemy: Enemy, weapon_name: Optional[str] = None):
        """Cast a spell from the player's equipped magic weapon."""
        if not self.player:
            return

        # Handle case where no weapon is equipped
        if not weapon_name:
            print("You need to equip a magic weapon to cast spells.")
            return

        # Gather spells allowed by the equipped weapon
        available = []
        for sname, sdata in self.spells_data.items():
            allowed = sdata.get('allowed_weapons', [])
            if weapon_name in allowed:
                available.append((sname, sdata))

        if not available:
            print("No spells available for your weapon.")
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

            print(f"\n{Colors.YELLOW}Options:{Colors.END}")
            if total_pages > 1:
                if page > 0:
                    print("P. Previous Page")
                if page < total_pages - 1:
                    print("N. Next Page")

            print(f"1-{len(current_spells)}. Cast Spell")
            print("B. Back")

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
                    print("Invalid selection.")
                    time.sleep(1)
            else:
                print("Invalid choice.")
                time.sleep(1)

        cost = sdata.get('mp_cost', 0)
        if self.player.mp < cost:
            print("Not enough MP to cast that spell.")
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
            print("No character created yet.")
            return

        print(f"\n{Colors.BOLD}=== INVENTORY ==={Colors.END}")
        print(f"Gold: {Colors.GOLD}{self.player.gold}{Colors.END}")

        if not self.player.inventory:
            print("Your inventory is empty.")
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
            print("\nEquipment options:")
            print("  E. Equip an item from inventory")
            print("  U. Unequip a slot")
            choice = ask("Choose option (E/U) or press Enter to return: ")
            if choice.lower() == 'e':
                print("\nEquipable items:")
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
                print("\nCurrently equipped:")
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
                        print("Nothing to unequip from that slot.")

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
                print(f"\n{Colors.CYAN}--- Active Missions ---{Colors.END}")
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

                print("\nOptions: [A] Available, [C] Cancel Mission, [B] Back")
            else:
                print("\nNo active missions.")
                print("\nOptions: [A] Available Missions, [B] Back")

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
                        print("Invalid mission number.")
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
                print("\nNo new missions available at this time.")
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
                    print("P. Previous Page")
                if page < total_pages - 1:
                    print("N. Next Page")

            if current_page_missions:
                print(f"1-{len(current_page_missions)}. Accept Mission")
            print("B. Back")

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
                    print("Invalid mission number.")
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
                time.sleep(1)
            else:
                print("Error: Mission data not found.")
                time.sleep(1)
        else:
            print("Mission already accepted!")
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
            time.sleep(2)

    def claim_rewards(self):
        """Claim rewards for completed missions"""
        if not self.player:
            print("No character created yet.")
            return

        completed_missions = [
            mid for mid, progress in self.mission_progress.items()
            if progress.get('completed', False)
        ]
        if not completed_missions:
            print("No completed missions to claim rewards for.")
            return

        print(f"\n{Colors.BOLD}=== CLAIM REWARDS ==={Colors.END}")
        print("Completed missions:")
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

                print(f"\n{Colors.GREEN}Rewards claimed!{Colors.END}")
                print(f"Gained {Colors.MAGENTA}{exp} experience{Colors.END}")
                print(f"Gained {Colors.GOLD}{gold} gold{Colors.END}")
                if items:
                    print(f"Received items: {', '.join(items)}")
            else:
                print("Invalid choice.")

    def visit_shop(self):
        """Visit the shop - displays items for sale in the current area"""
        if not self.player:
            print("No character created yet.")
            return

        area_data = self.areas_data.get(self.current_area, {})
        area_shops = area_data.get("shops", [])

        if not area_shops:
            print(
                f"\n{Colors.RED}There are no shops in {area_data.get('name', self.current_area)}.{Colors.END}"
            )
            return

        # Simple logic: combine all items from all shops in this area
        # In this game, shops are mostly identifiers, but we can filter items by their 'shop_type' or similar
        # For now, let's filter items_data to only show relevant items for the current area
        # Most areas have specific shop IDs like "general_store", "equipment_shop"

        print(
            f"\n{Colors.BOLD}=== SHOP ({', '.join(area_shops)}) ==={Colors.END}"
        )
        print("Welcome to the shop! What would you like to buy?")
        print(f"\nYour gold: {Colors.GOLD}{self.player.gold}{Colors.END}")

        # Filter items based on the shop types available in the area
        shop_items = {}
        for item_name, item_data in self.items_data.items():
            # Skip materials and items already in inventory
            if item_data.get(
                    "type"
            ) == "material" or item_name in self.player.inventory:
                continue

            # Check if item belongs to any shop in the current area
            # If item has no shop_tags, it might be a general item
            item_shops = item_data.get("shops", ["general_store"])
            if any(s in area_shops for s in item_shops):
                shop_items[item_name] = item_data

        if not shop_items:
            print("No items available for purchase here.")
            return

        # Paginate items (10 per page)
        items_list = list(shop_items.items())
        page_size = 10
        current_page = 0

        while True:
            start = current_page * page_size
            end = start + page_size
            page_items = items_list[start:end]

            if not page_items:
                print("No more items.")
                break

            print(
                f"\n--- Page {current_page + 1} of {(len(items_list) + page_size - 1) // page_size} ---"
            )
            for i, (item_name, item_data) in enumerate(page_items, 1):
                price = item_data.get("price", "?")
                rarity = item_data.get("rarity", "unknown")
                desc = item_data.get("description", "")
                print(
                    f"{i}. {item_name} ({rarity}) - {Colors.GOLD}{price} gold{Colors.END}"
                )
                print(f"   {desc}")

            print("Shortcuts: N-next, P-prev, Enter-leave")
            choice = ask(
                f"\nBuy item (1-{len(page_items)}), [N]ext page, [P]rev page, [S]ell, or press Enter to leave: "
            )

            if not choice:
                break
            elif choice.lower() == 'n':
                if end < len(items_list):
                    current_page += 1
                else:
                    print("No more pages.")
            elif choice.lower() == 'p':
                if current_page > 0:
                    current_page -= 1
                else:
                    print("Already on first page.")
            elif choice.isdigit():
                item_idx = int(choice) - 1
                if 0 <= item_idx < len(page_items):
                    item_name, item_data = page_items[item_idx]
                    price = item_data.get("price", 0)
                    if self.player.gold >= price:
                        self.player.gold -= price
                        self.player.inventory.append(item_name)
                        print(f"Purchased {item_name} for {price} gold!")
                        self.update_mission_progress('collect', item_name)
                    else:
                        print("Not enough gold!")
                else:
                    print("Invalid choice.")
            elif choice.lower() == 's':
                # Sell flow
                self.shop_sell()

    def visit_tavern(self):
        """Visit the tavern to hire companions."""
        if not self.player:
            print("No character created yet.")
            return

        print(f"\n{Colors.BOLD}=== TAVERN ==={Colors.END}")
        print(
            "Welcome to The Rusty Tankard. Here you can hire companions to join your party."
        )
        print(f"Your gold: {Colors.GOLD}{self.player.gold}{Colors.END}")

        companions = list(self.companions_data.items())
        if not companions:
            print("No companions are available at the moment.")
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

            print("Shortcuts: N-next, P-prev, Enter-leave")
            choice = ask(
                f"\nHire companion (1-{len(page_items)}) or press Enter to leave: "
            )

            if not choice:
                break
            elif choice.lower() == 'n':
                if end < len(companions):
                    current_page += 1
                else:
                    print("No more pages.")
            elif choice.lower() == 'p':
                if current_page > 0:
                    current_page -= 1
                else:
                    print("Already on first page.")
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
                        print("Not enough gold!")
                else:
                    print("Invalid choice.")

    def visit_market(self):
        """Visit the Elite Market - browse and buy items from the API at 50% off"""
        if not self.player:
            print("No character created yet.")
            return

        if not self.market_api:
            print("Market API not available.")
            return

        print(f"\n{Colors.MAGENTA}{Colors.BOLD}=== ELITE MARKET ==={Colors.END}")
        print("Welcome to the Elite Market! All items sold at 50% OFF!")
        print(f"\nYour gold: {Colors.GOLD}{self.player.gold}{Colors.END}")

        # Check cooldown
        remaining = self.market_api.get_cooldown_remaining()
        if remaining and remaining.total_seconds() > 0:
            mins = int(remaining.total_seconds() // 60)
            secs = int(remaining.total_seconds() % 60)
            print(f"\n{Colors.YELLOW}Market cooldown: {mins}m {secs}s remaining{Colors.END}")

        # Fetch market data
        market_data = self.market_api.fetch_market_data()
        if not market_data or not market_data.get('ok'):
            print(f"\n{Colors.RED}{Colors.BOLD}Market is currently closed!{Colors.END}")
            print(f"{Colors.YELLOW}Merchants have travelled to another distant far place!{Colors.END}")
            print(f"{Colors.YELLOW}Please wait until the merchants arrive!{Colors.END}")
            return

        items = self.market_api.get_all_items()
        if not items:
            print("No items available in the market.")
            return

        # Get filter options from player
        print(f"\n{Colors.CYAN}=== BROWSE ITEMS ==={Colors.END}")
        print("Filters available:")
        print("  1. All Items")
        print("  2. By Type (weapon, armor, consumable, etc.)")
        print("  3. By Rarity (common, uncommon, rare, legendary)")
        print("  4. By Class (Mage, Warrior, Rogue, etc.)")
        print("  5. By Max Price")
        print("  R. Refresh market (forces new fetch)")

        choice = ask("\nChoose filter (1-5, R) or press Enter to browse all: ").strip().upper()

        filtered_items = items

        if choice == '1' or not choice:
            pass  # All items
        elif choice == '2':
            print("\nItem types: weapon, armor, consumable, accessory, material, offhand")
            item_type = ask("Enter type: ").strip().lower()
            filtered_items = self.market_api.filter_items(item_type=item_type)
        elif choice == '3':
            print("\nRarities: common, uncommon, rare, legendary")
            rarity = ask("Enter rarity: ").strip().lower()
            filtered_items = self.market_api.filter_items(rarity=rarity)
        elif choice == '4':
            print("\nClasses: Warrior, Mage, Rogue, Hunter, Bard, etc.")
            class_req = ask("Enter class: ").strip()
            filtered_items = self.market_api.filter_items(class_req=class_req)
        elif choice == '5':
            try:
                max_price = int(ask("Enter max price: ").strip())
                filtered_items = self.market_api.filter_items(max_price=max_price)
            except ValueError:
                print("Invalid price, showing all items.")
        elif choice == 'R':
            filtered_items = self.market_api.get_all_items()
            # Force refresh
            self.market_api.fetch_market_data(force_refresh=True)
            filtered_items = self.market_api.get_all_items()

        if not filtered_items:
            print("No items match your filters.")
            return

        # Sort by market price by default
        filtered_items = sorted(filtered_items, key=lambda x: x.get('marketPrice', 0))

        # Paginate and display items
        page_size = 8
        current_page = 0

        while True:
            start = current_page * page_size
            end = start + page_size
            page_items = filtered_items[start:end]

            if not page_items:
                print("No more items.")
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
                desc = item.get('description', '')[:60]  # Truncate long descriptions
                reqs = item.get('requirements')
                class_req = reqs.get('class') if reqs else None
                level_req = reqs.get('level', 1) if reqs else 1

                # Color by rarity
                rarity_color = get_rarity_color(rarity)
                price_color = Colors.GREEN if market_price <= self.player.gold else Colors.RED

                print(f"\n{i}. {rarity_color}{name}{Colors.END} ({item_type})")
                print(f"   {Colors.DARK_GRAY}{desc}{Colors.END}")
                print(f"   {rarity_color}{rarity.title()}{Colors.END} | Level {level_req}" +
                      (f" | {Colors.CYAN}{class_req}{Colors.END}" if class_req else ""))
                print(f"   {Colors.GOLD}{market_price}{Colors.END} gold (was {original_price})")

            print(f"\n{Colors.YELLOW}Options:{Colors.END}")
            print(f"1-{len(page_items)}. Buy Item")
            if len(filtered_items) > page_size:
                print("N. Next Page")
                print("P. Previous Page")
            print("F. Filter Items")
            print("Enter. Return to Main Menu")

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
                print("\nRefine search:")
                print("  1. By Type")
                print("  2. By Rarity")
                print("  3. By Class")
                print("  4. By Max Price")
                sub_choice = ask("Choose filter: ").strip()
                if sub_choice == '1':
                    item_type = ask("Enter type: ").strip().lower()
                    filtered_items = [it for it in filtered_items if it.get('type', '').lower() == item_type]
                elif sub_choice == '2':
                    rarity = ask("Enter rarity: ").strip().lower()
                    filtered_items = [it for it in filtered_items if it.get('rarity', '').lower() == rarity]
                elif sub_choice == '3':
                    class_req = ask("Enter class: ").strip()
                    filtered_items = [it for it in filtered_items if (it.get('requirements') or {}).get('class', '').lower() == class_req.lower()]
                elif sub_choice == '4':
                    try:
                        max_price = int(ask("Enter max price: ").strip())
                        filtered_items = [it for it in filtered_items if it.get('marketPrice', 0) <= max_price]
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
                        print(f"\n{Colors.GREEN}Purchased {name} for {market_price} gold!{Colors.END}")
                        self.update_mission_progress('collect', name)
                    else:
                        print(f"\n{Colors.RED}Not enough gold! Need {market_price}, have {self.player.gold}.{Colors.END}")
                else:
                    print("Invalid selection.")

    def manage_companions(self):
        """Manage hired companions."""
        if not self.player:
            print("No character created yet.")
            return

        while True:
            print(f"\n{Colors.BOLD}=== COMPANIONS ==={Colors.END}")
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

            print("\nOptions:")
            print("D - Dismiss a companion")
            print("E - Equip item on companion")
            print("Enter - Return to main menu")

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
                            print("Invalid selection.")
                    except ValueError:
                        print("Invalid input.")
            elif choice == 'e':
                # Equip item on companion
                print("Companion equipment feature coming soon!")
                # TODO: Implement companion equipment
            else:
                print("Invalid choice.")

    def travel(self):
        """Travel to connected areas from the current area."""
        if not self.player:
            print("No character created yet.")
            return

        current = self.current_area
        area_data = self.areas_data.get(current, {})
        connections = area_data.get("connections", [])

        print(f"\n{Colors.BOLD}=== TRAVEL ==={Colors.END}")
        print(f"Current location: {area_data.get('name', current)}")
        if not connections:
            print("No connected areas to travel to.")
            return

        print("Connected areas:")
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
                print(
                    f"Traveling to {self.areas_data.get(new_area, {}).get('name', new_area)}..."
                )
                # small chance encounter on travel
                if random.random() < 0.3:
                    self.random_encounter()

    def shop_sell(self):
        """Sell items from the player's inventory to the shop."""
        if not self.player:
            return

        sellable = [it for it in self.player.inventory]
        if not sellable:
            print("You have nothing to sell.")
            return

        print("\nYour inventory:")
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
            print("Invalid selection.")
            return

        item = sellable[idx]
        # Prevent selling equipped items
        if item in self.player.equipment.values():
            print("Unequip the item before selling it.")
            return

        price = self.items_data.get(item, {}).get('price', 0)
        sell_price = price // 2 if price else 0
        self.player.inventory.remove(item)
        self.player.gold += sell_price
        print(f"Sold {item} for {sell_price} gold.")

    def rest(self):
        """Rest in a safe area to recover HP and MP for gold."""
        if not self.player:
            print("No character created yet.")
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
            print("You decide not to rest.")
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
        """Save the game with an optional filename prefix (keeps backward compatible signature).

        If `filename_prefix` is provided it will be prepended to the filename
        (useful for error/unstable saves like 'err_save_unstable_').
        """
        if not self.player:
            print("No character to save.")
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
                "active_buffs": self.player.active_buffs
            },
            "current_area": self.current_area,
            "mission_progress": self.mission_progress,
            "completed_missions": self.completed_missions,
            "save_version": "3.0",
            "save_time": datetime.now().isoformat(),
            "bosses_killed": self.player.bosses_killed if self.player else {}
        }

        saves_dir = "data/saves"
        os.makedirs(saves_dir, exist_ok=True)

        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        safe_prefix = filename_prefix or ""
        # sanitize prefix to avoid accidental path chars
        safe_prefix = safe_prefix.replace('/', '_')
        filename = f"{saves_dir}/{safe_prefix}{self.player.name}_{self.player.uuid[:8]}_save_{timestamp}_{self.player.character_class}_{self.player.level}.json"
        with open(filename, 'w') as f:
            json.dump(save_data, f, indent=2)

        print(f"Game saved successfully: {filename}")

    def load_game(self):
        """Load a saved game with enhanced equipment handling and backward compatibility"""
        saves_dir = "data/saves"
        if not os.path.exists(saves_dir):
            print("No save files found.")
            return

        save_files = [f for f in os.listdir(saves_dir) if f.endswith('.json')]
        if not save_files:
            print("No save files found.")
            return

        print("Available save files:")
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

                    # NEW: Enhanced equipment loading with validation
                    self._load_equipment_data(player_data, save_version)

                    self.current_area = save_data["current_area"]

                    # Mission system load with backward compatibility
                    self.mission_progress = save_data.get(
                        "mission_progress", {})
                    self.completed_missions = save_data.get(
                        "completed_missions", [])

                    # Load boss kill cooldowns
                    if self.player:
                        self.player.bosses_killed = save_data.get(
                            "bosses_killed", {})

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
                      filename_prefix: str = "err_save_unstable_"):
        """Attempt to save the current game state and write a traceback log when an error occurs.

        This is intended for use in exception and signal handlers. It will try to save the
        current player state with a filename prefixed by `filename_prefix` and also write a
        `.log` file containing the traceback.
        """
        try:
            # Build a safe player name for filenames
            pname = (self.player.name if self.player
                     and getattr(self.player, 'name', None) else 'unknown')
            # Try to save using the standard save function with prefix
            try:
                self.save_game(filename_prefix=filename_prefix)
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
        print("\nHave you saved your progress? (yes/no) (CASE SENSITIVE!!!)")
        response = input(">>> ").strip().lower()
        if response == "no":
            clear_screen()
            print("Saving your progress...")
            self.save_game()
            print("Progress saved!")
        print("Thank you for playing Our Legacy!")
        print("Your legacy will be remembered...")
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
            "Herb", "Spring Water", "Leather", "Leather Strip", 
            "Hardwood", "Stone Block", "Coal", "Iron Ore",
            "Goblin Ear", "Wolf Fang", "Bone Fragment"
        ]
        
        # Tier 2: Uncommon materials (difficulty 3)
        tier2_materials = [
            "Mana Herb", "Gold Nugget", "Steel Ingot",
            "Orc Tooth", "Serpent Tail", "Crystal Shard",
            "Venom Sac", "Swamp Scale", "Ancient Relic",
            "Wind Elemental Essence", "Demon Blood"
        ]
        
        # Tier 3: Rare materials (difficulty 4)
        tier3_materials = [
            "Dark Crystal", "Ice Crystal", "Void Crystal",
            "Shadow Essence", "Fire Essence", "Ice Essence",
            "Starlight Shard", "Eternal Essence",
            "Poison Crystal", "Lightning Crystal"
        ]
        
        # Tier 4: Legendary materials (difficulty 5-6)
        tier4_materials = [
            "Dragon Scale", "Dragon Bone", "Phoenix Feather",
            "Fire Gem", "Soul Fragment", "Demon Heart",
            "Golem Core", "Storm Elemental Core",
            "Zephyr's Scale", "Wind Dragon's Heart",
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
        valid_materials = [m for m in available_materials if m in self.items_data]
        
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
        print(f"\n{Colors.YELLOW}You found materials:{Colors.END}")
        for text in found_text:
            print(f"  - {text}")
        
        # Update mission progress for collected materials
        for material in gathered.keys():
            self.update_mission_progress('collect', material)

    def visit_alchemy(self):
        """Visit the Alchemy workshop to craft items"""
        if not self.player:
            print("No character created yet.")
            return

        if not self.crafting_data or not self.crafting_data.get('recipes'):
            print("No crafting recipes available.")
            return

        print(f"\n{Colors.MAGENTA}{Colors.BOLD}=== ALCHEMY WORKSHOP ==={Colors.END}")
        print("Welcome to the Alchemy Workshop! Here you can craft potions, elixirs, and items.")
        print(f"\nYour gold: {Colors.GOLD}{self.player.gold}{Colors.END}")

        # Display available materials from inventory
        self._display_crafting_materials()

        while True:
            clear_screen()
            print(f"\n{Colors.BOLD}=== ALCHEMY WORKSHOP ==={Colors.END}")
            print("Categories: [P]otions, [E]lixirs, [E]ntchantments, [U]tility, [A]ll")
            print("[C]raft Item, [M]aterials, [B]ack to Menu")

            choice = ask("\nChoose an option: ").strip().upper()

            if choice == 'B' or not choice:
                break
            elif choice == 'P':
                self._display_recipes_by_category('Potions')
            elif choice == 'E':
                # Ask which type of E (Elixirs or Enchantments)
                print("E - Elixirs, N - Enchantments")
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
                print("Invalid choice.")

    def _display_crafting_materials(self):
        """Display materials available in player's inventory"""
        if not self.player:
            return

        print(f"\n{Colors.CYAN}=== YOUR MATERIALS ==={Colors.END}")

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
            print("No crafting materials in your inventory.")
            print("Materials can be found as drops from enemies or purchased from shops.")
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
        category_recipes = [
            (rid, rdata) for rid, rdata in recipes.items()
            if rdata.get('category') == category
        ]

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
            print("\nNo recipes available.")
            return

        page_size = 10
        recipe_list = list(recipes.items())
        current_page = 0

        while True:
            start = current_page * page_size
            end = start + page_size
            page_items = recipe_list[start:end]

            print(f"\n{Colors.BOLD}=== ALL RECIPES ==={Colors.END}")
            for i, (rid, rdata) in enumerate(page_items, 1):
                name = rdata.get('name', rid)
                category = rdata.get('category', 'Unknown')
                rarity = rdata.get('rarity', 'common')
                rarity_color = get_rarity_color(rarity)
                print(
                    f"{start + i}. {rarity_color}{name}{Colors.END} ({category})")

            total_pages = (len(recipe_list) + page_size - 1) // page_size
            print(f"\nPage {current_page + 1}/{total_pages}")

            if total_pages > 1:
                if current_page > 0:
                    print("P. Previous Page")
                if current_page < total_pages - 1:
                    print("N. Next Page")
            print("C. Craft Item")
            print("B. Back")

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
                print("Invalid choice.")

    def _craft_item(self):
        """Craft an item using materials from inventory"""
        if not self.player or not self.crafting_data:
            print("Cannot craft items.")
            return

        recipes = self.crafting_data.get('recipes', {})

        # Show all recipes for selection
        print(f"\n{Colors.BOLD}=== CRAFT ITEM ==={Colors.END}")
        recipe_names = list(recipes.keys())

        for i, rid in enumerate(recipe_names, 1):
            rdata = recipes[rid]
            name = rdata.get('name', rid)
            rarity = rdata.get('rarity', 'common')
            rarity_color = get_rarity_color(rarity)
            print(f"{i}. {rarity_color}{name}{Colors.END}")

        choice = ask(f"\nChoose recipe (1-{len(recipe_names)}) or press Enter to cancel: ").strip()

        if not choice:
            return

        if not choice.isdigit():
            print("Invalid choice.")
            return

        idx = int(choice) - 1
        if not (0 <= idx < len(recipe_names)):
            print("Invalid recipe number.")
            return

        recipe_id = recipe_names[idx]
        recipe = recipes[recipe_id]

        # Check skill requirement
        skill_req = recipe.get('skill_requirement', 1)
        if self.player.level < skill_req:
            print(f"\n{Colors.RED}You need at least level {skill_req} to craft this item.{Colors.END}")
            return

        # Get materials required
        materials_needed = recipe.get('materials', {})

        # Check if player has materials
        missing_materials = []
        for material, quantity in materials_needed.items():
            in_inventory = self.player.inventory.count(material)
            if in_inventory < quantity:
                missing_materials.append(f"{material} (need {quantity}, have {in_inventory})")

        if missing_materials:
            print(f"\n{Colors.RED}Missing materials:{Colors.END}")
            for m in missing_materials:
                print(f"  - {m}")
            print("\nGather more materials before crafting.")
            return

        # Show craft confirmation
        output_items = recipe.get('output', {})
        print(f"\n{Colors.BOLD}=== CRAFT CONFIRMATION ==={Colors.END}")
        print(f"Recipe: {recipe.get('name')}")
        print(f"Output: {', '.join(f'{qty}x {item}' for item, qty in output_items.items())}")
        print("\nMaterials to consume:")
        for material, quantity in materials_needed.items():
            print(f"  - {quantity}x {material}")

        confirm = ask("\nCraft this item? (y/n): ").strip().lower()
        if confirm != 'y':
            print("Crafting cancelled.")
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

        print(f"\n{Colors.GREEN}Successfully crafted {recipe.get('name')}!{Colors.END}")
        for item, quantity in output_items.items():
            print(f"  Received: {quantity}x {item}")

    def run(self):
        """Main game loop"""
        choice = self.display_welcome()

        if choice == "new_game":
            self.create_character()
        elif choice == "load_game":
            self.load_game()
            if not self.player:
                print("No game loaded. Starting new game...")
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