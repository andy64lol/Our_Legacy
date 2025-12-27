#!/usr/bin/env python3
"""
Our Legacy - Text-Based CLI Fantasy RPG Game
A comprehensive exploration and grinding-driven RPG experience
"""

import json
import os
import random
import sys
import time
from datetime import datetime
from typing import Dict, List, Any, Optional

class Colors:
    """ANSI color codes for terminal output"""
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'
    GOLD = '\033[93m'

def clear_screen():
    """Clear the terminal screen in a cross-platform way."""
    if os.name == 'nt':
        os.system('cls')
    else:
        os.system('clear')

def ask(prompt: str) -> str:
    """Prompt the user for input, then clear the screen after Enter is pressed.

    Returns the stripped input string.
    """
    try:
        response = input(prompt)
    except EOFError:
        response = ''
    clear_screen()
    return response.strip()

class Character:
    """Player character class"""
    
    def __init__(self, name: str, character_class: str, classes_data: Optional[Dict] = None):
        self.name = name
        self.character_class = character_class
        self.level = 1
        self.experience = 0
        self.experience_to_next = 100
        self.class_data = {}
        self.level_up_bonuses = {}
        
        # Load class data if provided
        if classes_data and character_class in classes_data:
            self.class_data = classes_data[character_class]
            stats = self.class_data.get("base_stats", {})
            self.level_up_bonuses = self.class_data.get("level_up_bonuses", {})
        else:
            # Fallback defaults
            default_stats = {"hp": 100, "mp": 50, "attack": 10, "defense": 8, "speed": 10}
            stats = default_stats
        
        self.max_hp = stats.get("hp", 100)
        self.hp = self.max_hp
        self.max_mp = stats.get("mp", 50)
        self.mp = self.max_mp
        self.attack = stats.get("attack", 10)
        self.defense = stats.get("defense", 8)
        self.speed = stats.get("speed", 10)
        
        # Equipment slots (legacy compatibility)
        self.weapon = None
        self.armor = None
        self.accessory = None
        
        # Inventory and gold
        self.inventory = []
        self.gold = 100  # Starting gold
        # Save base stats so equipment bonuses can be recalculated
        self.base_max_hp = self.max_hp
        self.base_max_mp = self.max_mp
        self.base_attack = self.attack
        self.base_defense = self.defense
        self.base_speed = self.speed

        # Equipped items are stored by slot name
        self.equipment: Dict[str, Optional[str]] = {"weapon": None, "armor": None, "accessory": None}
        
        # Battle state
        self.defending = False
        
        # Sync legacy equipment slots with new system for compatibility
        self._sync_equipment_slots()
    
    def _sync_equipment_slots(self):
        """Sync legacy equipment slots with new equipment dictionary for compatibility"""
        # This ensures backward compatibility with any code that might use the old slots
        self.weapon = self.equipment.get("weapon")
        self.armor = self.equipment.get("armor")
        self.accessory = self.equipment.get("accessory")
    
    def _update_equipment_slots(self):
        """Update legacy equipment slots when equipment dictionary changes"""
        self.weapon = self.equipment.get("weapon")
        self.armor = self.equipment.get("armor")
        self.accessory = self.equipment.get("accessory")
        
    def is_alive(self) -> bool:
        """Check if character is alive"""
        return self.hp > 0
    
    def take_damage(self, damage: int) -> int:
        """Apply damage to character, return actual damage taken"""
        actual_damage = max(1, damage - self.defense)
        self.hp = max(0, self.hp - actual_damage)
        return actual_damage
    
    def heal(self, amount: int):
        """Heal character"""
        self.hp = min(self.max_hp, self.hp + amount)
    
    def gain_experience(self, exp: int):
        """Gain experience and level up if needed"""
        self.experience += exp
        while self.experience >= self.experience_to_next:
            self.level_up()
    
    def level_up(self):
        """Level up the character"""
        self.level += 1
        self.experience -= self.experience_to_next
        self.experience_to_next = int(self.experience_to_next * 1.5)
        
        # Apply stat increases from class data
        if self.level_up_bonuses:
            self.max_hp += self.level_up_bonuses.get("hp", 0)
            self.max_mp += self.level_up_bonuses.get("mp", 0)
            self.attack += self.level_up_bonuses.get("attack", 0)
            self.defense += self.level_up_bonuses.get("defense", 0)
            self.speed += self.level_up_bonuses.get("speed", 0)
            self.hp = self.max_hp
            self.mp = self.max_mp
            
        print(f"{Colors.GREEN}{Colors.BOLD}Level Up!{Colors.END} You are now level {self.level}!")
    
    def display_stats(self):
        """Display character statistics"""
        print(f"\n{Colors.CYAN}{Colors.BOLD}=== {self.name} - Level {self.level} {self.character_class} ==={Colors.END}")
        print(f"HP: {Colors.RED}{self.hp}/{self.max_hp}{Colors.END}")
        print(f"MP: {Colors.BLUE}{self.mp}/{self.max_mp}{Colors.END}")
        print(f"Attack: {Colors.YELLOW}{self.attack}{Colors.END}")
        print(f"Defense: {Colors.YELLOW}{self.defense}{Colors.END}")
        print(f"Speed: {Colors.YELLOW}{self.speed}{Colors.END}")
        print(f"Experience: {Colors.MAGENTA}{self.experience}/{self.experience_to_next}{Colors.END}")
        print(f"Gold: {Colors.GOLD}{self.gold}{Colors.END}")
        # Equipped items
        print(f"{Colors.CYAN}Equipped:{Colors.END}")
        print(f"  Weapon: {self.equipment.get('weapon', 'None')}")
        print(f"  Armor: {self.equipment.get('armor', 'None')}")
        print(f"  Accessory: {self.equipment.get('accessory', 'None')}")

    def update_stats_from_equipment(self, items_data: Dict[str, Any]):
        """Recalculate stats from base stats plus any equipped item bonuses."""
        # Start from base
        self.max_hp = self.base_max_hp
        self.max_mp = self.base_max_mp
        self.attack = self.base_attack
        self.defense = self.base_defense
        self.speed = self.base_speed

        # Apply bonuses from each equipped item
        for slot in ("weapon", "armor", "accessory"):
            item_name = self.equipment.get(slot)
            if not item_name:
                continue
            item = items_data.get(item_name, {})
            # Common bonus keys
            if item.get("attack_bonus"):
                self.attack += item.get("attack_bonus", 0)
            if item.get("defense_bonus"):
                self.defense += item.get("defense_bonus", 0)
            if item.get("speed_bonus"):
                self.speed += item.get("speed_bonus", 0)
            if item.get("mp_bonus"):
                self.max_mp += item.get("mp_bonus", 0)
            if item.get("defense_penalty"):
                self.defense -= item.get("defense_penalty", 0)
            if item.get("speed_penalty"):
                self.speed -= item.get("speed_penalty", 0)
            if item.get("attack_penalty"):
                self.attack -= item.get("attack_penalty", 0)
            if item.get("hp_bonus"):
                self.max_hp += item.get("hp_bonus", 0)

        # Clamp current HP/MP to new maxima
        self.hp = min(self.hp, self.max_hp)
        self.mp = min(self.mp, self.max_mp)

    def equip(self, item_name: str, items_data: Dict[str, Any]) -> bool:
        """Attempt to equip `item_name`. Returns True if equipped."""
        item = items_data.get(item_name)
        if not item:
            return False
        slot = item.get("type")
        if slot not in ("weapon", "armor", "accessory"):
            return False

        # Check requirements (simple level/class checks)
        reqs = item.get("requirements", {})
        if reqs.get("level") and self.level < reqs.get("level", 0):
            return False
        if reqs.get("class") and reqs.get("class") != self.character_class:
            return False

        # Equip into slot (replace existing)
        self.equipment[slot] = item_name
        self._update_equipment_slots()  # NEW: Sync legacy slots
        self.update_stats_from_equipment(items_data)
        return True

    def unequip(self, slot: str, items_data: Dict[str, Any]) -> Optional[str]:
        """Unequip an item from `slot`. Returns the item name if removed."""
        if slot not in ("weapon", "armor", "accessory"):
            return None
        prev = self.equipment.get(slot)
        self.equipment[slot] = None
        self._update_equipment_slots()  # NEW: Sync legacy slots
        self.update_stats_from_equipment(items_data)
        return prev

