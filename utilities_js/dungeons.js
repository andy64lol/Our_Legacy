/**
 * Dungeon System for Our Legacy (Browser Version)
 * Handles all dungeon-related gameplay
 * Ported from utilities/dungeons.py
 */

import { Colors } from './settings.js';
import { getRarityColor } from './shop.js';
import { Enemy, Boss } from './entities.js';

/**
 * Get the color for an item rarity
 * @param {string} rarity - Item rarity
 * @returns {string} Color code
 */
function getRarityColorLocal(rarity) {
  return getRarityColor(rarity);
}

/**
 * Dungeon System class
 */
export class DungeonSystem {
  /**
   * @param {Object} gameInstance - Game instance
   */
  constructor(gameInstance) {
    this.game = gameInstance;
    // Access game data through game instance
    this.lang = gameInstance.lang;
    this.enemiesData = gameInstance.enemiesData;
    this.areasData = gameInstance.areasData;
    this.itemsData = gameInstance.itemsData;
    this.bossesData = gameInstance.bossesData;
    this.dialoguesData = gameInstance.dialoguesData;
    this.dungeonsData = gameInstance.dungeonsData;
    
    // Dungeon state tracking
    this.currentDungeon = null;
    this.dungeonProgress = 0;
    this.dungeonRooms = [];
    this.dungeonState = {};
  }

  /**
   * Visit the dungeon menu
   * @param {Function} askFunc - Ask function for input
   * @returns {Promise<void>}
   */
  async visitDungeons(askFunc) {
    if (!this.game.player) {
      console.log(this.lang.get("no_character") || "No character created yet.");
      return;
    }

    console.log("\n=== DUNGEONS ===");
    console.log("The dungeon portal awaits...");

    // Check if player is in a dungeon
    if (this.currentDungeon) {
      console.log(`\n${Colors.YELLOW}You are currently in: ${this.currentDungeon.name}${Colors.END}`);
      console.log(`Progress: Room ${this.dungeonProgress + 1}/${this.dungeonRooms.length}`);

      const choice = (await askFunc("Continue dungeon (C) or Exit (E)? ")).trim().toUpperCase();
      if (choice === 'C') {
        await this.continueDungeon(askFunc);
      } else if (choice === 'E') {
        this.exitDungeon();
      }
      return;
    }

    // Show available dungeons
    const allDungeons = this.dungeonsData && this.dungeonsData.get ? this.dungeonsData.get('dungeons', []) : [];
    if (!allDungeons || allDungeons.length === 0) {
      console.log("No dungeons available.");
      return;
    }

    // Filter dungeons by allowed_areas
    const dungeons = [];
    for (const dungeon of allDungeons) {
      const allowedAreas = dungeon.get('allowed_areas', []);
      if (!allowedAreas || allowedAreas.length === 0 || allowedAreas.includes(this.game.currentArea)) {
        dungeons.push(dungeon);
      }
    }

    if (dungeons.length === 0) {
      console.log(`\n${Colors.YELLOW}No dungeons available in this area.${Colors.END}`);
      return;
    }

    console.log(`\n${Colors.CYAN}Available Dungeons:${Colors.END}`);
    for (let i = 0; i < dungeons.length; i++) {
      const dungeon = dungeons[i];
      const name = dungeon.get('name', 'Unknown');
      const difficulty = dungeon.get('difficulty', [1, 3]);
      const rooms = dungeon.get('rooms', 5);
      const desc = dungeon.get('description', '');

      // Check level requirement
      const minLevel = difficulty[0] * 5;
      const levelOk = this.game.player.level >= minLevel;

      const status = levelOk ? `${Colors.GREEN}Available${Colors.END}` : `${Colors.RED}Level ${minLevel}+ required${Colors.END}`;

      console.log(`${i + 1}. ${Colors.BOLD}${name}${Colors.END} (Difficulty ${difficulty[0]}-${difficulty[1]}, ${rooms} rooms)`);
      console.log(`   ${desc}`);
      console.log(`   Status: ${status}`);
    }

    const choice = (await askFunc(`\nChoose dungeon (1-${dungeons.length}) or press Enter to cancel: `)).trim();
    if (choice && /^\d+$/.test(choice)) {
      const idx = parseInt(choice) - 1;
      if (idx >= 0 && idx < dungeons.length) {
        const dungeon = dungeons[idx];
        const minLevel = dungeon.get('difficulty', [1, 3])[0] * 5;
        if (this.game.player.level >= minLevel) {
          this.enterDungeon(dungeon);
        } else {
          console.log(`You need to be at least level ${minLevel} to enter this dungeon.`);
        }
      } else {
        console.log("Invalid choice.");
      }
    }
  }

