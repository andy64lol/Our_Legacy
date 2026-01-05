#!/usr/bin/env python3
"""
Our Legacy - Scripting API

Provides a Python interface for modding and extending Our Legacy.
Scripts can hook into game events, modify state, and extend gameplay.
"""

from typing import Dict, Any, List, Optional, Callable
import json


class GameAPI:
    """Main API interface for game scripting."""

    def __init__(self, game_instance=None):
        """Initialize the scripting API with a game instance.
        
        Args:
            game_instance: Reference to the main Game instance
        """
        self.game = game_instance
        self.hooks: Dict[str, List[Callable]] = {
            'on_battle_start': [],
            'on_battle_end': [],
            'on_player_levelup': [],
            'on_item_acquired': [],
            'on_companion_hired': [],
            'on_mission_complete': [],
            'on_buff_applied': [],
            'on_area_entered': [],
        }
        self.custom_data: Dict[str, Any] = {}

    # ============ Player Access ============

    def get_player(self) -> Optional[Dict[str, Any]]:
        """Get current player data as a dictionary."""
        if not self.game or not self.game.player:
            return None
        p = self.game.player
        return {
            'name': p.name,
            'class': p.character_class,
            'rank': p.rank,
            'level': p.level,
            'experience': p.experience,
            'hp': p.hp,
            'max_hp': p.max_hp,
            'mp': p.mp,
            'max_mp': p.max_mp,
            'attack': p.get_effective_attack(),
            'defense': p.get_effective_defense(),
            'speed': p.get_effective_speed(),
            'gold': p.gold,
            'inventory': p.inventory.copy(),
            'companions': [c.get('name') if isinstance(c, dict) else c for c in p.companions],
            'active_buffs': p.active_buffs.copy(),
        }

    def set_player_stat(self, stat: str, value: int) -> bool:
        """Modify a player stat.
        
        Args:
            stat: 'hp', 'mp', 'attack', 'defense', 'speed', 'gold', 'level', 'experience'
            value: New value
            
        Returns:
            True if successful, False otherwise
        """
        if not self.game or not self.game.player:
            return False

        p = self.game.player
        try:
            if stat == 'hp':
                p.hp = min(p.max_hp, max(0, value))
            elif stat == 'mp':
                p.mp = min(p.max_mp, max(0, value))
            elif stat == 'attack':
                p.attack = max(0, value)
            elif stat == 'defense':
                p.defense = max(0, value)
            elif stat == 'speed':
                p.speed = max(0, value)
            elif stat == 'gold':
                p.gold = max(0, value)
            elif stat == 'level':
                p.level = max(1, value)
                p._update_rank()
            elif stat == 'experience':
                p.experience = max(0, value)
            else:
                return False
            return True
        except Exception:
            return False

    def add_item(self, item_name: str, count: int = 1) -> bool:
        """Add items to player inventory.
        
        Args:
            item_name: Name of item to add
            count: How many to add
            
        Returns:
            True if successful
        """
        if not self.game or not self.game.player:
            return False
        try:
            for _ in range(count):
                self.game.player.inventory.append(item_name)
            return True
        except Exception:
            return False

    def remove_item(self, item_name: str, count: int = 1) -> bool:
        """Remove items from player inventory.
        
        Args:
            item_name: Name of item to remove
            count: How many to remove
            
        Returns:
            True if successful
        """
        if not self.game or not self.game.player:
            return False
        try:
            for _ in range(count):
                if item_name in self.game.player.inventory:
                    self.game.player.inventory.remove(item_name)
                else:
                    return False
            return True
        except Exception:
            return False

    def apply_buff(self, buff_name: str, duration: int, modifiers: Dict[str, int]) -> bool:
        """Apply a temporary buff to the player.
        
        Args:
            buff_name: Name of the buff
            duration: How many turns it lasts
            modifiers: Dict like {'attack_bonus': 5, 'defense_bonus': 3}
            
        Returns:
            True if successful
        """
        if not self.game or not self.game.player:
            return False
        try:
            self.game.player.apply_buff(buff_name, duration, modifiers)
            return True
        except Exception:
            return False

    def heal_player(self, amount: int) -> int:
        """Heal player HP.
        
        Args:
            amount: How much to heal
            
        Returns:
            Actual amount healed
        """
        if not self.game or not self.game.player:
            return 0
        old_hp = self.game.player.hp
        self.game.player.heal(amount)
        return self.game.player.hp - old_hp

    def restore_mp(self, amount: int) -> int:
        """Restore player MP.
        
        Args:
            amount: How much to restore
            
        Returns:
            Actual amount restored
        """
        if not self.game or not self.game.player:
            return 0
        old_mp = self.game.player.mp
        self.game.player.mp = min(self.game.player.max_mp, self.game.player.mp + amount)
        return self.game.player.mp - old_mp

    # ============ Companions ============

    def get_companions(self) -> List[Dict[str, Any]]:
        """Get list of hired companions."""
        if not self.game or not self.game.player:
            return []
        companions = []
        for c in self.game.player.companions:
            if isinstance(c, dict):
                companions.append({
                    'name': c.get('name'),
                    'id': c.get('id'),
                    'level': c.get('level', 1),
                })
            else:
                companions.append({'name': c, 'id': None, 'level': 1})
        return companions

    def hire_companion(self, companion_name: str) -> bool:
        """Hire a companion by name.
        
        Args:
            companion_name: Name of companion from companions.json
            
        Returns:
            True if successful
        """
        if not self.game or not self.game.player:
            return False
        if len(self.game.player.companions) >= 4:
            return False
        try:
            # Find companion data
            for cid, cdata in self.game.companions_data.items():
                if cdata.get('name') == companion_name:
                    # Hire without cost check
                    companion_data = {
                        'id': cid,
                        'name': cdata.get('name'),
                        'level': 1,
                        'equipment': {'weapon': None, 'armor': None, 'accessory': None}
                    }
                    self.game.player.companions.append(companion_data)
                    self.game.player.update_stats_from_equipment(
                        self.game.items_data, self.game.companions_data
                    )
                    return True
            return False
        except Exception:
            return False

    # ============ Game Data Access ============

    def get_items_data(self) -> Dict[str, Any]:
        """Get all items data."""
        return self.game.items_data.copy() if self.game else {}

    def get_enemies_data(self) -> Dict[str, Any]:
        """Get all enemies data."""
        return self.game.enemies_data.copy() if self.game else {}

    def get_areas_data(self) -> Dict[str, Any]:
        """Get all areas data."""
        return self.game.areas_data.copy() if self.game else {}

    def get_companions_data(self) -> Dict[str, Any]:
        """Get all companions data."""
        return self.game.companions_data.copy() if self.game else {}

    def get_current_area(self) -> Optional[str]:
        """Get current area ID."""
        return self.game.current_area if self.game else None

    def set_current_area(self, area_id: str) -> bool:
        """Travel to an area.
        
        Args:
            area_id: Area identifier
            
        Returns:
            True if successful
        """
        if not self.game or area_id not in self.game.areas_data:
            return False
        self.game.current_area = area_id
        return True

    def get_area_info(self, area_id: str) -> Optional[Dict[str, Any]]:
        """Get info about an area."""
        if not self.game or area_id not in self.game.areas_data:
            return None
        return self.game.areas_data[area_id].copy()

    # ============ Missions ============

    def get_missions(self) -> Dict[str, Dict[str, Any]]:
        """Get all missions data."""
        return self.game.missions_data.copy() if self.game else {}

    def get_mission_progress(self) -> Dict[str, Dict[str, Any]]:
        """Get current mission progress."""
        return self.game.mission_progress.copy() if self.game else {}

    def accept_mission(self, mission_id: str) -> bool:
        """Accept a mission."""
        if not self.game:
            return False
        try:
            self.game.accept_mission(mission_id)
            return True
        except Exception:
            return False

    def complete_mission(self, mission_id: str) -> bool:
        """Force complete a mission."""
        if not self.game or mission_id not in self.game.mission_progress:
            return False
        try:
            self.game.complete_mission(mission_id)
            return True
        except Exception:
            return False

    # ============ Events & Hooks ============

    def register_hook(self, event_name: str, callback: Callable) -> bool:
        """Register a callback for a game event.
        
        Args:
            event_name: Name of event ('on_battle_start', 'on_player_levelup', etc.)
            callback: Function to call when event fires
            
        Returns:
            True if successful
        """
        if event_name not in self.hooks:
            return False
        self.hooks[event_name].append(callback)
        return True

    def trigger_hook(self, event_name: str, *args, **kwargs) -> List[Any]:
        """Trigger all callbacks for an event.
        
        Args:
            event_name: Name of event
            *args, **kwargs: Arguments to pass to callbacks
            
        Returns:
            List of callback results
        """
        if event_name not in self.hooks:
            return []
        results = []
        for callback in self.hooks[event_name]:
            try:
                result = callback(*args, **kwargs)
                results.append(result)
            except Exception as e:
                print(f"Error in hook {event_name}: {e}")
        return results

    # ============ Custom Data Storage ============

    def store_data(self, key: str, value: Any) -> None:
        """Store custom script data (persists in memory during game session).
        
        Args:
            key: Data key
            value: Any JSON-serializable value
        """
        self.custom_data[key] = value

    def retrieve_data(self, key: str, default=None) -> Any:
        """Retrieve custom script data.
        
        Args:
            key: Data key
            default: Default value if key not found
            
        Returns:
            Stored value or default
        """
        return self.custom_data.get(key, default)

    def clear_data(self, key: str) -> bool:
        """Clear a stored data key.
        
        Args:
            key: Data key to remove
            
        Returns:
            True if key existed and was removed
        """
        if key in self.custom_data:
            del self.custom_data[key]
            return True
        return False

    # ============ Utilities ============

    def log(self, message: str) -> None:
        """Log a message to console."""
        print(f"[Script] {message}")

    def get_random_item(self, items_list: List[str]) -> Optional[str]:
        """Pick a random item from a list."""
        import random
        if not items_list:
            return None
        return random.choice(items_list)

    def create_custom_enemy(self, name: str, stats: Dict[str, int]) -> Dict[str, Any]:
        """Create a custom enemy dynamically.
        
        Args:
            name: Enemy name
            stats: Dict with 'hp', 'attack', 'defense', 'speed', 'experience_reward', 'gold_reward'
            
        Returns:
            Enemy data dict
        """
        return {
            'name': name,
            'hp': stats.get('hp', 50),
            'attack': stats.get('attack', 5),
            'defense': stats.get('defense', 2),
            'speed': stats.get('speed', 5),
            'experience_reward': stats.get('experience_reward', 10),
            'gold_reward': stats.get('gold_reward', 5),
            'loot_table': stats.get('loot_table', []),
        }


# Global API instance (set by main.py when game starts)
game_api = None


def init_scripting_api(game_instance) -> GameAPI:
    """Initialize the scripting API with a game instance.
    
    Called by main.py during game startup.
    """
    global game_api
    game_api = GameAPI(game_instance)
    return game_api


def get_api() -> Optional[GameAPI]:
    """Get the global GameAPI instance."""
    return game_api
