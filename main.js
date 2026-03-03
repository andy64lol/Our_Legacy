/**
 * Our Legacy - Main Entry Point (Browser Version)
 * Ported from main.py
 */

import { Colors } from './utilities_js/UI.js';
import { Character } from './utilities_js/character.js';
import { SaveLoadSystem } from './utilities_js/save_load.js';
import { BattleSystem } from './utilities_js/battle.js';
import { SpellCastingSystem } from './utilities_js/spellcasting.js';
import MarketAPI from './utilities_js/market.js';
import { visitAlchemy } from './utilities_js/crafting.js';
import { visitSpecificShop } from './utilities_js/shop.js';
import { DungeonSystem } from './utilities_js/dungeons.js';
import { buildHome, farm } from './utilities_js/building.js';
import { ModManager } from './utilities_js/mod_manager.js';

// Simple ask function for browser (using window.prompt)
export async function ask(promptText, validChoices = null, allowEmpty = true) {
  let response;
  let attempts = 0;
  const maxAttempts = 10;

  while (attempts < maxAttempts) {
    response = prompt(promptText);
    
    if (response === null) {
      response = '';
    }
    
    const resp = response.trim();
    
    // Empty handling
    if (!resp && allowEmpty) {
      console.clear();
      return resp;
    }
    if (!resp && !allowEmpty) {
      attempts++;
      continue;
    }

    // If no validation requested, accept
    if (!validChoices) {
      console.clear();
      return resp;
    }

    // Prepare choices for comparison (case insensitive)
    const cmpChoices = validChoices.map(c => c.toLowerCase());
    const cmpResp = resp.toLowerCase();

    // Exact match
    if (cmpChoices.includes(cmpResp)) {
      console.clear();
      return resp;
    }

    console.log(`Invalid input. Allowed choices: ${validChoices.join(', ')}`);
    attempts++;
  }
  
  return '';
}

// Format item name with rarity color
export function formatItemName(itemName, rarity = "common") {
  const rarityColors = {
    "common": Colors.COMMON,
    "uncommon": Colors.UNCOMMON,
    "rare": Colors.RARE,
    "epic": Colors.EPIC,
    "legendary": Colors.LEGENDARY
  };
  const color = rarityColors[rarity] || Colors.WHITE;
  return Colors.wrap(itemName, color);
}

// Loading indicator
export function loadingIndicator(message = "Loading") {
  console.log(`${Colors.YELLOW}${message}${'.'.repeat(3)}${Colors.END}`);
}

// Game class - Main game logic
export class Game {
  constructor() {
    this.player = null;
    this.currentArea = "starting_village";
    this.visitedAreas = new Set();
    this.enemiesData = {};
    this.areasData = {};
    this.itemsData = {};
    this.missionsData = {};
    this.bossesData = {};
    this.classesData = {};
    this.spellsData = {};
    this.effectsData = {};
    this.companionsData = {};
    this.dialoguesData = {};
    this.dungeonsData = {};
    this.cutscenesData = {};
    this.missionProgress = {};
    this.completedMissions = [];
    this.marketApi = null;
    this.craftingData = {};
    this.weeklyChallengesData = {};
    this.housingData = {};
    this.shopsData = {};
    this.farmingData = {};
    this.petsData = {};
    this.challengeProgress = {};
    this.completedChallenges = [];
    this.currentDungeon = null;
    this.dungeonProgress = 0;
    this.dungeonRooms = [];
    this.dungeonState = {};
    
    // Simple language manager
    this.lang = {
      get: (key, defaultValue, params = {}) => {
        let text = defaultValue || key;
        if (params && typeof params === 'object') {
          for (const [k, v] of Object.entries(params)) {
            text = text.replace(new RegExp(`{${k}}`, 'g'), v);
          }
        }
        return text;
      }
    };
    
    this.saveLoadSystem = new SaveLoadSystem(this);
    this.CharacterClass = Character;
    this.print = console.log;

    this.battleSystem = new BattleSystem(this);
    this.spellCastingSystem = new SpellCastingSystem(this);
    this.marketApi = new MarketAPI(this.lang, Colors);
    this.dungeonSystem = new DungeonSystem(this);
    this.modManager = new ModManager(this.lang);

    this.missionProgress = {};
    this.challengeProgress = {};
  }

