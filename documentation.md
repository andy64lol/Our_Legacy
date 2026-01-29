# Our Legacy - Complete Modding & Data Structure Documentation

This comprehensive guide covers the complete structure of Our Legacy RPG, including all game data formats, mod system, and available parameters with examples.

---

## Table of Contents
1. [File Overview](#file-overview)
2. [Data Files Structure](#data-files-structure)
3. [Mod System](#mod-system)
4. [Complete Parameter Reference](#complete-parameter-reference)
5. [Examples](#examples)
6. [Tips & Best Practices](#tips--best-practices)

---

## File Overview

### Base Game Data (`data/` directory)
- **classes.json** - Player character classes with stats and progression
- **items.json** - All equipment, weapons, consumables, and accessories
- **companions.json** - Hireable companions with abilities
- **enemies.json** - Regular enemies and encounter data
- **bosses.json** - Boss encounters with multi-phase mechanics
- **areas.json** - World locations, connections, and shops
- **missions.json** - Quests and objectives
- **spells.json** - Magic spells and abilities
- **effects.json** - Status effects and buffs
- **crafting.json** - Alchemy recipes and materials
- **dialogues.json** - NPC and boss dialogue text
- **dungeons.json** - Dungeon definitions and challenges
- **weekly_challenges.json** - Recurring challenges
- **housing.json** - Housing items for home building ⭐ NEW
- **dungeons.json** - Dungeon definitions and challenges
- **weekly_challenges.json** - Recurring challenges

### Mod Data (`mods/` directory)
Mods can override or extend any base game data files. Each mod folder can contain:
- Any of the above JSON files (will be merged with base data)
- **mod.json** - Mod metadata (name, version, enabled status)

---

## Data Files Structure

### 1. CLASSES.JSON

**Purpose**: Define character classes with base stats and progression.

**Parameters**:
```json
{
  "class_id": {
    "name": "string",                          // Display name
    "description": "string",                   // Class flavor text
    "base_stats": {
      "max_hp": number,                        // Starting max HP
      "max_mp": number,                        // Starting max MP
      "attack": number,                        // Attack stat
      "defense": number,                       // Defense stat
      "speed": number                          // Speed/initiative stat
    },
    "level_up_bonuses": {
      "hp": number,                            // HP gain per level
      "mp": number,                            // MP gain per level
      "attack": number,                        // Attack gain per level
      "defense": number,                       // Defense gain per level
      "speed": number                          // Speed gain per level
    },
    "starting_equipment": {
      "weapon": "item_id",                     // Starting weapon
      "armor": "item_id",                      // Starting armor
      "accessory": "item_id" or null           // Optional starting accessory
    },
    "rank": number,                            // Class tier/rarity
    "class_skill": {
      "name": "string",
      "description": "string",
      "effect": "string",
      "damage_multiplier": number              // Optional damage multiplier
    }
  }
}
```

**Example**:
```json
{
  "warrior": {
    "name": "Warrior",
    "description": "A master of melee combat with unmatched strength.",
    "base_stats": {
      "max_hp": 120,
      "max_mp": 20,
      "attack": 18,
      "defense": 15,
      "speed": 8
    },
    "level_up_bonuses": {
      "hp": 8,
      "mp": 1,
      "attack": 1.5,
      "defense": 1.2,
      "speed": 0.3
    },
    "starting_equipment": {
      "weapon": "iron_sword",
      "armor": "leather_armor",
      "accessory": null
    },
    "rank": 1,
    "class_skill": {
      "name": "Cleave",
      "description": "Deal massive damage to a single target",
      "effect": "damage",
      "damage_multiplier": 1.8
    }
  }
}
```

---

### 2. ITEMS.JSON

**Purpose**: Define all equipment, consumables, and items.

**Parameters**:
```json
{
  "item_id": {
    "name": "string",                          // Display name
    "description": "string",                   // Item flavor text
    "type": "string",                          // weapon|armor|accessory|consumable|material
    "rarity": "string",                        // common|uncommon|rare|legendary
    "price": number,                           // Shop price in gold
    "effect": "string",                        // Optional effect (for consumables)
    "shop_type": ["string"],                   // Which shop types sell this
    "requirements": {
      "level": number,                         // Minimum level required
      "class": "string" or ["string"],         // Class requirement(s) or null
      "attack": number,                        // Min attack stat required
      "defense": number                        // Min defense stat required
    },
    "stats": {
      "attack": number,                        // Weapon/equipment bonus
      "defense": number,                       // Armor/equipment bonus
      "hp": number,                            // Max HP bonus
      "mp": number,                            // Max MP bonus
      "speed": number                          // Speed bonus
    }
  }
}
```

**Example**:
```json
{
  "iron_sword": {
    "name": "Iron Sword",
    "description": "A sturdy blade forged from iron ore.",
    "type": "weapon",
    "rarity": "common",
    "price": 50,
    "shop_type": ["general_store", "equipment_shop"],
    "requirements": {
      "level": 1,
      "class": null,
      "attack": 0,
      "defense": 0
    },
    "stats": {
      "attack": 8,
      "defense": 0,
      "hp": 0,
      "mp": 0,
      "speed": 0
    }
  },
  "health_potion": {
    "name": "Health Potion",
    "description": "Restores 50 HP when consumed.",
    "type": "consumable",
    "rarity": "common",
    "price": 25,
    "effect": "restore_hp",
    "stats": {
      "hp": 50
    }
  }
}
```

---

### 3. ENEMIES.JSON

**Purpose**: Define regular enemies encountered during exploration.

**Parameters**:
```json
{
  "enemy_id": {
    "name": "string",
    "description": "string",
    "hp": number,
    "attack": number,
    "defense": number,
    "speed": number,
    "experience_reward": number,
    "gold_reward": number,
    "possible_drops": ["item_id"],             // Loot table
    "drop_rates": [number],                    // Probability for each item (0-1)
    "special_abilities": [
      {
        "name": "string",
        "description": "string",
        "damage": number,
        "mp_cost": number,
        "cooldown": number
      }
    ]
  }
}
```

**Example**:
```json
{
  "goblin": {
    "name": "Goblin",
    "description": "A small, mischievous creature with sharp teeth.",
    "hp": 30,
    "attack": 8,
    "defense": 3,
    "speed": 6,
    "experience_reward": 50,
    "gold_reward": 10,
    "possible_drops": ["leather_armor", "copper_coin"],
    "drop_rates": [0.3, 0.5],
    "special_abilities": [
      {
        "name": "Claw Slash",
        "description": "A quick slash attack",
        "damage": 12,
        "mp_cost": 0,
        "cooldown": 2
      }
    ]
  }
}
```

---

### 4. BOSSES.JSON

**Purpose**: Define boss encounters with multi-phase mechanics.

**Parameters**:
```json
{
  "boss_id": {
    "name": "string",
    "description": "string",
    "hp": number,
    "attack": number,
    "defense": number,
    "speed": number,
    "special_abilities": [
      {
        "name": "string",
        "description": "string",
        "damage": number,
        "mp_cost": number,
        "cooldown": number,
        "effect": "string",                    // Optional: stun|buff|debuff
        "duration": number                     // Duration if effect present
      }
    ],
    "phases": [
      {
        "hp_threshold": number,                // (0-1) trigger at % HP
        "description": "string",
        "attack_multiplier": number,
        "defense_multiplier": number
      }
    ],
    "experience_reward": number,
    "gold_reward": number,
    "loot_table": ["item_id"],                // Guaranteed drops
    "unlock_conditions": {
      "level": number,
      "missions_required": ["mission_id"]
    },
    "dialogues": {
      "on_start_battle": "dialogue_key",
      "on_defeat": "dialogue_key"
    }
  }
}
```

**Example**:
```json
{
  "fire_dragon": {
    "name": "Ancient Fire Dragon",
    "description": "A legendary dragon wreathed in flames.",
    "hp": 300,
    "attack": 35,
    "defense": 20,
    "speed": 15,
    "special_abilities": [
      {
        "name": "Fire Breath",
        "description": "Deals massive fire damage",
        "damage": 50,
        "mp_cost": 20,
        "cooldown": 3
      }
    ],
    "phases": [
      {
        "hp_threshold": 0.7,
        "description": "The dragon fights with typical fury",
        "attack_multiplier": 1.0,
        "defense_multiplier": 1.0
      },
      {
        "hp_threshold": 0.4,
        "description": "The dragon becomes enraged",
        "attack_multiplier": 1.3,
        "defense_multiplier": 0.8
      }
    ],
    "experience_reward": 1000,
    "gold_reward": 500,
    "loot_table": ["dragon_scale_armor", "fire_gem"],
    "unlock_conditions": {
      "level": 8,
      "missions_required": []
    },
    "dialogues": {
      "on_start_battle": "fire_dragon.boss.start",
      "on_defeat": "fire_dragon.boss.defeat"
    }
  }
}
```

---

### 5. AREAS.JSON

**Purpose**: Define world locations, connections, and shops.

**Parameters**:
```json
{
  "area_id": {
    "name": "string",
    "description": "string",
    "possible_enemies": ["enemy_id"],
    "possible_bosses": ["boss_id"],
    "shops": ["shop_id"],                     // Shop identifiers
    "missions_available": boolean,
    "connections": ["area_id"],               // Connected areas
    "difficulty": number,                     // 1-5 difficulty rating
    "rest_cost": number,                      // Gold to rest
    "can_rest": boolean,                      // Can rest in this area
    "boss_area": boolean,                     // Is this a boss area
    "area_treasure": ["item_id"]              // Optional treasure
  }
}
```

**Example**:
```json
{
  "starting_village": {
    "name": "Starting Village",
    "description": "A peaceful village where new adventurers begin.",
    "possible_enemies": ["thief"],
    "possible_bosses": [],
    "shops": ["general_store"],
    "missions_available": true,
    "connections": ["forest_path", "ancient_ruins"],
    "difficulty": 1,
    "rest_cost": 5,
    "can_rest": true,
    "boss_area": false
  }
}
```

---

### 6. MISSIONS.JSON

**Purpose**: Define quests and objectives.

**Parameters**:
```json
{
  "mission_id": {
    "name": "string",
    "description": "string",
    "objectives": [
      {
        "type": "string",                      // kill|collect|explore|defend
        "target": "string",                    // Enemy/item/area name
        "count": number,                       // How many needed
        "current": number                      // Current progress
      }
    ],
    "rewards": {
      "gold": number,
      "experience": number,
      "items": ["item_id"]
    },
    "required_level": number,
    "repeatable": boolean
  }
}
```

**Example**:
```json
{
  "goblin_slayer": {
    "name": "Goblin Slayer",
    "description": "The village is plagued by goblins. Slay 10 of them.",
    "objectives": [
      {
        "type": "kill",
        "target": "goblin",
        "count": 10,
        "current": 0
      }
    ],
    "rewards": {
      "gold": 200,
      "experience": 300,
      "items": []
    },
    "required_level": 1,
    "repeatable": false
  }
}
```

---

### 7. DIALOGUES.JSON

**Purpose**: Store NPC and boss dialogue text.

**Parameters**:
```json
{
  "dialogue_key": "dialogue_text"
}
```

**Example**:
```json
{
  "fire_dragon.boss.start": "The dragon roars as flames erupt around it!",
  "fire_dragon.boss.defeat": "The mighty dragon falls, defeated at last.",
  "ethereal_guardian.boss.start": "The guardian materializes before you...",
  "merchant_greeting": "Welcome, traveler. What can I help you with?"
}
```

---

### 8. DUNGEONS.JSON

**Purpose**: Define procedural dungeons with challenges and rewards.

**Parameters**:
```json
{
  "dungeons": [
    {
      "id": "dungeon_id",
      "name": "string",
      "description": "string",
      "difficulty": [number, number],         // [min, max] difficulty
      "rooms": number,                        // Number of rooms
      "boss_id": "boss_id",
      "completion_reward": {
        "gold": number,
        "experience": number,
        "items": ["item_id"]
      },
      "room_weights": {
        "battle": number,                     // Probability weights
        "question": number,
        "chest": number,
        "trap_chest": number,
        "multi_choice": number,
        "empty": number
      }
    }
  ],
  "challenge_templates": {
    "question": {
      "types": [
        {
          "question": "string",
          "answer": "string",
          "hints": ["string"],
          "time_limit": number,
          "success_reward": {
            "gold": number,
            "experience": number
          },
          "failure_damage": number
        }
      ]
    },
    "selection": {
      "types": [
        {
          "question": "string",
          "options": [
            {
              "text": "string",
              "correct": boolean,
              "reason": "string",
              "reward": {"gold": number, "experience": number}
            }
          ],
          "success_reward": {"gold": number, "experience": number},
          "failure_damage": number
        }
      ]
    },
    "trap": {
      "types": [
        {
          "description": "string",
          "base_damage": number,
          "difficulty": "string"
        }
      ]
    }
  },
  "chest_templates": {
    "small": {
      "name": "string",
      "gold_range": [number, number],
      "item_count_range": [number, number],
      "experience": number,
      "item_rarity": ["string"],
      "guaranteed_legendary": number or false
    }
  }
}
```

**Example**:
```json
{
  "dungeons": [
    {
      "id": "ethereal_spire",
      "name": "Ethereal Spire",
      "description": "A mystical tower between worlds.",
      "difficulty": [4, 5],
      "rooms": 8,
      "boss_id": "ethereal_guardian",
      "completion_reward": {
        "gold": 1000,
        "experience": 1800,
        "items": ["ethereal_crown"]
      },
      "room_weights": {
        "question": 35,
        "battle": 25,
        "chest": 15,
        "trap_chest": 10,
        "multi_choice": 10,
        "empty": 5
      }
    }
  ],
  "challenge_templates": {
    "question": {
      "types": [
        {
          "question": "What is the name of the magical force?",
          "answer": "ether",
          "hints": ["It's the substance of magic", "Ancient name"],
          "time_limit": 60,
          "success_reward": {"gold": 100, "experience": 150},
          "failure_damage": 20
        }
      ]
    }
  }
}
```

---

### 9. CRAFTING.JSON

**Purpose**: Define alchemy recipes and material categories.

**Parameters**:
```json
{
  "material_categories": {
    "category_name": ["material_id"]
  },
  "recipes": {
    "recipe_id": {
      "name": "string",
      "category": "string",                   // Potions|Elixirs|Enchantments|Utility
      "rarity": "string",
      "skill_requirement": number,
      "materials": {
        "material_id": number                 // Material: quantity required
      },
      "output": {
        "item_id": number                     // Item: quantity produced
      }
    }
  }
}
```

**Example**:
```json
{
  "material_categories": {
    "ores": ["iron_ore", "coal", "steel_ingot"],
    "herbs": ["herb", "mana_herb", "spring_water"],
    "crystals": ["crystal_shard", "fire_gem", "ice_crystal"]
  },
  "recipes": {
    "health_potion": {
      "name": "Health Potion",
      "category": "Potions",
      "rarity": "common",
      "skill_requirement": 1,
      "materials": {
        "herb": 2,
        "spring_water": 1
      },
      "output": {
        "health_potion": 1
      }
    }
  }
}
```

---

### 10. SPELLS.JSON

**Purpose**: Define magic spells and abilities.

**Parameters**:
```json
{
  "spell_id": {
    "name": "string",
    "description": "string",
    "damage": number,
    "mp_cost": number,
    "cooldown": number,
    "effect": "string",                       // Optional effect type
    "duration": number,                       // For effects
    "range": "string",                        // single|all|ally|self
    "required_level": number,
    "class_requirement": "string" or null,
    "element": "string"                       // fire|ice|lightning|nature
  }
}
```

---

### 11. COMPANIONS.JSON

**Purpose**: Define hireable companions.

**Parameters**:
```json
{
  "companion_id": {
    "name": "string",
    "description": "string",
    "cost": number,                           // Gold to hire
    "base_stats": {
      "max_hp": number,
      "max_mp": number,
      "attack": number,
      "defense": number,
      "speed": number
    },
    "passive_ability": {
      "name": "string",
      "description": "string",
      "effect": "string"
    },
    "active_ability": {
      "name": "string",
      "description": "string",
      "damage": number,
      "mp_cost": number
    }
  }
}
```

---

## Mod System

### Mod Structure
```
mods/
├── The Ether/
│   ├── mod.json                 # Mod metadata
│   ├── bosses.json              # Optional - extends base bosses
│   ├── areas.json               # Optional - extends base areas
│   ├── items.json               # Optional - new items
│   ├── enemies.json             # Optional - new enemies
│   ├── dungeons.json            # Optional - new dungeons
│   ├── dialogues.json           # Optional - new dialogues
│   ├── classes.json             # Optional - new classes
│   ├── spells.json              # Optional - new spells
│   ├── crafting.json            # Optional - new recipes
│   └── ...other files
```

### mod.json Format
```json
{
  "name": "The Ether",
  "version": "1.0.0",
  "author": "Your Name",
  "description": "Ethereal dungeons and magical encounters",
  "enabled": true
}
```

### How Mods Are Loaded
1. Base game data loads from `data/` directory
2. Each enabled mod is scanned for data files
3. Mod data is merged with base data:
   - **Arrays** (dungeons): Extended with new entries
   - **Objects** (items, enemies): Updated/overridden
   - **Nested objects** (challenge_templates): Merged

---

## Complete Parameter Reference

### Boss Abilities Parameters
```
name: string                          - Ability name
description: string                  - What it does
damage: number                        - Damage dealt (0 for non-damaging)
mp_cost: number                       - MP required to use
cooldown: number                      - Turns between uses
effect: string (optional)             - stun|buff|debuff|heal|drain
duration: number (optional)           - How long effect lasts
ignores_defense: boolean (optional)   - Pierce armor
stun_chance: number 0-1 (optional)   - Probability to stun
heal_amount: number (optional)        - Health restored
```

### Item Requirements
```
level: number                         - Minimum character level
class: string|null                    - Class requirement (null = any)
attack: number                        - Min attack stat
defense: number                       - Min defense stat
```

### Area Difficulty Scales
- **1**: Beginner (Starting Village, Dark Forest)
- **2**: Novice (Deep Woods, Ancient Ruins)
- **3**: Intermediate (Crystal Caves, Spire)
- **4**: Advanced (Dragon Lair approach, High dungeons)
- **5**: Legendary (Final areas, End-game content)

### Rarity Tiers
- **common**: Standard items, low value
- **uncommon**: Better quality, mid value
- **rare**: High quality, high value
- **legendary**: Unique, very high value

---

## Examples

### Example: Creating a New Boss (Mod)

Create `mods/MyMod/bosses.json`:
```json
{
  "shadow_king": {
    "name": "Shadow King",
    "description": "Ruler of the dark realm",
    "hp": 400,
    "attack": 40,
    "defense": 25,
    "speed": 18,
    "special_abilities": [
      {
        "name": "Shadow Strike",
        "description": "Strike from darkness",
        "damage": 45,
        "mp_cost": 25,
        "cooldown": 2
      }
    ],
    "phases": [
      {
        "hp_threshold": 0.5,
        "description": "The king emerges from shadow",
        "attack_multiplier": 1.3
      }
    ],
    "experience_reward": 2000,
    "gold_reward": 1000,
    "loot_table": ["shadow_crown", "dark_gem"],
    "unlock_conditions": {
      "level": 12,
      "missions_required": []
    },
    "dialogues": {
      "on_start_battle": "shadow_king.boss.start",
      "on_defeat": "shadow_king.boss.defeat"
    }
  }
}
```

### Example: Creating a New Dungeon (Mod)

Create `mods/MyMod/dungeons.json`:
```json
{
  "dungeons": [
    {
      "id": "shadow_castle",
      "name": "Shadow Castle",
      "description": "A fortress of darkness",
      "difficulty": [5, 6],
      "rooms": 10,
      "boss_id": "shadow_king",
      "completion_reward": {
        "gold": 2000,
        "experience": 3000,
        "items": ["shadow_crown"]
      },
      "room_weights": {
        "battle": 40,
        "question": 20,
        "chest": 15,
        "trap_chest": 15,
        "multi_choice": 5,
        "empty": 5
      }
    }
  ],
  "challenge_templates": {
    "question": {
      "types": [
        {
          "question": "What is the color of shadow?",
          "answer": "black",
          "hints": ["Dark", "The absence of light"],
          "time_limit": 45,
          "success_reward": {"gold": 150, "experience": 200},
          "failure_damage": 25
        }
      ]
    }
  }
}
```

### Example: Creating New Items (Mod)

Create `mods/MyMod/items.json`:
```json
{
  "shadow_sword": {
    "name": "Shadow Sword",
    "description": "A blade wreathed in darkness",
    "type": "weapon",
    "rarity": "legendary",
    "price": 5000,
    "shop_type": ["dark_market"],
    "requirements": {
      "level": 10,
      "class": ["Warrior", "Rogue"],
      "attack": 25,
      "defense": 0
    },
    "stats": {
      "attack": 35,
      "defense": 0,
      "speed": 5,
      "hp": 0,
      "mp": 0
    }
  }
}
```

---

### 9. WEEKLY_CHALLENGES.JSON

**Purpose**: Define recurring weekly challenges that players can complete for rewards.

**Structure**: Weekly challenges are organized as an array within a "challenges" object.

**Parameters**:
```json
{
  "challenges": [
    {
      "id": "string",                          // Unique challenge identifier
      "name": "string",                        // Display name
      "description": "string",                 // Challenge objective description
      "type": "string",                        // Challenge type (see below)
      "target": number,                        // Number to reach for completion
      "reward_exp": number,                    // Experience points reward
      "reward_gold": number,                   // Gold reward,
      "reward_items": ["item_id"] (optional),  // Item rewards on completion
      "icon": "string" (optional),             // Icon/emoji for display
      "difficulty": "string" (optional)        // Difficulty tier (easy/medium/hard)
    }
  ]
}
```

**Challenge Types**:
| Type | Description | Tracking | Example |
|------|-------------|----------|---------|
| `kill_count` | Defeat a certain number of enemies | Auto-tracked on kill | "Defeat 10 enemies" |
| `mission_count` | Complete a number of missions | Auto-tracked on mission completion | "Complete 3 missions" |
| `level_reach` | Reach a specific character level | Auto-tracked on level up | "Reach level 10" |
| `boss_kill` | Defeat a certain number of bosses | Auto-tracked on boss defeat | "Defeat 1 boss" |
| `dungeon_complete` | Complete a number of dungeons | Auto-tracked on dungeon completion | "Complete 1 dungeon" |

**Example**:
```json
{
  "challenges": [
    {
      "id": "kill_10",
      "name": "Monster Hunter",
      "description": "Defeat 10 enemies",
      "type": "kill_count",
      "target": 10,
      "reward_exp": 2000,
      "reward_gold": 500,
      "icon": "⚔️",
      "difficulty": "easy"
    },
    {
      "id": "level_20",
      "name": "Power Leveler",
      "description": "Reach level 20",
      "type": "level_reach",
      "target": 20,
      "reward_exp": 10000,
      "reward_gold": 5000,
      "reward_items": ["rare_scroll"],
      "icon": "📈",
      "difficulty": "hard"
    },
    {
      "id": "dungeon_master",
      "name": "Dungeon Explorer",
      "description": "Complete 5 dungeons",
      "type": "dungeon_complete",
      "target": 5,
      "reward_exp": 15000,
      "reward_gold": 7500,
      "reward_items": ["legendary_key", "treasure_map"],
      "icon": "🏰",
      "difficulty": "hard"
    }
  ]
}
```

**Mod Merging Behavior**: 
- Mods can add new challenges to the base game challenges
- Challenges from mods are appended to the base challenge list
- Challenge IDs must be unique across all loaded mods and base game
- Progress tracking is automatically initialized for new challenges

---

### 10. HOUSING.JSON

**Purpose**: Define housing items that players can purchase and place in their home at "Your Land".

**Parameters**:
```json
{
  "housing_item_id": {
    "name": "string",                          // Display name in Housing Shop
    "description": "string",                   // Item description/flavor text
    "price": number,                           // Cost in gold to purchase
    "comfort_points": number                   // Comfort value for home tier
  }
}
```

**Housing Item Guidelines**:
- **Price Range**: 30-20000+ gold (scales with comfort and rarity)
- **Comfort Points**: 5-1000+ points (typically 1 point per 10-15 gold)
- **Home Tiers** (based on total comfort):
  - COMMON (0-99): Basic shelter with minimal comfort
  - UNCOMMON (100-199): Modest home with decent accommodations
  - RARE (200-499): Well-decorated home with many comforts
  - EPIC (500-999): Luxurious estate with exceptional amenities
  - LEGENDARY (1000+): Grand mansion fit for royalty

**Example**:
```json
{
  "small_tent": {
    "name": "Small tent",
    "description": "A basic makeshift tent that provides minimal shelter.",
    "price": 50,
    "comfort_points": 10
  },
  "crystal_greenhouse": {
    "name": "Crystal greenhouse",
    "description": "A greenhouse made of crystal, perfect for cultivating rare and exotic plants.",
    "price": 900,
    "comfort_points": 45
  },
  "imperial_palace": {
    "name": "Imperial palace with jade walls and diamond encrusted furnishings",
    "description": "An extraordinary imperial palace adorned with jade walls and lavish diamond-encrusted furnishings, representing the pinnacle of opulence.",
    "price": 20000,
    "comfort_points": 1000
  }
}
```

**Purchasing Housing**:
- Players can purchase multiple copies of the same item (comfort stacks)
- Housing items appear in Housing Shop in "Your Land" area
- Purchased items contribute to overall home comfort rating
- Items can be removed from home (refunding comfort points)

**Mod Merging Behavior**:
- Mods can add new housing items
- All items from base game and enabled mods appear in Housing Shop
- No ID conflicts (mod items coexist with base items)
- Items from all sources contribute equally to comfort

---

## Tips & Best Practices

1. **JSON Validation**: Always validate JSON files before loading - invalid JSON will crash the game
2. **ID Consistency**: Use consistent IDs across files (e.g., boss_id matches boss entry)
3. **Balance**: Increase difficulty and rewards proportionally
4. **Testing**: Test mods thoroughly before distribution
5. **Documentation**: Comment your mod's purpose and changes
6. **Backup**: Keep backups of original data files
7. **Version Control**: Track mod versions for compatibility
8. **Mod Conflicts**: Later-loading mods override earlier ones for same IDs
9. **Performance**: Keep mod data reasonable in size
10. **Community**: Share mods via the official repository

---

**For more help, join our community or visit the GitHub repository!**
