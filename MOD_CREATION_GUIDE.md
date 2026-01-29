# Our Legacy - Quick Mod Creation Guide

Fast reference for creating mods. For detailed documentation, see [documentation.md](documentation.md).

---

## Quick Start: Create Your First Mod

### Step 1: Create Mod Folder
```bash
mkdir mods/YourModName
cd mods/YourModName
```

### Step 2: Create mod.json
```json
{
  "name": "Your Mod Name",
  "version": "1.0.0",
  "author": "Your Name",
  "description": "Brief description of what your mod adds",
  "enabled": true
}
```

### Step 3: Add Data Files
Copy any of these files from `data/` and modify them:
- `bosses.json` - Add/modify bosses
- `areas.json` - Add/modify locations
- `items.json` - Add/modify items
- `enemies.json` - Add/modify enemies
- `dungeons.json` - Add/modify dungeons
- `dialogues.json` - Add dialogue text
- `classes.json` - Add/modify classes
- `companions.json` - Add companions
- `spells.json` - Add spells
- `crafting.json` - Add recipes
- `weekly_challenges.json` - Add weekly challenges

### Step 4: Test Your Mod
Start the game: `python3 main.py`

---

## Common Templates

### Add a New Boss

**File**: `mods/YourModName/bosses.json`

```json
{
  "your_boss_id": {
    "name": "Boss Name",
    "description": "What the boss looks like",
    "hp": 200,
    "attack": 25,
    "defense": 15,
    "speed": 10,
    "special_abilities": [
      {
        "name": "Ability Name",
        "description": "What it does",
        "damage": 30,
        "mp_cost": 20,
        "cooldown": 3
      }
    ],
    "phases": [
      {
        "hp_threshold": 0.5,
        "description": "Second phase description",
        "attack_multiplier": 1.3,
        "defense_multiplier": 0.9
      }
    ],
    "experience_reward": 500,
    "gold_reward": 300,
    "loot_table": ["item_id"],
    "unlock_conditions": {
      "level": 5,
      "missions_required": []
    },
    "dialogues": {
      "on_start_battle": "your_boss_id.boss.start",
      "on_defeat": "your_boss_id.boss.defeat"
    }
  }
}
```

**Add Dialogues** - `mods/YourModName/dialogues.json`:
```json
{
  "your_boss_id.boss.start": "The boss appears!",
  "your_boss_id.boss.defeat": "The boss falls!"
}
```

---

### Add a New Dungeon

**File**: `mods/YourModName/dungeons.json`

```json
{
  "dungeons": [
    {
      "id": "dungeon_id",
      "name": "Dungeon Name",
      "description": "Dungeon description",
      "difficulty": [3, 4],
      "rooms": 7,
      "boss_id": "your_boss_id",
      "completion_reward": {
        "gold": 1000,
        "experience": 1500,
        "items": ["legendary_item"]
      },
      "room_weights": {
        "battle": 40,
        "question": 25,
        "chest": 15,
        "trap_chest": 10,
        "multi_choice": 5,
        "empty": 5
      }
    }
  ],
  "challenge_templates": {
    "question": {
      "types": [
        {
          "question": "A riddle or question?",
          "answer": "the_answer",
          "hints": ["Hint 1", "Hint 2"],
          "time_limit": 60,
          "success_reward": {"gold": 100, "experience": 150},
          "failure_damage": 20
        }
      ]
    },
    "selection": {
      "types": [
        {
          "question": "What do you do?",
          "options": [
            {
              "text": "Good choice",
              "correct": true,
              "reason": "You succeed!",
              "reward": {"gold": 100, "experience": 150}
            },
            {
              "text": "Bad choice",
              "correct": false,
              "reason": "You fail!",
              "damage": 25
            }
          ]
        }
      ]
    }
  },
  "chest_templates": {
    "small": {
      "name": "Small Chest",
      "gold_range": [50, 100],
      "item_count_range": [1, 1],
      "experience": 100,
      "item_rarity": ["common"],
      "guaranteed_legendary": false
    }
  }
}
```

---

### Add a New Item

**File**: `mods/YourModName/items.json`

