# Our Legacy - Fantasy RPG

A comprehensive text-based CLI Fantasy RPG built in Python, with a parallel JavaScript port for browser play.

## Features
- 8 character classes with unique stats and abilities.
- Turn-based combat system with HP/MP bars displayed at the start of each turn.
- Exploration across multiple areas including Starting Village and Dark Forest.
- Crafting and Alchemy systems for potions and equipment.
- Mod support via JSON files.

## Project Structure
- `main.py`: Python entry point (Terminal).
- `game.html`: Browser entry point (Web).
- `main.js`: Core JavaScript engine for the browser port.
- `utilities/`: Python game logic (Battle, Character, etc.).
- `utilities_js/`: JavaScript game logic mirroring Python functionality.
- `data/`: Game data and configuration (JSON).

## How to Play
- **Terminal**: Run `python main.py`.
- **Browser**: Open `index.html` and click "Play in Browser" or navigate directly to `game.html`.
