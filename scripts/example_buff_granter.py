#!/usr/bin/env python3
"""
Example Script: Buff Granter
Grants the player a powerful buff every 5 levels.

## New Script Format
This script uses the standardized format with SCRIPT_INFO and HOOKS.
"""

from main import get_api


# ============================================================================
# SCRIPT INFO - Metadata about this script
# ============================================================================
SCRIPT_INFO = {
    "name": "Buff Granter",
    "version": "1.0",
    "author": "Our Legacy Team",
    "description": "Grants power buffs every 5 levels",
    "priority": 100,
    "dependencies": []
}


# ============================================================================
# HOOKS - Event handler mappings
# ============================================================================
HOOKS = {
    "on_player_levelup": "on_player_levelup_handler"
}


# ============================================================================
# BUFF DEFINITIONS
# ============================================================================
BUFFS = {
    5: {
        'name': 'Milestone Buff',
        'duration': 10,
        'modifiers': {
            'attack_bonus': 5,
            'defense_bonus': 3,
            'speed_bonus': 2,
        }
    },
    10: {
        'name': 'Decade Buff',
        'duration': 15,
        'modifiers': {
            'attack_bonus': 10,
            'defense_bonus': 6,
            'speed_bonus': 4,
        }
    },
    15: {
        'name': 'Veteran Buff',
        'duration': 20,
        'modifiers': {
            'attack_bonus': 15,
            'defense_bonus': 10,
            'speed_bonus': 6,
        }
    },
    20: {
        'name': 'Champion Buff',
        'duration': 25,
        'modifiers': {
            'attack_bonus': 25,
            'defense_bonus': 15,
            'speed_bonus': 10,
        }
    },
    25: {
        'name': 'Legendary Buff',
        'duration': 30,
        'modifiers': {
            'attack_bonus': 40,
            'defense_bonus': 25,
            'speed_bonus': 15,
        }
    },
}


# ============================================================================
# EVENT HANDLERS - Functions called by the ScriptManager
# ============================================================================

def on_player_levelup_handler():
    """Called when player levels up - grant appropriate buff."""
    api = get_api()
    if api is None:
        return

    player = api.get_player()
    if player is None:
        return

    level = player['level']
    
    # Check if this level has a buff defined
    if level in BUFFS:
        buff_data = BUFFS[level]
        api.log(f"Congratulations on reaching level {level}! Granting {buff_data['name']}...")
        api.apply_buff(
            buff_data['name'],
            duration=buff_data['duration'],
            modifiers=buff_data['modifiers']
        )


# ============================================================================
# INITIALIZATION - Optional init function called by ScriptManager
# ============================================================================

def init_script():
    """Initialize the buff granter when script is loaded."""
    api = get_api()
    if api:
        api.log("Buff Granter script initialized!")
    else:
        print("Buff Granter script loaded (API not available yet)")


def shutdown_script():
    """Clean up when script is unloaded or game shuts down."""
    api = get_api()
    if api:
        api.log("Buff Granter shutdown complete")

