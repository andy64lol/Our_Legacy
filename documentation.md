# Our Legacy - Complete Modding Documentation

This guide covers how to modify every aspect of the Our Legacy RPG game. All game content is stored in JSON files located in the `data/` directory, and logic can be extended via the JavaScript Scripting API.

---

## Table of Contents
1. [File Overview](#file-overview)
2. [Modifying Data (JSON)](#modifying-data)
3. [Scripting API (JavaScript)](#scripting-api)
4. [Tips & Best Practices](#tips--best-practices)

---

## File Overview

All modifiable game content is stored in `/data/`:
- **classes.json**: Player character classes and starting stats.
- **items.json**: Weapons, armor, offhand items, accessories, and consumables.
- **companions.json**: Companion definitions and purchasable companions.
- **enemies.json**: Regular enemies.
- **bosses.json**: Bosses with multi-phase abilities.
- **areas.json**: Map locations, shops, and connections.
- **missions.json**: Quests and objectives.
- **effects.json**: Combat status effects.

---

## Modifying Data

### Classes (`data/classes.json`)
Modify base stats, level-up bonuses, and starting equipment for each class.

### Items (`data/items.json`)
Define items and filter them into shops using the `shops` array matching area shop IDs.

### Bosses (`data/bosses.json`)
Configure HP thresholds for phase transitions and special abilities. Note that bosses have an **8-hour real-time cooldown** after defeat.

---

## Scripting API

The game now supports a JavaScript-based scripting system located in the `scripts/` directory. This allows you to hook into game events and automate actions.

### How it Works
1. Scripts are placed in the `scripts/` folder.
2. `scripts/scripts.json` defines which scripts are active.
3. `main.py` synchronizes game state to `scripts/activities.json`.
4. The JavaScript engine executes scripts, and they communicate back to the game by updating the activities log.

### API Reference
For a full list of functions available to scripts (including `player`, `enemy`, `battle`, `map`, and `events`), please refer to the [Scripting API Documentation](new_scripting.md).

### Example Script
See `scripts/example.js` for a comprehensive demonstration of:
- Importing the API.
- Printing to the console.
- Modifying player stats and inventory.
- Listening for and emitting events.

---

## Tips & Best Practices
- **Backup Saves**: Keep backups of `data/saves/` when testing new mods.
- **Validation**: Ensure all JSON files are valid to prevent game crashes.
- **Script Efficiency**: Scripts run frequently, so avoid heavy computations in the global scope of your scripts.
- **Activity Log**: Use `getActivityCount()` to monitor how many actions your scripts are performing.