  // Utility helpers needed by some modules
  createHpMpBar(current, max, width, color) {
    const filled = Math.round((current / max) * width);
    const empty = width - filled;
    return `${color}${'I'.repeat(Math.max(0, filled))}${Colors.GRAY}${'-'.repeat(Math.max(0, empty))}${Colors.END}`;
  }

  createBossHpBar(current, max) {
    return this.createHpMpBar(current, max, 40, Colors.RED);
  }

  async battle(enemy) {
    await this.battleSystem.battle(enemy);
  }

  async randomEncounter() {
    if (!this.player) return;
    const areaData = this.areasData[this.currentArea] || {};
    const possibleEnemies = areaData.possible_enemies || [];
    if (possibleEnemies.length === 0) return;
    const enemyName = possibleEnemies[Math.floor(Math.random() * possibleEnemies.length)];
    const enemyData = this.enemiesData[enemyName];
    if (enemyData) {
      const { Enemy } = await import('./utilities_js/entities.js');
      await this.battleSystem.battle(new Enemy(enemyData));
    }
  }

  async loadGameData() {
    try {
      this.enemiesData = await this.loadJSON('data/enemies.json');
      this.areasData = await this.loadJSON('data/areas.json');
      this.itemsData = await this.loadJSON('data/items.json');
      this.missionsData = await this.loadJSON('data/missions.json');
      this.bossesData = await this.loadJSON('data/bosses.json');
      this.classesData = await this.loadJSON('data/classes.json');
      this.spellsData = await this.loadJSON('data/spells.json');
      this.effectsData = await this.loadJSON('data/effects.json');
      try { this.companionsData = await this.loadJSON('data/companions.json'); } catch (e) { this.companionsData = {}; }
      try { this.craftingData = await this.loadJSON('data/crafting.json'); } catch (e) { this.craftingData = {}; }
      try { this.dialoguesData = await this.loadJSON('data/dialogues.json'); } catch (e) { this.dialoguesData = {}; }
      try { this.cutscenesData = await this.loadJSON('data/cutscenes.json'); } catch (e) { this.cutscenesData = {}; }
      try { this.weatherData = await this.loadJSON('data/weather.json'); } catch (e) { this.weatherData = {}; }
      try { this.timesData = await this.loadJSON('data/times.json'); } catch (e) { this.timesData = {}; }
      try { this.petsData = await this.loadJSON('data/pets.json'); } catch (e) { this.petsData = {}; }
    } catch (e) {
      console.error(`Error loading game data: ${e}`);
    }

    try {
      this.dungeonsData = await this.loadJSON('data/dungeons.json');
    } catch (e) {
      this.dungeonsData = {};
    }

    try {
      this.weeklyChallengesData = await this.loadJSON('data/weekly_challenges.json');
      if (this.weeklyChallengesData.challenges) {
        for (const challenge of this.weeklyChallengesData.challenges) {
          this.challengeProgress[challenge.id] = 0;
        }
      }
    } catch (e) {
      this.weeklyChallengesData = {};
    }

    try {
      this.housingData = await this.loadJSON('data/housing.json');
    } catch (e) {
      this.housingData = {};
    }

    try {
      this.shopsData = await this.loadJSON('data/shops.json');
    } catch (e) {
      this.shopsData = {};
    }

    try {
      this.farmingData = await this.loadJSON('data/farming.json');
    } catch (e) {
      this.farmingData = {};
    }
  }

  async loadJSON(path) {
    const response = await fetch(path);
    if (!response.ok) throw new Error(`Failed to load ${path}`);
    return await response.json();
  }

