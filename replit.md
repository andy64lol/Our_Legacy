# Our Legacy - Text-Based CLI Fantasy RPG

## Overview

"Our Legacy" is a text-based CLI fantasy RPG game built with Python, featuring exploration, combat, crafting, and a modular data-driven architecture. The game supports 5 character classes (Warrior, Mage, Rogue, Hunter, Bard), 7+ explorable areas, an alchemy/crafting system, companion recruitment, boss battles with multi-phase mechanics, and a JavaScript scripting engine for extensibility.

All game content is defined in JSON files, making the game highly moddable without code changes.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Core Game Engine
- **Language**: Python 3 (`main.py` is the single entry point)
- **Data-Driven Design**: All game content (classes, items, enemies, areas, missions, etc.) is stored in JSON files under `/data/`
- **CLI Interface**: Terminal-based with ANSI color support for text formatting

### Data Layer (`/data/`)
| File | Purpose |
|------|---------|
| `classes.json` | Character class definitions with base stats and level-up bonuses |
| `items.json` | Weapons, armor, consumables, accessories, and materials |
| `enemies.json` | Regular enemy definitions with stats and loot tables |
| `bosses.json` | Boss definitions with multi-phase abilities and HP thresholds |
| `areas.json` | Map locations with connections, shops, and enemy spawns |
| `missions.json` | Quest definitions with objectives and rewards |
| `companions.json` | Hireable companion definitions |
| `crafting.json` | Alchemy recipes and material requirements |
| `effects.json` | Status effect definitions (buffs, debuffs, DoTs) |
| `spells.json` | Spell definitions with weapon requirements |
| `config.json` | Game configuration and scripting settings |

### Scripting System (`/scripts/`)
- **Engine**: JavaScript (Node.js) via subprocess execution from Python
- **State Sync**: `activities.json` bridges Python game state with JavaScript scripts
- **API**: `scripting_API.js` provides player, battle, map, and menu manipulation functions
- **Custom Buttons**: `buttons.json` defines script-triggered menu actions

### Save System
- Save files stored in `/data/saves/` as JSON
- Naming convention: `{player}_{uuid}_save_{timestamp}_{class}_{level}.json`
- Autosave capability configured in `config.json`

### API Layer (`/api/`)
- Serverless-style API handlers (designed for potential Vercel/similar deployment)
- `ping.js` - Health check endpoint
- `market.js` - Item data API with filtering capabilities
- Duplicates item data in `/api/data/` for API isolation

## External Dependencies

### Python Dependencies
- **requests** (optional) - HTTP client for market API integration; falls back to `urllib` if unavailable
- **readline** (optional) - Tab completion for CLI; best-effort import

### Node.js/JavaScript
- **ES Modules** - Package configured with `"type": "module"`
- **fs/path** - Node.js built-ins for file operations in scripts
- Scripts communicate with Python via JSON file I/O (`activities.json`)

### Storage
- All data persists to local JSON files
- No external database required
- Save files and game state stored on filesystem

### Third-Party Services
- None required for core gameplay
- API layer designed for optional serverless deployment but works standalone