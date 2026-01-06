"""
Stat Tracker Script - Tracks gameplay statistics and achievements

This script demonstrates using the statistics API to track player achievements
and display them during gameplay.
"""

from scripting import get_api

class StatTracker:
    """Track gameplay statistics and achievements."""
    
    ACHIEVEMENTS = {
        'first_blood': {'enemies_defeated': 1, 'reward': 'First Kill'},
        'monster_slayer': {'enemies_defeated': 10, 'reward': 'Monster Slayer'},
        'legendary_hunter': {'enemies_defeated': 100, 'reward': 'Legendary Hunter'},
        'boss_slayer': {'bosses_defeated': 1, 'reward': 'Boss Slayer'},
        'quest_master': {'missions_completed': 5, 'reward': 'Quest Master'},
        'treasure_hoarder': {'items_collected': 50, 'reward': 'Treasure Hoarder'},
    }
    
    def __init__(self):
        self.api = get_api()
        if self.api:
            self.api.register_hook('on_battle_end', self.on_battle_end)
            self.api.register_hook('on_mission_complete', self.on_mission_complete)
            self.api.register_hook('on_item_acquired', self.on_item_acquired)
    
    def on_battle_end(self):
        """Called when battle ends."""
        if not self.api:
            return
        
        # Increment enemy counter
        enemies_defeated = self.api.increment_statistic('enemies_defeated', 1)
        
        # Check achievements
        self.check_achievements({'enemies_defeated': enemies_defeated})
    
    def on_mission_complete(self):
        """Called when mission is completed."""
        if not self.api:
            return
        
        missions_completed = self.api.increment_statistic('missions_completed', 1)
        self.check_achievements({'missions_completed': missions_completed})
    
    def on_item_acquired(self):
        """Called when item is acquired."""
        if not self.api:
            return
        
        items_collected = self.api.increment_statistic('items_collected', 1)
        self.check_achievements({'items_collected': items_collected})
    
    def check_achievements(self, stats):
        """Check if any achievements are unlocked."""
        if not self.api:
            return
        unlocked = self.api.retrieve_data('unlocked_achievements', [])
        
        for achievement_id, requirement in self.ACHIEVEMENTS.items():
            if achievement_id in unlocked:
                continue
            
            # Check if achievement requirements are met
            met = True
            for stat_name, stat_value in requirement.items():
                if stat_name == 'reward':
                    continue
                if stat_name in stats and stats[stat_name] >= stat_value:
                    continue
                met = False
                break
            
            if met:
                unlocked.append(achievement_id)
                self.api.store_data('unlocked_achievements', unlocked)
                self.api.log(f"🏆 Achievement Unlocked: {requirement.get('reward', achievement_id)}")
    
    def get_achievements(self):
        """Get list of unlocked achievements."""
        if not self.api:
            return []
        return self.api.retrieve_data('unlocked_achievements', [])
    
    def display_stats(self):
        """Display current stats."""
        if not self.api:
            return
        stats = self.api.get_game_statistics()
        self.api.log("\n=== Game Statistics ===")
        for key, value in stats.items():
            self.api.log(f"{key.replace('_', ' ').title()}: {value}")


# Initialize tracker
StatTracker()