  createCharacter() {
    this.player = new Character("Hero", "Warrior", this.classesData, null, this.lang);
    this.player.timesData = this.timesData;
    this.player.weatherData = this.weatherData;
    this.player.giveStartingItems("Warrior", this.classesData, this.itemsData);
    
    // Initialize missions
    if (this.missionsData) {
      for (const [id, mission] of Object.entries(this.missionsData)) {
        if (mission.auto_start) {
          this.missionProgress[id] = {
            current_count: 0,
            target_count: mission.target_count || 1,
            completed: false,
            type: mission.type || "kill",
            target: mission.target_enemy || mission.target
          };
        }
      }
    }
    
    // Initialize visited areas
    this.visitedAreas = new Set();
    this.player.currentArea = "starting_village";
    this.currentArea = "starting_village";
    this.visitedAreas.add(this.player.currentArea);
    
    // Set base stats for calculation
    this.player.baseMaxHp = this.player.maxHp;
    this.player.baseMaxMp = this.player.maxMp;
    this.player.baseAttack = this.player.attack;
    this.player.baseDefense = this.player.defense;
    this.player.baseSpeed = this.player.speed;
  }

  updateWeather() {
    if (!this.player) return;
    const areaData = this.areasData[this.player.currentArea] || {};
    const weatherProbs = areaData.weather_probabilities || areaData.weather_chances || { sunny: 1.0 };
    const weathers = Object.keys(weatherProbs);
    const weights = Object.values(weatherProbs);
    
    if (weathers.length > 0) {
      const totalWeight = weights.reduce((a, b) => a + b, 0);
      let random = Math.random() * totalWeight;
      for (let i = 0; i < weathers.length; i++) {
        random -= weights[i];
        if (random <= 0) {
          this.player.currentWeather = weathers[i];
          return;
        }
      }
      this.player.currentWeather = weathers[weathers.length - 1];
    }
  }

  displayWelcome() {
    console.log(Colors.CYAN + Colors.BOLD + "=".repeat(60) + Colors.END);
    console.log("             OUR LEGACY");
    console.log("       A Text-Based Fantasy RPG");
    console.log("=".repeat(60));
    console.log(Colors.END);
    console.log("Welcome, brave adventurer!");
    console.log("Your destiny awaits in this vast fantasy world.\n");
    console.log(Colors.BOLD + Colors.CYAN + "=== MAIN MENU ===" + Colors.END);
    console.log(Colors.CYAN + "1." + Colors.END + " New Game");
    console.log(Colors.CYAN + "2." + Colors.END + " Load Game");
    console.log(Colors.CYAN + "3." + Colors.END + " Settings");
    console.log(Colors.CYAN + "4." + Colors.END + " Quit\n");
  }

  async mainMenu() {
    if (this.player) {
      this.player.advanceTime(10.0);
    }

    const areaData = this.areasData[this.currentArea] || {};
    const areaName = areaData.name || this.currentArea;

    console.log(`\n${Colors.BOLD}=== MAIN MENU ===${Colors.END}`);
    console.log(`Location: ${areaName}`);
    console.log(`${Colors.CYAN}1.${Colors.END} Explore`);
    console.log(`${Colors.CYAN}2.${Colors.END} Character`);
    console.log(`${Colors.CYAN}3.${Colors.END} Travel`);
    console.log(`${Colors.CYAN}4.${Colors.END} Inventory`);
    console.log(`${Colors.CYAN}5.${Colors.END} Missions`);
    console.log(`${Colors.CYAN}6.${Colors.END} Fight Boss`);
    console.log(`${Colors.CYAN}7.${Colors.END} Tavern`);
    console.log(`${Colors.CYAN}8.${Colors.END} Shop`);
    console.log(`${Colors.CYAN}9.${Colors.END} Alchemy`);
    console.log(`${Colors.CYAN}10.${Colors.END} Elite Market`);
    console.log(`${Colors.CYAN}11.${Colors.END} Rest`);
    console.log(`${Colors.CYAN}12.${Colors.END} Companions`);
    console.log(`${Colors.CYAN}13.${Colors.END} Dungeons`);
    console.log(`${Colors.CYAN}14.${Colors.END} Challenges`);
    console.log(`${Colors.CYAN}15.${Colors.END} Build Home`);
    console.log(`${Colors.CYAN}16.${Colors.END} Farm`);
    console.log(`${Colors.CYAN}S.${Colors.END} Save Game`);
    console.log(`${Colors.CYAN}L.${Colors.END} Load Game`);
    console.log(`${Colors.CYAN}0.${Colors.END} Quit`);

    const choice = await ask(`${Colors.CYAN}Choose an option: ${Colors.END}`);
    await this.handleMenuChoice(choice);
  }

