#!/usr/bin/env python3
"""
Example Script: Companion Reward
Automatically recruit a companion when reaching certain levels.

## New Script Format
This script uses the standardized format with SCRIPT_INFO and HOOKS.
"""

from main import get_api


# ============================================================================
# SCRIPT INFO - Metadata about this script
# ============================================================================
SCRIPT_INFO = {
    "name": "Companion Reward",
    "version": "1.0",
    "author": "Our Legacy Team",
    "description": "Automatically recruits companions at certain levels",
    "priority": 90,
    "dependencies": []
}


# ============================================================================
# HOOKS - Event handler mappings
# ============================================================================
HOOKS = {
    "on_player_levelup": "on_player_levelup_handler"
}


# ============================================================================
# COMPANION REWARDS - Level -> Companion Name mapping
# ============================================================================
COMPANION_REWARDS = {
    5: 'Borin the Brave',
    10: 'Lyra the Swift',
    15: 'Mira the Healer',
    20: 'Ragnar the Warlord',
}


# ============================================================================
# EVENT HANDLERS - Functions called by the ScriptManager
# ============================================================================

def on_player_levelup_handler():
    """Called when player levels up - check for companion reward."""
    api = get_api()
    if api is None:
        return

    player = api.get_player()
    if player is None:
        return

    level = player['level']
    
    # Check if player reached a milestone level with companion reward
    if level in COMPANION_REWARDS:
        companion_name = COMPANION_REWARDS[level]
        
        # Check if companion is already hired
        companions = player.get('companions', [])
        companion_names = [
            c.get('name') if isinstance(c, dict) else c
            for c in companions
        ]
        
        if companion_name not in companion_names:
            # Try to hire the companion
            if api.hire_companion(companion_name):
                api.log(f"You've earned a companion! {companion_name} joins your party!")
            else:
                api.log(f"Could not hire {companion_name} - party may be full")
        else:
            api.log(f"{companion_name} is already with you!")


# ============================================================================
# INITIALIZATION - Optional init function called by ScriptManager
# ============================================================================

def init_script():
    """Initialize the companion reward script when loaded."""
    api = get_api()
    if api:
        api.log("Companion Reward script initialized!")
    else:
        print("Companion Reward script loaded (API not available yet)")


def shutdown_script():
    """Clean up when script is unloaded or game shuts down."""
    api = get_api()
    if api:
        api.log("Companion Reward shutdown complete")

