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

    # ============ Combat Hooks & Modifiers ============

    def get_combat_multipliers(self) -> Dict[str, float]:
        """Get current combat damage multipliers.
        
        Returns:
            Dict with 'player_damage_mult', 'enemy_damage_mult', 'experience_mult'
        """
        if not self.game:
            return {'player_damage_mult': 1.0, 'enemy_damage_mult': 1.0, 'experience_mult': 1.0}
        return {
            'player_damage_mult': getattr(self.game, 'player_damage_mult', 1.0),
            'enemy_damage_mult': getattr(self.game, 'enemy_damage_mult', 1.0),
            'experience_mult': getattr(self.game, 'experience_mult', 1.0),
        }

    def set_combat_multipliers(self, player_mult: float = 1.0, enemy_mult: float = 1.0, exp_mult: float = 1.0) -> bool:
        """Set combat damage and reward multipliers.
        
        Args:
            player_mult: Multiplier for player damage (default 1.0)
            enemy_mult: Multiplier for enemy damage (default 1.0)
            exp_mult: Multiplier for experience rewards (default 1.0)
            
        Returns:
            True if successful
        """
        if not self.game:
            return False
        self.game.player_damage_mult = max(0.1, player_mult)
        self.game.enemy_damage_mult = max(0.1, enemy_mult)
        self.game.experience_mult = max(0.1, exp_mult)
        return True

    # ============ Inventory & Equipment ============

    def get_inventory(self) -> List[str]:
        """Get player's full inventory list."""
        if not self.game or not self.game.player:
            return []
        return self.game.player.inventory.copy()

    def get_inventory_count(self, item_name: str) -> int:
        """Count how many of an item player has.
        
        Args:
            item_name: Name of item
            
        Returns:
            Count of item in inventory
        """
        if not self.game or not self.game.player:
            return 0
        return self.game.player.inventory.count(item_name)

    def clear_inventory(self) -> bool:
        """Clear entire inventory (dangerous!)."""
        if not self.game or not self.game.player:
            return False
        self.game.player.inventory.clear()
        return True

    def get_equipped_items(self) -> Dict[str, Optional[str]]:
        """Get equipped weapon, armor, offhand, and accessories.
        
        Returns:
            Dict with 'weapon', 'armor', 'offhand', 'accessory_1', 'accessory_2', 'accessory_3'
        """
        if not self.game or not self.game.player:
            return {}
        return {
            'weapon': self.game.player.equipped_weapon,
            'armor': self.game.player.equipped_armor,
            'offhand': getattr(self.game.player, 'equipped_offhand', None),
            'accessory_1': getattr(self.game.player, 'equipped_accessory_1', None),
            'accessory_2': getattr(self.game.player, 'equipped_accessory_2', None),
            'accessory_3': getattr(self.game.player, 'equipped_accessory_3', None),
        }

    def equip_item(self, item_name: str, slot: Optional[str] = None) -> bool:
        """Equip an item.
        
        Args:
            item_name: Item to equip
            slot: 'weapon', 'armor', 'offhand', 'accessory_1', 'accessory_2', 'accessory_3' (auto-detect if None)
            
        Returns:
            True if successful
        """
        if not self.game or not self.game.player or item_name not in self.game.player.inventory:
            return False
        try:
            if item_name in self.game.items_data:
                item_data = self.game.items_data[item_name]
                item_type = item_data.get('type')
                
                if slot is None:
                    # Auto-detect slot
                    if item_type == 'weapon':
                        slot = 'weapon'
                    elif item_type == 'armor':
                        slot = 'armor'
                    elif item_type == 'offhand':
                        slot = 'offhand'
                    elif item_type == 'accessory':
                        # Find first free accessory slot
                        for i in [1, 2, 3]:
                            acc = getattr(self.game.player, f'equipped_accessory_{i}', None)
                            if not acc:
                                slot = f'accessory_{i}'
                                break
                        if not slot:
                            slot = 'accessory_1'
                
                if slot == 'weapon':
                    self.game.player.equipped_weapon = item_name
                elif slot == 'armor':
                    self.game.player.equipped_armor = item_name
                elif slot == 'offhand':
                    self.game.player.equipped_offhand = item_name
                elif slot and slot.startswith('accessory'):
                    setattr(self.game.player, f'equipped_{slot}', item_name)
                else:
                    return False
                    
                self.game.player.update_stats_from_equipment(self.game.items_data, self.game.companions_data)
                return True
        except Exception:
            pass
        return False

    def unequip_item(self, slot: str) -> Optional[str]:
        """Unequip an item from a slot.
        
        Args:
            slot: 'weapon', 'armor', 'offhand', 'accessory_1', 'accessory_2', 'accessory_3'
            
        Returns:
            Name of unequipped item, or None if slot was empty
        """
        if not self.game or not self.game.player:
            return None
        try:
            item = None
            if slot == 'weapon':
                item = self.game.player.equipped_weapon
                self.game.player.equipped_weapon = None
            elif slot == 'armor':
                item = self.game.player.equipped_armor
                self.game.player.equipped_armor = None
            elif slot == 'offhand':
                item = getattr(self.game.player, 'equipped_offhand', None)
                self.game.player.equipped_offhand = None
            elif slot and slot.startswith('accessory'):
                item = getattr(self.game.player, f'equipped_{slot}', None)
                setattr(self.game.player, f'equipped_{slot}', None)
            
            if item:
                self.game.player.update_stats_from_equipment(self.game.items_data, self.game.companions_data)
                return item
            return None
        except Exception:
            return None

    def swap_equipment(self, slot1: str, slot2: str) -> bool:
        """Swap items between two equipment slots.
        
        Args:
            slot1: First slot
            slot2: Second slot
            
        Returns:
            True if successful
        """
        if not self.game or not self.game.player:
            return False
        try:
            equipped = self.get_equipped_items()
            item1 = equipped.get(slot1)
            item2 = equipped.get(slot2)
            
            if item1:
                self.unequip_item(slot1)
            if item2:
                self.unequip_item(slot2)
            
            if item1:
                self.equip_item(item1, slot2)
            if item2:
                self.equip_item(item2, slot1)
            
            return True
        except Exception:
            return False

    def get_item_price(self, item_name: str) -> int:
        """Get the value/price of an item.
        
        Args:
            item_name: Name of item
            
        Returns:
            Price in gold (0 if not found)
        """
        if not self.game or item_name not in self.game.items_data:
            return 0
        item_data = self.game.items_data[item_name]
        return item_data.get('price', 0)

    def get_inventory_value(self) -> int:
        """Calculate total value of all items in inventory.
        
        Returns:
            Total gold value
        """
        if not self.game or not self.game.player:
            return 0
        total = 0
        for item_name in self.game.player.inventory:
            total += self.get_item_price(item_name)
        return total

    def buy_item(self, item_name: str, quantity: int = 1) -> bool:
        """Buy an item (costs gold).
        
        Args:
            item_name: Item to buy
            quantity: How many to buy
            
        Returns:
            True if successful (has enough gold)
        """
        if not self.game or not self.game.player or item_name not in self.game.items_data:
            return False
        
        price = self.get_item_price(item_name)
        total_cost = price * quantity
        
        if self.game.player.gold < total_cost:
            return False
        
        # Deduct gold and add items
        self.game.player.gold -= total_cost
        for _ in range(quantity):
            self.game.player.inventory.append(item_name)
        
        return True

    def sell_item(self, item_name: str, quantity: int = 1) -> int:
        """Sell items from inventory for gold.
        
        Args:
            item_name: Item to sell
            quantity: How many to sell
            
        Returns:
            Gold received (0 if failed)
        """
        if not self.game or not self.game.player:
            return 0
        
        # Check if player has enough items
        if self.game.player.inventory.count(item_name) < quantity:
            return 0
        
        price = self.get_item_price(item_name)
        total_gold = price * quantity
        
        # Remove items and add gold
        for _ in range(quantity):
            self.game.player.inventory.remove(item_name)
        self.game.player.gold += total_gold
        
        return total_gold

    def give_item(self, item_name: str, quantity: int = 1) -> bool:
        """Give player item(s) without cost.
        
        Args:
            item_name: Item to give
            quantity: How many to give
            
        Returns:
            True if successful
        """
        if not self.game or not self.game.player:
            return False
        try:
            for _ in range(quantity):
                self.game.player.inventory.append(item_name)
            return True
        except Exception:
            return False

    def take_item(self, item_name: str, quantity: int = 1) -> int:
        """Remove item(s) from player inventory without payment.
        
        Args:
            item_name: Item to remove
            quantity: How many to remove
            
        Returns:
            Number of items actually removed
        """
        if not self.game or not self.game.player:
            return 0
        
        removed = 0
        for _ in range(quantity):
            if item_name in self.game.player.inventory:
                self.game.player.inventory.remove(item_name)
                removed += 1
            else:
                break
        
        return removed

    def has_item(self, item_name: str, minimum_quantity: int = 1) -> bool:
        """Check if player has item(s).
        
        Args:
            item_name: Item to check for
            minimum_quantity: Minimum quantity needed
            
        Returns:
            True if player has enough
        """
        if not self.game or not self.game.player:
            return False
        return self.game.player.inventory.count(item_name) >= minimum_quantity

    def sort_inventory(self) -> bool:
        """Sort player's inventory alphabetically.
        
        Returns:
            True if successful
        """
        if not self.game or not self.game.player:
            return False
        try:
            self.game.player.inventory.sort()
            return True
        except Exception:
            return False

    def get_inventory_summary(self) -> Dict[str, int]:
        """Get count of each unique item in inventory.
        
        Returns:
            Dict with item names as keys and counts as values
        """
        if not self.game or not self.game.player:
            return {}
        summary = {}
        for item in self.game.player.inventory:
            summary[item] = summary.get(item, 0) + 1
        return summary

    def get_item_info(self, item_name: str) -> Optional[Dict[str, Any]]:
        """Get detailed info about an item.
        
        Args:
            item_name: Item name
            
        Returns:
            Item data or None
        """
        if not self.game or item_name not in self.game.items_data:
            return None
        return self.game.items_data[item_name].copy()

    # ============ Stat Getters ============

    def get_base_stats(self) -> Dict[str, int]:
        """Get player's base stats (before equipment/buffs).
        
        Returns:
            Dict with 'hp', 'mp', 'attack', 'defense', 'speed'
        """
        if not self.game or not self.game.player:
            return {}
        p = self.game.player
        return {
            'hp': p.base_hp,
            'mp': p.base_mp,
            'attack': p.attack,
            'defense': p.defense,
            'speed': p.speed,
        }

    def get_effective_stats(self) -> Dict[str, int]:
        """Get player's effective stats (after equipment/buffs).
        
        Returns:
            Dict with current effective stats
        """
        if not self.game or not self.game.player:
            return {}
        p = self.game.player
        return {
            'hp': p.hp,
            'max_hp': p.max_hp,
            'mp': p.mp,
            'max_mp': p.max_mp,
            'attack': p.get_effective_attack(),
            'defense': p.get_effective_defense(),
            'speed': p.get_effective_speed(),
        }

    # ============ Area & Exploration ============

    def get_area_connections(self, area_id: str) -> List[str]:
        """Get areas connected to given area.
        
        Args:
            area_id: Area identifier
            
        Returns:
            List of connected area IDs
        """
        if not self.game or area_id not in self.game.areas_data:
            return []
        area = self.game.areas_data[area_id]
        return area.get('connections', [])

    def get_area_enemies(self, area_id: str) -> List[str]:
        """Get enemies that spawn in an area.
        
        Args:
            area_id: Area identifier
            
        Returns:
            List of enemy IDs
        """
        if not self.game or area_id not in self.game.areas_data:
            return []
        area = self.game.areas_data[area_id]
        return area.get('possible_enemies', [])

    def add_area_enemy(self, area_id: str, enemy_id: str) -> bool:
        """Add an enemy to an area's spawn list.
        
        Args:
            area_id: Area identifier
            enemy_id: Enemy identifier
            
        Returns:
            True if successful
        """
        if not self.game or area_id not in self.game.areas_data:
            return False
        area = self.game.areas_data[area_id]
        if enemy_id not in area.get('possible_enemies', []):
            area['possible_enemies'].append(enemy_id)
            return True
        return False

    def remove_area_enemy(self, area_id: str, enemy_id: str) -> bool:
        """Remove an enemy from an area's spawn list.
        
        Args:
            area_id: Area identifier
            enemy_id: Enemy identifier
            
        Returns:
            True if successful
        """
        if not self.game or area_id not in self.game.areas_data:
            return False
        area = self.game.areas_data[area_id]
        if enemy_id in area.get('possible_enemies', []):
            area['possible_enemies'].remove(enemy_id)
            return True
        return False

    def set_area_difficulty(self, area_id: str, difficulty: int) -> bool:
        """Set an area's difficulty level.
        
        Args:
            area_id: Area identifier
            difficulty: 1-5 difficulty rating
            
        Returns:
            True if successful
        """
        if not self.game or area_id not in self.game.areas_data:
            return False
        if not 1 <= difficulty <= 5:
            return False
        self.game.areas_data[area_id]['difficulty'] = difficulty
        return True

    # ============ Spells & Abilities ============

    def get_spells(self) -> Dict[str, Dict[str, Any]]:
        """Get all spell data."""
        return self.game.spells_data.copy() if self.game else {}

    def learn_spell(self, spell_name: str) -> bool:
        """Make a spell learnable (add to items that can cast it).
        
        Args:
            spell_name: Name of spell from spells.json
            
        Returns:
            True if successful
        """
        if not self.game or spell_name not in self.game.spells_data:
            return False
        # Mark spell as learned in custom data
        learned = self.retrieve_data('learned_spells', set())
        if isinstance(learned, list):
            learned = set(learned)
        learned.add(spell_name)
        self.store_data('learned_spells', list(learned))
        return True

    def get_learned_spells(self) -> List[str]:
        """Get list of spells player has learned."""
        return self.retrieve_data('learned_spells', [])

    # ============ Experience & Leveling ============

    def add_experience(self, amount: int) -> bool:
        """Give player experience points.
        
        Args:
            amount: XP to add
            
        Returns:
            True if successful
        """
        if not self.game or not self.game.player:
            return False
        self.game.player.experience += amount
        return True

    def level_up(self, levels: int = 1) -> bool:
        """Force level up the player.
        
        Args:
            levels: Number of levels to gain
            
        Returns:
            True if successful
        """
        if not self.game or not self.game.player:
            return False
        p = self.game.player
        for _ in range(levels):
            p.level_up()
        return True

    def get_level_progress(self) -> Dict[str, Any]:
        """Get player's current level progress.
        
        Returns:
            Dict with 'level', 'experience', 'experience_to_next'
        """
        if not self.game or not self.game.player:
            return {}
        p = self.game.player
        return {
            'level': p.level,
            'experience': p.experience,
            'experience_to_next': p.experience_to_next,
            'experience_for_next_level': int(p.experience_to_next - p.experience),
        }

    # ============ Buff Management ============

    def get_active_buffs(self) -> List[Dict[str, Any]]:
        """Get list of active buffs on player.
        
        Returns:
            List of buff dicts with name, duration, modifiers
        """
        if not self.game or not self.game.player:
            return []
        return self.game.player.active_buffs.copy()

    def remove_buff(self, buff_name: str) -> bool:
        """Remove a specific buff from player.
        
        Args:
            buff_name: Name of buff to remove
            
        Returns:
            True if buff was removed
        """
        if not self.game or not self.game.player:
            return False
        buffs = self.game.player.active_buffs
        for i, buff in enumerate(buffs):
            if buff.get('name') == buff_name:
                buffs.pop(i)
                return True
        return False

    def clear_buffs(self) -> int:
        """Remove all buffs from player.
        
        Returns:
            Number of buffs removed
        """
        if not self.game or not self.game.player:
            return 0
        count = len(self.game.player.active_buffs)
        self.game.player.active_buffs.clear()
        return count

    def extend_buff(self, buff_name: str, extra_duration: int) -> bool:
        """Extend the duration of a buff.
        
        Args:
            buff_name: Name of buff
            extra_duration: Additional turns to extend
            
        Returns:
            True if successful
        """
        if not self.game or not self.game.player:
            return False
        for buff in self.game.player.active_buffs:
            if buff.get('name') == buff_name:
                buff['duration'] = buff.get('duration', 0) + extra_duration
                return True
        return False

    # ============ Mission Management ============

    def has_mission_completed(self, mission_id: str) -> bool:
        """Check if a mission has been completed.
        
        Args:
            mission_id: Mission identifier
            
        Returns:
            True if completed
        """
        if not self.game:
            return False
        progress = self.game.mission_progress.get(mission_id, {})
        return progress.get('completed', False)

    def get_mission_info(self, mission_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed info about a specific mission.
        
        Args:
            mission_id: Mission identifier
            
        Returns:
            Mission data dict or None
        """
        if not self.game or mission_id not in self.game.missions_data:
            return None
        return self.game.missions_data[mission_id].copy()

    def reset_mission(self, mission_id: str) -> bool:
        """Reset a mission to incomplete state.
        
        Args:
            mission_id: Mission identifier
            
        Returns:
            True if successful
        """
        if not self.game or mission_id not in self.game.missions_data:
            return False
        if mission_id in self.game.mission_progress:
            del self.game.mission_progress[mission_id]
        return True

    # ============ Statistics & Tracking ============

    def get_game_statistics(self) -> Dict[str, Any]:
        """Get gameplay statistics.
        
        Returns:
            Dict with 'enemies_defeated', 'bosses_defeated', 'missions_completed', etc.
        """
        if not self.game:
            return {}
        return {
            'enemies_defeated': self.retrieve_data('enemies_defeated', 0),
            'bosses_defeated': self.retrieve_data('bosses_defeated', 0),
            'missions_completed': len([m for m in self.game.mission_progress.values() if m.get('completed')]),
            'gold_earned': self.retrieve_data('gold_earned', 0),
            'items_collected': self.retrieve_data('items_collected', 0),
            'playtime_seconds': self.retrieve_data('playtime_seconds', 0),
        }

    def increment_statistic(self, stat_name: str, amount: int = 1) -> int:
        """Increment a game statistic.
        
        Args:
            stat_name: Statistic name
            amount: Amount to increment by
            
        Returns:
            New statistic value
        """
        current = self.retrieve_data(stat_name, 0)
        new_value = current + amount
        self.store_data(stat_name, new_value)
        return new_value

    # ============ Validation & Checks ============

    def is_mission_available(self, mission_id: str) -> bool:
        """Check if player can accept a mission (meets level/prerequisites).
        
        Args:
            mission_id: Mission identifier
            
        Returns:
            True if player can accept
        """
        if not self.game or not self.game.player or mission_id not in self.game.missions_data:
            return False
        mission = self.game.missions_data[mission_id]
        player_level = self.game.player.level
        
        # Check level requirement
        if mission.get('unlock_level', 1) > player_level:
            return False
        
        # Check prerequisites
        for prereq in mission.get('prerequisites', []):
            if not self.has_mission_completed(prereq):
                return False
        
        return True

    def can_equip_item(self, item_name: str) -> bool:
        """Check if player meets requirements to equip an item.
        
        Args:
            item_name: Item name
            
        Returns:
            True if can equip
        """
        if not self.game or item_name not in self.game.items_data:
            return False
        item = self.game.items_data[item_name]
        requirements = item.get('requirements', {})
        
        if not self.game.player:
            return False
        
        # Check level requirement
        if self.game.player.level < requirements.get('level', 1):
            return False
        
        # Check class requirement (if any)
        if 'class' in requirements:
            if self.game.player.character_class != requirements['class']:
                return False
        
        return True

    # ============ Debugging ============

    def dump_player_data(self) -> str:
        """Get formatted string of all player data (for debugging).
        
        Returns:
            Formatted player data string
        """
        player_data = self.get_player()
        if not player_data:
            return "No player data"
        
        lines = ["=== Player Data ==="]
        for key, value in player_data.items():
            if isinstance(value, list) and len(value) > 5:
                lines.append(f"{key}: [{len(value)} items]")
            else:
                lines.append(f"{key}: {value}")
        return "\n".join(lines)

    def list_all_enemies(self) -> List[str]:
        """Get list of all enemy IDs.
        
        Returns:
            List of enemy identifiers
        """
        return list(self.game.enemies_data.keys()) if self.game else []

    def list_all_items(self) -> List[str]:
        """Get list of all item names.
        
        Returns:
            List of item names
        """
        return list(self.game.items_data.keys()) if self.game else []

    def list_all_areas(self) -> List[str]:
        """Get list of all area IDs.
        
        Returns:
            List of area identifiers
        """
        return list(self.game.areas_data.keys()) if self.game else []

    def list_all_companions(self) -> List[str]:
        """Get list of all companion names.
        
        Returns:
            List of companion identifiers
        """
        return list(self.game.companions_data.keys()) if self.game else []


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
