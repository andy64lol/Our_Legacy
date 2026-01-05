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
"""

from typing import Optional, Dict, Any, List
from scripting import get_api


class AchievementSystem:
    """Manages player achievements and milestone tracking."""
    
    # Achievement definitions with requirements
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
    
    def __init__(self):
        self.api = get_api()
        if self.api:
            # Initialize achievement tracking
            self.api.store_data('unlocked_achievements', [])
            self.api.store_data('achievement_points', 0)
            self.api.store_data('last_check', {})
            
            # Register hooks
            self.api.register_hook('on_battle_end', self.check_combat_achievements)
            self.api.register_hook('on_player_levelup', self.check_level_achievements)
            self.api.register_hook('on_mission_complete', self.check_mission_achievements)
            self.api.register_hook('on_item_acquired', self.check_item_achievements)
            
            self.api.log("Achievement System loaded!")
    
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
        
        for ach_id, ach_data in self.ACHIEVEMENTS.items():
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
                item_info = self.api.get_item_info(item_name) if item_name else None
                if item_info and item_info.get('rarity') == 'legendary':
                    has_legendary = True
                    break
            if not has_legendary:
                return False
        
        return True
    
    # ==================== Event-Based Checking ====================
    
    def check_combat_achievements(self):
        """Check combat-related achievements."""
        if not self.api:
            return
        self.check_all_achievements()
    
    def check_level_achievements(self):
        """Check level-related achievements."""
        if not self.api:
            return
        self.check_all_achievements()
    
    def check_mission_achievements(self):
        """Check mission-related achievements."""
        if not self.api:
            return
        self.check_all_achievements()
    
    def check_item_achievements(self):
        """Check item-related achievements."""
        if not self.api:
            return
        self.check_all_achievements()
    
    # ==================== Validation Methods ====================
    
    def can_accept_mission(self, mission_id: str) -> bool:
        """Check if player can accept a mission."""
        if not self.api:
            return False
        return self.api.is_mission_available(mission_id)
    
    def can_equip_item(self, item_name: str) -> bool:
        """Check if player can equip an item."""
        if not self.api:
            return False
        return self.api.can_equip_item(item_name)
    
    def get_mission_requirements(self, mission_id: str) -> dict:
        """Get detailed info about mission requirements."""
        if not self.api:
            return {}
        
        mission_info = self.api.get_mission_info(mission_id)
        if not mission_info:
            return {}
        
        player = self.api.get_player()
        if not player:
            return {}
        
        prereqs_complete = True
        prerequisites = mission_info.get('prerequisites', [])
        for prereq in prerequisites:
            if not self.api.has_mission_completed(prereq):
                prereqs_complete = False
                break
        
        return {
            'name': mission_info.get('name', 'Unknown Mission'),
            'unlock_level': mission_info.get('unlock_level', 1),
            'level_ok': player.get('level', 0) >= mission_info.get('unlock_level', 1),
            'prerequisites': prerequisites,
            'prereqs_complete': prereqs_complete,
            'target': mission_info.get('target', 'Unknown'),
            'target_count': mission_info.get('target_count', 0),
            'reward_exp': mission_info.get('reward', {}).get('experience', 0),
            'reward_gold': mission_info.get('reward', {}).get('gold', 0),
            'available': self.api.is_mission_available(mission_id),
        }
    
    def get_item_requirements(self, item_name: str) -> dict:
        """Get detailed info about item requirements."""
        if not self.api:
            return {}
        
        item_info = self.api.get_item_info(item_name)
        if not item_info:
            return {}
        
        player = self.api.get_player()
        if not player:
            return {}
        
        requirements = item_info.get('requirements', {})
        
        return {
            'name': item_name,
            'type': item_info.get('type', 'Unknown'),
            'rarity': item_info.get('rarity', 'common'),
            'price': item_info.get('price', 0),
            'level_required': requirements.get('level', 1),
            'level_ok': player.get('level', 0) >= requirements.get('level', 1),
            'class_required': requirements.get('class'),
            'class_ok': requirements.get('class') is None or 
                       player.get('class') == requirements.get('class'),
            'can_equip': self.api.can_equip_item(item_name),
        }
    
    # ==================== Progress Display ====================
    
    def get_achievement_progress(self) -> dict:
        """Get current achievement progress."""
        if not self.api:
            return {}
        
        unlocked = self.api.retrieve_data('unlocked_achievements', [])
        points = self.api.retrieve_data('achievement_points', 0)
        
        total_achievements = len(self.ACHIEVEMENTS)
        total_points = sum(a['points'] for a in self.ACHIEVEMENTS.values())
        
        return {
            'unlocked_count': len(unlocked),
            'total_achievements': total_achievements,
            'completion_percentage': int(len(unlocked) / total_achievements * 100) if total_achievements > 0 else 0,
            'points': points,
            'total_points': total_points,
            'points_percentage': int(points / total_points * 100) if total_points > 0 else 0,
            'unlocked_ids': unlocked,
        }
    
    def display_achievement_status(self):
        """Display formatted achievement status."""
        if not self.api:
            return
        
        player = self.api.get_player()
        if not player:
            return
        
        progress = self.get_achievement_progress()
        
        self.api.log("\n=== Achievement Status ===")
        self.api.log(f"Player: {player.get('name', 'Unknown')} (Level {player.get('level', 0)})")
        self.api.log(f"Progress: {progress['unlocked_count']}/{progress['total_achievements']} " +
                    f"({progress['completion_percentage']}%)")
        self.api.log(f"Points: {progress['points']}/{progress['total_points']} " +
                    f"({progress['points_percentage']}%)")
        
        self.api.log("\n--- Unlocked Achievements ---")
        unlocked_ids = progress.get('unlocked_ids', [])
        if unlocked_ids:
            for ach_id in unlocked_ids:
                ach = self.ACHIEVEMENTS.get(ach_id, {})
                if ach:
                    self.api.log(f"  [DONE] {ach.get('name', 'Unknown')} ({ach.get('points', 0)} pts)")
        else:
            self.api.log("  No achievements unlocked yet!")
        
        self.api.log("\n--- Locked Achievements ---")
        locked = [a for a in self.ACHIEVEMENTS.keys() if a not in unlocked_ids]
        for ach_id in locked[:5]:  # Show first 5 locked
            ach = self.ACHIEVEMENTS.get(ach_id, {})
            if ach:
                reqs = ach.get('requirements', {})
                req_text = self._format_requirements(reqs)
                self.api.log(f"  [LOCKED] {ach.get('name', 'Unknown')}: {req_text}")
        
        if len(locked) > 5:
            self.api.log(f"  ... and {len(locked) - 5} more")
    
    def _format_requirements(self, reqs: dict) -> str:
        """Format requirements as readable text."""
        parts = []
        if 'stat' in reqs:
            parts.append(f"{reqs['stat'].replace('_', ' ')} ≥ {reqs.get('value', 0)}")
        if 'level' in reqs:
            parts.append(f"Level {reqs.get('level', 0)}")
        if 'gold' in reqs:
            parts.append(f"{reqs.get('gold', 0)} gold")
        if 'equipment_slots' in reqs:
            parts.append(f"{reqs.get('equipment_slots', 0)} slots filled")
        if 'has_legendary' in reqs:
            parts.append("Own legendary item")
        return ", ".join(parts)
    
    # ==================== Statistics Display ====================
    
    def display_player_progress(self):
        """Display comprehensive player progress."""
        if not self.api:
            return
        
        player = self.api.get_player()
        if not player:
            return
        
        stats = self.api.get_game_statistics() or {}
        progress = self.get_achievement_progress()
        
        self.api.log("\n=== Player Progress ===")
        self.api.log(f"Level: {player.get('level', 0)} ({player.get('rank', 'N/A')})")
        self.api.log(f"Experience: {player.get('experience', 0)}/{player.get('experience_to_next', '???')}")
        self.api.log(f"Gold: {player.get('gold', 0)}")
        
        self.api.log("\n--- Combat Stats ---")
        self.api.log(f"Enemies Defeated: {stats.get('enemies_defeated', 0)}")
        self.api.log(f"Bosses Defeated: {stats.get('bosses_defeated', 0)}")
        
        self.api.log("\n--- Quest Stats ---")
        self.api.log(f"Missions Completed: {stats.get('missions_completed', 0)}")
        
        self.api.log("\n--- Collection Stats ---")
        self.api.log(f"Items Collected: {stats.get('items_collected', 0)}")
        inventory = player.get('inventory', [])
        self.api.log(f"Inventory Items: {len(inventory)}")
        inventory_value = 0
        if hasattr(self.api, 'get_inventory_value'):
            inventory_value = self.api.get_inventory_value()
        self.api.log(f"Inventory Value: {inventory_value} gold")
        
        self.api.log("\n--- Equipment ---")
        equipped = {}
        if hasattr(self.api, 'get_equipped_items'):
            equipped = self.api.get_equipped_items() or {}
        filled_slots = sum(1 for v in equipped.values() if v)
        self.api.log(f"Equipped Slots: {filled_slots}/6")
        
        self.api.log("\n--- Achievements ---")
        self.api.log(f"Achievements: {progress.get('unlocked_count', 0)}/{progress.get('total_achievements', 0)}")
        self.api.log(f"Points: {progress.get('points', 0)}")


# Initialize achievement system
achievement_system = AchievementSystem()


def register_hooks():
    """Register any additional hooks."""
    api = get_api()
    if api:
        api.log("Achievement System example loaded!")


register_hooks()