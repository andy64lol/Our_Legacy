"""
Dynamic Difficulty Script - Adjusts game difficulty based on player performance

This script demonstrates using combat multipliers and area difficulty to create
adaptive difficulty that scales with player performance.
"""

from main import get_api
from typing import Optional

class DynamicDifficulty:
    """Dynamically adjust game difficulty based on player stats."""
    
    def __init__(self):
        self.api = None
        self._initialized = False
    
    def initialize(self):
        """Initialize the dynamic difficulty system. Safe to call multiple times."""
        if self._initialized:
            return
        
        self.api = get_api()
        if self.api:
            self.api.register_hook('on_battle_end', self.adjust_difficulty)
            self.api.register_hook('on_player_levelup', self.scale_world)
            self.api.log("Dynamic Difficulty System enabled")
            self._initialized = True
    
    def adjust_difficulty(self):
        """Adjust difficulty after battles based on performance."""
        if not self.api:
            return
        
        # Track battle count
        battle_count = self.api.increment_statistic('battles_this_session', 1)
        
        # Get player stats
        player = self.api.get_player()
        if not player:
            return
        
        # Adjust difficulty every 5 battles
        if battle_count % 5 != 0:
            return
        
        # Get current multipliers
        multipliers = self.api.get_combat_multipliers()
        
        # Calculate health ratio
        health_ratio = player.get('hp', 0) / max(1, player.get('max_hp', 1))
        
        # If player is doing well, increase difficulty
        if health_ratio > 0.7:
            new_player_mult = min(2.0, multipliers.get('player_damage_mult', 1.0) * 1.05)
            new_enemy_mult = min(2.0, multipliers.get('enemy_damage_mult', 1.0) * 1.1)
            self.api.set_combat_multipliers(new_player_mult, new_enemy_mult)
            self.api.log("Difficulty increased!")
        
        # If player is struggling, decrease difficulty
        elif health_ratio < 0.3:
            new_player_mult = max(0.5, multipliers.get('player_damage_mult', 1.0) * 1.1)
            new_enemy_mult = max(0.5, multipliers.get('enemy_damage_mult', 1.0) * 0.9)
            self.api.set_combat_multipliers(new_player_mult, new_enemy_mult)
            self.api.log("Difficulty decreased!")
    
    def scale_world(self):
        """Scale world difficulty on level up."""
        if not self.api:
            return
        
        player = self.api.get_player()
        if not player:
            return
        
        level = player.get('level', 1)
        
        # Scale area difficulties
        areas = self.api.list_all_areas()
        for area_id in areas:
            area = self.api.get_area_info(area_id)
            if area and 'difficulty' in area:
                # Scale difficulty with player level
                scaled_diff = min(5, max(1, area.get('difficulty', 1) + (level // 5)))
                self.api.set_area_difficulty(area_id, scaled_diff)


# Global instance - lazily created
_dynamic_difficulty = None


def _get_dynamic_difficulty() -> 'DynamicDifficulty':
    """Get or create the dynamic difficulty instance."""
    global _dynamic_difficulty
    if _dynamic_difficulty is None:
        _dynamic_difficulty = DynamicDifficulty()
        _dynamic_difficulty.initialize()
    return _dynamic_difficulty


def register_hooks():
    """Register hooks for dynamic difficulty events."""
    diff = _get_dynamic_difficulty()
    print("Dynamic Difficulty script loaded!")


# Auto-register when imported
register_hooks()