  /**
   * Enter a dungeon
   * @param {Object} dungeon - Dungeon data
   */
  enterDungeon(dungeon) {
    console.log(`\n${Colors.MAGENTA}${Colors.BOLD}Entering ${dungeon.get('name', 'Dungeon')}!${Colors.END}`);
    console.log(dungeon.get('description', ''));

    // Set dungeon state
    this.currentDungeon = dungeon;
    this.dungeonProgress = 0;
    this.dungeonState = {
      startTime: new Date().toISOString(),
      totalRooms: dungeon.get('rooms', 5),
      currentRoom: 0
    };

    // Generate dungeon rooms
    this.generateDungeonRooms(dungeon);

    // Start with first room
    this.continueDungeonDungeon();
  }

  /**
   * Generate dungeon rooms
   * @param {Object} dungeon - Dungeon data
   */
  generateDungeonRooms(dungeon) {
    const roomWeights = dungeon.get('room_weights', {});
    const totalRooms = dungeon.get('rooms', 5);

    this.dungeonRooms = [];

    // Validate room_weights
    let finalWeights = {};
    if (!roomWeights || Object.values(roomWeights).reduce((a, b) => a + b, 0) === 0) {
      finalWeights = {
        'battle': 40,
        'question': 20,
        'chest': 15,
        'empty': 15,
        'trap_chest': 5,
        'multi_choice': 5
      };
    } else {
      finalWeights = roomWeights;
    }

    const roomTypes = Object.keys(finalWeights);
    const weights = Object.values(finalWeights);

    // Generate rooms
    for (let i = 0; i < totalRooms; i++) {
      let roomType;
      if (i === totalRooms - 1) {
        roomType = 'boss';
      } else {
        roomType = this.weightedRandom(roomTypes, weights);
      }

      const difficultyRange = dungeon.get('difficulty', [1, 3]);
      const difficulty = difficultyRange[0] + (i * 0.5);

      this.dungeonRooms.push({
        type: roomType,
        roomNumber: i + 1,
        difficulty: difficulty
      });
    }
  }

  /**
   * Weighted random selection
   * @param {Array} items - Items array
   * @param {Array} weights - Weights array
   * @returns {string} Selected item
   */
  weightedRandom(items, weights) {
    const totalWeight = weights.reduce((a, b) => a + b, 0);
    let random = Math.random() * totalWeight;
    for (let i = 0; i < items.length; i++) {
      random -= weights[i];
      if (random <= 0) {
        return items[i];
      }
    }
    return items[items.length - 1];
  }

  /**
   * Continue through the current dungeon
   */
  async continueDungeon(askFunc) {
    while (this.currentDungeon && this.dungeonProgress < this.dungeonRooms.length) {
      const room = this.dungeonRooms[this.dungeonProgress];

      console.log(`\n${Colors.CYAN}${Colors.BOLD}=== Room ${room.roomNumber} ===${Colors.END}`);

      // Handle room based on type
      const roomType = room.type;
      if (roomType === 'question') {
        await this.handleQuestionRoom(room, askFunc);
      } else if (roomType === 'battle') {
        await this.handleBattleRoom(room, askFunc);
      } else if (roomType === 'chest') {
        await this.handleChestRoom(room);
      } else if (roomType === 'trap_chest') {
        await this.handleTrapChestRoom(room, askFunc);
      } else if (roomType === 'multi_choice') {
        await this.handleMultiChoiceRoom(room, askFunc);
      } else if (roomType === 'empty') {
        await this.handleEmptyRoom(room);
      } else if (roomType === 'boss') {
        await this.handleBossRoom(room, askFunc);
      }

      // Check if player died
      if (!this.game.player || !this.game.player.isAlive()) {
        this.dungeonDeath();
        return;
      }
    }

    // Dungeon complete
    if (this.currentDungeon && this.dungeonProgress >= this.dungeonRooms.length) {
      this.completeDungeon();
    }
  }

