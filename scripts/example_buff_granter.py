#!/usr/bin/env python3
"""
Example Script: Buff Granter
Grants the player a powerful buff every 5 levels.
"""

from scripting import get_api


def on_levelup():
    """Called when player levels up."""
    api = get_api()
    if api is None:
        return

    player = api.get_player()
    if player is None:
        return

    # Every 5 levels, grant a power boost
    if player['level'] % 5 == 0:
        api.log(f"Congratulations on reaching level {player['level']}! Granting power boost...")
        api.apply_buff(
            'Milestone Buff',
            duration=10,
            modifiers={
                'attack_bonus': 5,
                'defense_bonus': 3,
                'speed_bonus': 2,
            }
        )


def register_hooks():
    """Register this script's event hooks."""
    api = get_api()
    if api:
        api.register_hook('on_player_levelup', on_levelup)
        api.log("Buff Granter script loaded!")


# Auto-register when imported
register_hooks()