```json
{
  "mythical_sword": {
    "name": "Mythical Sword",
    "description": "A legendary blade forged by ancient smiths",
    "type": "weapon",
    "rarity": "legendary",
    "price": 5000,
    "shop_type": ["dark_market", "artifact_shop"],
    "requirements": {
      "level": 15,
      "class": ["Warrior", "Paladin"],
      "attack": 30,
      "defense": 0
    },
    "stats": {
      "attack": 50,
      "defense": 5,
      "hp": 10,
      "mp": 0,
      "speed": 3
    }
  }
}
```

---

### Add a New Area

**File**: `mods/YourModName/areas.json`

```json
{
  "mystical_forest": {
    "name": "Mystical Forest",
    "description": "An ancient, magical forest shrouded in mystery",
    "possible_enemies": ["forest_spirit", "enchanted_wolf", "ancient_treant"],
    "possible_bosses": ["forest_guardian"],
    "shops": ["nature_shop"],
    "missions_available": true,
    "connections": ["starting_village", "crystal_caves"],
    "difficulty": 3,
    "rest_cost": 15,
    "can_rest": true,
    "boss_area": false
  }
}
```

---

### Add a New Enemy

**File**: `mods/YourModName/enemies.json`

```json
{
  "forest_spirit": {
    "name": "Forest Spirit",
    "description": "A ghostly entity of the ancient woods",
    "hp": 50,
    "attack": 15,
    "defense": 8,
    "speed": 12,
    "experience_reward": 150,
    "gold_reward": 50,
    "possible_drops": ["ancient_relic", "mana_crystal"],
    "drop_rates": [0.2, 0.3],
    "special_abilities": [
      {
        "name": "Spirit Touch",
        "description": "A chilling magical strike",
        "damage": 20,
        "mp_cost": 15,
        "cooldown": 2
      }
    ]
  }
}
```

---

### Add a New Class

**File**: `mods/YourModName/classes.json`

```json
{
  "paladin": {
    "name": "Paladin",
    "description": "A holy warrior blessed with divine power",
    "base_stats": {
      "max_hp": 110,
      "max_mp": 40,
      "attack": 16,
      "defense": 16,
      "speed": 8
    },
    "level_up_bonuses": {
      "hp": 7,
      "mp": 3,
      "attack": 1.2,
      "defense": 1.3,
      "speed": 0.4
    },
    "starting_equipment": {
      "weapon": "holy_mace",
      "armor": "plate_armor",
      "accessory": "holy_symbol"
    },
    "rank": 2,
    "class_skill": {
      "name": "Divine Shield",
      "description": "Protect with holy power for 2 turns",
      "effect": "shield",
      "defense_bonus": 30
    }
  }
}
```

---

### Add Crafting Recipes

**File**: `mods/YourModName/crafting.json`

```json
{
  "material_categories": {
    "exotic": ["phoenix_feather", "dragon_scale", "void_essence"]
  },
  "recipes": {
    "legendary_sword": {
      "name": "Legendary Sword",
      "category": "Enchantments",
      "rarity": "legendary",
      "skill_requirement": 15,
      "materials": {
        "steel_ingot": 5,
        "ancient_crystal": 3,
        "phoenix_feather": 1
      },
      "output": {
        "legendary_sword": 1
      }
    }
  }
}
```

---

### Add Weekly Challenges

**File**: `mods/YourModName/weekly_challenges.json`

```json
{
  "challenges": [
    {
      "id": "kill_100",
      "name": "Ultimate Slayer",
      "description": "Defeat 100 enemies",
      "type": "kill_count",
      "target": 100,
      "reward_exp": 25000,
      "reward_gold": 10000,
      "reward_items": ["legendary_weapon_mod"],
      "icon": "💀",
      "difficulty": "hard"
    },
    {
      "id": "reach_level_50",
      "name": "Half Century",
      "description": "Reach level 50",
      "type": "level_reach",
      "target": 50,
      "reward_exp": 50000,
      "reward_gold": 25000,
      "icon": "🎯",
      "difficulty": "very_hard"
    },
    {
      "id": "boss_five",
      "name": "Boss Mastery",
      "description": "Defeat 5 bosses",
      "type": "boss_kill",
      "target": 5,
      "reward_exp": 30000,
      "reward_gold": 15000,
      "reward_items": ["boss_trophy"],
      "icon": "👑",
      "difficulty": "hard"
    },
    {
      "id": "dungeon_ten",
      "name": "Dungeon Master",
      "description": "Complete 10 dungeons",
      "type": "dungeon_complete",
      "target": 10,
      "reward_exp": 40000,
      "reward_gold": 20000,
      "reward_items": ["dungeon_key"],
      "icon": "🗝️",
      "difficulty": "very_hard"
    }
  ]
}
```

