# Our Legacy - Replit Agent Guide

## Overview

Our Legacy is a text-based CLI fantasy RPG game built primarily in Python. Players create characters from 8 classes (Warrior, Mage, Rogue, Hunter, Bard, Paladin, Druid, Priest), explore areas, fight enemies and bosses, complete missions, craft items, manage companions, farm crops, build housing, and run dungeons. The game is entirely data-driven through JSON files, with a robust mod system that lets users extend or override any game data. It also includes a launcher, a global chat system, a mod downloader (Storyland), a mod uploader (Storywrite), and a GUI wrapper (Py2GUI). A set of serverless API endpoints (Vercel) handle mod uploads, global chat, and a market API.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Core Game Engine (`main.py`)
- **Single-file Python application** containing the full RPG game loop: character creation, exploration, combat, inventory, quests, crafting, companions, dungeons, farming, housing, cutscenes, and save/load.
- **Data-driven design**: All game content (classes, items, enemies, bosses, areas, missions, spells, effects, crafting recipes, dungeons, companions, dialogues, cutscenes, housing, farming, weather, weekly challenges, shops) is defined in JSON files under `data/`.
- **ModManager class** loads mods from `mods/` directory. Each mod has a `mod.json` metadata file and can include any data JSON file. Mod data is merged with base data at load time, allowing additions and overrides.
- **Localization**: Multi-language support via `data/languages/` with a config file and translation JSON files (English included, with slots for 10 languages).
- **Save system**: JSON-based saves stored in `data/saves/` with naming pattern `{name}_{uuid}_save_{timestamp}_{class}_{level}.json`.

### Launcher (`launcher.py`)
- Simple CLI menu that launches the main game, Storyland (mod downloader), Storywrite (mod uploader), or chat via subprocess calls.

### GUI Wrapper (`gui_all.py` + `py2gui.py`)
- `py2gui.py` is a custom tkinter-based terminal emulator GUI library that replaces `print()` and `input()` with GUI equivalents.
- `gui_all.py` wraps the launcher and all modules into a single GUI experience by monkey-patching builtins.

### Chat System (`chat.py`)
- CLI chat client that connects to the global chat API. Uses ANSI colors, threading for real-time updates, and readline for input.

### Mod Ecosystem
- **Storyland** (`storyland.py`): Downloads mods from GitHub repo `andy64lol/Our_Legacy_Mods` via GitHub API.
- **Storywrite** (`storywrite.py`): Uploads mods to the repository via a Vercel API endpoint.

### Serverless API (`api/` directory)
- **Deployed on Vercel** as serverless functions (JavaScript ES modules).
- `api/ping.js` - Health check endpoint.
- `api/send_message.js` - Global chat: reads/writes messages to `andy64lol/globalchat` GitHub repo. Includes profanity filtering and message archival (max 100 messages).
- `api/create_user.js` - User management: creates/reads users stored in the same GitHub repo.
- `api/upload_test.js` - Mod upload: pushes mod files to GitHub repo with profanity checking.
- `api/market.js` - Item market API: reads from `api/data/items.json` and filters by type/rarity/class/level.
- All API functions use **GitHub REST API** with a `GITHUB_REST_API` environment variable for authentication.

### Data File Architecture
All game content lives in `data/` as flat JSON files:
| File | Purpose |
|------|---------|
| `classes.json` | Character class definitions with stats and progression |
| `items.json` | All equipment, consumables, materials |
| `enemies.json` | Regular enemy definitions |
| `bosses.json` | Boss encounters with phases and special abilities |
| `areas.json` | World map locations and connections |
| `shops.json` | Shop inventories per location |
| `missions.json` | Quest definitions with prerequisites |
| `spells.json` | Magic spells with weapon restrictions |
| `effects.json` | Status effects (poison, stun, buffs) |
| `companions.json` | Hireable companion NPCs |
| `crafting.json` | Alchemy recipes |
| `dialogues.json` | NPC/boss dialogue strings |
| `dungeons.json` | Procedural dungeon definitions |
| `cutscenes.json` | Interactive story sequences |
| `housing.json` | Housing/decoration items |
| `farming.json` | Crop definitions |
| `weather.json` | Weather types and bonuses |
| `weekly_challenges.json` | Recurring challenge definitions |

### Key Design Decisions
- **No database**: Everything is file-based JSON. Saves, game data, and even the chat/user systems use GitHub repos as storage via API.
- **Mod merging over replacement**: Mods merge their JSON data with base data rather than replacing it, so multiple mods can coexist.
- **Subprocess isolation**: The launcher runs each module (game, chat, storyland, storywrite) as a separate subprocess to avoid state conflicts.
- **Weather/Time system**: Partially implemented (TODO.md tracks progress). Weather data exists in `data/weather.json` but full integration is in progress.

## External Dependencies

### Python Dependencies
- **Standard library only** for the core game: `json`, `os`, `random`, `sys`, `time`, `uuid`, `datetime`, `difflib`, `signal`, `traceback`, `io`
- `requests` - Used by storyland.py, storywrite.py, and chat.py for HTTP calls
- `tkinter` - Used by py2gui.py for the GUI wrapper
- `readline` - Used by chat.py for input handling

### Node.js / JavaScript Dependencies
- `@supabase/supabase-js` (^2.95.3) - Listed in package.json but not visibly used in current API code
- `octokit` (^3.2.2) - Listed in package.json but API files use raw fetch with GitHub REST API instead

### External Services
- **GitHub REST API**: Core backend storage for chat messages, user data, and mod uploads. Requires `GITHUB_REST_API` environment variable (personal access token).
  - Repo `andy64lol/globalchat` - Stores chat messages (`global_chat.json`) and users (`users.json`)
  - Repo `andy64lol/Our_Legacy_Mods` - Stores community mods
- **Vercel**: Hosts the serverless API functions in the `api/` directory
- **Profanity filter**: Fetches word list from `github.com/zautumnz/profane-words` at runtime for chat and mod upload filtering

### Running the Project
- **Main game**: `python3 main.py`
- **Launcher**: `python3 launcher.py`
- **GUI version**: `python3 gui_all.py`
- **Chat**: `python3 chat.py`
- **Mod downloader**: `python3 storyland.py`
- **Mod uploader**: `python3 storywrite.py`
- **npm start**: Runs `python3 main.py`