# Our Legacy

## Overview

Our Legacy is a text-based CLI fantasy RPG game built primarily in Python. Players create characters from 8 classes (Warrior, Mage, Rogue, Hunter, Bard, Paladin, Druid, Priest), explore interconnected areas, fight enemies and bosses, complete missions, craft items, manage companions, farm crops, build housing, and progress through dungeons. The game is entirely data-driven — all game content (classes, items, enemies, bosses, areas, spells, etc.) is defined in JSON files under the `data/` directory. The project also includes a mod system that lets users extend or override any game data, a mod downloader/uploader CLI, a global chat system, a GUI wrapper, and a static landing page. There are also serverless API endpoints (designed for Vercel) that handle chat messaging, user management, mod uploads, and an item market.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Core Game Engine (`main.py`)
- Single-file Python game engine (~thousands of lines) that handles all gameplay logic: character creation, combat, exploration, inventory, missions, crafting, dungeons, companions, farming, housing, cutscenes, weekly challenges, save/load, and more.
- All game content is loaded from JSON files in `data/`. The engine reads these at startup and merges any mod data on top.
- Save files are JSON stored in `data/saves/` with a naming convention: `{name}_{uuid}_save_{timestamp}_{class}_{level}.json`.
- The game uses ANSI color codes for terminal output. No external Python packages are required for the core game — it uses only the standard library.
- There is a language/translation system (`data/languages/`) with a config and translation key files (e.g., `en.json`). This is partially implemented — the TODO notes that translation keys need to be fully integrated into the UI.
- Time and weather systems are defined in `data/times.json` and `data/weather.json` but are still being implemented (see `TODO.md`).

### Data-Driven Design
- **All game content lives in JSON files** under `data/`. Key files:
  - `classes.json` — Character class definitions with base stats, level-up bonuses, starting items
  - `items.json` — All weapons, armor, consumables, accessories with stats, prices, rarity, level requirements
  - `enemies.json` — Regular enemy definitions with stats, loot tables, rewards
  - `bosses.json` — Boss encounters with multi-phase mechanics, special abilities, HP thresholds
  - `areas.json` — World map locations with connections, shops, available enemies/bosses, rest costs
  - `shops.json` — Shop inventories and purchase limits
  - `missions.json` — Quests with kill targets, rewards, prerequisites, area requirements
  - `spells.json` — Magic spells with MP costs, power, allowed weapons
  - `effects.json` — Status effects (poison, stun, buffs, etc.)
  - `companions.json` — Hireable party members with abilities and bonuses
  - `crafting.json` — Alchemy recipes with material requirements and skill levels
  - `dungeons.json` — Procedural dungeon definitions with room weights and boss encounters
  - `dialogues.json` — NPC and boss dialogue text
  - `cutscenes.json` — Interactive story sequences with branching choices
  - `housing.json` — Housing/decoration items with comfort points
  - `farming.json` — Crop definitions with growth times and harvest amounts
  - `weekly_challenges.json` — Recurring challenge definitions
  - `weather.json` / `times.json` — Weather and time-of-day definitions

### Mod System (`ModManager` class in `main.py`)
- Mods live in `mods/` directory, each in their own subfolder with a `mod.json` manifest.
- Mods can include any of the data JSON files to add or override game content.
- Mod data is merged with base data at load time (mod entries override base entries with matching keys).
- Mod settings (enabled/disabled) are stored in `data/mod_settings.json`.
- The `storyland.py` script downloads mods from a GitHub repository (`andy64lol/Our_Legacy_Mods`).
- The `storywrite.py` script uploads mods to the same repository via a Vercel API endpoint.

### Launcher (`launcher.py`)
- Simple CLI launcher that lets users choose between: main game, mod downloader (storyland), mod uploader (storywrite), chat, or credits.
- Uses subprocess to run each module.

### GUI Wrapper (`gui_all.py` + `py2gui.py`)
- `py2gui.py` is a custom tkinter-based terminal emulator GUI framework that replaces `print()` and `input()` with GUI equivalents.
- `gui_all.py` wraps the launcher and all modules into a single GUI experience by monkey-patching print/input.
- Strips ANSI color codes for GUI display.

### Chat System (`chat.py`)
- CLI-based global chat client that communicates with a GitHub-backed chat API.
- Uses the serverless API endpoints for sending/receiving messages.

### Serverless API (`api/` directory)
- Designed for deployment on **Vercel** as serverless functions (Node.js/ES modules).
- `api/ping.js` — Health check endpoint.
- `api/send_message.js` — Global chat: reads/writes messages to `global_chat.json` in a GitHub repo (`andy64lol/globalchat`). Includes profanity filtering and message archival when exceeding 100 messages.
- `api/create_user.js` — User management: reads/writes `users.json` in the same GitHub repo.
- `api/upload_test.js` — Mod upload endpoint: uploads mod files to a GitHub repo with profanity checking.
- `api/market.js` — Item market API: reads from `api/data/items.json` and supports filtering by type, rarity, etc.
- All GitHub interactions use a `GITHUB_REST_API` environment variable for authentication.
- The project uses `@supabase/supabase-js` and `octokit` as Node.js dependencies (see `package.json`), though Supabase doesn't appear actively used in the visible code.

### Static Landing Page (`index.html`)
- Single-page HTML/CSS site for the game's web presence and download links.

### File Structure Summary
```
main.py              — Core game engine (Python)
launcher.py          — CLI launcher
chat.py              — Global chat client
storyland.py         — Mod downloader
storywrite.py        — Mod uploader
gui_all.py           — GUI wrapper
py2gui.py            — Custom tkinter GUI framework
index.html           — Landing page
data/                — All game content JSON files
data/saves/          — Player save files
data/languages/      — Translation files
mods/                — User mods directory
api/                 — Vercel serverless functions (Node.js)
api/data/            — API-specific data files
utilities/           — Utility modules (dice roller)
```

## External Dependencies

### Python (Core Game)
- **No external packages required** — uses only Python 3.9+ standard library (json, os, random, sys, time, uuid, datetime, difflib, signal, traceback, io, tkinter for GUI).
- `requests` is used by `chat.py`, `storyland.py`, and `storywrite.py` for HTTP calls.

### Node.js (API Layer)
- `@supabase/supabase-js` ^2.39.0 — Supabase client (declared but not visibly used in current code)
- `octokit` ^3.2.2 — GitHub API client (declared in package.json)
- API functions use native `fetch()` directly for GitHub API calls rather than octokit.

### External Services
- **GitHub REST API** — Used as a backend data store for chat messages, user data, and mod uploads. Repos: `andy64lol/globalchat` (chat + users), `andy64lol/Our_Legacy_Mods` (mod repository). Requires `GITHUB_REST_API` environment variable with a valid token.
- **Vercel** — Target deployment platform for the `api/` serverless functions.
- **Profanity Filter** — Fetches word list from `https://raw.githubusercontent.com/zautumnz/profane-words/master/words.json` at runtime for chat and mod upload filtering.

### Environment Variables
- `GITHUB_REST_API` — GitHub personal access token used by all API endpoints for repository read/write access.