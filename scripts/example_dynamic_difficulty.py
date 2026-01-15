"""
Dynamic Difficulty Script - Adjusts game difficulty based on player performance

This script demonstrates using combat multipliers and area difficulty to create
adaptive difficulty that scales with player performance.
"""

from main import get_api

class DynamicDifficulty:
    """Dynamically adjust game difficulty based on player stats."""
    
    def __init__(self):
        self.api = get_api()
        if self.api:
            self.api.register_hook('on_battle_end', self.adjust_difficulty)
            self.api.register_hook('on_player_levelup', self.scale_world)
            self.api.log("Dynamic Difficulty System enabled")
    
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
        health_ratio = player['hp'] / max(1, player['max_hp'])
        
        # If player is doing well, increase difficulty
        if health_ratio > 0.7:
            new_player_mult = min(2.0, multipliers['player_damage_mult'] * 1.05)
            new_enemy_mult = min(2.0, multipliers['enemy_damage_mult'] * 1.1)
            self.api.set_combat_multipliers(new_player_mult, new_enemy_mult)
            self.api.log("📈 Difficulty increased!")
        
        # If player is struggling, decrease difficulty
        elif health_ratio < 0.3:
            new_player_mult = min(2.0, multipliers['player_damage_mult'] * 1.1)
            new_enemy_mult = max(0.5, multipliers['enemy_damage_mult'] * 0.9)
            self.api.set_combat_multipliers(new_player_mult, new_enemy_mult)
            self.api.log("📉 Difficulty decreased!")
    
    def scale_world(self):
        """Scale world difficulty on level up."""
        if not self.api:
            return
        
        player = self.api.get_player()
        if not player:
            return
        
        level = player['level']
        
        # Scale area difficulties
        areas = self.api.list_all_areas()
        for area_id in areas:
            area = self.api.get_area_info(area_id)
            if area and 'difficulty' in area:
                # Scale difficulty with player level
                scaled_diff = min(5, max(1, area['difficulty'] + (level // 5)))
                self.api.set_area_difficulty(area_id, scaled_diff)


# Initialize system
DynamicDifficulty()
