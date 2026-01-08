<path>home/andy64lolxd/Our_Legacy/README.md</path>
<parameter name="content"># Our Legacy - Text-Based CLI Fantasy RPG Game</parameter>

## Overview

"Our Legacy" is a comprehensive text-based CLI fantasy RPG game focused on exploration, grinding, and adventure. Create your character, explore diverse areas, complete missions, and face powerful bosses to forge your legendary legacy!

## Features

### Core Gameplay
- **Character Classes**: Choose from Warrior, Mage, Rogue, or Hunter
- **Exploration**: 7 unique areas to discover and conquer
- **Grinding System**: Level up your character through combat
- **Mission System**: Complete quests for rewards and progression
- **Boss Battles**: Face powerful enemies with special abilities
- **Economy**: Gold system with shops and trading

### Areas to Explore
1. **Starting Village** - Your humble beginning
2. **The Rusty Tankard (Tavern)** - Hire companions and hear rumors
2. **Dark Forest** - Home to goblins and wolves
3. **Deep Woods** - Orcs and dark magic lurk here
4. **Ancient Ruins** - Bandits and skeletons await
5. **Underground Tombs** - Undead warriors guard secrets
6. **Crystal Caves** - Ice elementals dominate
7. **Dragon's Lair** - The ultimate challenge

### Combat System
- Turn-based battles with strategic depth
- Experience gain and character progression
- Loot drops from defeated enemies
- Special abilities and magic spells
- Dynamic difficulty scaling

### Economy & Loot
- Gold currency for all transactions
- Shop system for equipment and consumables
- Random loot drops from enemies
- Equipment progression system
- Valuable materials collection

### Companions & Tavern
- **Tavern** - Hire companions to join your party (up to 4 active)
- **Companion Classes** - Fighter, Scout, Mage, Support, Guardian, Berserker, Cleric, Assassin, Strategist
- **Companion Ranks** - Common, Uncommon, Rare, Epic, Legendary (higher rank = stronger bonuses)
- **Active Companion Abilities** - Companions use special abilities in battle (attacks, heals, buffs, taunt, MP regen)
- **Direct Combat Help** - Each companion has a chance to act each turn (not just once per battle)
- **Post-Battle Healing** - Some companions restore HP after victory
- **Passive Bonuses** - Attack, defense, speed, healing, and MP bonuses always active

### Mission System
- Main story quests
- Side missions for extra rewards
- Kill missions to prove your strength
- Collection quests for materials
- Progressive difficulty unlocking

### Rank & Progression System
- **Novice** (Level 1-4): Starting rank
- **Adept** (Level 5-9): Improving skills
- **Veteran** (Level 10-14): Battle-hardened
- **Elite** (Level 15-19): Master warrior
- **Champion** (Level 20-29): Legendary combatant
- **Legend** (Level 30+): Ultimate power

### Buff & Effect System
- **Temporary Buffs**: Apply stat boosts, healing, MP regen, and more with durations
- **Shield/Absorb**: Magical shields absorb incoming damage before HP
- **Per-Turn Effects**: Buffs like MP regen and healing apply each combat round
- **Buff Expiration**: Automatically expire and recalculate stats when duration ends
- **Spell Buffs**: Magic spells cast from weapons apply temporary buffs instead of permanent changes

### Boss Battles
- **Ancient Fire Dragon** - The ultimate boss
- **Troll King** - Massive underground ruler
- **Shadow Lord** - Dark entity of ancient ruins
- **Ice Queen** - Ethereal ruler of crystal caves
- **Orc Chieftain** - Brutal clan leader

## Installation & Setup

### Prerequisites
- Python 3.6 or higher
- No additional dependencies required

### Quick Start
```bash
# Navigate to the game directory
cd /home/andy64lolxd/Our_Legacy

# Run the game
python3 main.py
```

### Custom Scripts