**Challenge Types Available**:
- `kill_count` - Track number of enemies defeated
- `mission_count` - Track completed missions
- `level_reach` - Track character level
- `boss_kill` - Track bosses defeated
- `dungeon_complete` - Track completed dungeons

**All Parameters Explained**:
- `id` *(required)* - Unique identifier for the challenge
- `name` *(required)* - Display name shown to player
- `description` *(required)* - What player must do
- `type` *(required)* - One of the challenge types above
- `target` *(required)* - Number to reach for completion
- `reward_exp` *(required)* - Experience gained on completion
- `reward_gold` *(required)* - Gold gained on completion
- `reward_items` *(optional)* - Array of item IDs to receive
- `icon` *(optional)* - Emoji or symbol for display
- `difficulty` *(optional)* - "easy", "medium", "hard", "very_hard"

---

## Parameter Quick Reference

### Boss Parameters
| Parameter | Type | Example |
|-----------|------|---------|
| name | string | "Fire Dragon" |
| hp | number | 300 |
| attack | number | 35 |
| defense | number | 20 |
| speed | number | 15 |
| experience_reward | number | 1000 |
| gold_reward | number | 500 |

### Item Stats
| Stat | Effect |
|------|--------|
| attack | Increases damage dealt |
| defense | Reduces damage taken |
| hp | Increases max health |
| mp | Increases max mana |
| speed | Increases turn order priority |

### Rarity Levels
- `common` - Basic items
- `uncommon` - Better quality
- `rare` - High quality
- `legendary` - Unique/powerful

### Difficulty Scale
- 1: Beginner
- 2: Novice
- 3: Intermediate
- 4: Advanced
- 5: Legendary

### Ability Effects
- `damage` - Deals damage
- `stun` - Stuns target
- `buff` - Buffs stats
- `debuff` - Debuffs stats
- `heal` - Heals health
- `drain` - Drains enemy HP to self
- `shield` - Adds defense
- `summon` - Summons allies

---

## Testing Your Mod

1. **Validate JSON**
   - Use an online JSON validator
   - Ensure no syntax errors

2. **Check ID References**
   - Boss IDs match dialogue keys
   - Item IDs exist in items.json
   - Enemy IDs exist in enemies.json

3. **Balance Check**
   - Higher difficulty = more rewards
   - Boss stats scale with level requirement
   - Item prices match rarity

4. **In-Game Testing**
   - Create new character
   - Visit areas with your content
   - Fight bosses/enemies
   - Use dungeons/crafting

---

## Common Issues

**Problem**: Mod doesn't load
- Check `"enabled": true` in mod.json
- Ensure mod folder is in `mods/` directory
- Restart the game

**Problem**: Errors in console
- Validate JSON (missing commas, brackets)
- Check all referenced IDs exist
- Review parameter types

**Problem**: Game crashes
- Check for circular references
- Ensure no duplicate IDs
- Validate all stat numbers are positive

---

## Distribution

1. **Prepare Your Mod**
   - Test thoroughly
   - Write good mod.json description
   - Create README if complex

2. **Submit**
   - Use `storywrite.py` to submit
   - Or create GitHub PR

3. **Community**
   - Share on Discord
   - Get feedback
   - Update based on suggestions

---

## Need Help?

- **Detailed Docs**: See [documentation.md](documentation.md)
- **Examples**: Check `mods/The Ether/` for a complete mod
- **Discord**: Join our community server
- **GitHub**: Report issues and contribute

---

**Happy modding! Create amazing content for Our Legacy!**