  async handleMenuChoice(choice) {
    const c = choice.toLowerCase();
    switch (c) {
      case "1":
        await this.explore();
        break;
      case "2":
        if (this.player) this.player.displayStats(console.log);
        await ask("Press Enter to continue...");
        break;
      case "3":
        await this.travel();
        break;
      case "4":
        await this.viewInventory();
        await ask("Press Enter to continue...");
        break;
      case "5":
        await this.viewMissions();
        await ask("Press Enter to continue...");
        break;
      case "6":
        await this.fightBoss();
        break;
      case "7":
        console.log("Tavern coming soon...");
        await ask("Press Enter to continue...");
        break;
      case "8":
        await this.visitShop();
        break;
      case "9":
        await visitAlchemy(this, ask);
        break;
      case "10":
        await this.visitMarket();
        break;
      case "11":
        await this.rest();
        break;
      case "12":
        await this.viewCompanions();
        await ask("Press Enter to continue...");
        break;
      case "13":
        await this.dungeonSystem.visitDungeons(ask);
        break;
      case "14":
        await this.viewChallenges();
        await ask("Press Enter to continue...");
        break;
      case "15":
        await buildHome(this, ask);
        break;
      case "16":
        await farm(this, ask);
        break;
      case "s":
        await this.saveGame();
        await ask("Press Enter to continue...");
        break;
      case "l":
        await this.loadGame();
        await ask("Press Enter to continue...");
        break;
      case "0":
        this.quitGame();
        break;
      default:
        console.log("Invalid choice.");
        await ask("Press Enter to continue...");
    }
  }

  async viewCompanions() {
    console.log(`\n${Colors.BOLD}=== COMPANIONS ===${Colors.END}`);
    const companions = this.player?.companions || [];
    if (companions.length === 0) {
      console.log("You have no companions.");
      return;
    }
    companions.forEach((c, i) => {
      console.log(`${i+1}. ${c.name || c} (Level ${c.level || 1})`);
    });
  }

  async viewDungeons() {
    console.log(`\n${Colors.BOLD}=== DUNGEONS ===${Colors.END}`);
    const allDungeons = this.dungeonsData?.dungeons || [];
    const dungeons = allDungeons.filter(d => {
      const allowedAreas = d.allowed_areas || [];
      return allowedAreas.length === 0 || allowedAreas.includes(this.currentArea);
    });
    if (dungeons.length === 0) {
      console.log("No dungeons discovered in this area.");
      return;
    }
    dungeons.forEach((d, i) => {
      const difficulty = Array.isArray(d.difficulty) ? d.difficulty[0] : (d.difficulty || 1);
      console.log(`${i+1}. ${d.name} (Difficulty: ${difficulty})`);
    });
  }

  async viewChallenges() {
    console.log(`\n${Colors.BOLD}=== WEEKLY CHALLENGES ===${Colors.END}`);
    const challenges = this.weeklyChallengesData?.challenges || [];
    if (challenges.length === 0) {
      console.log("No challenges available.");
      return;
    }
    challenges.forEach(c => {
      const prog = this.challengeProgress?.[c.id] || 0;
      const status = prog >= (c.target || c.target_count) ? `${Colors.GREEN}Completed${Colors.END}` : `${prog}/${c.target || c.target_count}`;
      console.log(`${c.name}: ${status}`);
    });
  }

  async saveGame() {
    await this.saveLoadSystem.save_game();
  }

  async loadGame() {
    await this.saveLoadSystem.load_game();
  }

  async viewMissions() {
    console.log(`\n${Colors.BOLD}=== MISSIONS ===${Colors.END}`);
    const missions = Object.entries(this.missionProgress || {});
    if (missions.length === 0) {
      console.log("No active missions.");
      // Give a starter mission
      if (this.missionsData["starter_hunt"]) {
        const m = this.missionsData["starter_hunt"];
        this.missionProgress["starter_hunt"] = {
          current: 0,
          target: m.target_count || 3,
          completed: false,
          type: m.type || "kill",
          target_name: m.target_enemy || "Slime"
        };
        console.log(`New Mission Accepted: ${m.name}`);
      }
      return;
    }
    missions.forEach(([id, data]) => {
      const status = data.completed ? `${Colors.GREEN}Completed${Colors.END}` : `${data.current || data.current_count}/${data.target || data.target_count}`;
      console.log(`${id}: ${status}`);
    });
  }