Create Python scripts in the `scripts/` directory to extend gameplay. See [documentation.md](documentation.md#scripting-api) for the Scripting API reference and examples.

## Game Controls

### Main Menu Options
1. **Explore** - Enter the current area for random encounters
2. **View Character** - Check your stats and progression
3. **Travel** - Move between connected areas
4. **Inventory** - Manage your items and equipment (equip offhand & accessories)
5. **Missions** - View and accept available quests
6. **Tavern** - Hire companions (companions are purchased here)
7. **Shop** - Buy and sell items for gold
8. **Rest** - Pay to recover HP/MP in safe areas
9. **Save Game** - Save your progress
10. **Load Game** - Continue a saved adventure
11. **Claim Rewards** - Collect completed mission rewards
12. **Quit** - Exit the game

### Combat Controls
1. **Attack** - Standard melee attack
2. **Use Item** - Consume potions or items
3. **Defend** - Reduce incoming damage
4. **Flee** - Attempt to escape from battle

## Character Classes & Ranks

### Warrior
- **Stats**: High HP and Defense, balanced Attack
- **Strengths**: Excellent survivability, reliable damage
- **Best For**: New players, tank builds
- **Equipment Focus**: Heavy armor, swords, shields
- **Rank Progression**: Novice > Adept > Veteran > Elite > Champion > Legend

### Mage
- **Stats**: High MP and magical power, low HP
- **Strengths**: Powerful spells, area effects, buff casting
- **Best For**: Strategic players, spell builds
- **Equipment Focus**: Staves, robes, magical items
- **Rank Progression**: Novice > Adept > Veteran > Elite > Champion > Legend

### Rogue
- **Stats**: High Speed and agility, balanced stats
- **Strengths**: Fast attacks, critical strikes, evasiveness
- **Best For**: Experienced players, hit-and-run tactics
- **Equipment Focus**: Light armor, daggers, speed items
- **Rank Progression**: Novice > Adept > Veteran > Elite > Champion > Legend

### Hunter
- **Stats**: High Speed and accuracy, balanced combat stats
- **Strengths**: Ranged attacks, tracking abilities, versatile weapons
- **Best For**: Strategic players, ranged combat specialists
- **Equipment Focus**: Bows, crossbows, spears, hunting knives
- **Rank Progression**: Novice > Adept > Veteran > Elite > Champion > Legend

## Equipment System

### Weapon Types
- **Swords** - Balanced damage and speed
- **Daggers** - Fast attacks, critical strikes
- **Staves** - Magical enhancement, MP bonus
- **Greatswords** - Massive damage, slower attacks
- **Bows** - Ranged attacks, high precision (Hunter exclusive)
- **Crossbows** - Powerful ranged attacks, slower reload (Hunter exclusive)
- **Spears** - Reach advantage, versatile melee (Hunter & Warrior)
- **Hunting Knives** - Fast melee, critical strikes (Hunter & Rogue)

### Armor Types
- **Leather** - Light protection, speed bonus
- **Chain Mail** - Good defense, slight speed penalty
- **Robes** - Magical enhancement, light protection
- **Dragon Scale** - Ultimate protection, special resistances

### Item Rarity
- **Common** - Basic items, easy to find
- **Uncommon** - Better stats, moderate price
- **Rare** - Powerful equipment, expensive
- **Legendary** - Ultimate items, very rare

### Offhand & Accessories
- **Offhand** - New item type used in the offhand slot (shields, tomes, small focuses). Offhand items grant defense, MP, or other utility bonuses and are equipped separately from weapons.
- **Accessories** - You can equip up to **three** accessories simultaneously. Accessories grant small stat bonuses and unique passive effects (rings, charms, amulets).

### Buffs & Temporary Effects
- **Stat Boosts** - Temporarily increase attack, defense, speed, HP, or MP (with duration)
- **Shields/Absorb** - Magical shields that absorb damage before HP loss
- **Per-Turn Healing** - Regenerate HP each combat round
- **MP Regeneration** - Restore MP each combat round
- **Spell Power** - Increase magic damage output
- **Party Buffs** - Companion-granted bonuses affecting your stats

## Tips for Success

### General Strategy
1. **Start Strong** - Choose a class that fits your playstyle
2. **Explore Early** - Find equipment and level up
3. **Complete Missions** - They provide excellent rewards
4. **Manage Resources** - Don't waste potions or gold
5. **Save Frequently** - Progress can be lost if defeated

### Combat Tips
1. **Know Your Enemy** - Different enemies require different strategies
2. **Use Items Wisely** - Save powerful potions for tough battles
3. **Level Appropriately** - Don't fight bosses too early
4. **Defend Strategically** - Use when facing strong attacks
5. **Manage Buffs** - Check active buffs to plan spell casts
6. **Companion Abilities** - Stronger companions use more powerful abilities
7. **Flee When Needed** - Sometimes retreat is the best option
8. **Equip Shields** - Shields provide damage absorption before HP loss

### Economy Tips
1. **Sell Junk** - Keep inventory clean by selling low-value items
2. **Buy Early** - Good equipment makes a big difference
3. **Hire Companions** - Companion bonuses are worth the cost
4. **Upgrade Gradually** - Don't waste gold on marginal improvements
5. **Collect Materials** - Some missions require specific items
6. **Shop Around** - Compare prices in different areas

## Companion Directory

| Name | Class | Rank | Special Ability | Cost | Notes |
|------|-------|------|-----------------|------|-------|
| Borin the Brave | Fighter | Common | Shield Bash (taunt) | 100g | Starting-friendly |
| Lyra the Swift | Scout | Uncommon | Quick Strike (atk+) | 120g | Speed boost |
| Eldon the Wise | Mage | Rare | Arcane Insight (mp/turn) | 150g | MP regeneration |
| Mira the Healer | Support | Rare | Tend Wounds (heal) | 140g | Active healing |
| Tharos the Bulwark | Guardian | Epic | Hold The Line (taunt) | 350g | Strong defense |
| Seraphine the Arcane | Mage | Epic | Arcane Surge (spell+) | 400g | Magic boosting |
| Ragnar the Warlord | Berserker | Legendary | Rage (attack++) | 420g | Highest attack |
| Astra the Lifegiver | Cleric | Legendary | Sanctuary (post-heal) | 450g | Best healer |
| Nyx the Shadow | Assassin | Rare | Backstab (crit++) | 220g | Critical damage |
| Galen the Tactician | Strategist | Uncommon | Inspire (party buff) | 160g | Team support |

## Mission Guide

### Early Game Missions
1. **First Steps** - Defeat 3 goblins (Level 1+)
2. **Wolf Problem** - Clear 5 wolves (Level 2+)
3. **Trading Favor** - Collect trade goods (Level 2+)

### Mid Game Missions
1. **Orc Menace** - Defeat 3 orcs (Level 3+)
2. **Lost Relic** - Retrieve ancient artifact (Level 4+)
3. **Undead Rising** - Clear 5 skeletons (Level 4+)

### Late Game Missions
1. **Crystal Protector** - Defeat Ice Elementals (Level 5+)
2. **Troll Bane** - Defeat the Troll King (Level 6+)
3. **Dragon's End** - Face the Ancient Fire Dragon (Level 8+)

## File Structure

```
Our_Legacy/
├── main.py                 # Core game engine
├── README.md              # This file
├── data/                  # Game data directory
│   ├── enemies.json       # Enemy definitions and stats
│   ├── areas.json         # World areas and connections
│   ├── items.json         # Equipment, offhand, accessories, and consumables
│   ├── companions.json    # Companion definitions and purchasable companions
│   ├── missions.json      # Quest definitions
│   ├── bosses.json        # Boss encounters and abilities
│   └── saves/             # Saved game files
└── TODO.md                # Development roadmap
```

## Advanced Features

### Boss Battle Mechanics
- **Multi-phase fights** with increasing difficulty
- **Special abilities** unique to each boss
- **Phase transitions** when bosses reach certain HP thresholds
- **Epic rewards** for successful completion

### Character Progression
- **Experience scaling** increases with level
- **Stat growth** varies by character class
- **Skill unlocks** at specific levels
- **Equipment requirements** prevent premature use

### Save System
- **Automatic saves** recommended before boss fights
- **Multiple character support** - save different characters
- **Progress tracking** includes all stats and inventory
- **Timestamp logging** for save dates

## Troubleshooting

### Common Issues
1. **Game won't start** - Ensure Python 3.6+ is installed
2. **Save files missing** - Check data/saves/ directory exists
3. **JSON errors** - Verify all data files are present and valid
4. **Missing items** - Some equipment may require specific levels

### Performance
- **Save frequently** to avoid losing progress
- **Clear inventory** regularly to maintain performance
- **Monitor gold** to ensure continued progression
- **Check mission requirements** before accepting quests

## Contributing

This is a complete, standalone RPG experience. To modify or extend:

1. **Add Content** - Edit JSON files to add new items, enemies, or areas
2. **Balance Changes** - Modify stats in the respective JSON files
3. **New Features** - Extend the main.py file with additional functionality
4. **Bug Fixes** - Test thoroughly after any modifications

For modding assistance, please read the [documentation for modding](documentation.md)

## Credits

- **Andy64lolxd** - Creator of the project and maintainer.

**Our Legacy** - A text-based CLI fantasy RPG experience
Created with Python and JSON for maximum accessibility and modifiability.

---

**Your legacy awaits, adventurer. Choose your path wisely and forge the legend that will be remembered for ages!**
