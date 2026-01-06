#!/usr/bin/env python3
"""
Example Script: Companion Reward
Automatically recruit a companion when reaching certain levels.
"""

from scripting import get_api


COMPANION_REWARDS = {
    5: 'Borin the Brave',
    10: 'Lyra the Swift',
    15: 'Mira the Healer',
    20: 'Ragnar the Warlord',
}


def on_levelup_companion_reward():
    """Called when player levels up."""
    api = get_api()
    if api is None:
        return

    player = api.get_player()
    if player is None:
        return

    # Check if player reached a milestone level
    if player['level'] in COMPANION_REWARDS:
        companion_name = COMPANION_REWARDS[player['level']]
        if companion_name not in player['companions']:
            api.log(f"You've earned a companion! {companion_name} joins your party!")
            api.hire_companion(companion_name)
        else:
            api.log(f"{companion_name} is already with you!")


def register_hooks():
    """Register this script's event hooks."""
    api = get_api()
    if api:
        api.register_hook('on_player_levelup', on_levelup_companion_reward)
        api.log("Companion Reward script loaded!")


# Auto-register when imported
register_hooks()
