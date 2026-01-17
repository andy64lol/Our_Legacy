#!/usr/bin/env python3
"""
Example Script: Equipment Manager
Demonstrates inventory and equipment management methods.

This script provides a comprehensive equipment management system including:
- Getting equipped items and inventory
- Equipping and unequipping items
- Auto-equipping best items based on stats
- Swapping equipment between slots
- Equipment validation and recommendations
"""

from typing import Optional, Dict, Any, List
from main import get_api


class EquipmentManager:
    """Manages player equipment with smart auto-equip features."""
    
    # Stat priority for different equipment slots
    STAT_PRIORITY = {
        'weapon': ['attack', 'speed'],
        'armor': ['defense', 'hp'],
        'offhand': ['defense', 'mp'],
        'accessory': ['attack', 'defense', 'speed', 'hp', 'mp'],
    }
    
    def __init__(self):
        self.api = None
        self._initialized = False
    
    def initialize(self):
        """Initialize the equipment manager. Safe to call multiple times."""
        if self._initialized:
            return
        
        self.api = get_api()
        if self.api:
            self.api.log("Equipment Manager System loaded!")
            self._initialized = True
    
    # ==================== Basic Equipment Operations ====================
    
    def get_all_equipment(self) -> Dict[str, Any]:
        """Get a complete overview of player equipment."""
        if not self.api:
            return {}
        
        equipped = self.api.get_equipped_items() or {}
        inventory = self.api.get_inventory() or []
        inventory_summary = self.api.get_inventory_summary() or {}
        
        return {
            'equipped': equipped,
            'inventory_count': len(inventory),
            'inventory_summary': inventory_summary,
            'total_inventory_value': self.api.get_inventory_value(),
        }
    
    def equip_item_by_name(self, item_name: str) -> bool:
        """Equip an item by name (auto-detects slot)."""
        if not self.api:
            return False
        
        if not self.api.has_item(item_name):
            self.api.log(f"You don't have: {item_name}")
            return False
        
        return self.api.equip_item(item_name)
    
    def unequip_slot(self, slot: str) -> bool:
        """Unequip an item from a specific slot."""
        if not self.api:
            return False
        
        item = self.api.unequip_item(slot)
        if item:
            self.api.log(f"Unequipped {item} from {slot}")
            return True
        else:
            self.api.log(f"Nothing equipped in {slot}")
            return False
    
    def swap_equipment_slots(self, slot1: str, slot2: str) -> bool:
        """Swap items between two equipment slots."""
        if not self.api:
            return False
        
        equipped = self.api.get_equipped_items() or {}
        item1 = equipped.get(slot1)
        item2 = equipped.get(slot2)
        
        self.api.log(f"Swapping {slot1}: {item1} <-> {slot2}: {item2}")
        
        return self.api.swap_equipment(slot1, slot2)
    
    # ==================== Auto-Equip System ====================
    
    def get_item_stats(self, item_name: str) -> Dict[str, Any]:
        """Get the stat bonuses of an item."""
        if not self.api or not item_name:
            return {}
        
        item_info = self.api.get_item_info(item_name) or {}
        if not item_info:
            return {}
        
        stats: Dict[str, Any] = {}
        if 'attack_bonus' in item_info:
            stats['attack'] = item_info['attack_bonus']
        if 'defense_bonus' in item_info:
            stats['defense'] = item_info['defense_bonus']
        if 'speed_bonus' in item_info:
            stats['speed'] = item_info['speed_bonus']
        if 'stat_bonuses' in item_info:
            stats.update(item_info['stat_bonuses'])
        
        # Calculate total stat score
        stats['_total'] = sum(stats.values())
        return stats
    
    def get_item_score(self, item_name: str, slot: str) -> float:
        """Score an item for a specific slot based on stat priority."""
        item_stats = self.get_item_stats(item_name)
        if not item_stats:
            return 0.0
        
        priority = self.STAT_PRIORITY.get(slot, ['attack', 'defense'])
        score = 0.0
        
        for stat in priority:
            if stat in item_stats:
                score += item_stats[stat] * (len(priority) - priority.index(stat))
        
        return score
    
    def can_equip_item(self, item_name: str) -> bool:
        """Check if player can equip an item (meets requirements)."""
        if not self.api:
            return False
        return self.api.can_equip_item(item_name)
    
    def get_best_item_for_slot(self, slot: str) -> Optional[str]:
        """Find the best item in inventory for a slot."""
        if not self.api:
            return None
        
        inventory = self.api.get_inventory() or []
        best_item: Optional[str] = None
        best_score = -1.0
        
        for item_name in inventory:
            if not item_name:
                continue
            
            # Check if item can go in this slot
            if not self._item_fits_slot(item_name, slot):
                continue
            
            # Check if player can equip it
            if not self.api.can_equip_item(item_name):
                continue
            
            # Score the item
            score = self.get_item_score(item_name, slot)
            if score > best_score:
                best_score = score
                best_item = item_name
        
        return best_item
    
    def _item_fits_slot(self, item_name: str, slot: str) -> bool:
        """Check if an item type matches the target slot."""
        if not self.api or not item_name:
            return False
        
        item_info = self.api.get_item_info(item_name)
        if not item_info:
            return False
        
        item_type = item_info.get('type')
        
        if slot == 'weapon':
            return item_type == 'weapon'
        elif slot == 'armor':
            return item_type == 'armor'
        elif slot == 'offhand':
            return item_type == 'offhand'
        elif slot.startswith('accessory'):
            return item_type == 'accessory'
        
        return False
    
    def auto_equip_best(self) -> Dict[str, str]:
        """Automatically equip the best item for each slot."""
        if not self.api:
            return {}
        
        results: Dict[str, str] = {}
        slots = ['weapon', 'armor', 'offhand', 'accessory_1', 'accessory_2', 'accessory_3']
        
        for slot in slots:
            best_item = self.get_best_item_for_slot(slot)
            if best_item:
                # Unequip current item first
                current = (self.api.get_equipped_items() or {}).get(slot)
                if current and current != best_item:
                    self.api.unequip_item(slot)
                
                # Equip best item
                if self.api.equip_item(best_item, slot):
                    results[slot] = best_item
        
        return results
    
    # ==================== Equipment Recommendations ====================
    
    def get_equipment_recommendations(self) -> Dict[str, Dict[str, Any]]:
        """Get recommendations for equipment upgrades."""
        if not self.api:
            return {}
        
        recommendations: Dict[str, Dict[str, Any]] = {}
        equipped = self.api.get_equipped_items() or {}
        
        for slot, current_item in equipped.items():
            if not current_item:
                continue
            
            # Find best alternative
            best_alternative: Optional[str] = None
            best_score = self.get_item_score(current_item, slot)
            
            inventory = self.api.get_inventory() or []
            for item_name in inventory:
                if not item_name or item_name == current_item:
                    continue
                if not self._item_fits_slot(item_name, slot):
                    continue
                if not self.api.can_equip_item(item_name):
                    continue
                
                score = self.get_item_score(item_name, slot)
                if score > best_score:
                    best_score = score
                    best_alternative = item_name
            
            if best_alternative:
                current_score = self.get_item_score(current_item, slot)
                recommendations[slot] = {
                    'current': current_item,
                    'recommended': best_alternative,
                    'improvement': best_score - current_score
                }
        
        return recommendations
    
    # ==================== Equipment Stats Display ====================
    
    def display_equipment_stats(self):
        """Display detailed equipment statistics."""
        if not self.api:
            return
        
        player = self.api.get_player()
        if not player:
            return
        
        self.api.log("\n=== Equipment Overview ===")
        
        equipped = self.api.get_equipped_items() or {}
        for slot, item in equipped.items():
            if item:
                item_info = self.api.get_item_info(item) or {}
                self.api.log(f"  {slot}: {item}")
                if item_info:
                    stats = self.get_item_stats(item)
                    for stat, value in stats.items():
                        if stat != '_total':
                            self.api.log(f"    +{value} {stat}")
        
        # Show comparison
        base = self.api.get_base_stats() or {}
        effective = self.api.get_effective_stats() or {}
        
        self.api.log("\n=== Stat Comparison ===")
        self.api.log(f"{'Stat':<10} {'Base':>8} {'Effective':>10} {'Bonus':>8}")
        for stat in ['attack', 'defense', 'speed']:
            base_stat = base.get(stat, 0)
            eff_stat = effective.get(stat, 0)
            bonus = eff_stat - base_stat
            self.api.log(f"{stat:<10} {base_stat:>8} {eff_stat:>10} {'+' + str(bonus) if bonus > 0 else bonus:>8}")


# Global instance - lazily created
_equipment_manager = None


def _get_equipment_manager() -> 'EquipmentManager':
    """Get or create the equipment manager instance."""
    global _equipment_manager
    if _equipment_manager is None:
        _equipment_manager = EquipmentManager()
        _equipment_manager.initialize()
    return _equipment_manager


def register_hooks():
    """Register hooks for equipment-related events."""
    manager = _get_equipment_manager()
    print("Equipment Manager example loaded!")


# Auto-register when imported
register_hooks()