class Enemy:
    """Enemy class"""
    
    def __init__(self, enemy_data: Dict):
        self.name = enemy_data["name"]
        self.max_hp = enemy_data["hp"]
        self.hp = enemy_data["hp"]
        self.attack = enemy_data["attack"]
        self.defense = enemy_data["defense"]
        self.speed = enemy_data["speed"]
        self.experience_reward = enemy_data["experience_reward"]
        self.gold_reward = enemy_data["gold_reward"]
        self.loot_table = enemy_data.get("loot_table", [])
        
    def is_alive(self) -> bool:
        """Check if enemy is alive"""
        return self.hp > 0
    
    def take_damage(self, damage: int) -> int:
        """Apply damage to enemy, return actual damage taken"""
        actual_damage = max(1, damage - self.defense)
        self.hp = max(0, self.hp - actual_damage)
        return actual_damage

class Game:
    """Main game class"""
    
    def __init__(self):
        self.player: Optional[Character] = None
        self.current_area = "starting_village"
        self.enemies_data: Dict[str, Any] = {}
        self.areas_data: Dict[str, Any] = {}
        self.items_data: Dict[str, Any] = {}
        self.missions_data: Dict[str, Any] = {}
        self.bosses_data: Dict[str, Any] = {}
        self.classes_data: Dict[str, Any] = {}
        self.spells_data: Dict[str, Any] = {}
        self.effects_data: Dict[str, Any] = {}
        self.mission_progress: Dict[str, Dict] = {}  # mission_id -> {current_count, target_count, completed, type}
        self.completed_missions: List[str] = []
        
        # Load game data
        self.load_game_data()
    
    def load_game_data(self):
        """Load all game data from JSON files"""
        try:
            with open('data/enemies.json', 'r') as f:
                self.enemies_data = json.load(f)
            with open('data/areas.json', 'r') as f:
                self.areas_data = json.load(f)
            with open('data/items.json', 'r') as f:
                self.items_data = json.load(f)
            with open('data/missions.json', 'r') as f:
                self.missions_data = json.load(f)
            with open('data/bosses.json', 'r') as f:
                self.bosses_data = json.load(f)
            with open('data/classes.json', 'r') as f:
                self.classes_data = json.load(f)
            with open('data/spells.json', 'r') as f:
                self.spells_data = json.load(f)
            with open('data/effects.json', 'r') as f:
                self.effects_data = json.load(f)
        except FileNotFoundError as e:
            print(f"Error loading game data: {e}")
            print("Please ensure all data files exist in the data/ directory.")
            sys.exit(1)
    
    def display_welcome(self) -> str:
        """Display welcome screen"""
        print(f"{Colors.CYAN}{Colors.BOLD}")
        print("=" * 60)
        print("             OUR LEGACY")
        print("       Text-Based CLI Fantasy RPG")
        print("=" * 60)
        print(f"{Colors.END}")
        print("Welcome, adventurer! Your legacy awaits...")
        print("Choose your path wisely, for every decision shapes your destiny.")
        print()
        
        print(f"{Colors.BOLD}=== MAIN MENU ==={Colors.END}")
        print("1. New Game")
        print("2. Load Game")
        print("3. Quit")
        
        while True:
            choice = ask("Choose an option (1-3): ")
            if choice == "1":
                return "new_game"
            elif choice == "2":
                return "load_game"
            elif choice == "3":
                print("Thank you for playing Our Legacy!")
                clear_screen()
                sys.exit(0)
            else:
                print("Invalid choice. Please enter 1, 2, or 3.")
    
    def display_available_classes(self):
        """Display all available character classes from classes.json"""
        print("\nChoose your class:")
        
        color_map = [
            Colors.RED, Colors.BLUE, Colors.GREEN, 
            Colors.YELLOW, Colors.MAGENTA, Colors.CYAN,
            Colors.WHITE, Colors.GOLD
        ]
        
        for i, (class_name, class_data) in enumerate(self.classes_data.items(), 1):
            color = color_map[(i-1) % len(color_map)]
            description = class_data.get("description", "No description available")
            print(f"{color}{i}. {class_name}{Colors.END} - {description}")
    
    def select_class(self) -> str:
        """Allow user to select a class from available options"""
        class_names = list(self.classes_data.keys())
        
        while True:
            choice = ask(f"Enter class choice (1-{len(class_names)}): ")
            if choice.isdigit():
                choice_idx = int(choice) - 1
                if 0 <= choice_idx < len(class_names):
                    return class_names[choice_idx]
                else:
                    print(f"Invalid choice. Please enter a number between 1 and {len(class_names)}.")
            else:
                print("Invalid input. Please enter a number.")

    def create_character(self):
        """Create a new character"""
        print(f"{Colors.BOLD}Character Creation{Colors.END}")
        print("-" * 30)
        
        name = ask("Enter your character's name: ")
        if not name:
            name = "Hero"
        
        # Use dynamic class selection instead of hardcoded options
        self.display_available_classes()
        
        character_class = self.select_class()
        
        self.player = Character(name, character_class, self.classes_data)
        print(f"\n{Colors.GREEN}Welcome, {name} the {character_class}!{Colors.END}")
        
        # Give starting items based on class data
        self.give_starting_items(character_class)
        
        if self.player:
            self.player.display_stats()
    
    def give_starting_items(self, character_class: str):
        """Grant starting items based on character class from classes.json"""
        if not self.player or character_class not in self.classes_data:
            return
        
        class_info = self.classes_data[character_class]
        items = class_info.get("starting_items", [])
        starting_gold = class_info.get("starting_gold", 100)
        
        for item in items:
            self.player.inventory.append(item)
        
        self.player.gold = starting_gold
        
        if items:
            print(f"{Colors.YELLOW}You received starting equipment:{Colors.END}")
            for item in items:
                print(f"  - {item}")
        
        # Auto-equip first weapon and armor if available
        for slot in ("weapon", "armor"):
            for item in items:
                item_type = self.items_data.get(item, {}).get("type")
                if item_type == slot:
                    self.player.equip(item, self.items_data)
                    print(f"{Colors.GREEN}Equipped: {item}{Colors.END}")
                    break
    
    def main_menu(self):
        """Display main menu"""
        print(f"\n{Colors.BOLD}=== MAIN MENU ==={Colors.END}")
        print("1. Explore")
        print("2. View Character")
        print("3. Travel")
        print("4. Inventory")
        print("5. Missions")
        print("6. Shop")
        print("7. Rest")
        print("8. Save Game")
        print("9. Load Game")
        print("10. Claim Rewards")
        print("11. Quit")

        choice = ask("Choose an option (1-11): ")
        
        if choice == "1":
            self.explore()
        elif choice == "2":
            if self.player:
                self.player.display_stats()
            else:
                print("No character created yet.")
        elif choice == "3":
            self.travel()
        elif choice == "4":
            self.view_inventory()
        elif choice == "5":
            self.view_missions()
        elif choice == "6":
            self.visit_shop()
        elif choice == "7":
            self.rest()
        elif choice == "8":
            self.save_game()
        elif choice == "9":
            self.load_game()
        elif choice == "10":
            self.claim_rewards()  # Fixed: was calling quit_game()
        elif choice == "11":
            self.quit_game()
        else:
            print("Invalid choice. Please try again.")
    
    def explore(self):
        """Explore the current area"""
        if not self.player:
            print("No character created yet. Please create a character first.")
            return
            
        area_data = self.areas_data.get(self.current_area, {})
        area_name = area_data.get("name", "Unknown Area")
        
        print(f"\n{Colors.CYAN}Exploring {area_name}...{Colors.END}")
        
        # Random encounter chance
        if random.random() < 0.7:  # 70% chance of encounter
            self.random_encounter()
        else:
            print("You explore the area but find nothing of interest.")
            
            # Small chance to find gold
            if random.random() < 0.3:  # 30% chance to find gold
                found_gold = random.randint(5, 20)
                self.player.gold += found_gold
                print(f"{Colors.GOLD}You found {found_gold} gold!{Colors.END}")
    
    def random_encounter(self):
        """Handle random encounter"""
        if not self.player:
            return
            
        area_data = self.areas_data.get(self.current_area, {})
        possible_enemies = area_data.get("possible_enemies", [])
        
        if not possible_enemies:
            print("No enemies found in this area.")
            return
        
        enemy_name = random.choice(possible_enemies)
        enemy_data = self.enemies_data.get(enemy_name)
        
        if enemy_data:
            enemy = Enemy(enemy_data)
            print(f"\n{Colors.RED}A wild {enemy.name} appears!{Colors.END}")
            self.battle(enemy)
    
    def battle(self, enemy: Enemy):
        """Handle turn-based battle"""
        if not self.player:
            return
            
        print(f"\n{Colors.BOLD}=== BATTLE ==={Colors.END}")
        print(f"VS {enemy.name}")
        
        # Determine who goes first
        player_first = self.player.speed >= enemy.speed
        
        while self.player.is_alive() and enemy.is_alive():
            if player_first:
                if not self.player_turn(enemy):
                    break
                if enemy.is_alive():
                    self.enemy_turn(enemy)
            else:
                self.enemy_turn(enemy)
                if self.player.is_alive():
                    if not self.player_turn(enemy):
                        break
            
            # Display current HP
            print(f"\n{Colors.RED}{self.player.name}: {self.player.hp}/{self.player.max_hp} HP{Colors.END}")
            print(f"{Colors.RED}{enemy.name}: {enemy.hp}/{enemy.max_hp} HP{Colors.END}")
        
        # Battle outcome
        if self.player.is_alive():
            print(f"\n{Colors.GREEN}You defeated the {enemy.name}!{Colors.END}")
            
            # Rewards
            exp_reward = enemy.experience_reward
            gold_reward = enemy.gold_reward
            
            print(f"Gained {Colors.MAGENTA}{exp_reward} experience{Colors.END}")
            print(f"Gained {Colors.GOLD}{gold_reward} gold{Colors.END}")
            
            self.player.gain_experience(exp_reward)
            self.player.gold += gold_reward
            
            # Update mission progress for kill
            self.update_mission_progress('kill', enemy.name)
            
            # Loot drop
            if enemy.loot_table and random.random() < 0.5:  # 50% chance for loot
                loot = random.choice(enemy.loot_table)
                self.player.inventory.append(loot)
                print(f"{Colors.YELLOW}Loot acquired: {loot}!{Colors.END}")
                # Update mission progress for collection
                self.update_mission_progress('collect', loot)
        else:
            print(f"\n{Colors.RED}You were defeated by the {enemy.name}...{Colors.END}")
            # Respawn penalty
            self.player.hp = self.player.max_hp // 2
            self.player.mp = self.player.max_mp // 2
            print("You respawn at the starting village.")
            self.current_area = "starting_village"
    
    def player_turn(self, enemy: Enemy) -> bool:
        """Player's turn in battle. Returns False if player fled."""
        if not self.player:
            return True
            
        print(f"\n{Colors.BOLD}Your turn!{Colors.END}")
        print("1. Attack")
        print("2. Use Item")
        print("3. Defend")
        print("4. Flee")
        # Can only cast spells if weapon is magic-capable
        weapon_name: Optional[str] = self.player.equipment.get('weapon')
        weapon_data = self.items_data.get(weapon_name, {}) if weapon_name else {}
        can_cast = bool(weapon_data.get('magic_weapon'))
        if can_cast:
            print("5. Cast Spell")
        
        choice = ask("Choose action (1-5): " if can_cast else "Choose action (1-4): ")
        
        if choice == "1":
            damage = self.player.attack
            actual_damage = enemy.take_damage(damage)
            print(f"You attack for {actual_damage} damage!")
        elif choice == "2":
            self.use_item_in_battle()
        elif choice == "5" and can_cast:
            self.cast_spell(enemy, weapon_name)
        elif choice == "3":
            print("You defend, reducing incoming damage by half!")
            self.player.defending = True
        elif choice == "4":
            flee_chance = 0.7 if self.player.speed > enemy.speed else 0.4
            if random.random() < flee_chance:
                print("You successfully fled from battle!")
                return False
            else:
                print("Failed to flee!")
                return True
        else:
            print("Invalid choice. You lose your turn!")
        
        return True
    
    def enemy_turn(self, enemy: Enemy):
        """Enemy's turn in battle"""
        if not self.player:
            return
            
        damage = enemy.attack
        if self.player.defending:
            damage = damage // 2
            self.player.defending = False
        
        actual_damage = self.player.take_damage(damage)
        print(f"{enemy.name} attacks for {actual_damage} damage!")
    
    def use_item_in_battle(self):
        """Use item during battle"""
        if not self.player:
            return
            
        consumables = [item for item in self.player.inventory if item in self.items_data and 
                      self.items_data[item].get("type") == "consumable"]
        
        if not consumables:
            print("No consumable items available!")
            return
        
        print("Available consumables:")
        for i, item in enumerate(consumables, 1):
            item_data = self.items_data[item]
            print(f"{i}. {item} - {item_data.get('description', 'Unknown effect')}")
        
        try:
            choice = int(ask("Choose item (1-{}): ".format(len(consumables)))) - 1
            if 0 <= choice < len(consumables):
                item = consumables[choice]
                self.use_item(item)
                self.player.inventory.remove(item)
            else:
                print("Invalid choice!")
        except ValueError:
            print("Invalid input!")

    def cast_spell(self, enemy: Enemy, weapon_name: Optional[str] = None):
        """Cast a spell from the player's equipped magic weapon."""
        if not self.player:
            return
            
        # Handle case where no weapon is equipped
        if not weapon_name:
            print("You need to equip a magic weapon to cast spells.")
            return
            
        # Gather spells allowed by the equipped weapon
        available = []
        for sname, sdata in self.spells_data.items():
            allowed = sdata.get('allowed_weapons', [])
            if weapon_name in allowed:
                available.append((sname, sdata))

        if not available:
            print("No spells available for your weapon.")
            return

        print("Available spells:")
        for i, (sname, sdata) in enumerate(available, 1):
            print(f"{i}. {sname} - MP {sdata.get('mp_cost', 0)} - {sdata.get('description', '')}")

        choice = ask(f"Choose spell (1-{len(available)}) or press Enter to cancel: ")
        if not choice or not choice.isdigit():
            return
        idx = int(choice) - 1
        if not (0 <= idx < len(available)):
            print("Invalid selection.")
            return

        sname, sdata = available[idx]
        cost = sdata.get('mp_cost', 0)
        if self.player.mp < cost:
            print("Not enough MP to cast that spell.")
            return

        # Pay cost
        self.player.mp -= cost

        if sdata.get('type') == 'damage':
            power = sdata.get('power', 0)
            damage = power + (self.player.attack // 2)
            actual = enemy.take_damage(damage)
            print(f"You cast {sname} for {actual} damage!")
            
            # Apply effects if any
            effects = sdata.get('effects', [])
            for effect_name in effects:
                effect_data = self.effects_data.get(effect_name, {})
                effect_type = effect_data.get('type', '')
                
                if effect_type == 'damage_over_time':
                    print(f"{Colors.RED}{enemy.name} is afflicted with {effect_name}!{Colors.END}")
                elif effect_type == 'stun':
                    if random.random() < effect_data.get('chance', 0.5):
                        print(f"{Colors.YELLOW}{enemy.name} is stunned!{Colors.END}")
                elif effect_type == 'mixed_effect':
                    if random.random() < effect_data.get('chance', 0.5):
                        print(f"{Colors.CYAN}{enemy.name} is frozen!{Colors.END}")
                        
        elif sdata.get('type') == 'heal':
            heal_amount = sdata.get('power', 0)
            old_hp = self.player.hp
            self.player.heal(heal_amount)
            print(f"You cast {sname} and healed {self.player.hp - old_hp} HP!")
            
            # Apply healing effects if any
            effects = sdata.get('effects', [])
            for effect_name in effects:
                effect_data = self.effects_data.get(effect_name, {})
                if effect_data.get('type') == 'healing_over_time':
                    print(f"{Colors.GREEN}You are affected by regeneration!{Colors.END}")
                    
        elif sdata.get('type') == 'buff':
            power = sdata.get('power', 0)
            effects = sdata.get('effects', [])
            
            for effect_name in effects:
                effect_data = self.effects_data.get(effect_name, {})
                effect_type = effect_data.get('type', '')
                
                if effect_type == 'stat_boost':
                    if 'defense_bonus' in effect_data:
                        self.player.defense += effect_data['defense_bonus']
                        print(f"{Colors.GREEN}Your defense increases by {effect_data['defense_bonus']}!{Colors.END}")
                    elif 'speed_bonus' in effect_data:
                        self.player.speed += effect_data['speed_bonus']
                        print(f"{Colors.GREEN}Your speed increases by {effect_data['speed_bonus']}!{Colors.END}")
                    elif 'attack_bonus' in effect_data:
                        self.player.attack += effect_data['attack_bonus']
                        print(f"{Colors.GREEN}Your attack increases by {effect_data['attack_bonus']}!{Colors.END}")
                        
                elif effect_type == 'damage_absorb':
                    print(f"{Colors.BLUE}You create a magical shield!{Colors.END}")
                    
                elif effect_type == 'reconnaissance':
                    print(f"{Colors.CYAN}You can see enemy weaknesses!{Colors.END}")
                    
        elif sdata.get('type') == 'debuff':
            power = sdata.get('power', 0)
            effects = sdata.get('effects', [])
            
            for effect_name in effects:
                effect_data = self.effects_data.get(effect_name, {})
                effect_type = effect_data.get('type', '')
                
                if effect_type == 'action_block':
                    if random.random() < effect_data.get('chance', 0.5):
                        print(f"{Colors.YELLOW}{enemy.name} is stunned and cannot act!{Colors.END}")
                        
                elif effect_type == 'accuracy_reduction':
                    print(f"{Colors.RED}{enemy.name}'s accuracy is reduced!{Colors.END}")
                    
                elif effect_type == 'speed_reduction':
                    print(f"{Colors.YELLOW}{enemy.name} is slowed!{Colors.END}")
                    
                elif effect_type == 'stat_reduction':
                    print(f"{Colors.RED}{enemy.name}'s stats are cursed!{Colors.END}")
                    
        else:
            print(f"Unknown spell type: {sdata.get('type')}")
            # Refund MP for unknown spell types
            self.player.mp += cost
    
    def use_item(self, item: str):
        """Use an item"""
        if not self.player:
            return
            
        item_data = self.items_data.get(item, {})
        item_type = item_data.get("type")
        
        if item_type == "consumable":
            if item_data.get("effect") == "heal":
                heal_amount = item_data.get("value", 0)
                old_hp = self.player.hp
                self.player.heal(heal_amount)
                print(f"Used {item}, healed {self.player.hp - old_hp} HP!")
            elif item_data.get("effect") == "mp_restore":
                mp_amount = item_data.get("value", 0)
                old_mp = self.player.mp
                self.player.mp = min(self.player.max_mp, self.player.mp + mp_amount)
                print(f"Used {item}, restored {self.player.mp - old_mp} MP!")
    
    def view_inventory(self):
        """View character inventory"""
        if not self.player:
            print("No character created yet.")
            return
            
        print(f"\n{Colors.BOLD}=== INVENTORY ==={Colors.END}")
        print(f"Gold: {Colors.GOLD}{self.player.gold}{Colors.END}")
        
        if not self.player.inventory:
            print("Your inventory is empty.")
            return
        
        # Group items by type
        items_by_type = {}
        for item in self.player.inventory:
            item_type = self.items_data.get(item, {}).get("type", "unknown")
            if item_type not in items_by_type:
                items_by_type[item_type] = []
            items_by_type[item_type].append(item)
        
        for item_type, items in items_by_type.items():
            print(f"\n{Colors.CYAN}{item_type.title()}:{Colors.END}")
            for item in items:
                item_data = self.items_data.get(item, {})
                print(f"  - {item}")
                if item_data.get("description"):
                    print(f"    {item_data['description']}")

        # Offer equip/unequip options for equipment items
        equipable = [it for it in self.player.inventory if self.items_data.get(it, {}).get('type') in ('weapon', 'armor', 'accessory')]
        if equipable:
            print("\nEquipment options:")
            print("  E. Equip an item from inventory")
            print("  U. Unequip a slot")
            choice = ask("Choose option (E/U) or press Enter to return: ")
            if choice.lower() == 'e':
                print("\nEquipable items:")
                for i, item in enumerate(equipable, 1):
                    print(f"{i}. {item} - {self.items_data.get(item, {}).get('description','')}")
                sel = ask(f"Choose item to equip (1-{len(equipable)}) or press Enter: ")
                if sel and sel.isdigit():
                    idx = int(sel) - 1
                    if 0 <= idx < len(equipable):
                        item_name = equipable[idx]
                        ok = self.player.equip(item_name, self.items_data)
                        if ok:
                            print(f"Equipped {item_name}.")
                        else:
                            print(f"Cannot equip {item_name} (requirements not met).")
            elif choice.lower() == 'u':
                print("\nCurrently equipped:")
                for slot in ('weapon', 'armor', 'accessory'):
                    print(f"{slot.title()}: {self.player.equipment.get(slot, 'None')}")
                slot_choice = ask("Enter slot to unequip (weapon/armor/accessory) or press Enter: ")
                if slot_choice in ('weapon', 'armor', 'accessory'):
                    removed = self.player.unequip(slot_choice, self.items_data)
                    if removed:
                        print(f"Unequipped {removed} from {slot_choice}.")
                    else:
                        print("Nothing to unequip from that slot.")
    
    def view_missions(self):
        """View available and active missions with pagination"""
        page = 0
        per_page = 10
        
        while True:
            clear_screen()
            print(f"\n{Colors.BOLD}=== MISSIONS ==={Colors.END}")
            
            # Active Missions
            active_missions = [mid for mid in self.mission_progress.keys() if not self.mission_progress[mid].get('completed', False)]
            print(f"\n{Colors.CYAN}Active Missions:{Colors.END}")
            if not active_missions:
                print("No active missions.")
            else:
                for mid in active_missions:
                    mission = self.missions_data.get(mid, {})
                    progress = self.mission_progress[mid]
                    if progress['type'] == 'kill':
                        print(f"- {mission.get('name')}: {progress['current_count']}/{progress['target_count']} killed")
                    elif progress['type'] == 'collect':
                        if 'current_counts' in progress:
                            counts = [f"{item}: {c}/{progress['target_counts'][item]}" for item, c in progress['current_counts'].items()]
                            print(f"- {mission.get('name')}: {', '.join(counts)}")
                        else:
                            print(f"- {mission.get('name')}: {progress['current_count']}/{progress['target_count']} collected")

            # Available Missions (those not accepted and not completed)
            available_missions = [mid for mid in self.missions_data.keys() 
                                if mid not in self.mission_progress and mid not in self.completed_missions]
            
            total_pages = (len(available_missions) + per_page - 1) // per_page
            if total_pages == 0: total_pages = 1
            
            start_idx = page * per_page
            end_idx = start_idx + per_page
            current_page_missions = available_missions[start_idx:end_idx]
            
            print(f"\n{Colors.GREEN}Available Missions (Page {page + 1}/{total_pages}):{Colors.END}")
            for i, mission_id in enumerate(current_page_missions, 1):
                mission = self.missions_data.get(mission_id, {})
                print(f"{i}. {mission.get('name', 'Unknown')} - {mission.get('description', 'No description')}")
            
            print(f"\n{Colors.YELLOW}Options:{Colors.END}")
            if total_pages > 1:
                if page > 0: print("P. Previous Page")
                if page < total_pages - 1: print("N. Next Page")
            
            if current_page_missions:
                print(f"1-{len(current_page_missions)}. Accept Mission")
            print("B. Back to Menu")
            
            choice = ask("\nChoose an option: ").upper()
            
            if choice == 'B' or not choice:
                break
            elif choice == 'N' and page < total_pages - 1:
                page += 1
            elif choice == 'P' and page > 0:
                page -= 1
            elif choice.isdigit():
                idx = int(choice) - 1
                if 0 <= idx < len(current_page_missions):
                    mission_id = current_page_missions[idx]
                    self.accept_mission(mission_id)
                else:
                    print("Invalid mission number.")
                    time.sleep(1)
    
    def accept_mission(self, mission_id: str):
        """Accept a mission"""
        if mission_id not in self.mission_progress:
            mission = self.missions_data.get(mission_id, {})
            
            # Initialize progress tracking for this mission
            if mission:
                mission_type = mission.get('type', 'kill')
                target_count = mission.get('target_count', 1)
                
                if mission_type == 'collect' and isinstance(target_count, dict):
                    # For collect missions with multiple items
                    self.mission_progress[mission_id] = {
                        'current_counts': {item: 0 for item in target_count.keys()},
                        'target_counts': target_count,
                        'completed': False,
                        'type': mission_type
                    }
                else:
                    # For kill missions or single item collect missions
                    self.mission_progress[mission_id] = {
                        'current_count': 0,
                        'target_count': target_count,
                        'completed': False,
                        'type': mission_type
                    }
                
                print(f"Mission accepted: {mission.get('name', 'Unknown')}")
                time.sleep(1)
            else:
                print("Error: Mission data not found.")
                time.sleep(1)
        else:
            print("Mission already accepted!")
            time.sleep(1)

    def update_mission_progress(self, update_type: str, target: str, count: int = 1):
        """Update mission progress for a specific target"""
        for mid, progress in self.mission_progress.items():
            if progress.get('completed', False):
                continue
                
            mission = self.missions_data.get(mid, {})
            
            if progress['type'] == 'kill' and update_type == 'kill':
                target_enemy = mission.get('target', '').lower()
                if target_enemy == target.lower():
                    progress['current_count'] += count
                    print(f"{Colors.CYAN}[Mission Progress] {mission.get('name')}: {progress['current_count']}/{progress['target_count']}{Colors.END}")
                    
                    if progress['current_count'] >= progress['target_count']:
                        self.complete_mission(mid)
                        
            elif progress['type'] == 'collect' and update_type == 'collect':
                # Handle collection missions
                if 'current_counts' in progress:
                    # Multi-item collection
                    if target in progress['current_counts']:
                        progress['current_counts'][target] += count
                        print(f"{Colors.CYAN}[Mission Progress] {mission.get('name')} - {target}: {progress['current_counts'][target]}/{progress['target_counts'][target]}{Colors.END}")
                        
                        # Check if all items are collected
                        all_collected = all(progress['current_counts'][item] >= progress['target_counts'][item] for item in progress['target_counts'])
                        if all_collected:
                            self.complete_mission(mid)
                else:
                    # Single item collection
                    target_item = mission.get('target', '')
                    if target_item == target:
                        progress['current_count'] += count
                        print(f"{Colors.CYAN}[Mission Progress] {mission.get('name')}: {progress['current_count']}/{progress['target_count']}{Colors.END}")
                        
                        if progress['current_count'] >= progress['target_count']:
                            self.complete_mission(mid)

    def complete_mission(self, mission_id: str):
        """Mark a mission as completed and notify player"""
        if mission_id in self.mission_progress:
            self.mission_progress[mission_id]['completed'] = True
            mission = self.missions_data.get(mission_id, {})
            print(f"\n{Colors.GOLD}{Colors.BOLD}!!! MISSION COMPLETE: {mission.get('name')} !!!{Colors.END}")
            print(f"{Colors.YELLOW}You can now claim your rewards from the menu.{Colors.END}")
            time.sleep(2)

    def claim_rewards(self):
        """Claim rewards for completed missions"""
        if not self.player:
            print("No character created yet.")
            return

        completed_missions = [mid for mid, progress in self.mission_progress.items() if progress.get('completed', False)]
        if not completed_missions:
            print("No completed missions to claim rewards for.")
            return

        print(f"\n{Colors.BOLD}=== CLAIM REWARDS ==={Colors.END}")
        print("Completed missions:")
        for i, mid in enumerate(completed_missions, 1):
            mission = self.missions_data.get(mid, {})
            reward = mission.get('reward', {})
            exp = reward.get('experience', 0)
            gold = reward.get('gold', 0)
            items = reward.get('items', [])
            print(f"{i}. {mission.get('name')} - Exp: {exp}, Gold: {gold}, Items: {', '.join(items) if items else 'None'}")

        choice = ask(f"Claim rewards for mission (1-{len(completed_missions)}) or press Enter to cancel: ")
        if choice and choice.isdigit():
            idx = int(choice) - 1
            if 0 <= idx < len(completed_missions):
                mission_id = completed_missions[idx]
                mission = self.missions_data.get(mission_id, {})
                reward = mission.get('reward', {})

                # Apply rewards
                exp = reward.get('experience', 0)
                gold = reward.get('gold', 0)
                items = reward.get('items', [])

                self.player.gain_experience(exp)
                self.player.gold += gold
                for item in items:
                    self.player.inventory.append(item)

                # Remove from progress and add to completed
                del self.mission_progress[mission_id]
                self.completed_missions.append(mission_id)

                print(f"\n{Colors.GREEN}Rewards claimed!{Colors.END}")
                print(f"Gained {Colors.MAGENTA}{exp} experience{Colors.END}")
                print(f"Gained {Colors.GOLD}{gold} gold{Colors.END}")
                if items:
                    print(f"Received items: {', '.join(items)}")
            else:
                print("Invalid choice.")
    
    def visit_shop(self):
        """Visit the shop - displays all items for sale"""
        if not self.player:
            print("No character created yet.")
            return
            
        print(f"\n{Colors.BOLD}=== SHOP ==={Colors.END}")
        print("Welcome to the shop! What would you like to buy?")
        
        print(f"\nYour gold: {Colors.GOLD}{self.player.gold}{Colors.END}")
        
        # Show all items from items_data (excluding materials which are not for sale)
        sellable_items = {k: v for k, v in self.items_data.items() 
                         if v.get("type") != "material" and k not in self.player.inventory}
        
        if not sellable_items:
            print("No items available for purchase.")
            return
        
        # Paginate items (10 per page)
        items_list = list(sellable_items.items())
        page_size = 10
        current_page = 0
        
        while True:
            start = current_page * page_size
            end = start + page_size
            page_items = items_list[start:end]
            
            if not page_items:
                print("No more items.")
                break
            
            print(f"\n--- Page {current_page + 1} of {(len(items_list) + page_size - 1) // page_size} ---")
            for i, (item_name, item_data) in enumerate(page_items, 1):
                price = item_data.get("price", "?")
                rarity = item_data.get("rarity", "unknown")
                desc = item_data.get("description", "")
                print(f"{i}. {item_name} ({rarity}) - {Colors.GOLD}{price} gold{Colors.END}")
                print(f"   {desc}")
            
            choice = ask(f"\nBuy item (1-{len(page_items)}), [N]ext page, [P]rev page, [S]ell, or press Enter to leave: ")
            
            if not choice:
                break
            elif choice.lower() == 'n':
                if end < len(items_list):
                    current_page += 1
                else:
                    print("No more pages.")
            elif choice.lower() == 'p':
                if current_page > 0:
                    current_page -= 1
                else:
                    print("Already on first page.")
            elif choice.isdigit():
                item_idx = int(choice) - 1
                if 0 <= item_idx < len(page_items):
                    item_name, item_data = page_items[item_idx]
                    price = item_data.get("price", 0)
                    if self.player.gold >= price:
                        self.player.gold -= price
                        self.player.inventory.append(item_name)
                        print(f"Purchased {item_name} for {price} gold!")
                        self.update_mission_progress('collect', item_name)
                    else:
                        print("Not enough gold!")
                else:
                    print("Invalid choice.")
            elif choice.lower() == 's':
                # Sell flow
                self.shop_sell()

    def travel(self):
        """Travel to connected areas from the current area."""
        if not self.player:
            print("No character created yet.")
            return
            
        current = self.current_area
        area_data = self.areas_data.get(current, {})
        connections = area_data.get("connections", [])

        print(f"\n{Colors.BOLD}=== TRAVEL ==={Colors.END}")
        print(f"Current location: {area_data.get('name', current)}")
        if not connections:
            print("No connected areas to travel to.")
            return

        print("Connected areas:")
        for i, aid in enumerate(connections, 1):
            a = self.areas_data.get(aid, {})
            print(f"{i}. {a.get('name', aid)} - {a.get('description','')}")

        choice = ask(f"Travel to (1-{len(connections)}) or press Enter to cancel: ")
        if choice and choice.isdigit():
            idx = int(choice) - 1
            if 0 <= idx < len(connections):
                new_area = connections[idx]
                self.current_area = new_area
                print(f"Traveling to {self.areas_data.get(new_area, {}).get('name', new_area)}...")
                # small chance encounter on travel
                if random.random() < 0.3:
                    self.random_encounter()

    def shop_sell(self):
        """Sell items from the player's inventory to the shop."""
        if not self.player:
            return
            
        sellable = [it for it in self.player.inventory]
        if not sellable:
            print("You have nothing to sell.")
            return

        print("\nYour inventory:")
        for i, item in enumerate(sellable, 1):
            equip_marker = ''
            for slot, eq in self.player.equipment.items():
                if eq == item:
                    equip_marker = ' (equipped)'
            price = self.items_data.get(item, {}).get('price', 0)
            sell_price = price // 2 if price else 0
            print(f"{i}. {item}{equip_marker} - Sell for {sell_price} gold")

        choice = ask(f"Choose item to sell (1-{len(sellable)}) or press Enter to cancel: ")
        if not choice or not choice.isdigit():
            return
        idx = int(choice) - 1
        if not (0 <= idx < len(sellable)):
            print("Invalid selection.")
            return

        item = sellable[idx]
        # Prevent selling equipped items
        if item in self.player.equipment.values():
            print("Unequip the item before selling it.")
            return

        price = self.items_data.get(item, {}).get('price', 0)
        sell_price = price // 2 if price else 0
        self.player.inventory.remove(item)
        self.player.gold += sell_price
        print(f"Sold {item} for {sell_price} gold.")
    
    def rest(self):
        """Rest in a safe area to recover HP and MP for gold."""
        if not self.player:
            print("No character created yet.")
            return
            
        area_data = self.areas_data.get(self.current_area, {})
        area_name = area_data.get("name", "Unknown Area")
        can_rest = area_data.get("can_rest", False)
        rest_cost = area_data.get("rest_cost", 0)
        
        if not can_rest:
            print(f"\n{Colors.RED}You cannot rest in {area_name}. It's too dangerous!{Colors.END}")
            return
        
        print(f"\n{Colors.CYAN}=== REST IN {area_name.upper()} ==={Colors.END}")
        print(f"Rest Cost: {Colors.GOLD}{rest_cost} gold{Colors.END}")
        print(f"Current HP: {Colors.RED}{self.player.hp}/{self.player.max_hp}{Colors.END}")
        print(f"Current MP: {Colors.BLUE}{self.player.mp}/{self.player.max_mp}{Colors.END}")
        
        if self.player.gold < rest_cost:
            print(f"\n{Colors.RED}You don't have enough gold to rest! Need {rest_cost}, have {self.player.gold}.{Colors.END}")
            return
        
        choice = ask(f"Rest for {rest_cost} gold? (y/n): ")
        if choice.lower() != 'y':
            print("You decide not to rest.")
            return
        
        # Deduct gold and restore HP/MP
        self.player.gold -= rest_cost
        old_hp = self.player.hp
        old_mp = self.player.mp
        self.player.hp = self.player.max_hp
        self.player.mp = self.player.max_mp
        
        print(f"\n{Colors.GREEN}You rest and recover your strength...{Colors.END}")
        print(f"HP restored: {old_hp} → {Colors.GREEN}{self.player.hp}{Colors.END}")
        print(f"MP restored: {old_mp} → {Colors.GREEN}{self.player.mp}{Colors.END}")
        print(f"Gold remaining: {Colors.GOLD}{self.player.gold}{Colors.END}")
    
    def save_game(self):
        """Save the game with enhanced data including equipment"""
        if not self.player:
            print("No character to save.")
            return
            
        save_data = {
            "player": {
                "name": self.player.name,
                "character_class": self.player.character_class,
                "level": self.player.level,
                "experience": self.player.experience,
                "experience_to_next": self.player.experience_to_next,
                "max_hp": self.player.max_hp,
                "hp": self.player.hp,
                "max_mp": self.player.max_mp,
                "mp": self.player.mp,
                "attack": self.player.attack,
                "defense": self.player.defense,
                "speed": self.player.speed,
                "inventory": self.player.inventory,
                "gold": self.player.gold,
                # NEW: Equipment data that was missing
                "equipment": self.player.equipment,
                # NEW: Base stats for equipment recalculation
                "base_stats": {
                    "base_max_hp": self.player.base_max_hp,
                    "base_max_mp": self.player.base_max_mp,
                    "base_attack": self.player.base_attack,
                    "base_defense": self.player.base_defense,
                    "base_speed": self.player.base_speed
                },
                # NEW: Class data for validation
                "class_data": self.player.class_data
            },
            "current_area": self.current_area,
            "mission_progress": self.mission_progress,
            "completed_missions": self.completed_missions,
            "save_version": "2.0",  # NEW: Version for compatibility
            "save_time": datetime.now().isoformat()
        }
        
        saves_dir = "data/saves"
        # Create the saves directory if it doesn't exist
        os.makedirs(saves_dir, exist_ok=True)
        
        filename = f"{saves_dir}/{self.player.name}_save.json"
        with open(filename, 'w') as f:
                json.dump(save_data, f, indent=2)
        
        print(f"Game saved successfully!")
    
    def load_game(self):
        """Load a saved game with enhanced equipment handling and backward compatibility"""
        saves_dir = "data/saves"
        if not os.path.exists(saves_dir):
            print("No save files found.")
            return
        
        save_files = [f for f in os.listdir(saves_dir) if f.endswith('.json')]
        if not save_files:
            print("No save files found.")
            return
        
        print("Available save files:")
        for i, save_file in enumerate(save_files, 1):
            character_name = save_file.replace('_save.json', '')
            print(f"{i}. {character_name}")
        
        choice = ask(f"Load save (1-{len(save_files)}) or press Enter to cancel: ")
        if choice and choice.isdigit():
            save_index = int(choice) - 1
            if 0 <= save_index < len(save_files):
                save_file = save_files[save_index]
                filename = os.path.join(saves_dir, save_file)
                
                try:
                    with open(filename, 'r') as f:
                        save_data = json.load(f)
                    
                    # Check save version for compatibility
                    save_version = save_data.get("save_version", "1.0")
                    
                    # Recreate player
                    player_data = save_data["player"]
                    self.player = Character(player_data["name"], player_data["character_class"], self.classes_data)
                    
                    # Restore stats
                    self.player.level = player_data["level"]
                    self.player.experience = player_data["experience"]
                    self.player.experience_to_next = player_data["experience_to_next"]
                    self.player.max_hp = player_data["max_hp"]
                    self.player.hp = player_data["hp"]
                    self.player.max_mp = player_data["max_mp"]
                    self.player.mp = player_data["mp"]
                    self.player.attack = player_data["attack"]
                    self.player.defense = player_data["defense"]
                    self.player.speed = player_data["speed"]
                    self.player.inventory = player_data["inventory"]
                    self.player.gold = player_data["gold"]
                    
                    # NEW: Enhanced equipment loading with validation
                    self._load_equipment_data(player_data, save_version)
                    
                    self.current_area = save_data["current_area"]
                    
                    # Mission system load with backward compatibility
                    self.mission_progress = save_data.get("mission_progress", {})
                    self.completed_missions = save_data.get("completed_missions", [])
                    
                    # Backward compatibility for old saves using current_missions
                    if not self.mission_progress and "current_missions" in save_data:
                        for mid in save_data["current_missions"]:
                            mission = self.missions_data.get(mid)
                            if mission:
                                mission_type = mission.get('type', 'kill')
                                target_count = mission.get('target_count', 1)
                                if mission_type == 'collect' and isinstance(target_count, dict):
                                    self.mission_progress[mid] = {
                                        'current_counts': {item: 0 for item in target_count.keys()},
                                        'target_counts': target_count,
                                        'completed': False,
                                        'type': mission_type
                                    }
                                else:
                                    self.mission_progress[mid] = {
                                        'current_count': 0,
                                        'target_count': target_count,
                                        'completed': False,
                                        'type': mission_type
                                    }
                    
                    if self.player:
                        print(f"Game loaded successfully! Welcome back, {self.player.name}!")
                        self.player.display_stats()
                    
                except Exception as e:
                    print(f"Error loading save file: {e}")
    
    def _load_equipment_data(self, player_data: Dict, save_version: str):
        """Load and validate equipment data with backward compatibility"""
        if not self.player:
            return
        
        # NEW: Handle enhanced save format (v2.0+)
        if save_version >= "2.0":
            # Load equipment if present
            equipment: Dict[str, Optional[str]] = player_data.get("equipment", {"weapon": None, "armor": None, "accessory": None})
            self.player.equipment = equipment
            
            # Load base stats if present for equipment recalculation
            base_stats = player_data.get("base_stats", {})
            if base_stats:
                self.player.base_max_hp = base_stats.get("base_max_hp", self.player.base_max_hp)
                self.player.base_max_mp = base_stats.get("base_max_mp", self.player.base_max_mp)
                self.player.base_attack = base_stats.get("base_attack", self.player.base_attack)
                self.player.base_defense = base_stats.get("base_defense", self.player.base_defense)
                self.player.base_speed = base_stats.get("base_speed", self.player.base_speed)
            
            # Load class data if present
            class_data = player_data.get("class_data", {})
            if class_data:
                self.player.class_data = class_data
                self.player.level_up_bonuses = class_data.get("level_up_bonuses", {})
            
            # Validate equipped items exist and meet requirements
            self._validate_and_fix_equipment()
            
            # Recalculate stats from equipment
            self.player.update_stats_from_equipment(self.items_data)
            
        else:
            # OLD: Backward compatibility for v1.0 saves
            print(f"{Colors.YELLOW}Loading legacy save (v{save_version}). Equipment may not be restored.{Colors.END}")
            
            # Try to find equipment in inventory for old saves
            equipment: Dict[str, Optional[str]] = {"weapon": None, "armor": None, "accessory": None}
            
            # Heuristic: look for likely equipped items in inventory
            for item in player_data.get("inventory", []):
                item_data = self.items_data.get(item, {})
                item_type = item_data.get("type")
                
                if item_type == "weapon" and not equipment["weapon"]:
                    equipment["weapon"] = item
                elif item_type == "armor" and not equipment["armor"]:
                    equipment["armor"] = item
                elif item_type == "accessory" and not equipment["accessory"]:
                    equipment["accessory"] = item
            
            self.player.equipment = equipment
            self._validate_and_fix_equipment()
            self.player.update_stats_from_equipment(self.items_data)
    
    def _validate_and_fix_equipment(self):
        """Validate equipped items and auto-unequip invalid ones"""
        if not self.player:
            return
            
        invalid_items = []
        
        for slot in ("weapon", "armor", "accessory"):
            item_name = self.player.equipment.get(slot)
            if not item_name:
                continue
                
            # Check if item still exists in game data
            if item_name not in self.items_data:
                invalid_items.append((slot, item_name, "Item no longer exists"))
                self.player.equipment[slot] = None
                continue
            
            item_data = self.items_data[item_name]
            
            # Check if item type matches slot
            if item_data.get("type") != slot:
                invalid_items.append((slot, item_name, "Item type mismatch"))
                self.player.equipment[slot] = None
                continue
            
            # Check requirements
            requirements = item_data.get("requirements", {})
            if requirements:
                level_req = requirements.get("level", 0)
                class_req = requirements.get("class")
                
                if self.player.level < level_req:
                    invalid_items.append((slot, item_name, f"Level {level_req} required"))
                    self.player.equipment[slot] = None
                    continue
                
                if class_req and class_req != self.player.character_class:
                    invalid_items.append((slot, item_name, f"{class_req} class required"))
                    self.player.equipment[slot] = None
                    continue
        
        # Report any items that were auto-unequipped
        if invalid_items:
            print(f"\n{Colors.YELLOW}Some equipped items were invalid and have been unequipped:{Colors.END}")
            for slot, item_name, reason in invalid_items:
                print(f"  - {slot.title()}: {item_name} ({reason})")
            print(f"{Colors.YELLOW}Please check your inventory and re-equip valid items.{Colors.END}")
    
    def quit_game(self):
        """Quit the game"""
        print("\nHave you saved your progress? (yes/no) (CASE SENSITIVE!!!)")
        response = input(">>> ").strip().lower()
        if response == "no":
            clear_screen()
            print("Saving your progress...")
            self.save_game()
            print("Progress saved!")
        print("Thank you for playing Our Legacy!")
        print("Your legacy will be remembered...")
        sys.exit(0)
    
    def run(self):
        """Main game loop"""
        choice = self.display_welcome()
        
        if choice == "new_game":
            self.create_character()
        elif choice == "load_game":
            self.load_game()
            if not self.player:
                print("No game loaded. Starting new game...")
                self.create_character()
        
        # Main game loop
        while True:
            self.main_menu()

def main():
    """Main entry point"""
    game = Game()
    game.run()

if __name__ == "__main__":
    clear_screen()
    main()
