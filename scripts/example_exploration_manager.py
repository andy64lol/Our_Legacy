#!/usr/bin/env python3
"""
Example Script: Exploration Manager
Demonstrates area exploration and modification methods.

This script provides exploration enhancements including:
- Getting area connections and enemy lists
- Adding/removing enemies from areas dynamically
- Setting area difficulty
- Creating area exploration reports
- Discovering connected areas
"""

from typing import Optional, Dict, Any, List, Set
from scripting import get_api


class ExplorationManager:
    """Manages area exploration and dynamic world modification."""
    
    def __init__(self):
        self.api = get_api()
        if self.api:
            # Track exploration progress
            self.api.store_data('areas_discovered', [])
            self.api.store_data('exploration_notes', {})
            
            self.api.log("Exploration Manager loaded!")
    
    # ==================== Area Discovery ====================
    
    def discover_current_area(self) -> Dict[str, Any]:
        """Mark current area as discovered and log connections."""
        if not self.api:
            return {}
        
        current_area = self.api.get_current_area()
        if not current_area:
            return {}
        
        # Add to discovered set
        discovered = self.api.retrieve_data('areas_discovered', [])
        discovered_set = set(discovered) if discovered else set()
        discovered_set.add(current_area)
        self.api.store_data('areas_discovered', list(discovered_set))
        
        # Get area info
        area_info = self.api.get_area_info(current_area) or {}
        connections = self.api.get_area_connections(current_area) or []
        
        # Log discovery
        self.api.log(f"Discovered: {area_info.get('name', current_area)}")
        self.api.log(f"   Connections: {', '.join(connections)}")
        
        return {
            'area': current_area,
            'name': area_info.get('name', 'Unknown'),
            'connections': connections,
        }
    
    def get_exploration_progress(self) -> Dict[str, Any]:
        """Get current exploration progress."""
        if not self.api:
            return {}
        
        discovered = self.api.retrieve_data('areas_discovered', [])
        all_areas = self.api.list_all_areas() or []
        
        return {
            'discovered_count': len(discovered),
            'total_areas': len(all_areas),
            'percentage': int(len(discovered) / max(1, len(all_areas)) * 100) if all_areas else 0,
            'discovered_areas': discovered,
        }
    
    def discover_all_connections(self, start_area: Optional[str] = None) -> List[str]:
        """Discover all connected areas recursively."""
        if not self.api:
            return []
        
        if not start_area:
            start_area = self.api.get_current_area()
        
        if not start_area:
            return []
        
        discovered: Set[str] = set()
        to_explore = [start_area]
        
        while to_explore:
            area_id = to_explore.pop()
            if area_id in discovered:
                continue
            
            discovered.add(area_id)
            
            # Get and queue connections
            connections = self.api.get_area_connections(area_id) or []
            for conn_id in connections:
                if conn_id and conn_id not in discovered:
                    to_explore.append(conn_id)
        
        # Store discovered areas
        current_discovered = self.api.retrieve_data('areas_discovered', [])
        all_discovered = set(current_discovered) | discovered
        self.api.store_data('areas_discovered', list(all_discovered))
        
        return list(discovered)
    
    # ==================== Area Information ====================
    
    def get_area_report(self, area_id: Optional[str] = None) -> Dict[str, Any]:
        """Generate a detailed report for an area."""
        if not self.api:
            return {}
        
        if not area_id:
            area_id = self.api.get_current_area()
        
        if not area_id:
            return {'error': 'No area specified'}
        
        all_areas = self.api.list_all_areas() or []
        if area_id not in all_areas:
            return {'error': 'Invalid area'}
        
        area_info = self.api.get_area_info(area_id) or {}
        connections = self.api.get_area_connections(area_id) or []
        enemies = self.api.get_area_enemies(area_id) or []
        
        # Get enemy details
        enemy_details = []
        for enemy_id in enemies:
            if not enemy_id:
                continue
            enemies_data = self.api.get_enemies_data() or {}
            enemy_info = enemies_data.get(enemy_id, {}) if enemies_data else {}
            if enemy_info:
                enemy_details.append({
                    'id': enemy_id,
                    'name': enemy_info.get('name', 'Unknown'),
                    'hp': enemy_info.get('hp', 0),
                    'attack': enemy_info.get('attack', 0),
                    'difficulty': enemy_info.get('hp', 0) / 10,
                })
        
        return {
            'area_id': area_id,
            'name': area_info.get('name', 'Unknown'),
            'description': area_info.get('description', 'No description'),
            'difficulty': area_info.get('difficulty', 1),
            'connections': connections,
            'connection_count': len(connections),
            'enemies': enemies,
            'enemy_count': len(enemies),
            'enemy_details': enemy_details,
            'rest_cost': area_info.get('rest_cost', 0),
            'can_rest': area_info.get('can_rest', False),
        }
    
    def display_area_report(self, area_id: Optional[str] = None):
        """Display a formatted area report."""
        if not self.api:
            return
        
        report = self.get_area_report(area_id)
        if 'error' in report:
            self.api.log(f"Error: {report['error']}")
            return
        
        self.api.log(f"\n=== Area Report: {report.get('name', 'Unknown')} ===")
        self.api.log(f"ID: {report.get('area_id', 'Unknown')}")
        self.api.log(f"Description: {report.get('description', 'No description')}")
        self.api.log(f"Difficulty: {'*' * report.get('difficulty', 1)}")
        if report.get('can_rest', False):
            self.api.log(f"Rest Cost: {report.get('rest_cost', 0)} gold")
        else:
            self.api.log("Cannot Rest Here")
        
        self.api.log(f"\n--- Connections ({report.get('connection_count', 0)}) ---")
        for conn in report.get('connections', []):
            if not conn:
                continue
            conn_info = self.api.get_area_info(conn) or {}
            self.api.log(f"  -> {conn_info.get('name', conn)} ({conn})")
        
        self.api.log(f"\n--- Enemies ({report.get('enemy_count', 0)}) ---")
        for enemy in report.get('enemy_details', []):
            self.api.log(f"  {enemy.get('name', 'Unknown')} (HP: {enemy.get('hp', 0)}, ATK: {enemy.get('attack', 0)})")
    
    # ==================== Dynamic Area Modification ====================
    
    def add_enemy_to_area(self, area_id: str, enemy_id: str) -> bool:
        """Add an enemy to an area's spawn list."""
        if not self.api or not area_id or not enemy_id:
            return False
        
        if hasattr(self.api, 'add_area_enemy') and self.api.add_area_enemy(area_id, enemy_id):
            enemies_data = self.api.get_enemies_data() or {}
            enemy_info = enemies_data.get(enemy_id, {}) if enemies_data else {}
            enemy_name = enemy_info.get('name', enemy_id)
            self.api.log(f"Added {enemy_name} to {area_id}")
            return True
        
        return False
    
    def remove_enemy_from_area(self, area_id: str, enemy_id: str) -> bool:
        """Remove an enemy from an area's spawn list."""
        if not self.api or not area_id or not enemy_id:
            return False
        
        if hasattr(self.api, 'remove_area_enemy') and self.api.remove_area_enemy(area_id, enemy_id):
            self.api.log(f"Removed {enemy_id} from {area_id}")
            return True
        
        return False
    
    def set_area_difficulty(self, area_id: str, difficulty: int) -> bool:
        """Set an area's difficulty level (1-5)."""
        if not self.api or not area_id:
            return False
        
        if 1 <= difficulty <= 5:
            if hasattr(self.api, 'set_area_difficulty') and self.api.set_area_difficulty(area_id, difficulty):
                self.api.log(f"Set {area_id} difficulty to {difficulty}")
                return True
        
        return False
    
    def populate_area_with_elites(self, area_id: str) -> bool:
        """Add elite enemies to an area (enemies scaled to player level)."""
        if not self.api or not area_id:
            return False
        
        player = self.api.get_player() or {}
        if not player:
            return False
        
        level = player.get('level', 1)
        
        # Add elite versions of base enemies
        base_enemies = self.api.get_area_enemies(area_id) or []
        added = 0
        
        for enemy_id in base_enemies:
            if not enemy_id:
                continue
            enemies_data = self.api.get_enemies_data() or {}
            enemy_info = enemies_data.get(enemy_id, {}) if enemies_data else {}
            if enemy_info:
                # Create scaled enemy ID
                elite_id = f"{enemy_id}_elite"
                
                # Check if already added
                current_enemies = self.api.get_area_enemies(area_id) or []
                if elite_id not in current_enemies:
                    if hasattr(self.api, 'add_area_enemy') and self.api.add_area_enemy(area_id, elite_id):
                        added += 1
        
        if added > 0:
            self.api.log(f"Added {added} elite enemies to {area_id}")
        
        return added > 0
    
    def clear_area_enemies(self, area_id: str) -> int:
        """Remove all enemies from an area (dangerous!)."""
        if not self.api or not area_id:
            return 0
        
        enemies = self.api.get_area_enemies(area_id) or []
        removed = 0
        
        for enemy_id in enemies[:]:  # Copy list to iterate safely
            if not enemy_id:
                continue
            if hasattr(self.api, 'remove_area_enemy') and self.api.remove_area_enemy(area_id, enemy_id):
                removed += 1
        
        self.api.log(f"Cleared {removed} enemies from {area_id}")
        return removed
    
    # ==================== World Exploration ====================
    
    def get_shortest_path(self, start: str, end: str) -> List[str]:
        """Find shortest path between two areas using BFS."""
        if not self.api or not start or not end:
            return []
        
        if start == end:
            return [start]
        
        # BFS
        queue = [(start, [start])]
        visited = {start}
        
        while queue:
            area, path = queue.pop(0)
            connections = self.api.get_area_connections(area) or []
            
            for conn in connections:
                if not conn:
                    continue
                if conn == end:
                    return path + [conn]
                
                if conn not in visited:
                    visited.add(conn)
                    queue.append((conn, path + [conn]))
        
        return []  # No path found
    
    def get_world_map(self) -> Dict[str, Dict[str, Any]]:
        """Generate a complete world map."""
        if not self.api:
            return {}
        
        all_areas = self.api.list_all_areas() or []
        world_map: Dict[str, Dict[str, Any]] = {}
        
        for area_id in all_areas:
            if not area_id:
                continue
            area_info = self.api.get_area_info(area_id) or {}
            connections = self.api.get_area_connections(area_id) or []
            
            world_map[area_id] = {
                'name': area_info.get('name', 'Unknown'),
                'difficulty': area_info.get('difficulty', 1),
                'connections': connections,
                'connection_count': len(connections),
                'enemy_count': len(self.api.get_area_enemies(area_id) or []),
            }
        
        return world_map
    
    def display_world_map(self):
        """Display a formatted world map."""
        if not self.api:
            return
        
        world_map = self.get_world_map()
        current_area = self.api.get_current_area() or "Unknown"
        
        self.api.log("\n=== World Map ===")
        self.api.log(f"Current Location: {current_area}")
        self.api.log(f"Total Areas: {len(world_map)}")
        
        # Group by difficulty
        by_difficulty: Dict[int, List[tuple]] = {}
        for area_id, info in world_map.items():
            diff = info.get('difficulty', 1)
            if diff not in by_difficulty:
                by_difficulty[diff] = []
            by_difficulty[diff].append((area_id, info))
        
        for diff in sorted(by_difficulty.keys()):
            self.api.log(f"\n--- Difficulty {diff} ({len(by_difficulty[diff])}) ---")
            for area_id, info in by_difficulty[diff]:
                marker = "[HERE]" if area_id == current_area else "      "
                connections = info.get('connection_count', 0)
                self.api.log(f"{marker} {info.get('name', 'Unknown')} ({connections} connections)")
    
    def add_exploration_note(self, area_id: str, note: str):
        """Add a note about an area."""
        if not self.api or not area_id or not note:
            return
        
        notes = self.api.retrieve_data('exploration_notes', {}) or {}
        notes[area_id] = note
        self.api.store_data('exploration_notes', notes)
        self.api.log(f"Note added for {area_id}")
    
    def get_exploration_note(self, area_id: str) -> str:
        """Get note for an area."""
        if not self.api or not area_id:
            return ""
        notes = self.api.retrieve_data('exploration_notes', {}) or {}
        return notes.get(area_id, "")


# Initialize exploration manager
exploration_manager = ExplorationManager()


def register_hooks():
    """Register hooks for exploration events."""
    api = get_api()
    if api:
        api.register_hook('on_area_entered', exploration_manager.discover_current_area)
        api.log("Exploration Manager example loaded!")


register_hooks()