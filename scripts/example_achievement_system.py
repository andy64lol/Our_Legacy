#!/usr/bin/env python3
"""
Example Script: Achievement System
Demonstrates statistics tracking, mission validation, and equipment checks.

This script provides a comprehensive achievement system including:
- Tracking various game statistics
- Checking achievement conditions
- Validating mission availability
- Checking equipment requirements
- Displaying player progress

## New Script Format
This script uses the standardized format with SCRIPT_INFO and HOOKS.
"""

from typing import Optional
from main import get_api


# ============================================================================
# SCRIPT INFO - Metadata about this script
# ============================================================================
SCRIPT_INFO = {
    "name": "Achievement System",
    "version": "1.0",
    "author": "Our Legacy Team",
    "description": "Tracks player achievements and milestones",
    "priority": 100,
    "dependencies": []
}


# ============================================================================
# HOOKS - Event handler mappings
# ============================================================================
HOOKS = {
    "on_battle_end": "on_battle_end_handler",
    "on_player_levelup": "on_player_levelup_handler",
    "on_mission_complete": "on_mission_complete_handler",
    "on_item_acquired": "on_item_acquired_handler"
}


# ============================================================================
# ACHIEVEMENT DEFINITIONS
# ============================================================================
ACHIEVEMENTS = {
    # Combat achievements
    'first_blood': {
        'name': 'First Blood',
        'description': 'Defeat your first enemy',
        'requirements': {'stat': 'enemies_defeated', 'value': 1},
        'points': 10,
    },
    'monster_slayer': {
        'name': 'Monster Slayer',
        'description': 'Defeat 10 enemies',
        'requirements': {'stat': 'enemies_defeated', 'value': 10},
        'points': 50,
    },
    'boss_hunter': {
        'name': 'Boss Hunter',
        'description': 'Defeat your first boss',
        'requirements': {'stat': 'bosses_defeated', 'value': 1},
        'points': 100,
    },
    
    # Leveling achievements
    'level_5': {
        'name': 'Getting Stronger',
        'description': 'Reach level 5',
        'requirements': {'level': 5},
        'points': 20,
    },
    'level_10': {
        'name': 'Adventurer',
        'description': 'Reach level 10',
        'requirements': {'level': 10},
        'points': 50,
    },
    'level_25': {
        'name': 'Heroic',
        'description': 'Reach level 25',
        'requirements': {'level': 25},
        'points': 100,
    },
    
    # Collection achievements
    'item_collector': {
        'name': 'Item Collector',
        'description': 'Collect 20 items',
        'requirements': {'stat': 'items_collected', 'value': 20},
        'points': 30,
    },
    'wealthy': {
        'name': 'Wealthy',
        'description': 'Accumulate 1000 gold',
        'requirements': {'gold': 1000},
        'points': 40,
    },
    
    # Mission achievements
    'quest_starter': {
        'name': 'Quest Starter',
        'description': 'Complete your first mission',
        'requirements': {'stat': 'missions_completed', 'value': 1},
        'points': 20,
    },
    'quest_master': {
        'name': 'Quest Master',
        'description': 'Complete 10 missions',
        'requirements': {'stat': 'missions_completed', 'value': 10},
        'points': 80,
    },
    
    # Equipment achievements
    'well_equipped': {
        'name': 'Well Equipped',
        'description': 'Have all equipment slots filled',
        'requirements': {'equipment_slots': 6},
        'points': 30,
    },
    'legendary_collector': {
        'name': 'Legendary Collector',
        'description': 'Own a legendary item',
        'requirements': {'has_legendary': True},
        'points': 60,
    },
}


