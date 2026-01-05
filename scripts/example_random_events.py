#!/usr/bin/env python3
"""
Example Script: Random Events System
Demonstrates on_battle_start/end hooks, custom data storage, and conditional event triggering.

This script adds random events that can occur during gameplay, such as:
- Random encounters with special enemies
- Bonus experience events
- Treasure discovery events
- Curse events
"""

from typing import Optional, Dict, Any
from scripting import get_api
import random


class RandomEventManager:
    """Manages random events that can occur during gameplay."""
    
    # Event types with weights (higher = more common)
    EVENT_TYPES = {
        'bonus_xp': {'weight': 30, 'min_battles': 3},
        'treasure': {'weight': 20, 'min_battles': 5},
        'special_enemy': {'weight': 25, 'min_battles': 2},
        'curse': {'weight': 15, 'min_battles': 4},
        'blessing': {'weight': 10, 'min_battles': 7},
    }
    
    def __init__(self):
        self.api = get_api()
        if self.api:
            # Register hooks
            self.api.register_hook('on_battle_start', self.on_battle_start)
            self.api.register_hook('on_battle_end', self.on_battle_end)
            
            # Initialize session data
            self.api.store_data('battles_since_last_event', 0)
            self.api.store_data('events_triggered', 0)
            self.api.store_data('active_event', None)
            
            self.api.log("Random Event System loaded!")
    
    def on_battle_start(self):
        """Called when a battle starts - check for special enemy spawns."""
        if not self.api:
            return
        
        # Check if there's an active event
        active_event = self.api.retrieve_data('active_event')
        if active_event == 'special_enemy':
            player = self.api.get_player()
            if player:
                self.api.log("A special enemy appears! Battle difficulty increased!")
                # Increase enemy damage multiplier temporarily
                if hasattr(self.api, 'get_combat_multipliers'):
                    multipliers = self.api.get_combat_multipliers() or {}
                    if hasattr(self.api, 'set_combat_multipliers'):
                        self.api.set_combat_multipliers(
                            multipliers.get('player_damage_mult', 1.0),
                            multipliers.get('enemy_damage_mult', 1.0) * 1.5,
                            multipliers.get('experience_mult', 1.0)
                        )
    
    def on_battle_end(self):
        """Called when a battle ends - potentially trigger random events."""
        if not self.api:
            return
        
        # Track battle count
        battles = self.api.retrieve_data('battles_since_last_event', 0) + 1
        self.api.store_data('battles_since_last_event', battles)
        
        # Check if we should trigger an event
        min_required = min(data['min_battles'] for data in self.EVENT_TYPES.values())
        if battles < min_required:
            return
        
        # Roll for random event
        if random.random() < 0.3:  # 30% chance after minimum battles
            self.trigger_random_event()
    
    def trigger_random_event(self):
        """Trigger a random event based on weights."""
        if not self.api:
            return
        
        # Select event type based on weights
        available_events = []
        for event_type, data in self.EVENT_TYPES.items():
            battles = self.api.retrieve_data('battles_since_last_event', 0)
            if battles >= data['min_battles']:
                available_events.extend([event_type] * data['weight'])
        
        if not available_events:
            return
        
        event_type = random.choice(available_events)
        self.api.store_data('active_event', event_type)
        
        # Execute event
        event_handlers = {
            'bonus_xp': self._handle_bonus_xp,
            'treasure': self._handle_treasure,
            'special_enemy': self._handle_special_enemy,
            'curse': self._handle_curse,
            'blessing': self._handle_blessing,
        }
        
        if event_type in event_handlers:
            event_handlers[event_type]()
        
        # Increment event counter
        events = self.api.retrieve_data('events_triggered', 0) + 1
        self.api.store_data('events_triggered', events)
        
        # Reset battle counter
        self.api.store_data('battles_since_last_event', 0)
    
    def _handle_bonus_xp(self):
        """Give bonus experience points."""
        if not self.api:
            return
        
        player = self.api.get_player()
        if player:
            bonus_xp = random.randint(20, 50)
            if hasattr(self.api, 'add_experience'):
                self.api.add_experience(bonus_xp)
            self.api.log(f"BONUS! You gained {bonus_xp} bonus experience!")
            self.api.store_data('active_event', None)
    
    def _handle_treasure(self):
        """Grant bonus treasure."""
        if not self.api:
            return
        
        player = self.api.get_player()
        if player:
            treasure_items = ['Gold Coin', 'Silver Ring', 'Health Potion', 'Mana Potion']
            item = random.choice(treasure_items)
            quantity = random.randint(1, 3)
            if hasattr(self.api, 'give_item'):
                self.api.give_item(item, quantity)
            self.api.log(f"Treasure found! You received: {item} x{quantity}")
            self.api.store_data('active_event', None)
    
    def _handle_special_enemy(self):
        """Flag for special enemy in next battle."""
        if not self.api:
            return
        
        self.api.log("A menacing presence lurks nearby... The next battle will be tougher!")
        # Event stays active until battle ends
    
    def _handle_curse(self):
        """Apply a temporary debuff."""
        if not self.api:
            return
        
        self.api.log("A dark curse falls upon you! Stats reduced for 3 battles.")
        player = self.api.get_player()
        if player and hasattr(self.api, 'apply_buff'):
            self.api.apply_buff('Curse of Weakness', 3, {
                'attack_bonus': -3,
                'defense_bonus': -2,
            })
        self.api.store_data('active_event', None)
    
    def _handle_blessing(self):
        """Apply a temporary buff."""
        if not self.api:
            return
        
        self.api.log("A divine blessing! Stats increased for 5 battles!")
        player = self.api.get_player()
        if player and hasattr(self.api, 'apply_buff'):
            self.api.apply_buff('Divine Blessing', 5, {
                'attack_bonus': 5,
                'defense_bonus': 5,
                'speed_bonus': 2,
            })
        self.api.store_data('active_event', None)
    
    def get_event_stats(self) -> Dict[str, Any]:
        """Get statistics about triggered events."""
        if not self.api:
            return {}
        
        return {
            'events_triggered': self.api.retrieve_data('events_triggered', 0),
            'battles_since_last': self.api.retrieve_data('battles_since_last_event', 0),
            'active_event': self.api.retrieve_data('active_event', None),
        }


# Initialize the random event manager
random_events = RandomEventManager()


def register_hooks():
    """Register any additional hooks if needed."""
    api = get_api()
    if api:
        api.log("Random Events example loaded!")


register_hooks()