  /**
   * Continue dungeon (internal)
   */
  continueDungeonDungeon() {
    // Placeholder for internal continuation
  }

  /**
   * Handle question room
   * @param {Object} room - Room data
   * @param {Function} askFunc - Ask function
   */
  async handleQuestionRoom(room, askFunc) {
    if (!this.game.player) return;
    console.log("A mystical pedestal stands in the center of the room...");

    const challengeTemplates = this.dungeonsData && this.dungeonsData.get ? this.dungeonsData.get('challenge_templates', {}) : {};
    const questionTemplate = challengeTemplates.get ? challengeTemplates.get('question', {}) : {};

    if (!questionTemplate || !questionTemplate.get || !questionTemplate.get('types') || questionTemplate.get('types').length === 0) {
      console.log("No questions available. Moving forward...");
      this.advanceRoom();
      return;
    }

    const questionTypes = questionTemplate.get('types', []);
    const questionData = questionTypes[Math.floor(Math.random() * questionTypes.length)];

    console.log("\n=== Riddle ===");
    console.log(questionData.get('question', 'Riddle not found'));

    let attempts = 0;
    const maxAttempts = questionData.get('max_attempts', 3);

    while (attempts < maxAttempts) {
      const answer = (await askFunc(`Your answer (${maxAttempts - attempts} tries left, or type 'leave'): `)).trim().toLowerCase();

      if (answer === 'leave') {
        console.log("You give up on the riddle.");
        break;
      }

      const correctAnswer = (questionData.get('answer', '')).toLowerCase();
      if (answer === correctAnswer) {
        console.log("Correct!");
        
        const reward = questionData.get('success_reward', {});
        if (reward.get && this.game.player) {
          if (reward.get('gold')) {
            this.game.player.gold += reward.get('gold');
            console.log(`You gained ${reward.get('gold')} gold!`);
          }
          if (reward.get('experience')) {
            this.game.player.gainExperience(reward.get('experience'));
            console.log(`You gained ${reward.get('experience')} experience!`);
          }
        }
        this.advanceRoom();
        return;
      } else {
        attempts++;
        console.log("Incorrect. Try again.");
      }
    }

    // Failed - take damage
    const damage = questionData.get('failure_damage', 15);
    if (this.game.player) {
      const actualDamage = this.game.player.takeDamage(damage);
      console.log(`You took ${actualDamage} damage from the failed riddle!`);

      if (this.game.player.isAlive()) {
        this.advanceRoom();
      } else {
        this.dungeonDeath();
      }
    }
  }

