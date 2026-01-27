# Our Legacy - Text-Based CLI Fantasy RPG Game

## Overview

"Our Legacy" is a comprehensive text-based CLI fantasy RPG game focused on exploration, grinding, and adventure. Built with Python and driven by modular JSON data, the game offers a rich, extensible experience for players and modders alike. Now featuring a powerful **JavaScript Scripting Engine** powered by Node.js and a new **Alchemy & Crafting** system.

## Features

### Core Gameplay
- **Character Classes**: Choose from **Warrior**, **Mage**, **Rogue**, **Hunter**, or the new **Bard** class.
- **Exploration**: 7 diverse areas including the Starting Village, Dark Forest, Ancient Ruins, and more.
- **Alchemy & Crafting**: Collect materials from monsters and the environment to brew potent potions or forge powerful equipment.
- **Grinding System**: Level up through combat, gaining stats and unlocking new equipment.
- **Mission System**: Complete main story and side quests for gold and experience rewards.
- **Boss Battles**: Face legendary bosses like the **Ancient Fire Dragon** with multi-phase mechanics and HP thresholds.
- **Scripting Engine**: Extend and automate your journey using JavaScript (Node.js).

### Advanced Systems
- **Companions**: Hire unique companions at the Tavern with active abilities and passive party bonuses.
- **Buff & Effect System**: Manage temporary status effects, magical shields, and per-turn HP/MP regeneration.
- **Offhand & Accessories**: Deep equipment customization with dedicated offhand slots and up to 3 accessory slots.
- **Real-time Cooldowns**: Bosses feature an 8-hour real-time cooldown after defeat.

## Character Classes

| Class | Description | Key Stats | Starting Gear |
|-------|-------------|-----------|---------------|
| **Warrior** | Strong melee fighter | High HP & Defense | Iron Sword, Leather Armor |
| **Mage** | Powerful spellcaster | High MP & Magic | Wooden Wand, Cloth Tunic |
| **Rogue** | Agile assassin | High Speed & Crit | Steel Dagger, Leather Armor |
| **Hunter** | Experienced tracker | High Attack & Aim | Hunter's Bow, Hunting Knife |
| **Bard** | Master of melodies | High Speed & Support | Enchanting Lute, Colourful Robe |

## Alchemy & Crafting

The new Crafting system allows you to create items using materials gathered during your travels.

### Material Collection
Materials are found by defeating enemies or exploring specific areas:
- **Ores**: Iron Ore, Coal, Steel Ingot, Gold Nugget.
- **Herbs**: Herbs, Mana Herbs, Spring Water.
- **Crystals**: Crystal Shards, Dark Crystals, Fire Gems.
- **Monster Parts**: Goblin Ears, Orc Teeth, Wolf Fangs, Venom Sacs.
- **Magical**: Phoenix Feathers, Dragon Scales, Ancient Relics.

### Alchemy Recipes
- **Potions**: Brew Health and Mana potions (Basic to Greater), or specialized Frost Potions.
- **Elixirs**: Create powerful boosters like the *Elixir of Giant Strength*.
- **Enchantments**: Forge weapons and armor like *Steel Daggers* or *Swamp Scale Armor*.
- **Utility**: Craft Luck Charms or extract pure Elemental Essences into Gems.

## Installation & Setup

### Prerequisites
- **Python 3.9+**

### Quick Start
```bash
python3 main.py
```

## Game Controls

### Main Menu
- **Explore**: Engage in random encounters and collect crafting materials.
- **Inventory**: Manage items and access the **Crafting** menu.
- **View Character**: Check stats, equipment, and active buffs.
- **Travel**: Move between connected world areas.
- **Missions**: Track and accept quests.
- **Tavern**: Hire and manage your party members.
- **Shop**: Trade gold for gear and items.
- **Save/Load**: Persist your progress to JSON save files.

## File Structure

```
Our_Legacy/
├── launcher.py             # Unified launcher for all
├── storyland.py            # The place where you download mods
├── storywrite.py           # Where you submit mods
├── main.py                 # Core game engine (Unified Python script)
├── README.md               # Game overview and quick start guide
├── documentation.md        # Comprehensive modding and mechanics guide
├── package.json            # Node.js project configuration
├── data/                   # Game Content (Modular JSON)
│   ├── classes.json        # Player character class definitions
│   ├── items.json          # Equipment, weapons, and consumables
│   ├── crafting.json       # Alchemy recipes and material types
│   ├── areas.json          # World map, shops, and connections
│   ├── enemies.json        # Regular combat encounters
│   ├── bosses.json         # Boss mechanics and phase definitions
│   ├── missions.json       # Quest objectives and rewards
│   ├── spells.json         # Magic system and weapon requirements
│   ├── effects.json        # Status effect definitions
│   ├── config.json         # Global game engine configuration
│   ├── dialogues.json      # Dialogues for bosses
│   └── saves/              # Player save files (.json)
├── mods/                   # installed mods
└── LICENSE                 # Project license
```

---
**Forge your destiny and leave behind a legend that will never be forgotten!**
