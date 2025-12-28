# Our Legacy - Complete Modding Documentation

This guide covers how to modify every aspect of the Our Legacy RPG game. All game content is stored in JSON files located in the `data/` directory for easy customization.

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
9. [Modifying Game Code](#modifying-game-code)
10. [Tips & Best Practices](#tips--best-practices)

---

## File Overview

All modifiable game content is stored in JSON files in `/data/`:

- **classes.json** - Player character classes with stats and starting items
- **items.json** - Weapons, armor, accessories, and consumables
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

- **type** - Type of item (consumable, weapon, armor, accessory)
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

## Troubleshooting

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
├── main.py              (Game code)
├── README.md
├── documentation.md     (This file)
├── TODO.md
└── data/
    ├── classes.json     (Player classes)
    ├── items.json       (Equipment & consumables)
    ├── enemies.json     (Regular enemies)
    ├── bosses.json      (Boss enemies)
    ├── areas.json       (Game world locations)
    ├── spells.json      (Magic spells)
    ├── missions.json    (Quests)
    └── saves/           (Save files)
```

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

**Happy Modding!** 🎮✨

For questions or issues, check the console output when running `python3 main.py` for helpful error messages.
