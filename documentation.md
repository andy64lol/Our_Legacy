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
9. [Scripting API](#scripting-api)
10. [Tips & Best Practices](#tips--best-practices)

---

## File Overview

All modifiable game content is stored in JSON files in `/data/`:

- **classes.json** - Player character classes with stats and starting items
- **items.json** - Weapons, armor, offhand items, accessories, and consumables
- **companions.json** - Companion definitions and purchasable companions (hired at the tavern)
- **enemies.json** - Regular enemies that appear in combat
- **bosses.json** - Boss enemies with special abilities and phases
- **areas.json** - Game world locations, shop definitions, and connections
- **spells.json** - Magic spells that can be cast in battle
- **missions.json** - Quests that players can undertake
- **effects.json** - Status effects for combat
- **config.json** - General game settings (Difficulty, Scripting, etc.)

---

## Game Menus & Structure

### Main Menu
1. **Explore** - Encounter regular enemies and find gold in the current area.
2. **View Character** - Check your stats, equipment, and active buffs.
3. **Travel** - Move to connected areas.
4. **Inventory** - Manage your items and equip gear.
5. **Missions** - View quests and progress.
6. **Fight Boss** - A dedicated menu to challenge the bosses of the current area.
7. **Tavern** - Hire companions.
8. **Shop** - Buy and sell items (area-specific).
9. **Rest** - Restore HP and MP for a small gold fee.
10. **Companions** - Manage your party.
11-13. **System** - Save, Load, and Claim Rewards.

### Mission Menu
- **Available Missions** - List of quests you can accept.
- **Active Missions** - Current objectives and progress tracking.

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

---

## Modifying Items & Shops

**File:** `data/items.json`

Items are filtered by area-specific shop IDs.

### Shop Filtering
In `data/areas.json`, areas define which shops are available:
```json
"starting_village": {
  "shops": ["general_store"]
}
```
In `data/items.json`, items define where they are sold:
```json
"Health Potion": {
  "type": "consumable",
  "shops": ["general_store", "alchemist"]
}
```

---

## Modifying Bosses

**File:** `data/bosses.json`

Bosses feature multi-phase combat and cooldowns.

### Boss Structure
```json
{
  "fire_dragon_boss": {
    "name": "Ancient Fire Dragon",
    "hp": 300,
    "attack": 35,
    "defense": 20,
    "speed": 15,
    "phases": [
      {
        "hp_threshold": 0.5,
        "description": "The dragon glows with intense heat!",
        "attack_multiplier": 1.5
      }
    ],
    "special_abilities": [...]
  }
}
```
**Note:** Bosses have an 8-hour cooldown (real-time) after being defeated before they can be challenged again.

---

## Combat Interface

The Battle UI displays:
- **HP Bars**: Visual health status for player and enemy.
- **MP Bar**: Visual mana tracking for casting spells.
- **Turn Order**: Determined by the Speed stat (including buffs).
- **Actions**: Attack, Item, Defend, Flee, and Cast Spell (if a magic weapon is equipped).

---

## Scripting API

[Go to new_scripting.md for more info](new_scripting.md).
