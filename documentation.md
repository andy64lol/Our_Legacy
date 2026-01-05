# Our Legacy - Complete Modding Documentation

This guide covers how to modify every aspect of the Our Legacy RPG game. All game content is stored in JSON files located in the `data/` directory for easy customization. I made it this easy because as an Minecraft Bedrock Add-on developer, I personally wanted to have the same flavour of their JSON-based system, as it's so much easier than having to modify the game directly. Here is the guide!

---

## Table of Contents

1. [File Overview](#file-overview)
2. [Modifying Classes](#modifying-classes)
3. [Modifying Items](#modifying-items)
4. [Modifying Enemies](#modifying-enemies)
5. [Modifying Bosses](#modifying-bosses)
6. [Modifying Areas](#modifying-areas)
7. [Modifying Spells](#modifying-spells)
8. [Modifying Missions](#modifying-missions)
9. [Scripting API](#scripting-api)
10. [Modifying Game Code](#modifying-game-code)
11. [Tips & Best Practices](#tips--best-practices)

---

## File Overview

All modifiable game content is stored in JSON files in `/data/`:

- **classes.json** - Player character classes with stats and starting items
- **items.json** - Weapons, armor, offhand items, accessories, and consumables
- **companions.json** - Companion definitions and purchasable companions (hired at the tavern)
- **enemies.json** - Regular enemies that appear in combat
- **bosses.json** - Boss enemies with special abilities
- **areas.json** - Game world locations and connections
- **spells.json** - Magic spells that can be cast in battle
- **missions.json** - Quests that players can undertake
- **main.py** - Main game code

---

## Modifying Classes

**File:** `data/classes.json`

Each class defines the player's starting stats, progression, and items.

### Class Structure

```json
{
  "ClassName": {
    "description": "A brief description of the class",
    "base_stats": {
      "hp": 100,
      "mp": 50,
      "attack": 10,
      "defense": 8,
      "speed": 10
    },
    "level_up_bonuses": {
      "hp": 15,
      "mp": 5,
      "attack": 2,
      "defense": 1,
      "speed": 1
    },
    "starting_items": ["Item Name 1", "Item Name 2"],
    "starting_gold": 100
  }
}
```

### How to Add a New Class

1. Open `data/classes.json`
2. Add a new entry with a unique class name
3. Set `base_stats` (initial character stats at level 1)
4. Set `level_up_bonuses` (stats gained per level)
5. Add `starting_items` (must match item names in `items.json`)
6. Set `starting_gold` (initial money)

### Example: Adding a "Paladin" Class

```json
"Paladin": {
  "description": "A holy warrior balanced between offense and defense",
  "base_stats": {
    "hp": 110,
    "mp": 40,
    "attack": 12,
    "defense": 14,
    "speed": 9
  },
  "level_up_bonuses": {
    "hp": 18,
    "mp": 3,
    "attack": 2,
    "defense": 3,
    "speed": 1
  },
  "starting_items": ["Iron Sword", "Knight's Armor", "Health Potion"],
  "starting_gold": 120
}
```

### Existing Classes Reference

The game currently includes four playable classes:

**Warrior** - High HP and defense, melee combat specialist
**Mage** - High MP and magical power, spellcasting specialist  
**Rogue** - High speed and agility, stealth and critical strikes
**Hunter** - Balanced combat stats with ranged weapon expertise

### Stats Explained

- **hp** - Health Points (max health)
- **mp** - Mana Points (for casting spells)
- **attack** - Physical damage dealt
- **defense** - Damage reduction from attacks
- **speed** - Turn order in combat

---

## Modifying Items

**File:** `data/items.json`

Items include weapons, armor, accessories, and consumables.

### Item Types

#### Consumable Items

```json
{
  "Health Potion": {
    "type": "consumable",
    "description": "A basic healing potion",
    "effect": "heal",
    "value": 50,
    "price": 25,
    "rarity": "common"
  }
}
```

#### Weapon Items

```json
{
  "Iron Sword": {
    "type": "weapon",
    "description": "A sturdy iron blade",
    "attack_bonus": 8,
    "price": 50,
    "rarity": "common",
    "requirements": {"level": 1}
  }
}
```

#### Armor Items

```json
{
  "Leather Armor": {
    "type": "armor",
    "description": "Light leather protection",
    "defense_bonus": 5,
    "price": 45,
    "rarity": "common",
    "requirements": {"level": 1}
  }
}
```

#### Accessory Items

```json
{
  "Ring of Power": {
    "type": "accessory",
    "description": "Increases all stats slightly",
    "stat_bonuses": {
      "attack": 2,
      "defense": 2,
      "speed": 1
    },
    "price": 100,
    "rarity": "rare",
    "requirements": {"level": 5}
  }
}
```

#### Hunter-Specific Weapons

#### Offhand Items

Offhand items are a new item type stored in `data/items.json` with `"type": "offhand"`.
They occupy a dedicated `offhand` slot (separate from `weapon`) and provide defensive, MP, or utility bonuses (shields, tomes, small focuses).

Example:

```json
{
  "Wooden Shield": {
    "type": "offhand",
    "description": "A basic shield that grants defense",
    "defense_bonus": 3,
    "price": 30,
    "rarity": "common",
    "requirements": {"level": 1}
  }
}
```

#### Accessories and Slots

The game now supports up to **three** accessory slots: `accessory_1`, `accessory_2`, and `accessory_3`.
Accessories are defined with `"type": "accessory"` in `data/items.json` and may grant multiple stat bonuses and passive effects.


**Bows (Ranged Weapons)**
```json
{
  "Hunter's Bow": {
    "type": "weapon",
    "description": "A well-crafted bow favored by hunters",
    "attack_bonus": 7,
    "speed_bonus": 2,
    "price": 60,
    "rarity": "common",
    "requirements": {"level": 1, "class": "Hunter"}
  }
}
```

**Crossbows (Heavy Ranged Weapons)**
```json
{
  "Light Crossbow": {
    "type": "weapon",
    "description": "A compact crossbow that's easy to reload",
    "attack_bonus": 9,
    "price": 75,
    "rarity": "common",
    "requirements": {"level": 2, "class": "Hunter"}
  }
}
```

**Spears (Melee Weapons)**
```json
{
  "Hunting Spear": {
    "type": "weapon",
    "description": "A sturdy spear perfect for hunting large game",
    "attack_bonus": 11,
    "price": 70,
    "rarity": "common",
    "requirements": {"level": 1}
  }
}
```

**Hunting Knives (Light Melee Weapons)**
```json
{
  "Hunting Knife": {
    "type": "weapon",
    "description": "A sharp knife essential for any hunter's toolkit",
    "attack_bonus": 6,
    "speed_bonus": 3,
    "price": 40,
    "rarity": "common",
    "requirements": {"level": 1}
  }
}
```

#### Universal Charms and Accessories

**Stat Boosting Charms**
```json
{
  "Luck Charm": {
    "type": "accessory",
    "description": "A simple charm believed to bring good fortune",
    "price": 30,
    "rarity": "common"
  }
}
```

### How to Add a New Item

1. Open `data/items.json`
2. Add a new entry with the item name as key
3. Choose the type (consumable, weapon, armor, or accessory)
4. Set appropriate bonuses and properties
5. Set price and rarity

### Item Properties Reference

- **type** - Type of item (consumable, weapon, armor, offhand, accessory)
- **description** - Item description shown in-game
- **effect** - For consumables: "heal", "mp_restore", "defense_boost", etc.
- **value** - Effect magnitude (healing amount, MP restored, etc.)
- **attack_bonus** - Extra damage for weapons
- **defense_bonus** - Extra defense for armor
- **speed_bonus** - Extra speed increase
- **stat_bonuses** - Multiple stat increases (for accessories)
- **price** - Cost in gold
- **rarity** - Item rarity (common, uncommon, rare, epic, legendary)
- **requirements** - Level/stat requirements to use

### Rarity Levels (from weakest to strongest)

1. common
2. uncommon
3. rare
4. legendary

*Note: Epic rarity is not currently used in the game*

### Class Restrictions

Some items are restricted to specific classes:

**Hunter Exclusive Weapons:**
- Bows: Hunter's Bow, Longbow, Composite Bow, Elven Bow
- Crossbows: Light Crossbow, Heavy Crossbow, Repeating Crossbow

**Multi-Class Weapons:**
- Spears: Available to Hunter and Warrior classes
- Hunting Knives: Available to Hunter and Rogue classes

**Universal Items:**
- Most consumables, basic armor, and charms are available to all classes

---

## Modifying Enemies

**File:** `data/enemies.json`

Regular enemies that spawn in areas and can be fought.

### Enemy Structure

```json
{
  "goblin": {
    "name": "Goblin",
    "hp": 25,
    "attack": 8,
    "defense": 3,
    "speed": 10,
    "experience_reward": 15,
    "gold_reward": 8,
    "loot_table": ["Health Potion", "Goblin Ear"]
  }
}
```

### How to Add a New Enemy

1. Open `data/enemies.json`
2. Add a new entry with a unique enemy ID (use lowercase with underscores)
3. Set name, stats, and rewards
4. Add to `loot_table` (items that drop when defeated)
5. Add the enemy ID to an area's `possible_enemies` list in `areas.json`

### Example: Adding an "Ice Troll" Enemy

```json
"ice_troll": {
  "name": "Ice Troll",
  "hp": 60,
  "attack": 14,
  "defense": 8,
  "speed": 6,
  "experience_reward": 40,
  "gold_reward": 25,
  "loot_table": ["Large Health Potion", "Ice Crystal", "Troll Fang"]
}
```

### Enemy Properties

- **name** - Display name
- **hp** - Health points
- **attack** - Attack power
- **defense** - Defense value
- **speed** - Speed (affects turn order)
- **experience_reward** - XP gained when defeated
- **gold_reward** - Gold received when defeated
- **loot_table** - List of possible item drops (randomly selected)

### Thematic Loot Distribution

Enemy loot tables have been carefully designed to match enemy types:

**Goblin**: Weak creature dropping basic hunting tools
- Loot: Health Potion, Goblin Ear, Hunting Knife

**Orc**: Warrior-like creature with heavy weapons
- Loot: Orc Tooth, Iron Axe, Warrior Spear

**Skeleton**: Undead creature with dark weapons
- Loot: Bone Fragment, Rusty Dagger, Steel Hunting Knife

**Wolf**: Wild animal creature
- Loot: Wolf Fang, Health Potion, Hunting Spear

**Bandit**: Rogue-like human adversary
- Loot: Steel Dagger, Mana Potion, Assassin Hunting Knife

**Troll**: Large, powerful creature
- Loot: Troll Club, Large Health Potion, Tri-point Spear

**Fire Wraith**: Elemental creature
- Loot: Spellsword, Fire Gem, Dragon Spear (legendary)

**Goblin Archer**: Ranged goblin fighter
- Loot: Light Crossbow, Health Potion, Hunter's Bow

This distribution ensures that players can naturally acquire Hunter weapons and other equipment through gameplay while maintaining thematic consistency.

---

## Modifying Bosses

**File:** `data/bosses.json`

Boss enemies with special abilities and dialogue.

### Boss Structure

```json
{
  "fire_dragon_boss": {
    "name": "Ancient Fire Dragon",
    "hp": 300,
    "attack": 35,
    "defense": 20,
    "speed": 15,
    "description": "A legendary dragon...",
    "special_abilities": [
      {
        "name": "Fire Breath",
        "description": "Deals massive fire damage",
        "damage": 50,
        "mp_cost": 20,
        "cooldown": 3
      }
    ],
    "experience_reward": 500,
    "gold_reward": 200,
    "loot_table": ["Dragon Scales", "Fire Orb", "Dragon Egg"]
  }
}
```

### How to Add a New Boss

1. Open `data/bosses.json`
2. Add a new boss with unique ID
3. Set high stats (bosses should be challenging)
4. Define special abilities with damage, MP cost, and cooldown
5. Set generous rewards

### Boss Special Ability Structure

```json
{
  "name": "Ability Name",
  "description": "What the ability does",
  "damage": 30,          // For damage abilities
  "effect": "debuff",    // For status effects
  "mp_cost": 15,         // MP required to use
  "cooldown": 3,         // Turns before usable again
  "attack_reduction": 5, // For debuff abilities
  "defense_reduction": 2 // For debuff abilities
}
```

---

## Modifying Areas

**File:** `data/areas.json`

Game world locations that players can visit and explore.

### Area Structure

```json
{
  "starting_village": {
    "name": "Starting Village",
    "description": "A peaceful village...",
    "possible_enemies": [],
    "shops": ["general_store"],
    "missions_available": true,
    "connections": ["forest_path", "ancient_ruins"],
    "rest_cost": 5,
    "can_rest": true
  }
}
```

### How to Add a New Area

1. Open `data/areas.json`
2. Add a new area with unique ID
3. Set name and description
4. Add possible enemies (enemy IDs from `enemies.json`)
5. Connect to other areas using their IDs
6. Set rest cost and whether missions are available

### Example: Adding a "Mountain Peak" Area

```json
"mountain_peak": {
  "name": "Mountain Peak",
  "description": "A treacherous mountain summit where ancient dragons once nested. The air is thin and cold.",
  "possible_enemies": ["mountain_golem", "ice_troll", "giant_eagle"],
  "shops": [],
  "missions_available": false,
  "connections": ["mountain_pass", "sky_citadel"],
  "difficulty": 4,
  "rest_cost": 15,
  "can_rest": true
}
```

### Area Properties

- **name** - Display name
- **description** - Flavor text describing the area
- **possible_enemies** - Enemy IDs that can spawn here
- **shops** - Shop IDs available (usually "general_store")
- **missions_available** - Whether quests can be picked up
- **connections** - Area IDs that connect to this area
- **difficulty** - Area difficulty level (1-5)
- **rest_cost** - Gold cost to rest and restore HP/MP
- **can_rest** - Whether the player can rest here

### Important: Creating Connections

When adding a new area, remember to:
1. Add it to other areas' `connections` lists if they should connect
2. Add it to the game's area network (create bidirectional connections for logical travel)

---

## Companions & Tavern

**File:** `data/companions.json`

Companions are NPC allies that the player can hire at the tavern. The game supports up to **4 companions** in the player's party. Companions provide passive stat bonuses and/or on-use effects (healing, taunts, post-battle heals, etc.).

Example companion entry:

```json
"companion_1": {
  "name": "Borin the Brave",
  "description": "A stalwart fighter who increases your attack and draws enemy attention.",
  "attack_bonus": 3,
  "defense_bonus": 2,
  "price": 100
}
```

Key fields:
- `name` - Display name for the companion
- `description` - Flavor text
- Stat fields such as `attack_bonus`, `defense_bonus`, `speed_bonus`, `mp_bonus`, `healing_bonus` - applied while companion is hired
- `price` - Gold cost to hire the companion in the tavern
- Additional custom fields (e.g., `taunt_chance`, `post_battle_heal`, `spell_power_bonus`) may be added and handled by game code for specific companion effects.

Tavern behavior:
- The tavern is defined as an area (for example `tavern` / "The Rusty Tankard") in `data/areas.json` and contains a shop id (e.g., `tavern_keeper`) or is handled directly by the game to present available companions.
- Players can hire companions at the tavern for the listed `price`.
- The game enforces a maximum of 4 companions; attempting to hire more will be prevented.

Balance tips:
- High-tier companions should cost significantly more and grant larger bonuses (see the added high-tier companions in `data/companions.json`).
- Companion effects can be expanded in `main.py` to implement active abilities or more complex behaviors.

## Modifying Spells

**File:** `data/spells.json`

Magic spells that can be cast during combat.

### Spell Structure

```json
{
  "Fireball": {
    "mp_cost": 20,
    "power": 25,
    "type": "damage",
    "description": "A burst of flame that scorches a foe.",
    "allowed_weapons": ["Wooden Wand", "Crystalline Wand", "Magic Staff"]
  }
}
```

### How to Add a New Spell

1. Open `data/spells.json`
2. Add a new spell with a unique name
3. Set MP cost and power (damage or healing)
4. Choose type: "damage" or "heal"
5. List weapons that can cast this spell

### Spell Types

- **damage** - Deals damage to enemy
- **heal** - Restores HP to caster
- **buff** - Increases stats (not yet implemented)
- **debuff** - Decreases enemy stats (not yet implemented)

### Example: Adding a "Meteor Storm" Spell

```json
"Meteor Storm": {
  "mp_cost": 50,
  "power": 60,
  "type": "damage",
  "description": "Summons a devastating meteor shower on enemies.",
  "allowed_weapons": ["Magic Staff", "Ethereal Staff", "Spellsword", "Dragonsoul Blade"]
}
```

### Hunter Class Weapon Specialization

The Hunter class introduces new weapon types with specific mechanics:

**Bows and Crossbows (Hunter Exclusive):**
- Provide ranged attack options
- Generally offer higher attack bonuses but may have speed penalties
- Crossbows are more powerful but slower to reload
- Require Hunter class to equip

**Spears (Hunter & Warrior):**
- Offer reach advantage in combat
- Balanced between power and speed
- Available to both Hunter and Warrior classes

**Hunting Knives (Hunter & Rogue):**
- Light, fast weapons with critical strike potential
- Speed bonuses compensate for lower base damage
- Available to both Hunter and Rogue classes

These weapon types expand tactical options while maintaining class identity and balance.

### Spell Properties

- **mp_cost** - MP required to cast
- **power** - Damage dealt or HP healed
- **type** - Spell type (damage, heal, etc.)
- **description** - Spell description
- **allowed_weapons** - Weapons capable of casting this spell

---

## Modifying Missions

**File:** `data/missions.json`

Quests that players can undertake for rewards.

### Mission Structure

```json
{
  "tutorial_quest": {
    "name": "First Steps",
    "description": "Defeat 3 goblins...",
    "type": "kill",
    "target": "goblin",
    "target_count": 3,
    "reward": {
      "experience": 50,
      "gold": 25,
      "items": ["Health Potion"]
    },
    "area": "forest_path",
    "unlock_level": 1,
    "prerequisites": []
  }
}
```

### How to Add a New Mission

1. Open `data/missions.json`
2. Add a new mission with unique ID
3. Set name and description
4. Choose type (currently "kill" is main type)
5. Set target (enemy or item ID) and count
6. Define rewards (XP, gold, items)
7. Set area where mission is available
8. Set unlock level and prerequisites

### Mission Types

- **kill** - Kill X number of enemies
- **collect** - Collect X items (not yet fully implemented)
- **explore** - Explore an area (not yet fully implemented)

### Example: Adding a "Dragon Slayer" Mission

```json
"dragon_slayer": {
  "name": "Dragon Slayer",
  "description": "The kingdom calls upon a brave hero to slay the fire dragon terrorizing the mountain. Defeat the Ancient Fire Dragon to save the kingdom!",
  "type": "kill",
  "target": "fire_dragon_boss",
  "target_count": 1,
  "reward": {
    "experience": 500,
    "gold": 300,
    "items": ["Crown of Heroes", "Dragon Scale Armor"]
  },
  "area": "mountain_peak",
  "unlock_level": 15,
  "prerequisites": ["mountain_pass_quest"]
}
```

### Mission Properties

- **name** - Quest name
- **description** - Quest description/objective
- **type** - Quest type (kill, collect, explore)
- **target** - Enemy or item ID to target
- **target_count** - How many to kill/collect
- **reward.experience** - XP reward
- **reward.gold** - Gold reward
- **reward.items** - Item rewards
- **area** - Where quest is available
- **unlock_level** - Minimum player level
- **prerequisites** - Quest IDs that must be completed first

---

## Modifying Game Code

**File:** `main.py`

For more advanced customization, you can modify the Python code.

### Key Code Sections

#### Character Class (Lines 47-138)
Defines player character statistics and methods.

#### Game Class (Lines 145+)
Main game engine with combat, exploration, and inventory systems.

#### Important Methods

- `create_character()` - Character creation flow
- `explore()` - Area exploration menu
- `combat()` - Battle system
- `save_game()` - Save game data
- `load_game()` - Load saved game
- `display_stats()` - Show character stats

### Modifying Combat

Find the `combat()` method to adjust:
- Damage calculations
- Turn order logic
- Enemy AI behavior
- Combat balance

### Modifying Colors

The `Colors` class (lines 13-27) defines terminal colors:

```python
class Colors:
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
```

### Common Code Modifications

#### Change Starting Gold

Find: `self.gold = 100`
Change the number to desired starting gold.

#### Modify Experience Multiplier

Find: `self.experience_to_next = int(self.experience_to_next * 1.5)`
Change 1.5 to adjust leveling speed (higher = slower leveling).

#### Adjust Damage Formula

Find in `combat()` method:
```python
actual_damage = max(1, damage - self.defense)
```
Modify the formula to change damage calculations.

---

## Tips & Best Practices

### 1. **Backup Your Files**
Always backup `data/` and `main.py` before making major changes.

### 2. **JSON Formatting**
- Use proper JSON syntax (commas between entries, no trailing commas)
- Validate JSON with online tools if you get errors
- Use consistent indentation (2 spaces recommended)

### 3. **Naming Conventions**
- Use lowercase with underscores for IDs: `fire_dragon_boss`
- Use Title Case for display names: "Fire Dragon Boss"
- Keep names under 50 characters

### 4. **Balance Guidelines**

**Enemy Stats vs Player:**
- Early enemies should have 30-50% of player attack power
- Bosses should have 150-200% of average player attack power

**Rewards:**
- XP: roughly 5-10 per HP the enemy has
- Gold: 1/3 to 1/2 of XP value
- Items: 1-3 items per enemy in loot table

**Difficulty Scaling:**
- Level 1-5: Basic enemies and areas
- Level 5-10: Intermediate difficulty
- Level 10+: Challenging content and bosses

### 5. **Interconnected Systems**

Remember these dependencies:
- Enemies added to `enemies.json` must be referenced in `areas.json`
- Items must exist in `items.json` to be:
  - Starting items for classes
  - Rewards in missions
  - Loot drops from enemies
- Missions can only target existing enemies
- Spells can only be cast by existing weapons

### 6. **Testing Changes**

1. Save your modifications
2. Run the game: `python3 main.py`
3. Test the area/enemy/item you modified
4. Check for errors in the console
5. If JSON errors occur, validate syntax

### 7. **Performance Tips**

- Limit enemy spawn lists to 5-8 enemies per area
- Keep loot tables under 10 items
- Don't create too many mission prerequisites (max 3)

### 8. **Creating Progression Chains**

Link content by level:
- Low level: basic items, weak enemies, tutorial missions
- Mid level: better equipment, tougher enemies, longer quest chains
- High level: legendary items, bosses, endgame missions

### 9. **Balancing Difficulty**

Use the difficulty setting in areas to indicate danger level:
- difficulty: 1 (beginner)
- difficulty: 2-3 (intermediate)
- difficulty: 4-5 (advanced/bosses)

### 10. **Common Mistakes to Avoid**

❌ **Don't:**
- Leave trailing commas in JSON
- Create circular mission prerequisites
- Add items to starting items that don't exist
- Use spaces in IDs (use underscores instead)
- Make one class drastically overpowered

✓ **Do:**
- Test after each major change
- Keep items balanced with prices
- Create a progression path
- Document custom content
- Maintain consistent naming

---

## Scripting API

**EXPERIMENTAL FEATURE** - The Scripting API is still in development. Features may change or break between versions. Use at your own risk.

The Scripting API allows you to extend gameplay with Python scripts. Create custom events, modify game state, and hook into game mechanics without editing the core code.

### Getting Started

**Important:** The scripting API is disabled by default. To enable it:

1. Open `data/config.json`
2. Set `"scripting_enabled": true`
3. Restart the game

Example config.json:
```json
{
  "scripting_enabled": true,
  "auto_load_scripts": true,
  "scripts": [
    "example_buff_granter",
    "example_companion_reward"
  ],
  "difficulty": "normal",
  "autosave_enabled": true,
  "autosave_interval": 5
}
```

If `config.json` doesn't exist, it will be created with scripting disabled by default for stability.

### Basic Example

```python
from scripting import get_api

def my_callback():
    api = get_api()
    player = api.get_player()
    api.log(f"Player is level {player['level']}")

# Register callback
api = get_api()
api.register_hook('on_player_levelup', my_callback)
```

### Complete API Reference

The Scripting API provides comprehensive access to game state, player data, and game systems. This section documents all available methods.

#### Player Management

- `get_player()` - Get player data dict with name, level, stats, inventory, companions, buffs
- `set_player_stat(stat, value)` - Set a player stat (hp, mp, attack, defense, speed, gold, level, experience)
- `get_base_stats()` - Get base stats (before equipment/buffs): hp, mp, attack, defense, speed
- `get_effective_stats()` - Get effective stats (after equipment/buffs): hp, max_hp, mp, max_mp, attack, defense, speed
- `add_item(item_name, count)` - Add items to inventory (free, no gold cost)
- `remove_item(item_name, count)` - Remove items from inventory
- `heal_player(amount)` - Heal player HP, returns actual amount healed
- `restore_mp(amount)` - Restore player MP, returns actual amount restored

#### Experience & Leveling

- `add_experience(amount)` - Give player XP points
- `level_up(levels)` - Force level up player by N levels
- `get_level_progress()` - Get current level/experience info: level, experience, experience_to_next

#### Inventory Management (UNDOCUMENTED)

- `get_inventory()` - Get full inventory list as list of item names
- `get_inventory_count(item_name)` - Count how many of an item player has
- `clear_inventory()` - Clear entire inventory (use with caution!)
- `get_inventory_summary()` - Get dict with item names as keys and counts as values
- `sort_inventory()` - Sort inventory alphabetically, returns success bool
- `has_item(item_name, minimum_quantity)` - Check if player has at least N of an item
- `give_item(item_name, quantity)` - Give player item(s) without cost (alias for add_item)
- `take_item(item_name, quantity)` - Remove item(s) from inventory without payment, returns count removed

#### Equipment Management (UNDOCUMENTED)

- `get_equipped_items()` - Get dict with weapon, armor, offhand, accessory_1/2/3
- `equip_item(item_name, slot)` - Equip an item, optionally to specific slot (auto-detect if None)
- `unequip_item(slot)` - Unequip item from slot, returns item name or None
- `swap_equipment(slot1, slot2)` - Swap items between two equipment slots
- `can_equip_item(item_name)` - Check if player meets requirements to equip an item
- `get_item_info(item_name)` - Get detailed info about an item (type, price, bonuses, requirements)
- `get_item_price(item_name)` - Get the value/price of an item in gold

#### Trading & Economy (UNDOCUMENTED)

- `buy_item(item_name, quantity)` - Buy an item (costs gold), returns success bool
- `sell_item(item_name, quantity)` - Sell items for gold, returns gold received
- `get_inventory_value()` - Calculate total value of all items in inventory

#### Buff Management

- `apply_buff(name, duration, modifiers)` - Apply temporary buff with stat modifiers
- `get_active_buffs()` - Get list of active buff dicts with name, duration, modifiers
- `remove_buff(buff_name)` - Remove specific buff by name, returns success bool
- `clear_buffs()` - Remove all buffs, returns count removed
- `extend_buff(buff_name, extra_duration)` - Extend duration of a buff, returns success bool

#### Companions

- `get_companions()` - Get list of hired companions with name, id, level
- `hire_companion(name)` - Recruit a companion by name (ignores cost), returns success bool

#### Game Data Access

- `get_items_data()` - Get all items data as dict
- `get_enemies_data()` - Get all enemies data as dict
- `get_areas_data()` - Get all areas data as dict
- `get_companions_data()` - Get all companions data as dict
- `get_spells()` - Get all spell data as dict
- `get_missions()` - Get all missions data as dict
- `get_current_area()` - Get current area ID (str or None)
- `set_current_area(area_id)` - Travel to an area, returns success bool
- `get_area_info(area_id)` - Get info dict about an area (name, description, difficulty, etc.)

#### Area & Exploration (UNDOCUMENTED)

- `get_area_connections(area_id)` - Get list of connected area IDs
- `get_area_enemies(area_id)` - Get list of enemy IDs that spawn in area
- `add_area_enemy(area_id, enemy_id)` - Add enemy to area's spawn list, returns success bool
- `remove_area_enemy(area_id, enemy_id)` - Remove enemy from area's spawn list, returns success bool
- `set_area_difficulty(area_id, difficulty)` - Set area difficulty (1-5), returns success bool

#### Mission Management (UNDOCUMENTED)

- `get_mission_progress()` - Get current mission progress as dict
- `accept_mission(mission_id)` - Accept a mission, returns success bool
- `complete_mission(mission_id)` - Force complete a mission, returns success bool
- `has_mission_completed(mission_id)` - Check if mission is completed, returns bool
- `get_mission_info(mission_id)` - Get detailed mission data dict (name, description, rewards, etc.)
- `reset_mission(mission_id)` - Reset mission to incomplete state, returns success bool
- `is_mission_available(mission_id)` - Check if player meets requirements to accept mission

#### Combat & Multipliers

- `get_combat_multipliers()` - Get dict with player_damage_mult, enemy_damage_mult, experience_mult
- `set_combat_multipliers(player_mult, enemy_mult, exp_mult)` - Set combat multipliers (min 0.1)

#### Spells & Abilities

- `learn_spell(spell_name)` - Mark a spell as learned, returns success bool
- `get_learned_spells()` - Get list of learned spell names

#### Statistics & Tracking

- `get_game_statistics()` - Get gameplay stats dict: enemies_defeated, bosses_defeated, missions_completed, gold_earned, items_collected, playtime_seconds
- `increment_statistic(stat_name, amount)` - Increment a statistic, returns new value

#### Validation & Checks (UNDOCUMENTED)

- `is_mission_available(mission_id)` - Check if player can accept a mission (meets level/prerequisites)
- `can_equip_item(item_name)` - Check if player meets requirements to equip an item

#### Events & Hooks

- `register_hook(event_name, callback)` - Register event listener callback
- `trigger_hook(event_name, *args, **kwargs)` - Trigger all callbacks for an event, returns list of results

**Available Events:**
- `on_battle_start` - Called when battle begins
- `on_battle_end` - Called when battle ends
- `on_player_levelup` - Called when player levels up
- `on_item_acquired` - Called when item is added to inventory
- `on_companion_hired` - Called when companion is recruited
- `on_mission_complete` - Called when mission is completed
- `on_buff_applied` - Called when buff is applied to player
- `on_area_entered` - Called when player enters an area

#### Debugging (UNDOCUMENTED)

- `dump_player_data()` - Get formatted string of all player data for debugging
- `list_all_enemies()` - Get list of all enemy IDs
- `list_all_items()` - Get list of all item names
- `list_all_areas()` - Get list of all area IDs
- `list_all_companions()` - Get list of all companion IDs

#### Utilities

- `log(message)` - Print message to console with [Script] prefix
- `get_random_item(items_list)` - Pick a random item from a list, returns item or None
- `create_custom_enemy(name, stats)` - Create a custom enemy dict dynamically

#### Data Storage

- `store_data(key, value)` - Store custom script data (persists in memory during game session)
- `retrieve_data(key, default)` - Retrieve stored data, returns default if key not found
- `clear_data(key)` - Delete a stored data key, returns success bool

### Example Scripts

The `scripts/` directory contains comprehensive examples demonstrating various API features. Each script is self-contained with detailed comments.

#### Core Examples (Original)

**example_buff_granter.py** - Grant power buffs every 5 levels
```python
# Demonstrates: on_player_levelup hook, apply_buff()
def on_levelup():
    api = get_api()
    player = api.get_player()
    if player['level'] % 5 == 0:
        api.apply_buff('Milestone Buff', 10, {
            'attack_bonus': 5,
            'defense_bonus': 3,
        })
```

**example_companion_reward.py** - Auto-recruit companions at milestones
```python
# Demonstrates: hire_companion(), get_player(), on_player_levelup hook
COMPANION_REWARDS = {5: 'Borin the Brave', 10: 'Lyra the Swift', ...}

def on_levelup_reward():
    api = get_api()
    player = api.get_player()
    if player['level'] in COMPANION_REWARDS:
        api.hire_companion(COMPANION_REWARDS[player['level']])
```

**example_quest_giver.py** - Implement custom quest system
```python
# Demonstrates: store_data(), retrieve_data(), custom class patterns
class QuestGiver:
    def check_quests(self):
        api = get_api()
        # Implement quest logic using get_mission_info(), complete_mission()
```

**example_stat_tracker.py** - Track achievements and statistics
```python
# Demonstrates: increment_statistic(), get_game_statistics(), achievement checking
class StatTracker:
    ACHIEVEMENTS = {'first_blood': {'enemies_defeated': 1}, ...}
    
    def check_achievements(self):
        # Uses on_battle_end, on_mission_complete, on_item_acquired hooks
```

**example_dynamic_difficulty.py** - Adaptive difficulty system
```python
# Demonstrates: get_combat_multipliers(), set_combat_multipliers()
class DynamicDifficulty:
    def adjust_difficulty(self):
        # Scales enemy/player damage based on player performance
```

**example_loot_modifier.py** - Customize and enhance loot drops
```python
# Demonstrates: get_inventory(), theming, rarity-based drops
class LootModifier:
    THEMATIC_LOOT = {'goblin': [...], 'dragon': [...]}
```

#### New Comprehensive Examples (UNDOCUMENTED)

**example_random_events.py** - Random event system with hooks
```python
# Demonstrates: on_battle_start/end hooks, custom data storage, conditional events
class RandomEventManager:
    EVENT_TYPES = {'bonus_xp': {'weight': 30}, 'treasure': {...}, ...}
    
    def on_battle_end(self):
        # Check for random events after battles
        # Uses store_data(), retrieve_data() for state management
```

**example_equipment_manager.py** - Equipment management and auto-equip
```python
# Demonstrates: get_equipped_items(), equip_item(), unequip_item(), swap_equipment()
#             can_equip_item(), get_item_info(), get_item_score()
class EquipmentManager:
    def auto_equip_best(self):
        # Finds best item for each slot based on stat priority
        # Shows equipment recommendations and stat comparisons
```

**example_shop_system.py** - Trading and economy management
```python
# Demonstrates: buy_item(), sell_item(), get_item_price(), get_inventory_value()
#             get_inventory_summary(), transaction history tracking
class ShopSystem:
    def buy_item(self, item_name, quantity):
        # Handle purchases with markup calculation
    def sell_item(self, item_name, quantity):
        # Handle sales with sell price calculation
```

**example_exploration_manager.py** - Area exploration and world modification
```python
# Demonstrates: get_area_connections(), get_area_enemies(), add_area_enemy()
#             remove_area_enemy(), set_area_difficulty(), get_world_map()
class ExplorationManager:
    def discover_current_area(self):
        # Mark areas as discovered and log connections
    def get_shortest_path(self, start, end):
        # BFS algorithm to find shortest path between areas
```

**example_achievement_system.py** - Complete achievement and validation system
```python
# Demonstrates: get_game_statistics(), is_mission_available(), can_equip_item()
#             achievement checking, mission validation, equipment requirements
class AchievementSystem:
    ACHIEVEMENTS = {
        'first_blood': {'name': 'First Blood', 'requirements': {...}},
        ...
    }
    
    def check_all_achievements(self):
        # Comprehensive achievement checking system
```

### Loading Custom Scripts

Scripts in the `scripts/` directory can be auto-loaded by adding them to `config.json`:

```json
{
  "scripting_enabled": true,
  "auto_load_scripts": true,
  "scripts": [
    "example_buff_granter",
    "example_companion_reward",
    "example_quest_giver"
  ]
}
```

Or manually load in `main.py`:

```python
# In main() after Game() init
if game.scripting_enabled:
    from scripts import my_custom_script
```

### Advanced Usage

#### Creating a Plugin System

```python
from scripting import get_api

class MyPlugin:
    def __init__(self):
        self.api = get_api()
        self.api.register_hook('on_player_levelup', self.on_levelup)
    
    def on_levelup(self):
        player = self.api.get_player()
        self.api.log(f"Custom event: {player['name']} is level {player['level']}")

# Auto-initialize
MyPlugin()
```

#### Conditional Item Rewards

```python
def on_item_acquired(item_name):
    api = get_api()
    if item_name == 'Legendary Sword':
        player = api.get_player()
        api.apply_buff('Legendary Blessing', 20, {
            'attack_bonus': 10,
            'defense_bonus': 5,
        })
        api.log("You feel the legendary power surge through you!")

api.register_hook('on_item_acquired', on_item_acquired)
```

#### Custom Enemy Encounters

```python
def create_boss_encounter():
    api = get_api()
    boss = api.create_custom_enemy('Shadow Master', {
        'hp': 500,
        'attack': 30,
        'defense': 20,
        'speed': 15,
        'experience_reward': 1000,
        'gold_reward': 500,
    })
    return boss
```

#### Equipment System Interaction

```python
def auto_equip_best_items():
    api = get_api()
    inventory = api.get_inventory()
    
    for item_name in inventory:
        if api.can_equip_item(item_name):
            api.equip_item(item_name)
            api.log(f"Auto-equipped: {item_name}")
```

#### Area Customization

```python
def customize_area():
    api = get_api()
    
    # Get area info
    area = api.get_area_info('forest_path')
    connections = api.get_area_connections('forest_path')
    
    # Add new enemy type to area
    api.add_area_enemy('forest_path', 'fire_wraith')
    
    # Set difficulty
    api.set_area_difficulty('forest_path', 3)
```

#### Mission Chain System

```python
class MissionChain:
    def __init__(self, mission_ids):
        self.api = get_api()
        self.mission_ids = mission_ids
        self.api.register_hook('on_mission_complete', self.on_mission_complete)
    
    def on_mission_complete(self, mission_id):
        # Automatically unlock next mission in chain
        current_index = self.mission_ids.index(mission_id)
        if current_index < len(self.mission_ids) - 1:
            next_mission = self.mission_ids[current_index + 1]
            self.api.log(f"Next quest unlocked: {next_mission}")
```

#### Buff-Based Damage Amplification

```python
def apply_damage_buff_cascade():
    api = get_api()
    
    # Apply escalating damage buff
    for i in range(5):
        duration = 10 - i
        bonus = 5 * (i + 1)
        api.apply_buff(f'Power Surge {i+1}', duration, {
            'attack_bonus': bonus,
            'speed_bonus': i + 1
        })
    
    api.log("Damage buff cascade applied!")
```

#### Player Statistics Dashboard

```python
def display_player_dashboard():
    api = get_api()
    
    # Get all player data
    player = api.get_player()
    stats = api.get_game_statistics()
    buffs = api.get_active_buffs()
    inventory = api.get_inventory()
    
    api.log("\n=== Player Dashboard ===")
    api.log(f"Level: {player['level']} ({player['rank']})")
    api.log(f"HP: {player['hp']}/{player['max_hp']}")
    api.log(f"Equipment: {api.get_equipped_items()}")
    api.log(f"Active Buffs: {len(buffs)}")
    api.log(f"Inventory: {len(inventory)} items")
    api.log(f"Enemies Defeated: {stats['enemies_defeated']}")
```

#### Experience Gain Multiplier

```python
class ExperienceBooster:
    def __init__(self):
        self.api = get_api()
        self.boosts = {}
    
    def add_exp_boost(self, name, multiplier, duration):
        """Add temporary XP multiplier."""
        self.api.apply_buff(f"XP Boost: {name}", duration, {
            'experience_multiplier': int(multiplier * 10)  # Store as int
        })
        self.api.log(f"XP boost active: {multiplier}x for {duration} battles")
    
    def apply_weekend_bonus(self):
        """Apply a weekend bonus."""
        self.add_exp_boost("Weekend Bonus", 1.5, 100)
```

#### Inventory Limitation System

```python
class InventoryManager:
    MAX_SLOTS = 20
    
    def __init__(self):
        self.api = get_api()
    
    def get_inventory_space(self):
        """Check remaining inventory slots."""
        inventory = self.api.get_inventory()
        return max(0, self.MAX_SLOTS - len(inventory))
    
    def is_full(self):
        """Check if inventory is full."""
        return self.get_inventory_space() <= 0
    
    def add_item_safe(self, item_name):
        """Add item only if space available."""
        if self.is_full():
            self.api.log("Inventory full!")
            return False
        return self.api.add_item(item_name)
```

#### Difficulty Scaling by Player Level

```python
def scale_difficulty_with_level():
    api = get_api()
    player = api.get_player()
    level = player['level']
    
    # Calculate scaling factor
    scale = 1.0 + (level / 50.0)  # +1% difficulty per level
    
    # Set combat multipliers
    api.set_combat_multipliers(
        player_mult=1.0,      # Player stays the same
        enemy_mult=scale,     # Enemies get harder
        exp_mult=0.8 + (scale * 0.2)  # XP adjusts too
    )
```

### Best Practices

1. **Always check if API exists** before using it:
   ```python
   api = get_api()
   if api is None:
       return
   ```

2. **Handle exceptions** gracefully:
   ```python
   try:
       api.apply_buff('Name', 10, {'bonus': 5})
   except Exception as e:
       print(f"Error: {e}")
   ```

3. **Store state in custom_data** instead of globals:
   ```python
   api.store_data('my_counter', api.retrieve_data('my_counter', 0) + 1)
   ```

4. **Use logging** for debugging:
   ```python
   api.log(f"Debug info: {value}")
   ```

5. **Test thoroughly** before distributing scripts

---

## Modifying Game Code

### "AttributeError" or "KeyError"

Check that:
- Item names in missions/classes exist in `items.json`
- Enemy IDs in areas exist in `enemies.json`
- All JSON files have valid syntax

### Game Won't Start

1. Check for JSON syntax errors
2. Ensure all referenced items/enemies exist
3. Look for Python indentation errors in `main.py`
4. Check the error message for missing quotes or commas

### Missing Items/Enemies

Verify they exist in the correct JSON file and are referenced properly in other files.

---

## Quick Reference: File Locations

```
Our_Legacy/
├── main.py                  (Game code)
├── scripting.py             (Scripting API)
├── README.md
├── documentation.md         (This file)
├── TODO_Scripting_API.md    (Scripting task tracking)
├── scripts/                 (Custom scripts - 11 examples)
│   ├── example_buff_granter.py         (Buffs every 5 levels)
│   ├── example_companion_reward.py     (Auto-recruit companions)
│   ├── example_quest_giver.py          (Custom quest system)
│   ├── example_stat_tracker.py         (Achievement tracking)
│   ├── example_dynamic_difficulty.py   (Adaptive difficulty)
│   ├── example_loot_modifier.py        (Loot customization)
│   ├── example_random_events.py        (Random events system)
│   ├── example_equipment_manager.py    (Equipment management)
│   ├── example_shop_system.py          (Trading/economy)
│   ├── example_exploration_manager.py  (Area exploration)
│   └── example_achievement_system.py   (Achievements/validation)
└── data/
    ├── classes.json         (Player classes)
    ├── items.json           (Equipment & consumables)
    ├── enemies.json         (Regular enemies)
    ├── bosses.json          (Boss enemies)
    ├── areas.json           (Game world locations)
    ├── spells.json          (Magic spells)
    ├── missions.json        (Quests)
    ├── companions.json      (Companion definitions)
    ├── effects.json         (Status effects)
    ├── config.json          (Game configuration)
    └── saves/               (Save files)
```

## Scripting API Summary (70+ Methods)

| Category | Methods | Description |
|----------|---------|-------------|
| **Player** | 8 | get_player, set_player_stat, get_base_stats, get_effective_stats, add_item, remove_item, heal_player, restore_mp |
| **Experience** | 3 | add_experience, level_up, get_level_progress |
| **Inventory** | 8 | get_inventory, get_inventory_count, clear_inventory, get_inventory_summary, sort_inventory, has_item, give_item, take_item |
| **Equipment** | 7 | get_equipped_items, equip_item, unequip_item, swap_equipment, can_equip_item, get_item_info, get_item_price |
| **Trading** | 3 | buy_item, sell_item, get_inventory_value |
| **Buffs** | 5 | apply_buff, get_active_buffs, remove_buff, clear_buffs, extend_buff |
| **Companions** | 2 | get_companions, hire_companion |
| **Game Data** | 9 | get_items_data, get_enemies_data, get_areas_data, get_companions_data, get_spells, get_missions, get_current_area, set_current_area, get_area_info |
| **Area/Exploration** | 5 | get_area_connections, get_area_enemies, add_area_enemy, remove_area_enemy, set_area_difficulty |
| **Missions** | 7 | get_mission_progress, accept_mission, complete_mission, has_mission_completed, get_mission_info, reset_mission, is_mission_available |
| **Combat** | 2 | get_combat_multipliers, set_combat_multipliers |
| **Spells** | 2 | learn_spell, get_learned_spells |
| **Statistics** | 2 | get_game_statistics, increment_statistic |
| **Validation** | 2 | is_mission_available, can_equip_item |
| **Events** | 2 | register_hook, trigger_hook |
| **Debugging** | 5 | dump_player_data, list_all_enemies, list_all_items, list_all_areas, list_all_companions |
| **Utilities** | 3 | log, get_random_item, create_custom_enemy |
| **Data Storage** | 3 | store_data, retrieve_data, clear_data |

---

## Advanced Topics

### Extending the Game

To add completely new features, you'll need to modify `main.py`:

1. **New Item Types:** Add to the item handling in the inventory system
2. **New Combat Mechanics:** Modify the `combat()` method
3. **New Spell Effects:** Update spell execution logic
4. **New Status Effects:** Extend the Character class with new attributes

### JSON Schema Overview

Each JSON file follows a dictionary/object structure:

```
{
  "identifier": {
    "property1": "value",
    "property2": 123,
    "property3": ["array", "of", "values"]
  }
}
```

All modifications must maintain this structure for the game to read the data correctly.

---

## Advanced Mechanics

### Buff System
Buffs are temporary stat modifiers that expire after a duration:
- Applied via spells or companion abilities
- Tick down each combat round
- Can provide attack/defense/speed/HP/MP bonuses
- Per-turn effects: MP regen, healing each round
- Consumed shields reduce damage before HP

### Companion Abilities
Companions execute abilities during combat with different chances:
- **attack_boost** / **rage** / **crit_boost** - Enhanced attacks
- **taunt** - Draws enemy attention, applies defense buff
- **heal** - Restore player HP
- **mp_regen** - Grant MP per turn buff
- **spell_power** - Boost magical damage
- **party_buff** - Grant team-wide stat bonuses
- **post_battle_heal** - Restore HP after victory

Each companion has an `action_chance` (0-1) to use abilities each turn.

### Shield & Absorb Mechanics
- Shields created via spells or buff abilities
- `absorb_amount` in modifiers reduces incoming damage
- Shields are consumed before HP damage is applied
- When absorbed amount reaches 0, shield expires

### Rank System
Character rank updates automatically on level-up:
- Novice (1-4) → Adept (5-9) → Veteran (10-14) → Elite (15-19) → Champion (20-29) → Legend (30+)
- Shown in character stats display alongside level
- Used for narrative/flavor (no stat bonuses yet)

---

**Happy Modding!**

For questions or issues, check the console output when running `python3 main.py` for helpful error messages.
