# Our Legacy - Text-Based CLI Fantasy RPG

## Overview
A comprehensive text-based CLI fantasy RPG game served through a web terminal interface. The Flask app provides a browser-based terminal (using xterm.js) that runs the Python RPG game via a pseudo-terminal.

## Project Architecture
- **flask_app/app.py**: Flask web server serving the terminal UI on port 5000
- **flask_app/templates/index.html**: Web terminal interface using xterm.js
- **main.py**: Core RPG game logic (classes, combat, dungeons, items, etc.)
- **launcher.py**: Game launcher/menu system
- **chat.py / chat.js / chat.html**: Chat functionality
- **storyland.py / storywrite.py**: Story creation and management
- **data/**: JSON data files for game content (items, enemies, areas, spells, etc.)
- **utilities/**: Helper modules (dice, settings)
- **api/ & functions/**: Node.js API endpoints (Supabase integration)

## Tech Stack
- **Backend**: Python 3.11, Flask
- **Frontend**: HTML/JS with xterm.js terminal emulator
- **Dependencies**: flask, requests (Python); @supabase/supabase-js, octokit (Node.js)

## Running
- The Flask app runs on `0.0.0.0:5000`
- Workflow: `python flask_app/app.py`