  async fightBoss() {
    const areaData = this.areasData[this.currentArea] || {};
    const bosses = areaData.bosses || [];
    if (bosses.length === 0) {
      console.log("No bosses in this area.");
      await ask("Press Enter to continue...");
      return;
    }
    const bossName = bosses[0];
    const bossData = this.bossesData[bossName];
    if (!bossData) {
      console.log(`Boss data for ${bossName} not found.`);
      await ask("Press Enter to continue...");
      return;
    }
    const { Boss } = await import('./utilities_js/entities.js');
    await this.battleSystem.battle(new Boss(bossData));
  }

  async visitShop() {
    const areaData = this.areasData[this.currentArea] || {};
    const shops = areaData.shops || [];
    if (shops.length === 0) {
      console.log("No shops in this area.");
      await ask("Press Enter to continue...");
      return;
    }
    await visitSpecificShop(this, shops[0], ask);
  }

  async visitMarket() {
    const data = await this.marketApi.fetchMarketData();
    if (data) {
      console.log(`\n${Colors.BOLD}=== ELITE MARKET ===${Colors.END}`);
      const items = data.items || [];
      for (let i = 0; i < items.length; i++) {
        const item = items[i];
        console.log(`${i+1}. ${item.name} - ${item.marketPrice} gold`);
      }
      const choice = await ask("Buy something? (Number or Enter to exit): ");
      if (choice && !isNaN(parseInt(choice))) {
        const idx = parseInt(choice) - 1;
        if (idx >= 0 && idx < items.length) {
          const item = items[idx];
          if (this.player.gold >= item.marketPrice) {
            this.player.gold -= item.marketPrice;
            this.player.inventory.push(item.name);
            console.log(`Bought ${item.name}!`);
          } else {
            console.log("Not enough gold.");
          }
        }
      }
    }
    await ask("Press Enter to continue...");
  }

  async explore() {
    if (!this.player) {
      console.log("No character created. Start a new game first!");
      await ask("Press Enter to continue...");
      return;
    }

    this.player.advanceTime(5.0);

    const areaData = this.areasData[this.currentArea] || {};
    const areaName = areaData.name || "Unknown Area";

    console.log(`\nExploring ${areaName}...`);

    if (Math.random() < 0.7) {
      const possibleEnemies = areaData.possible_enemies || [];
      if (possibleEnemies.length > 0) {
        const enemyName = possibleEnemies[Math.floor(Math.random() * possibleEnemies.length)];
        const enemyData = this.enemiesData[enemyName];
        if (enemyData) {
          const { Enemy } = await import('./utilities_js/entities.js');
          await this.battleSystem.battle(new Enemy(enemyData));
        }
      } else {
        console.log("You explored but found no enemies.");
      }
    } else {
      console.log("You explored but found nothing.");

      if (Math.random() < 0.3) {
        const goldFound = Math.floor(Math.random() * 16) + 5;
        this.player.gold += goldFound;
        console.log(`You found ${goldFound} gold!`);
      }
    }
    await ask("Press Enter to continue...");
  }

  async updateChallengeProgress(type) {
    const challenges = this.weeklyChallengesData.challenges || [];
    for (const c of challenges) {
      if (c.type === type) {
        this.challengeProgress[c.id] = (this.challengeProgress[c.id] || 0) + 1;
      }
    }
  }

  async useItemInBattle() {
    console.log("\n=== USE ITEM ===");
    const items = this.player.inventory.filter(i => {
      const data = this.itemsData[i];
      return data && (data.type === 'potion' || data.type === 'consumable');
    });
    if (items.length === 0) {
      console.log("No usable items.");
      return;
    }
    items.forEach((item, i) => console.log(`${i+1}. ${item}`));
    const choice = await ask("Choose item: ");
    if (choice && !isNaN(parseInt(choice))) {
      const idx = parseInt(choice) - 1;
      if (idx >= 0 && idx < items.length) {
        const item = items[idx];
        const data = this.itemsData[item];
        if (data.hp_heal) this.player.heal(data.hp_heal);
        if (data.mp_heal) this.player.mp = Math.min(this.player.maxMp, this.player.mp + data.mp_heal);
        this.player.inventory.splice(this.player.inventory.indexOf(item), 1);
        console.log(`Used ${item}!`);
      }
    }
  }

