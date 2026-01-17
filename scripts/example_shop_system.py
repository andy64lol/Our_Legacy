#!/usr/bin/env python3
"""
Example Script: Shop System
Demonstrates buying, selling, and inventory management methods.

This script creates a merchant/shop system that allows:
- Buying items from shops
- Selling items for gold
- Calculating item values
- Managing shop inventory
- Tracking transaction history
"""

from typing import Optional, Dict, Any, List, Tuple
from main import get_api
import random


class ShopSystem:
    """Manages a player-run shop and trading system."""
    
    # Sell price multiplier (usually 50% of buy price)
    SELL_MULTIPLIER = 0.5
    
    # Markup for shop items (usually 120% of base price)
    BUY_MARKUP = 1.2
    
    def __init__(self):
        self.api = None
        self._initialized = False
    
    def initialize(self):
        """Initialize the shop system. Safe to call multiple times."""
        if self._initialized:
            return
        
        self.api = get_api()
        if self.api:
            # Initialize transaction history
            self.api.store_data('total_gold_spent', 0)
            self.api.store_data('total_gold_earned', 0)
            self.api.store_data('transactions', [])
            
            self.api.log("Shop System loaded!")
            self._initialized = True
    
    # ==================== Buying Items ====================
    
    def buy_item(self, item_name: str, quantity: int = 1) -> bool:
        """Buy an item from the shop."""
        if not self.api or not item_name:
            return False
        
        # Check if item exists
        if not self.api.has_item(item_name, 0):
            self.api.log(f"Item not found in game data: {item_name}")
            return False
        
        # Get price with markup
        base_price = self.api.get_item_price(item_name)
        total_cost = int(base_price * self.BUY_MARKUP * quantity)
        
        # Check player's gold
        player = self.api.get_player() or {}
        if not player:
            return False
        
        if player.get('gold', 0) < total_cost:
            self.api.log(f"Not enough gold! Need {total_cost}, have {player.get('gold', 0)}")
            return False
        
        # Complete transaction
        if self.api.buy_item(item_name, quantity):
            # Track spending
            spent = self.api.retrieve_data('total_gold_spent', 0) + total_cost
            self.api.store_data('total_gold_spent', spent)
            
            # Log transaction
            self._log_transaction('buy', item_name, quantity, total_cost)
            
            self.api.log(f"Bought {quantity}x {item_name} for {total_cost} gold")
            return True
        
        return False
    
    def buy_multiple_items(self, items: List[Tuple[str, int]]) -> Dict[str, Any]:
        """Buy multiple items at once."""
        if not self.api:
            return {'success': False, 'items_bought': 0}
        
        player = self.api.get_player() or {}
        if not player:
            return {'success': False, 'items_bought': 0}
        
        total_cost = 0
        for item_name, quantity in items:
            if not item_name:
                continue
            base_price = self.api.get_item_price(item_name)
            total_cost += int(base_price * self.BUY_MARKUP * quantity)
        
        if player.get('gold', 0) < total_cost:
            self.api.log(f"Not enough gold for bulk purchase! Need {total_cost}")
            return {'success': False, 'items_bought': 0}
        
        bought = 0
        for item_name, quantity in items:
            if not item_name:
                continue
            if self.api.buy_item(item_name, quantity):
                bought += 1
        
        if bought > 0:
            spent = self.api.retrieve_data('total_gold_spent', 0) + total_cost
            self.api.store_data('total_gold_spent', spent)
            self.api.log(f"Bulk purchase complete: {bought}/{len(items)} item types acquired")
        
        return {'success': bought == len(items), 'items_bought': bought}
    
    # ==================== Selling Items ====================
    
    def sell_item(self, item_name: str, quantity: int = 1) -> int:
        """Sell an item from inventory."""
        if not self.api or not item_name:
            return 0
        
        # Check if player has the item
        if not self.api.has_item(item_name, quantity):
            self.api.log(f"You don't have {quantity}x {item_name}")
            return 0
        
        # Calculate sell price
        base_price = self.api.get_item_price(item_name)
        sell_price = int(base_price * self.SELL_MULTIPLIER)
        total_gold = sell_price * quantity
        
        # Complete transaction
        earned = self.api.sell_item(item_name, quantity)
        
        if earned > 0:
            # Track earnings
            total_earned = self.api.retrieve_data('total_gold_earned', 0) + earned
            self.api.store_data('total_gold_earned', total_earned)
            
            # Log transaction
            self._log_transaction('sell', item_name, quantity, earned)
            
            self.api.log(f"Sold {quantity}x {item_name} for {earned} gold")
        
        return earned
    
    def sell_all_items(self, item_name: Optional[str] = None) -> Dict[str, int]:
        """Sell all instances of an item, or all sellable items."""
        if not self.api:
            return {'items_sold': 0, 'gold_earned': 0}
        
        inventory = self.api.get_inventory_summary()
        if not inventory:
            return {'items_sold': 0, 'gold_earned': 0}
        
        total_gold = 0
        items_sold = 0
        
        if item_name:
            # Sell specific item
            if item_name in inventory:
                quantity = inventory[item_name]
                earned = self.sell_item(item_name, quantity)
                total_gold += earned
                items_sold += quantity
        else:
            # Sell all items (except quest items, consumables)
            for name, quantity in inventory.items():
                if not name:
                    continue
                
                # Skip if it's a quest item or special item
                item_info = self.api.get_item_info(name) or {}
                if item_info and item_info.get('type') in ['consumable', 'key']:
                    continue
                
                earned = self.sell_item(name, quantity)
                if earned > 0:
                    total_gold += earned
                    items_sold += quantity
        
        return {'items_sold': items_sold, 'gold_earned': total_gold}
    
    # ==================== Value Calculations ====================
    
    def get_item_value(self, item_name: str) -> Dict[str, Any]:
        """Get buy and sell prices for an item."""
        if not self.api or not item_name:
            return {}
        
        base_price = self.api.get_item_price(item_name)
        return {
            'name': item_name,
            'base_price': base_price,
            'buy_price': int(base_price * self.BUY_MARKUP),
            'sell_price': int(base_price * self.SELL_MULTIPLIER),
        }
    
    def get_inventory_worth(self) -> Dict[str, Any]:
        """Calculate total value of inventory."""
        if not self.api:
            return {}
        
        inventory = self.api.get_inventory_summary()
        total_value = self.api.get_inventory_value()
        
        breakdown = {}
        for item_name, count in inventory.items():
            if not item_name:
                continue
            base_price = self.api.get_item_price(item_name)
            breakdown[item_name] = {
                'count': count,
                'unit_price': base_price,
                'total': base_price * count,
            }
        
        return {
            'total_value': total_value,
            'item_count': len(inventory),
            'total_items': sum(inventory.values()) if inventory else 0,
            'breakdown': breakdown,
        }
    
    def get_best_items_to_sell(self) -> List[Dict[str, Any]]:
        """Get list of most valuable items to sell."""
        if not self.api:
            return []
        
        inventory = self.api.get_inventory_summary()
        items = []
        
        for item_name, count in inventory.items():
            if not item_name:
                continue
            
            item_info = self.api.get_item_info(item_name) or {}
            if not item_info:
                continue
            
            # Skip non-sellable items
            if item_info.get('type') in ['consumable', 'key']:
                continue
            
            base_price = self.api.get_item_price(item_name)
            sell_price = int(base_price * self.SELL_MULTIPLIER)
            
            items.append({
                'name': item_name,
                'count': count,
                'sell_price': sell_price,
                'total_value': sell_price * count,
            })
        
        # Sort by total value descending
        items.sort(key=lambda x: x.get('total_value', 0), reverse=True)
        return items
    
    # ==================== Transaction History ====================
    
    def _log_transaction(self, trans_type: str, item_name: str, 
                         quantity: int, gold: int):
        """Log a transaction to history."""
        if not self.api or not trans_type or not item_name:
            return
        
        transactions = self.api.retrieve_data('transactions', [])
        transactions.append({
            'type': trans_type,
            'item': item_name,
            'quantity': quantity,
            'gold': gold,
        })
        
        # Keep only last 50 transactions
        if len(transactions) > 50:
            transactions = transactions[-50:]
        
        self.api.store_data('transactions', transactions)
    
    def get_transaction_history(self) -> List[Dict[str, Any]]:
        """Get recent transaction history."""
        if not self.api:
            return []
        return self.api.retrieve_data('transactions', [])
    
    def get_shop_statistics(self) -> Dict[str, Any]:
        """Get shop/trading statistics."""
        if not self.api:
            return {}
        
        spent = self.api.retrieve_data('total_gold_spent', 0)
        earned = self.api.retrieve_data('total_gold_earned', 0)
        
        return {
            'total_gold_spent': spent,
            'total_gold_earned': earned,
            'net_profit': earned - spent,
            'transaction_count': len(self.api.retrieve_data('transactions', [])),
        }
    
    # ==================== Shop Interface ====================
    
    def display_shop_menu(self):
        """Display a formatted shop menu."""
        if not self.api:
            return
        
        player = self.api.get_player() or {}
        if not player:
            return
        
        self.api.log("\n=== Player Shop ===")
        self.api.log(f"Current Gold: {player.get('gold', 0)}")
        
        # Show inventory worth
        worth = self.get_inventory_worth()
        self.api.log(f"Inventory Value: {worth.get('total_value', 0)} gold")
        
        # Show top sellable items
        best_items = self.get_best_items_to_sell()[:5]
        if best_items:
            self.api.log("\nTop Items to Sell:")
            for item in best_items:
                self.api.log(f"  - {item.get('name', 'Unknown')}: {item.get('sell_price', 0)}g x{item.get('count', 0)}")
        
        # Show shop statistics
        stats = self.get_shop_statistics()
        self.api.log(f"\nLifetime Trading:")
        self.api.log(f"  Gold Spent: {stats.get('total_gold_spent', 0)}")
        self.api.log(f"  Gold Earned: {stats.get('total_gold_earned', 0)}")
        self.api.log(f"  Net Profit: {stats.get('net_profit', 0)}")


# Global instance - lazily created
_shop_system = None


def _get_shop_system() -> 'ShopSystem':
    """Get or create the shop system instance."""
    global _shop_system
    if _shop_system is None:
        _shop_system = ShopSystem()
        _shop_system.initialize()
    return _shop_system


def register_hooks():
    """Register hooks for shop-related events."""
    shop = _get_shop_system()
    print("Shop System example loaded!")


# Auto-register when imported
register_hooks()