  /**
   * Handle battle room
   * @param {Object} room - Room data
   * @param {Function} askFunc - Ask function
   */
  async handleBattleRoom(room, askFunc) {
    if (!this.game.player) {
      this.advanceRoom();
      return;
    }

    console.log("Combat approaches! Enemies are preparing to attack...");

    // Generate enemies
    const difficulty = room.difficulty || 1;
    const enemyCount = Math.max(1, Math.floor(difficulty));

    // Get enemies from current area
    const currentArea = this.game.currentArea;
    const areaData = this.areasData && this.areasData[currentArea] ? this.areasData[currentArea] : {};
    let areaEnemies = areaData.get ? areaData.get('possible_enemies', []) : [];

    if (!areaEnemies || areaEnemies.length === 0) {
      const fallbackEnemies = ['goblin', 'orc', 'skeleton'];
      areaEnemies = fallbackEnemies.filter(e => this.enemiesData && this.enemiesData[e]);
      if (areaEnemies.length === 0 && this.enemiesData) {
        areaEnemies = Object.keys(this.enemiesData).slice(0, 5);
      }
    }

    const enemies = [];
    for (let i = 0; i < enemyCount; i++) {
      if (areaEnemies.length === 0) break;
      const enemyName = areaEnemies[Math.floor(Math.random() * areaEnemies.length)];
      const enemyData = this.enemiesData ? this.enemiesData[enemyName] : null;
      
      if (enemyData) {
        // Scale enemy stats
        const scaledData = { ...enemyData };
        scaledData.hp = Math.floor(scaledData.hp * (0.8 + difficulty * 0.2));
        scaledData.attack = Math.floor(scaledData.attack * (0.8 + difficulty * 0.2));
        scaledData.defense = Math.floor(scaledData.defense * (0.8 + difficulty * 0.2));
        
        const enemy = new Enemy(scaledData);
        enemies.push(enemy);
      }
    }

    if (enemies.length === 0) {
      console.log(`${Colors.YELLOW}No enemies found! You proceed safely.${Colors.END}`);
      this.advanceRoom();
      return;
    }

    console.log(`Encounter: ${enemies.length} enemy(s)!`);

    // Battle each enemy
    for (const enemy of enemies) {
      if (!this.game.player || !this.game.player.isAlive()) break;
      await this.game.battle(enemy);
    }

    if (this.game.player && this.game.player.isAlive()) {
      console.log("You cleared the battle room!");
      this.advanceRoom();
    } else {
      this.dungeonDeath();
    }
  }

  /**
   * Handle chest room
   * @param {Object} room - Room data
   */
  async handleChestRoom(room) {
    if (!this.game.player) {
      this.advanceRoom();
      return;
    }

    console.log("A treasure chest stands in the center of the room!");

    const difficulty = room.difficulty || 1;
    let chestType;
    if (difficulty >= 8) chestType = 'legendary';
    else if (difficulty >= 5) chestType = 'large';
    else if (difficulty >= 3) chestType = 'medium';
    else chestType = 'small';

    const chestTemplates = this.dungeonsData && this.dungeonsData.get ? this.dungeonsData.get('chest_templates', {}) : {};
    const chestData = chestTemplates.get ? chestTemplates.get(chestType, chestTemplates.get('small', {})) : {};

    console.log(`You found a ${chestData.get ? chestData.get('name', 'chest') : 'chest'}!`);

    // Generate rewards
    const goldRange = chestData.get ? chestData.get('gold_range', [50, 150]) : [50, 150];
    const goldReward = Math.floor(Math.random() * (goldRange[1] - goldRange[0] + 1)) + goldRange[0];

    const itemCountRange = chestData.get ? chestData.get('item_count_range', [1, 2]) : [1, 2];
    const itemCount = Math.floor(Math.random() * (itemCountRange[1] - itemCountRange[0] + 1)) + itemCountRange[0];

    const expReward = chestData.get ? chestData.get('experience', 100) : 100;

    // Give rewards
    this.game.player.gold += goldReward;
    this.game.player.gainExperience(expReward);

    console.log(`\n${Colors.GOLD}You found ${goldReward} gold!${Colors.END}`);
    console.log(`${Colors.MAGENTA}You gained ${expReward} experience!${Colors.END}`);

    // Generate items
    const itemsFound = [];
    const itemRarities = chestData.get ? chestData.get('item_rarity', ['common']) : ['common'];

    for (let i = 0; i < itemCount; i++) {
      const rarity = itemRarities[Math.floor(Math.random() * itemRarities.length)];
      const possibleItems = this.itemsData ? Object.values(this.itemsData).filter(item => item.rarity === rarity) : [];
      
      if (possibleItems.length > 0) {
        const item = possibleItems[Math.floor(Math.random() * possibleItems.length)];
        itemsFound.push(item.name);
        this.game.player.inventory.push(item.name);
        this.game.updateMissionProgress('collect', item.name);
      } else {
        const bonusGold = Math.floor(Math.random() * (75 - 25 + 1)) + 25;
        this.game.player.gold += bonusGold;
        console.log(`Added ${bonusGold} gold instead.`);
      }
    }

    if (itemsFound.length > 0) {
      console.log("\nItems found:");
      for (const itemName of itemsFound) {
        const itemData = this.itemsData ? this.itemsData[itemName] : {};
        const color = getRarityColorLocal(itemData.rarity || 'common');
        console.log(`  - ${color}${itemName}${Colors.END}`);
      }
    }

    this.advanceRoom();
  }