class AchievementSystem:
    """Manages player achievements and milestone tracking."""
    
    def __init__(self):
        self.api = None
        self._initialized = False
    
    def initialize(self):
        """Initialize the achievement system. Safe to call multiple times."""
        if self._initialized:
            return
        
        self.api = get_api()
        if self.api:
            self._init_achievement_tracking()
            self._initialized = True
    
    def _init_achievement_tracking(self):
        """Initialize achievement tracking data."""
        if self.api:
            self.api.store_data('unlocked_achievements', [])
            self.api.store_data('achievement_points', 0)
            self.api.store_data('last_check', {})
    
    # ==================== Achievement Checking ====================
    
    def check_all_achievements(self):
        """Check all achievements for unlock eligibility."""
        if not self.api:
            return
        
        player = self.api.get_player()
        if not player:
            return
        
        stats = self.api.get_game_statistics()
        unlocked = self.api.retrieve_data('unlocked_achievements', [])
        points = self.api.retrieve_data('achievement_points', 0)
        
        for ach_id, ach_data in ACHIEVEMENTS.items():
            if ach_id in unlocked:
                continue
            
            reqs = ach_data['requirements']
            
            if self._check_requirements(player, stats, reqs):
                unlocked.append(ach_id)
                points += ach_data['points']
                self.api.log(f"ACHIEVEMENT UNLOCKED: {ach_data['name']} (+{ach_data['points']} pts)")
                self.api.log(f"   {ach_data['description']}")
        
        self.api.store_data('unlocked_achievements', unlocked)
        self.api.store_data('achievement_points', points)
    
    def _check_requirements(self, player: dict, stats: dict, reqs: dict) -> bool:
        """Check if requirements are met."""
        # Check stat requirements
        if 'stat' in reqs:
            stat_name = reqs['stat']
            if stat_name not in stats:
                return False
            if stats[stat_name] < reqs['value']:
                return False
        
        # Check level requirement
        if 'level' in reqs:
            if player.get('level', 0) < reqs['level']:
                return False
        
        # Check gold requirement
        if 'gold' in reqs:
            if player.get('gold', 0) < reqs['gold']:
                return False
        
        # Check equipment slots
        if 'equipment_slots' in reqs:
            if not self.api:
                return False
            equipped = self.api.get_equipped_items()
            filled = sum(1 for v in equipped.values() if v) if equipped else 0
            if filled < reqs['equipment_slots']:
                return False
        
        # Check for legendary item
        if 'has_legendary' in reqs and reqs['has_legendary']:
            if not self.api:
                return False
            inventory = self.api.get_inventory() or []
            has_legendary = False
            for item_name in inventory:
                if not item_name:
                    continue
                item_info = self.api.get_item_info(item_name)
                if item_info and item_info.get('rarity') == 'legendary':
                    has_legendary = True
                    break
            if not has_legendary:
                return False
        
        return True
    
    # ==================== Progress Display ====================
    
    def get_achievement_progress(self) -> dict:
        """Get current achievement progress."""
        if not self.api:
            return {}
        
        unlocked = self.api.retrieve_data('unlocked_achievements', [])
        points = self.api.retrieve_data('achievement_points', 0)
        
        total_achievements = len(ACHIEVEMENTS)
        total_points = sum(a['points'] for a in ACHIEVEMENTS.values())
        
        return {
            'unlocked_count': len(unlocked),
            'total_achievements': total_achievements,
            'completion_percentage': int(len(unlocked) / total_achievements * 100) if total_achievements > 0 else 0,
            'points': points,
            'total_points': total_points,
            'points_percentage': int(points / total_points * 100) if total_points > 0 else 0,
            'unlocked_ids': unlocked,
        }


# Global instance - lazily created
_achievement_system = None


def _get_achievement_system() -> Optional[AchievementSystem]:
    """Get or create the achievement system instance."""
    global _achievement_system
    if _achievement_system is None:
        _achievement_system = AchievementSystem()
        _achievement_system.initialize()
    return _achievement_system


# ============================================================================
# EVENT HANDLERS - Functions called by the ScriptManager
# ============================================================================

def on_battle_end_handler():
    """Handle battle end event - check combat achievements."""
    system = _get_achievement_system()
    if system:
        system.check_all_achievements()


def on_player_levelup_handler():
    """Handle player level up event - check level achievements."""
    system = _get_achievement_system()
    if system:
        system.check_all_achievements()


def on_mission_complete_handler():
    """Handle mission complete event - check mission achievements."""
    system = _get_achievement_system()
    if system:
        system.check_all_achievements()


def on_item_acquired_handler(item_name: Optional[str] = None):
    """Handle item acquired event - check collection achievements."""
    system = _get_achievement_system()
    if system:
        system.check_all_achievements()


# ============================================================================
# INITIALIZATION - Optional init function called by ScriptManager
# ============================================================================

def init_script():
    """Initialize the achievement system when script is loaded."""
    system = _get_achievement_system()
    api = get_api()
    if api:
        api.log("Achievement System initialized!")
        # Perform initial check
        if system:
            system.check_all_achievements()
    else:
        # Still log that the script tried to initialize
        print("[Achievement System] Warning: No API available during init")


def shutdown_script():
    """Clean up when script is unloaded or game shuts down."""
    global _achievement_system
    api = get_api()
    if api:
        api.log("Achievement System shutdown complete")
    _achievement_system = None

