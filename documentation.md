# Our Legacy - Complete Modding Documentation

This guide covers how to modify every aspect of the Our Legacy RPG game. All game content is stored in JSON files located in the `data/` directory, and logic can be extended via the JavaScript Scripting API.

---

## Table of Contents
1. [File Overview](#file-overview)
2. [Modifying Data (JSON)](#modifying-data)
3. [Mod Downloader CLI](#mod-downloader-cli)
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

## Mod Downloader CLI

The mod downloader (`mod_downloading.py`) is a Python CLI tool for browsing and downloading mods from the GitHub repository.

### Features
- **Paginated Display**: Shows 10 mods per page with navigation
- **Colored Output**: Cyan titles, yellow mod numbers, white names, green success messages, red errors
- **Screen Clearing**: Clears terminal after each action
- **Navigation Commands**:
  - `n` or `next` - Go to next page
  - `p` or `prev` - Go to previous page
  - `#` (number) - Select and download a mod
  - `q` or `quit` - Exit the application

### Usage
```bash
python3 mod_downloading.py
```

### Configuration
The downloader connects to: `https://github.com/andy64lol/Our_Legacy_Mods`
- Mods are stored in the `mods/` branch
- Downloaded mods are saved to the local `mods/` directory

---

## Tips & Best Practices
- **Backup Saves**: Keep backups of `data/saves/` when testing new mods.
- **Validation**: Ensure all JSON files are valid to prevent game crashes.
- **Script Efficiency**: Scripts run frequently, so avoid heavy computations in the global scope of your scripts.
- **Activity Log**: Use `getActivityCount()` to monitor how many actions your scripts are performing.