  /**
   * Handle trap chest room
   * @param {Object} room - Room data
   * @param {Function} askFunc - Ask function
   */
  async handleTrapChestRoom(room, askFunc) {
    if (!this.game.player) {
      this.advanceRoom();
      return;
    }

    console.log("A suspicious-looking chest is in the room...");

    const choice = (await askFunc("Open the chest (O) or leave it (L)? ")).trim().toUpperCase();

    if (choice === 'L') {
      console.log("You leave the chest alone.");
      this.advanceRoom();
      return;
    }

    // Roll for trap
    const trapChance = 0.7;
    if (Math.random() < trapChance) {
      console.log("The chest was trapped!");

      const challengeTemplates = this.dungeonsData && this.dungeonsData.get ? this.dungeonsData.get('challenge_templates', {}) : {};
      const trapTemplates = challengeTemplates.get ? challengeTemplates.get('trap', {}) : {};
      const trapTypes = trapTemplates.get ? trapTemplates.get('types', []) : [];

      if (trapTypes.length > 0) {
        const trap = trapTypes[Math.floor(Math.random() * trapTypes.length)];
        console.log(trap.description || "A trap springs!");

        // Roll d20 for avoidance
        const roll = Math.floor(Math.random() * 20) + 1;
        const threshold = trapTemplates.get ? trapTemplates.get('success_threshold', 10) : 10;

        console.log(`Roll: ${roll}, Threshold: ${threshold}`);

        if (roll >= threshold) {
          console.log(`${Colors.GREEN}You successfully avoid the trap!${Colors.END}`);
          const successReward = trapTemplates.get ? trapTemplates.get('success_reward', {}) : {};
          if (successReward.get) {
            if (successReward.get('gold')) {
              this.game.player.gold += successReward.get('gold');
            }
            if (successReward.get('experience')) {
              this.game.player.gainExperience(successReward.get('experience'));
            }
          }
        }
      }
    }

    this.advanceRoom();
  }

  /**
   * Handle multi choice room
   * @param {Object} room - Room data
   * @param {Function} askFunc - Ask function
   */
  async handleMultiChoiceRoom(room, askFunc) {
    if (!this.game.player) {
      this.advanceRoom();
      return;
    }

    console.log("You stand at a crossroads with multiple paths...");

    const challengeTemplates = this.dungeonsData && this.dungeonsData.get ? this.dungeonsData.get('challenge_templates', {}) : {};
    const selectionTemplate = challengeTemplates.get ? challengeTemplates.get('selection', {}) : {};

    if (!selectionTemplate.get || !selectionTemplate.get('types') || selectionTemplate.get('types').length === 0) {
      console.log("The path seems safe. You proceed.");
      this.advanceRoom();
      return;
    }

    const challenge = selectionTemplate.get('types', [])[Math.floor(Math.random() * selectionTemplate.get('types', []).length)];

    console.log("\n=== Decision ===");
    console.log(challenge.get('question', 'What will you do?'));

    const options = challenge.get('options', []);
    for (let i = 0; i < options.length; i++) {
      console.log(`${i + 1}. ${options[i].text}`);
    }

    const choice = (await askFunc(`Your choice (1-${options.length}): `)).trim();

    let outcome;
    if (choice && /^\d+$/.test(choice) && parseInt(choice) >= 1 && parseInt(choice) <= options.length) {
      outcome = options[parseInt(choice) - 1];
    } else {
      console.log("Invalid choice. You hesitate...");
      return;
    }

    console.log(`\n${outcome.reason || 'You proceed...'}`);

    if (outcome.correct) {
      const successReward = challenge.get('success_reward', {});
      if (successReward.get && this.game.player) {
        if (successReward.get('gold')) {
          this.game.player.gold += successReward.get('gold');
        }
        if (successReward.get('experience')) {
          this.game.player.gainExperience(successReward.get('experience'));
        }
      }
    } else if (this.game.player) {
      const damage = challenge.get('failure_damage', 10);
      const actualDamage = this.game.player.takeDamage(damage);
      console.log(`You took ${actualDamage} damage!`);

      if (!this.game.player.isAlive()) {
        this.dungeonDeath();
        return;
      }
    }

    this.advanceRoom();
  }

