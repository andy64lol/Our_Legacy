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
- [ ] Add death penalty (gold reduction) for dungeon deaths and respawn

## Phase 3: Room Types Implementation
- [ ] Dungeon must contain max and min rooms to reach to boss (if true, if not then directly to reward)
- [ ] question will be "room_id_here":{"room_name": "name", "type":"question", "question": "question to be asked", "correct_answer":"answer","if_answer_incorrect": "type of punishment here, either gold, monster or hp"}
- [ ] battle must be "room_id_here": {"room_name": "name", "type": "battle", "enemy": "enemy_id"},
- [ ] chest "room_id_here": {"room_name":"name","type":"chest","gold":integrer_number},
- [ ] trap chest is similar, but instead of type being chest it'll be trap_chest, and no gold shall be defined
- [ ] multichoice, change type question to type multichoice, add answers_to_choose parameter
- [ ] empty, just room name and description

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

