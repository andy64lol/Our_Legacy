# Dungeon Implementation Plan

## Phase 1: Restructure dungeons.json

### New Dungeon Format Structure
```json
{
  "dungeons": {
    "dungeon_id": {
      "name": "Dungeon Name",
      "description": "Description",
      "difficulty": 1-10,
      "min_rooms_to_boss": 3,
      "max_rooms_to_boss": 5,
      "has_boss": true/false,
      "boss_id": "boss_id_from_bosses.json",
      "completion_reward": {
        "gold": 500,
        "experience": 1000,
        "items": ["item1", "item2"]
      },
      "rooms": {
        "room_1": {
          "room_name": "Room Name",
          "type": "question|battle|chest|trap_chest|multichoice|empty",
          "description": "Room description",
          // question type
          "question": "Question text?",
          "correct_answer": "answer",
          "if_answer_incorrect": "gold|monster|hp",
          //these are for both multichoice and question
          "incorrect_monster": "monster_id",
          "incorrect_penalty": 50, //only for hp or gold
          // battle type
          "enemy": "enemy_id",
          // chest type
          "gold": 100,
          "items": ["item1"],
          // multichoice type
          "question": "Question?",
          "answers_to_choose": [
            {"answer": "Option A", "correct": true},
            {"answer": "Option B", "correct": false}
          ]
        }
      }
    }
  }
}
```

### 15 Dungeons to Create (Increasing Difficulty)
1. **Forest Crypt** - Difficulty 1-2
2. **Goblin Cave** - Difficulty 2-3
3. **Ancient Ruins** - Difficulty 3-4
4. **Swamp Den** - Difficulty 3-4
5. **Crystal Cavern** - Difficulty 4-5
6. **Shadow Fortress** - Difficulty 4-5
7. **Fire Temple** - Difficulty 5-6
8. **Ice Citadel** - Difficulty 5-6
9. **Thunder Peak** - Difficulty 6
10. **Undead Crypt** - Difficulty 6-7
11. **Demon Portal** - Difficulty 7-8
12. **Void Realm** - Difficulty 8
13. **Dragon's Lair** - Difficulty 8-9
14. **Celestial Tower** - Difficulty 9
15. **Supreme Realm** - Difficulty 10

## Phase 2: Update main.py

### Menu Reordering
Current menu order (1-16):
1. Explore
2. View Character
3. Travel
4. Inventory
5. Missions
6. Fight Boss
7. Tavern
8. Shop
9. Alchemy (becomes 10)
10. Elite Market (becomes 11)
11. Rest (becomes 12)
12. Companions (becomes 13)
13. Save Game (becomes 14)
14. Load Game (becomes 15)
15. Claim Rewards (becomes 16)
16. Quit (becomes 17)

**NEW:** Dungeons becomes option 9 (before Alchemy)

### New Methods to Add
1. `visit_dungeons()` - Main dungeon menu
2. `display_dungeon_list()` - List available dungeons
3. `enter_dungeon(dungeon_id)` - Enter and start dungeon exploration
4. `explore_dungeon_room()` - Process current room
5. `dungeon_battle(enemy_id)` - Battle in dungeon
6. `handle_dungeon_question(room)` - Handle question rooms
7. `handle_dungeon_multichoice(room)` - Handle multichoice rooms
8. `handle_dungeon_chest(room)` - Handle chest rooms
9. `handle_dungeon_trap(room)` - Handle trap rooms
10. `dungeon_boss_encounter()` - Boss fight
11. `complete_dungeon(dungeon_id)` - Handle completion
12. `dungeon_death_penalty()` - Handle death in dungeon

### Dungeon State Tracking
Add to Game class:
- `current_dungeon`: str or None
- `current_dungeon_room`: str or None
- `dungeon_rooms_completed`: List[str]
- `dungeon_visited`: bool

### Death Penalty in Dungeons
- Lose 10-20% of current gold
- Lose all current dungeon progress
- Respawn at starting area (not dungeon entry)
- Cannot retry the same dungeon for 10 minutes

## Phase 3: Room Type Details

### Question Room
```json
"question_room": {
  "room_name": "Riddle Chamber",
  "type": "question",
  "description": "An ancient sphinx guards the passage...",
  "question": "I speak without a mouth and hear without ears. What am I?",
  "correct_answer": "echo",
  "if_answer_incorrect": "gold",
  "incorrect_penalty": 50
}
```

### Battle Room
```json
"battle_room": {
  "room_name": "Guard Post",
  "type": "battle",
  "description": "Two goblins stand guard here...",
  "enemy": "goblin",
  "enemy_count": 2
}
```

### Chest Room
```json
"chest_room": {
  "room_name": "Treasure Room",
  "type": "chest",
  "description": "A golden chest sits in the center...",
  "gold": 200,
  "items": ["Steel Sword"]
}
```

### Trap Chest Room
```json
"trap_chest_room": {
  "room_name": "Suspicious Chest",
  "type": "trap_chest",
  "description": "A chest with strange markings...",
  "trap_damage": 30,
  "trap_effect": "poison"
}
```

### Multi-choice Room
```json
"multichoice_room": {
  "room_name": "Fork in the Road",
  "type": "multichoice",
  "description": "Three paths lie before you...",
  "question": "Which path leads to safety?",
  "answers_to_choose": [
    {"answer": "Left path", "correct": true, "result": "Fortune favors the bold!"},
    {"answer": "Middle path", "correct": false, "result": "A trap awaits!"},
    {"answer": "Right path", "correct": false, "result": "You got lost..."}
  ]
}
```

### Empty Room
```json
"empty_room": {
  "room_name": "Quiet Hall",
  "type": "empty",
  "description": "An empty hallway. Nothing here but dust and cobwebs."
}
```

## Phase 4: Boss Integration
- Link boss_id to bosses.json
- Add boss dialogues from dialogues.json
- Boss loot tables from boss data
- Completion rewards scale with difficulty

## Files to Modify
1. `data/dungeons.json` - Complete rewrite
2. `main.py` - Add dungeon methods and menu integration
3. `data/bosses.json` - Ensure all dungeon bosses exist

## Testing Plan
1. Test dungeon browsing and selection
2. Test all room types (question, battle, chest, trap, multichoice, empty)
3. Test room progression
4. Test boss encounters
5. Test death penalties
6. Test reward system
7. Test completion tracking