  updateMissionProgress(type, target) {
    for (const [missionId, progress] of Object.entries(this.missionProgress)) {
      if (!progress.completed && progress.type === type && progress.target === target) {
        progress.current_count++;
        if (progress.current_count >= progress.target_count) {
          progress.completed = true;
          console.log(`${Colors.GREEN}Mission Objective Complete: ${missionId}${Colors.END}`);
        }
      }
    }
  }

  async viewInventory() {
    if (!this.player) {
      console.log("No character created.");
      return;
    }

    console.log(`\n${Colors.BOLD}=== INVENTORY ===${Colors.END}`);
    console.log(`Gold: ${Colors.GOLD}${this.player.gold}${Colors.END}`);

    if (this.player.inventory.length === 0) {
      console.log("Inventory is empty.");
      return;
    }

    for (const item of this.player.inventory) {
      const itemData = this.itemsData[item] || {};
      const rarity = itemData.rarity || 'common';
      console.log(`  - ${formatItemName(item, rarity)}`);
    }
  }

  async travel() {
    if (!this.player) {
      console.log("No character created.");
      return;
    }

    const areaData = this.areasData[this.currentArea] || {};
    const connections = areaData.connections || [];

    console.log(`\n${Colors.BOLD}=== TRAVEL ===${Colors.END}`);
    console.log(`Current: ${areaData.name || this.currentArea}`);

    if (connections.length === 0) {
      console.log("No connected areas.");
      return;
    }

    console.log("\nConnected areas:");
    for (let i = 0; i < connections.length; i++) {
      const aid = connections[i];
      const a = this.areasData[aid] || {};
      console.log(`${i + 1}. ${a.name || aid}`);
    }

    const choice = await ask(`Travel to (1-${connections.length}): `);
    const idx = parseInt(choice) - 1;
    if (idx >= 0 && idx < connections.length) {
      this.currentArea = connections[idx];
      this.player.currentArea = this.currentArea;
      console.log(`Traveled to ${this.areasData[this.currentArea]?.name || this.currentArea}!`);
      this.updateWeather();
    }
  }

  async rest() {
    if (!this.player) {
      console.log("No character created.");
      return;
    }

    const areaData = this.areasData[this.currentArea] || {};
    const canRest = areaData.can_rest || false;

    if (!canRest) {
      console.log("You cannot rest here. It's too dangerous!");
      return;
    }

    const cost = areaData.rest_cost || 10;
    console.log(`Rest cost: ${cost} gold`);
    
    if (this.player.gold < cost) {
      console.log("Not enough gold!");
      return;
    }

    this.player.gold -= cost;
    this.player.hp = this.player.maxHp;
    this.player.mp = this.player.maxMp;
    console.log("You rest and recover all HP and MP!");
  }

  quitGame() {
    console.log("\nThank you for playing Our Legacy!");
    console.log("Your legacy will be remembered...");
  }

  async run() {
    this.displayWelcome();
    const choice = await ask("Choose an option (1-4): ", ["1", "2", "3", "4"], false);

    if (choice === "1") {
      this.createCharacter();
      console.log(`\n${Colors.GREEN}Welcome, ${this.player.name} the ${this.player.characterClass}!${Colors.END}`);
      console.log("Your adventure begins now!\n");
      
      // Main game loop
      while (this.player && this.player.isAlive()) {
        await this.mainMenu();
      }
      
      if (this.player && !this.player.isAlive()) {
        console.log("\nYou have died! Game Over.");
      }
    } else if (choice === "4") {
      this.quitGame();
    }
  }
}

// Main entry point
export async function main() {
  console.clear();
  const game = new Game();
  await game.loadGameData();
  await game.run();
}

export default { Game, main };