  /**
   * Handle empty room
   * @param {Object} room - Room data
   */
  async handleEmptyRoom(room) {
    console.log("An empty room stretches before you...");

    // Small chance for hidden treasure or encounter
    if (Math.random() < 0.3) {
      if (Math.random() < 0.5) {
        // Hidden treasure
        if (this.game.player) {
          const goldFound = Math.floor(Math.random() * (50 - 10 + 1)) + 10;
          this.game.player.gold += goldFound;
          console.log(`${Colors.GOLD}You found ${goldFound} gold hidden in the room!${Colors.END}`);
        }
      } else {
        // Random encounter
        console.log("You hear a noise...");
        if (this.game.player && this.game.randomEncounter) {
          await this.game.randomEncounter();
          if (this.game.player && !this.game.player.isAlive()) {
            this.dungeonDeath();
            return;
          }
        }
      }
    } else {
      console.log("Nothing of interest here.");
    }

    this.advanceRoom();
  }

  /**
   * Handle boss room
   * @param {Object} room - Room data
   * @param {Function} askFunc - Ask function
   */
  async handleBossRoom(room, askFunc) {
    const dungeon = this.currentDungeon;
    const bossId = dungeon ? dungeon.get('boss_id') : null;

    if (bossId && this.bossesData && this.bossesData[bossId]) {
      const bossData = this.bossesData[bossId];
      const boss = new Boss(bossData, this.dialoguesData);

      console.log("\n=== BOSS BATTLE ===");
      console.log(`You face: ${boss.name}`);
      console.log(boss.description);

      const startDialogue = boss.getDialogue ? boss.getDialogue("on_start_battle") : null;
      if (startDialogue) {
        console.log(`\n${Colors.CYAN}${boss.name}:${Colors.END} ${startDialogue}`);
      }

      await this.game.battle(boss);

      if (this.game.player && this.game.player.isAlive()) {
        console.log("\n=== VICTORY ===");
        console.log(`You defeated ${boss.name}!`);

        const expReward = (boss.experienceReward || 0) * 2;
        const goldReward = (boss.goldReward || 0) * 2;

        this.game.player.gainExperience(expReward);
        this.game.player.gold += goldReward;

        console.log(`Gained ${Colors.MAGENTA}${expReward} experience${Colors.END}`);
        console.log(`Gained ${Colors.GOLD}${goldReward} gold${Colors.END}`);

        this.completeDungeon();
      } else {
        this.dungeonDeath();
      }
    } else {
      console.log(`${Colors.YELLOW}Boss data not found. A powerful enemy appears!${Colors.END}`);
      
      if (this.game.player) {
        const completionReward = dungeon ? dungeon.get('completion_reward', {}) : {};
        const expReward = Math.floor((completionReward.get ? completionReward.get('experience', 500) : 500) / 2);
        const goldReward = Math.floor((completionReward.get ? completionReward.get('gold', 300) : 300) / 2);

        this.game.player.gainExperience(expReward);
        this.game.player.gold += goldReward;

        console.log(`Gained ${Colors.MAGENTA}${expReward} experience${Colors.END}`);
        console.log(`Gained ${Colors.GOLD}${goldReward} gold${Colors.END}`);
      }

      this.completeDungeon();
    }
  }

  /**
   * Advance to the next room
   */
  advanceRoom() {
    this.dungeonProgress++;
    if (this.dungeonProgress < this.dungeonRooms.length) {
      this.dungeonState.currentRoom = this.dungeonProgress;
    }

    if (this.dungeonProgress >= this.dungeonRooms.length) {
      this.completeDungeon();
    } else {
      console.log("\nMoving to the next room...");
    }
  }

