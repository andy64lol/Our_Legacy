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
      this.game.print(this.lang.get("no_character") || "No character created yet.");
      return;
    }

    this.game.print("\n=== DUNGEONS ===");
    this.game.print("The dungeon portal awaits...");

    // Check if player is in a dungeon
    if (this.currentDungeon) {
      this.game.print(`\n${Colors.YELLOW}You are currently in: ${this.currentDungeon.name}${Colors.END}`);
      this.game.print(`Progress: Room ${this.dungeonProgress + 1}/${this.dungeonRooms.length}`);

      const choice = (await askFunc("Continue dungeon (C) or Exit (E)? ")).trim().toUpperCase();
      if (choice === 'C') {
        await this.continueDungeon(askFunc);
      } else if (choice === 'E') {
        this.exitDungeon();
      }
      return;
    }

    // Show available dungeons
    const allDungeons = this.dungeonsData.dungeons || [];
    if (!allDungeons || allDungeons.length === 0) {
      this.game.print("No dungeons available.");
      return;
    }

    // Filter dungeons by allowed_areas
    const dungeons = allDungeons.filter(d => {
      const allowedAreas = d.allowed_areas || [];
      return allowedAreas.length === 0 || allowedAreas.includes(this.game.currentArea);
    });

    if (dungeons.length === 0) {
      this.game.print(`\n${Colors.YELLOW}No dungeons available in this area.${Colors.END}`);
      return;
    }

    this.game.print(`\n${Colors.CYAN}Available Dungeons:${Colors.END}`);
    dungeons.forEach((d, i) => {
      const difficulty = d.difficulty || [1, 3];
      const minLevel = difficulty[0] * 5;
      const status = this.game.player.level >= minLevel ? `${Colors.GREEN}Available${Colors.END}` : `${Colors.RED}Level ${minLevel}+ required${Colors.END}`;
      this.game.print(`${i + 1}. ${Colors.BOLD}${d.name || 'Unknown'}${Colors.END} (Difficulty ${difficulty[0]}-${difficulty[1]}, ${d.rooms || 5} rooms)`);
      this.game.print(`   ${d.description || ''}`);
      this.game.print(`   Status: ${status}`);
    });

    const choice = (await askFunc(`\nChoose dungeon (1-${dungeons.length}) or Enter: `)).trim();
    if (choice && /^\d+$/.test(choice)) {
      const idx = parseInt(choice) - 1;
      const dungeon = dungeons[idx];
      if (dungeon) {
        const minLevel = (dungeon.difficulty || [1, 3])[0] * 5;
        if (this.game.player.level >= minLevel) this.enterDungeon(dungeon);
        else this.game.print(`Need level ${minLevel}!`);
      }
    }
  }

  enterDungeon(dungeon) {
    this.game.print(`\n${Colors.MAGENTA}${Colors.BOLD}Entering ${dungeon.name || 'Dungeon'}!${Colors.END}`);
    this.game.print(dungeon.description || '');

    this.currentDungeon = dungeon;
    this.dungeonProgress = 0;
    this.dungeonState = { startTime: new Date().toISOString(), totalRooms: dungeon.rooms || 5, currentRoom: 0 };
    this.generateDungeonRooms(dungeon);
    this.continueDungeon(this.game.ask);
  }

  generateDungeonRooms(dungeon) {
    const roomWeights = dungeon.room_weights || { 'battle': 40, 'question': 20, 'chest': 15, 'empty': 15, 'trap_chest': 5, 'multi_choice': 5 };
    const totalRooms = dungeon.rooms || 5;
    this.dungeonRooms = [];

    const roomTypes = Object.keys(roomWeights);
    const weights = Object.values(roomWeights);

    for (let i = 0; i < totalRooms; i++) {
      const roomType = (i === totalRooms - 1) ? 'boss' : this.weightedRandom(roomTypes, weights);
      const diff = Array.isArray(dungeon.difficulty) ? dungeon.difficulty[0] : (dungeon.difficulty || 1);
      const difficulty = diff + (i * 0.5);
      this.dungeonRooms.push({ type: roomType, roomNumber: i + 1, difficulty });
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

      this.game.print(`\n${Colors.CYAN}${Colors.BOLD}=== Room ${room.roomNumber} ===${Colors.END}`);

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
    this.game.print("A mystical pedestal stands in the center of the room...");

    const challengeTemplates = this.dungeonsData?.challenge_templates || {};
    const questionTemplate = challengeTemplates.question || {};
    const questionTypes = questionTemplate.types || [];

    if (questionTypes.length === 0) {
      this.game.print("No questions available. Moving forward...");
      this.advanceRoom();
      return;
    }

    const questionData = questionTypes[Math.floor(Math.random() * questionTypes.length)];
    this.game.print("\n=== Riddle ===");
    this.game.print(questionData.question || 'Riddle not found');

    let attempts = 0;
    const maxAttempts = questionData.max_attempts || 3;

    while (attempts < maxAttempts) {
      const answer = (await askFunc(`Your answer (${maxAttempts - attempts} tries left, or type 'leave'): `)).trim().toLowerCase();
      if (answer === 'leave') break;

      if (answer === (questionData.answer || '').toLowerCase()) {
        this.game.print("Correct!");
        const reward = questionData.success_reward || {};
        if (reward.gold) this.game.player.gold += reward.gold;
        if (reward.experience) this.game.player.gainExperience(reward.experience);
        this.advanceRoom();
        return;
      }
      attempts++;
      this.game.print("Incorrect.");
    }

    const damage = questionData.failure_damage || 15;
    this.game.player.takeDamage(damage);
    if (this.game.player.isAlive()) this.advanceRoom();
    else this.dungeonDeath();
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

    this.game.print("Combat approaches! Enemies are preparing to attack...");

    // Generate enemies
    const difficulty = room.difficulty || 1;
    const enemyCount = Math.max(1, Math.floor(difficulty));

    // Get enemies from current area
    const currentArea = this.game.currentArea;
    const areaData = (this.areasData && this.areasData[currentArea]) ? this.areasData[currentArea] : {};
    let areaEnemies = areaData.possible_enemies || [];

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
      this.game.print(`${Colors.YELLOW}No enemies found! You proceed safely.${Colors.END}`);
      this.advanceRoom();
      return;
    }

    this.game.print(`Encounter: ${enemies.length} enemy(s)!`);

    // Battle each enemy
    for (const enemy of enemies) {
      if (!this.game.player || !this.game.player.isAlive()) break;
      await this.game.battle(enemy);
    }

    if (this.game.player && this.game.player.isAlive()) {
      this.game.print("You cleared the battle room!");
      this.advanceRoom();
    } else {
      this.dungeonDeath();
    }
  }

  async handleChestRoom(room) {
    if (!this.game.player) {
      this.advanceRoom();
      return;
    }

    this.game.print("A treasure chest stands in the center of the room!");
    const difficulty = room.difficulty || 1;
    let chestType = 'small';
    if (difficulty >= 8) chestType = 'legendary';
    else if (difficulty >= 5) chestType = 'large';
    else if (difficulty >= 3) chestType = 'medium';

    const chestTemplates = this.dungeonsData?.chest_templates || {};
    const chestData = chestTemplates[chestType] || chestTemplates['small'] || {};

    this.game.print(`You found a ${chestData.name || 'chest'}!`);

    const goldRange = chestData.gold_range || [50, 150];
    const goldReward = Math.floor(Math.random() * (goldRange[1] - goldRange[0] + 1)) + goldRange[0];
    const itemCountRange = chestData.item_count_range || [1, 2];
    const itemCount = Math.floor(Math.random() * (itemCountRange[1] - itemCountRange[0] + 1)) + itemCountRange[0];
    const expReward = chestData.experience || 100;

    this.game.player.gold += goldReward;
    this.game.player.gainExperience(expReward);
    this.game.print(`\n${Colors.GOLD}You found ${goldReward} gold!${Colors.END}`);
    this.game.print(`${Colors.MAGENTA}You gained ${expReward} experience!${Colors.END}`);

    const itemRarities = chestData.item_rarity || ['common'];
    for (let i = 0; i < itemCount; i++) {
      const rarity = itemRarities[Math.floor(Math.random() * itemRarities.length)];
      const possibleItems = Object.values(this.game.itemsData || {}).filter(item => item.rarity === rarity);
      if (possibleItems.length > 0) {
        const item = possibleItems[Math.floor(Math.random() * possibleItems.length)];
        this.game.player.inventory.push(item.name);
        this.game.updateMissionProgress('collect', item.name);
        this.game.print(`  - ${getRarityColor(item.rarity || 'common')}${item.name}${Colors.END}`);
      }
    }
    this.advanceRoom();
  }

  async handleTrapChestRoom(room, askFunc) {
    if (!this.game.player) return;
    this.game.print("A suspicious-looking chest is in the room...");
    const choice = (await askFunc("Open (O) or Leave (L)? ")).trim().toUpperCase();
    if (choice !== 'O') {
      this.advanceRoom();
      return;
    }

    if (Math.random() < 0.7) {
      this.game.print("The chest was trapped!");
      const trapTemplates = this.dungeonsData?.challenge_templates?.trap || {};
      const trapTypes = trapTemplates.types || [];
      if (trapTypes.length > 0) {
        const trap = trapTypes[Math.floor(Math.random() * trapTypes.length)];
        this.game.print(trap.description || "A trap springs!");
        const roll = Math.floor(Math.random() * 20) + 1;
        if (roll < (trapTemplates.success_threshold || 10)) {
          this.game.player.takeDamage(trap.damage || 20);
        } else {
          this.game.print("You avoided it!");
        }
      }
    } else {
      await this.handleChestRoom(room);
      return;
    }
    this.advanceRoom();
  }

  async handleMultiChoiceRoom(room, askFunc) {
    if (!this.game.player) return;
    const selectionTemplate = this.dungeonsData?.challenge_templates?.selection || {};
    const types = selectionTemplate.types || [];
    if (types.length === 0) {
      this.advanceRoom();
      return;
    }
    const challenge = types[Math.floor(Math.random() * types.length)];
    if (!challenge) {
      this.advanceRoom();
      return;
    }

    this.game.print(`\n=== Decision ===\n${challenge.question}`);
    challenge.options.forEach((o, i) => this.game.print(`${i+1}. ${o.text}`));
    const choice = parseInt(await askFunc("Choice: ")) - 1;
    const outcome = challenge.options[choice];
    if (outcome) {
      this.game.print(outcome.reason);
      if (outcome.correct) {
        if (challenge.success_reward?.gold) this.game.player.gold += challenge.success_reward.gold;
      } else {
        this.game.player.takeDamage(challenge.failure_damage || 10);
      }
    }
    this.advanceRoom();
  }

  /**
   * Handle empty room
   * @param {Object} room - Room data
   */
  async handleEmptyRoom(room) {
    this.game.print("An empty room stretches before you...");

    // Small chance for hidden treasure or encounter
    if (Math.random() < 0.3) {
      if (Math.random() < 0.5) {
        // Hidden treasure
        if (this.game.player) {
          const goldFound = Math.floor(Math.random() * (50 - 10 + 1)) + 10;
          this.game.player.gold += goldFound;
          this.game.print(`${Colors.GOLD}You found ${goldFound} gold hidden in the room!${Colors.END}`);
        }
      } else {
        // Random encounter
        this.game.print("You hear a noise...");
        if (this.game.player && this.game.randomEncounter) {
          await this.game.randomEncounter();
          if (this.game.player && !this.game.player.isAlive()) {
            this.dungeonDeath();
            return;
          }
        }
      }
    } else {
      this.game.print("Nothing of interest here.");
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
    const bossId = dungeon ? dungeon.boss_id : null;

    if (bossId && this.bossesData && this.bossesData[bossId]) {
      const bossData = this.bossesData[bossId];
      const boss = new Boss(bossData, this.dialoguesData);

      this.game.print("\n=== BOSS BATTLE ===");
      this.game.print(`You face: ${boss.name}`);
      this.game.print(boss.description);

      const startDialogue = boss.dialogue?.on_start_battle;
      if (startDialogue) {
        this.game.print(`\n${Colors.CYAN}${boss.name}:${Colors.END} ${startDialogue}`);
      }

      await this.game.battle(boss);

      if (this.game.player && this.game.player.isAlive()) {
        this.game.print("\n=== VICTORY ===");
        this.game.print(`You defeated ${boss.name}!`);

        const expReward = (boss.experienceReward || 0) * 2;
        const goldReward = (boss.goldReward || 0) * 2;

        this.game.player.gainExperience(expReward);
        this.game.player.gold += goldReward;

        this.game.print(`Gained ${Colors.MAGENTA}${expReward} experience${Colors.END}`);
        this.game.print(`Gained ${Colors.GOLD}${goldReward} gold${Colors.END}`);

        this.completeDungeon();
      } else {
        this.dungeonDeath();
      }
    } else {
      this.game.print(`${Colors.YELLOW}Boss data not found. A powerful enemy appears!${Colors.END}`);
      
      if (this.game.player) {
        const completionReward = dungeon ? (dungeon.completion_reward || {}) : {};
        const expReward = Math.floor((completionReward.experience || 500) / 2);
        const goldReward = Math.floor((completionReward.gold || 300) / 2);

        this.game.player.gainExperience(expReward);
        this.game.player.gold += goldReward;

        this.game.print(`Gained ${Colors.MAGENTA}${expReward} experience${Colors.END}`);
        this.game.print(`Gained ${Colors.GOLD}${goldReward} gold${Colors.END}`);
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
      this.game.print("\nMoving to the next room...");
    }
  }

  /**
   * Complete the current dungeon
   */
  completeDungeon() {
    if (!this.currentDungeon) return;

    const dungeon = this.currentDungeon;
    this.game.print("\n=== DUNGEON COMPLETE ===");
    this.game.print(`You cleared ${dungeon.name || 'the dungeon'}!`);

    // Calculate completion time
    const startTimeStr = this.dungeonState.startTime;
    if (startTimeStr) {
      const startTime = new Date(startTimeStr);
      const endTime = new Date();
      const duration = Math.floor((endTime - startTime) / 1000);
      this.game.print(`Completion time: ${Math.floor(duration / 60)}m ${duration % 60}s`);
    }

    // Update challenge
    if (this.game.updateChallengeProgress) {
      this.game.updateChallengeProgress('dungeon_complete');
    }

    // Give completion rewards
    const completionReward = dungeon.completion_reward || {};
    if (completionReward && this.game.player) {
      this.game.print(`\n${Colors.GOLD}${Colors.BOLD}Completion Rewards:${Colors.END}`);

      if ((completionReward.gold || 0) > 0) {
        this.game.player.gold += completionReward.gold || 0;
        this.game.print(`  ${Colors.GOLD}+${completionReward.gold || 0} gold${Colors.END}`);
      }

      if ((completionReward.experience || 0) > 0) {
        this.game.player.gainExperience(completionReward.experience || 0);
        this.game.print(`  ${Colors.MAGENTA}+${completionReward.experience || 0} experience${Colors.END}`);
      }

      const items = completionReward.items || [];
      if (items.length > 0) {
        this.game.print("\nItems received:");
        for (const itemName of items) {
          this.game.player.inventory.push(itemName);
          const itemData = this.itemsData ? this.itemsData[itemName] : {};
          const color = getRarityColorLocal(itemData.rarity || 'common');
          this.game.print(`    - ${color}${itemName}${Colors.END}`);
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
      this.game.print(`\n${Colors.YELLOW}Exiting ${this.currentDungeon.name}...${Colors.END}`);
    } else {
      this.game.print("\nExiting dungeon...");
    }

    // Optional penalty for early exit
    if (this.dungeonProgress > 0 && this.game.player) {
      const penaltyGold = Math.min(Math.floor(this.game.player.gold / 10), 100);
      if (penaltyGold > 0) {
        this.game.player.gold -= penaltyGold;
        this.game.print(`${Colors.RED}Exit penalty: Lost ${penaltyGold} gold${Colors.END}`);
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
    
    this.game.print(`\n${Colors.RED}${Colors.BOLD}You have fallen in the dungeon!${Colors.END}`);

    if (this.game.player) {
      // Death penalty
      this.game.player.hp = Math.floor(this.game.player.maxHp / 2);
      this.game.player.mp = Math.floor(this.game.player.maxMp / 2);

      // Lose some gold
      const goldLoss = Math.min(Math.floor(this.game.player.gold / 5), 200);
      this.game.player.gold -= goldLoss;
      this.game.print(`Lost ${goldLoss} gold.`);
    }

    // Return to starting village
    this.game.currentArea = "starting_village";
    this.game.print("You respawn at the starting village.");

    // Clear dungeon state
    this.currentDungeon = null;
    this.dungeonProgress = 0;
    this.dungeonRooms = [];
    this.dungeonState = {};
  }
}

export default DungeonSystem;
