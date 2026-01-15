#!/usr/bin/env python3
"""
Example Script: Quest Giver
Provides custom quests via the scripting API.
"""

from main import get_api


class QuestGiver:
    """Manages custom quests."""

    def __init__(self):
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

    def check_quest_progress(self):
        """Check and complete quests."""
        api = get_api()
        if api is None:
            return

        player = api.get_player()
        if player is None:
            return

        # Check collection quest
        quest = self.quests['custom_1']
        potions = player['inventory'].count('Health Potion')
        if potions >= quest['target_count']:
            api.log(f"Quest Complete: {quest['name']}!")
            api.set_player_stat('gold', player['gold'] + quest['reward_gold'])


def register_hooks():
    """Register this script's event hooks."""
    api = get_api()
    if api:
        api.log("Quest Giver script loaded!")
        api.store_data('quest_giver', QuestGiver())


# Auto-register when imported
register_hooks()