  /**
   * Complete the current dungeon
   */
  completeDungeon() {
    if (!this.currentDungeon) return;

    const dungeon = this.currentDungeon;
    console.log("\n=== DUNGEON COMPLETE ===");
    console.log(`You cleared ${dungeon.get('name', 'the dungeon')}!`);

    // Calculate completion time
    const startTimeStr = this.dungeonState.startTime;
    if (startTimeStr) {
      const startTime = new Date(startTimeStr);
      const endTime = new Date();
      const duration = Math.floor((endTime - startTime) / 1000);
      console.log(`Completion time: ${Math.floor(duration / 60)}m ${duration % 60}s`);
    }

    // Update challenge
    if (this.game.updateChallengeProgress) {
      this.game.updateChallengeProgress('dungeon_complete');
    }

    // Give completion rewards
    const completionReward = dungeon.get ? dungeon.get('completion_reward', {}) : {};
    if (completionReward && completionReward.get && this.game.player) {
      console.log(`\n${Colors.GOLD}${Colors.BOLD}Completion Rewards:${Colors.END}`);

      if (completionReward.get('gold', 0) > 0) {
        this.game.player.gold += completionReward.get('gold', 0);
        console.log(`  ${Colors.GOLD}+${completionReward.get('gold', 0)} gold${Colors.END}`);
      }

      if (completionReward.get('experience', 0) > 0) {
        this.game.player.gainExperience(completionReward.get('experience', 0));
        console.log(`  ${Colors.MAGENTA}+${completionReward.get('experience', 0)} experience${Colors.END}`);
      }

      const items = completionReward.get ? completionReward.get('items', []) : [];
      if (items.length > 0) {
        console.log("\nItems received:");
        for (const itemName of items) {
          this.game.player.inventory.push(itemName);
          const itemData = this.itemsData ? this.itemsData[itemName] : {};
          const color = getRarityColorLocal(itemData.rarity || 'common');
          console.log(`    - ${color}${itemName}${Colors.END}`);
          this.game.updateMissionProgress('collect', itemName);
        }
      }
    }

    // Clear dungeon state
    this.currentDungeon = null;
    this.dungeonProgress = 0;
    this.dungeonRooms = [];
    this.dungeonState = {};
  }

  /**
   * Exit the current dungeon
   */
  exitDungeon() {
    if (!this.game.player) return;

    if (this.currentDungeon) {
      console.log(`\n${Colors.YELLOW}Exiting ${this.currentDungeon.name}...${Colors.END}`);
    } else {
      console.log("\nExiting dungeon...");
    }

    // Optional penalty for early exit
    if (this.dungeonProgress > 0 && this.game.player) {
      const penaltyGold = Math.min(Math.floor(this.game.player.gold / 10), 100);
      if (penaltyGold > 0) {
        this.game.player.gold -= penaltyGold;
        console.log(`${Colors.RED}Exit penalty: Lost ${penaltyGold} gold${Colors.END}`);
      }
    }

    // Clear dungeon state
    this.currentDungeon = null;
    this.dungeonProgress = 0;
    this.dungeonRooms = [];
    this.dungeonState = {};
  }

  /**
   * Handle death in dungeon
   */
  dungeonDeath() {
    if (!this.game.player) return;
    
    console.log(`\n${Colors.RED}${Colors.BOLD}You have fallen in the dungeon!${Colors.END}`);

    if (this.game.player) {
      // Death penalty
      this.game.player.hp = Math.floor(this.game.player.maxHp / 2);
      this.game.player.mp = Math.floor(this.game.player.maxMp / 2);

      // Lose some gold
      const goldLoss = Math.min(Math.floor(this.game.player.gold / 5), 200);
      this.game.player.gold -= goldLoss;
      console.log(`Lost ${goldLoss} gold.`);
    }

    // Return to starting village
    this.game.currentArea = "starting_village";
    console.log("You respawn at the starting village.");

    // Clear dungeon state
    this.currentDungeon = null;
    this.dungeonProgress = 0;
    this.dungeonRooms = [];
    this.dungeonState = {};
  }
}

export default DungeonSystem;
