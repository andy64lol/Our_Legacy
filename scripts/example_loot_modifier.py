"""
Loot Modifier Script - Enhances and customizes loot drops

This script demonstrates modifying enemy drops, creating themed loot tables,
and implementing rarity-based drop chances.
"""

from main import get_api
import random

class LootModifier:
    """Customize and enhance loot drops from enemies."""
    
    # Rarity tiers and their drop rates
    RARITY_RATES = {
        'common': 0.50,      # 50% chance
        'uncommon': 0.30,    # 30% chance
        'rare': 0.15,        # 15% chance
        'epic': 0.04,        # 4% chance
        'legendary': 0.01,   # 1% chance
    }
    
    # Custom loot tables by enemy type
    THEMATIC_LOOT = {
        'goblin': ['Health Potion', 'Gold Coin', 'Goblin Ear', 'Copper Ring'],
        'orc': ['Orc Tooth', 'Iron Axe', 'Large Health Potion', 'War Horn'],
        'dragon': ['Dragon Scale', 'Fire Gem', 'Dragon Heart', 'Golden Hoard'],
        'skeleton': ['Bone Fragment', 'Dark Crystal', 'Soul Gem', 'Cursed Rune'],
        'bandit': ['Gold Coin', 'Steel Dagger', 'Stolen Necklace', 'Secret Map'],
        'troll': ['Troll Club', 'Large Health Potion', 'Troll Hide', 'Stone Tooth'],
    }
    
    def __init__(self):
        self.api = get_api()
        if self.api:
            self.api.register_hook('on_battle_end', self.enhance_loot)
            self.api.log("Loot Modifier System enabled")
    
    def enhance_loot(self):
        """Enhance loot drops based on rarity and player level."""
        if not self.api:
            return
        
        player = self.api.get_player()
        if not player:
            return
        
        # Generate bonus loot items
        level = player['level']
        
        # Higher level = more loot drops (every 5 levels, +1 item)
        bonus_items = max(0, (level - 1) // 5)
        
        for _ in range(bonus_items):
            # Roll for rarity
            roll = random.random()
            rarity = None
            
            cumulative = 0
            for rarity_tier, rate in self.RARITY_RATES.items():
                cumulative += rate
                if roll <= cumulative:
                    rarity = rarity_tier
                    break
            
            if rarity:
                self.api.log(f"✨ Bonus {rarity} item dropped!")
    
    def get_thematic_loot(self, enemy_name):
        """Get thematic loot for an enemy."""
        if not self.api:
            return []
        
        # Check if we have custom loot for this enemy
        for enemy_key, loot_list in self.THEMATIC_LOOT.items():
            if enemy_key.lower() in enemy_name.lower():
                return loot_list
        
        # Fallback to generic loot
        items = self.api.list_all_items()
        return random.sample(items, min(3, len(items)))


# Initialize system
LootModifier()
