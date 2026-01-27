# TODO: Dungeon and Weekly Challenges Overhaul

## Phase 1: Restructure dungeons.json
- [ ] Create new dungeon format with pre-defined rooms
- [ ] Add 15 dungeons with increasing difficulty
- [ ] Include all room types: question, battle, chest, chest_trap, multi_choice, empty
- [ ] Add boss encounters for dungeons with has_boss: true
- [ ] Add completion rewards to each dungeon

## Phase 2: Update main.py Menu Structure
- [ ] Reorder menu options:
  - Dungeons becomes option 9 (before Alchemy)
  - Shift other options accordingly
- [ ] Add new `visit_dungeons()` method
- [ ] Add dungeon exploration mechanics
- [ ] Implement room-by-room progression
- [ ] Implement boss encounter system for dungeons
- [ ] Add death penalty (gold reduction) for dungeon failures

## Phase 3: Room Types Implementation
- [ ] question: Riddle challenges from challenge_templates
- [ ] battle: Combat encounters with NO flee option
- [ ] chest: Rewards (gold/items) with choice to take
- [ ] chest_trap: Hidden trap that deals damage
- [ ] multi_choice: Multiple options with different effects
- [ ] empty: Nothing happens, continue to next room
- [ ] Implement chest room (final room with boss or treasure)

## Phase 4: Boss Integration
- [ ] Link dungeon bosses from bosses.json
- [ ] Implement boss dialogue system
- [ ] Add boss loot tables
- [ ] Add completion rewards for defeating dungeon bosses

## Phase 5: Testing
- [ ] Test dungeon browsing
- [ ] Test all room types
- [ ] Test boss encounters
- [ ] Test death penalties
- [ ] Test reward system

