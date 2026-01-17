#!/usr/bin/env python3
"""
Example Script: Quest Giver
Provides custom quests via the scripting API.
"""

from main import get_api


class QuestGiver:
    """Manages custom quests."""
    
    def __init__(self):
        self.api = None
        self._initialized = False
        self.quests = {
            'custom_1': {
                'name': 'Gathering Task',
                'description': 'Collect 5 Health Potions',
                'reward_gold': 200,
                'reward_exp': 100,
                'target_item': 'Health Potion',
                'target_count': 5,
            },
            'custom_2': {
                'name': 'Strength Training',
                'description': 'Reach Attack stat of 50',
                'reward_gold': 300,
                'reward_exp': 150,
                'target_stat': 'attack',
                'target_value': 50,
            },
        }
    
    def initialize(self):
        """Initialize the quest giver. Safe to call multiple times."""
        if self._initialized:
            return
        
        self.api = get_api()
        if self.api:
            self.api.log("Quest Giver script loaded!")
            self.api.store_data('quest_giver', self)
            self._initialized = True
    
    def check_quest_progress(self):
        """Check and complete quests."""
        if not self.api:
            return

        player = self.api.get_player()
        if player is None:
            return

        # Check collection quest
        quest = self.quests.get('custom_1', {})
        target_item = quest.get('target_item', '')
        target_count = quest.get('target_count', 5)
        inventory = player.get('inventory', [])
        potions = inventory.count(target_item) if isinstance(inventory, list) else 0
        if potions >= target_count:
            self.api.log(f"Quest Complete: {quest.get('name', 'Unknown')}!")
            reward_gold = quest.get('reward_gold', 0)
            current_gold = player.get('gold', 0)
            self.api.set_player_stat('gold', current_gold + reward_gold)


# Global instance - lazily created
_quest_giver = None


def _get_quest_giver() -> 'QuestGiver':
    """Get or create the quest giver instance."""
    global _quest_giver
    if _quest_giver is None:
        _quest_giver = QuestGiver()
        _quest_giver.initialize()
    return _quest_giver


def register_hooks():
    """Register this script's event hooks."""
    quest_giver = _get_quest_giver()
    print("Quest Giver script loaded!")


# Auto-register when imported
register_hooks()

