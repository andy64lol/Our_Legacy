/**
 * Our Legacy - Main Entry Point (Browser Version)
 * Ported from main.py
 */

import { Colors } from './utilities_js/UI.js';
import { Character } from './utilities_js/character.js';

// Simple ask function for browser (using window.prompt)
export async function ask(prompt, validChoices = null, allowEmpty = true) {
  let response;
  let attempts = 0;
  const maxAttempts = 10;

  while (attempts < maxAttempts) {
    response = prompt(prompt);
    
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
      get: (key, defaultValue) => defaultValue || key
    };
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
    this.player = new Character("Hero", "Warrior", this.classesData);
    this.player.inventory = ["Iron Sword", "Health Potion"];
    this.player.gold = 100;
    this.player.currentArea = "starting_village";
    this.currentArea = "starting_village";
    this.visitedAreas.add(this.player.currentArea);
  }

  updateWeather() {
    if (!this.player) return;
    const areaData = this.areasData[this.player.currentArea] || {};
    const weatherProbs = areaData.weather_probabilities || { sunny: 1.0 };
    const weathers = Object.keys(weatherProbs);
    if (weathers.length > 0) {
      this.player.currentWeather = weathers[0];
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
    console.log(`${Colors.CYAN}0.${Colors.END} Quit`);

    const choice = await ask(`${Colors.CYAN}Choose an option: ${Colors.END}`);
    await this.handleMenuChoice(choice);
  }

  async handleMenuChoice(choice) {
    switch (choice) {
      case "1":
        await this.explore();
        break;
      case "2":
        if (this.player) this.player.displayStats(console.log);
        break;
      case "3":
        await this.travel();
        break;
      case "4":
        await this.viewInventory();
        break;
      case "5":
        console.log("Missions coming soon...");
        break;
      case "6":
        console.log("Boss fights coming soon...");
        break;
      case "7":
        console.log("Tavern coming soon...");
        break;
      case "8":
        console.log("Shop coming soon...");
        break;
      case "9":
        console.log("Alchemy coming soon...");
        break;
      case "10":
        console.log("Market coming soon...");
        break;
      case "11":
        await this.rest();
        break;
      case "12":
        console.log("Companions coming soon...");
        break;
      case "13":
        console.log("Dungeons coming soon...");
        break;
      case "14":
        console.log("Challenges coming soon...");
        break;
      case "0":
        this.quitGame();
        break;
      default:
        console.log("Invalid choice.");
    }
  }

  async explore() {
    if (!this.player) {
      console.log("No character created. Start a new game first!");
      return;
    }

    this.player.advanceTime(5.0);

    const areaData = this.areasData[this.currentArea] || {};
    const areaName = areaData.name || "Unknown Area";

    console.log(`\nExploring ${areaName}...`);

    if (Math.random() < 0.7) {
      await this.randomEncounter();
    } else {
      console.log("You explored but found nothing.");

      if (Math.random() < 0.3) {
        const goldFound = Math.floor(Math.random() * 16) + 5;
        this.player.gold += goldFound;
        console.log(`You found ${goldFound} gold!`);
      }
    }
  }

  async randomEncounter() {
    if (!this.player) return;

    const areaData = this.areasData[this.currentArea] || {};
    const possibleEnemies = areaData.possible_enemies || [];

    if (possibleEnemies.length === 0) {
      console.log("No enemies in this area.");
      return;
    }

    const enemyName = possibleEnemies[Math.floor(Math.random() * possibleEnemies.length)];
    const enemyData = this.enemiesData[enemyName];

    if (enemyData) {
      console.log(`\n${Colors.RED}A wild ${enemyData.name} appears!${Colors.END}`);
      console.log(`HP: ${enemyData.hp} | ATK: ${enemyData.attack} | DEF: ${enemyData.defense}`);
      
      // Simple battle
      await this.simpleBattle(enemyData);
    }
  }

  async simpleBattle(enemyData) {
    let enemyHp = enemyData.hp;
    
    while (enemyHp > 0 && this.player.hp > 0) {
      // Player attacks
      const playerDamage = Math.max(1, this.player.getEffectiveAttack() - enemyData.defense);
      enemyHp -= playerDamage;
      console.log(`You attack for ${playerDamage} damage! (Enemy HP: ${Math.max(0, enemyHp)})`);
      
      if (enemyHp <= 0) break;
      
      // Enemy attacks
      const enemyDamage = Math.max(1, enemyData.attack - this.player.getEffectiveDefense());
      const actualDamage = this.player.takeDamage(enemyDamage);
      console.log(`${enemyData.name} attacks for ${actualDamage} damage! (Your HP: ${this.player.hp})`);
    }

    if (this.player.isAlive()) {
      console.log(`\n${Colors.GREEN}Victory! You defeated ${enemyData.name}!${Colors.END}`);
      const expGain = enemyData.experience_reward || 10;
      const goldGain = enemyData.gold_reward || 5;
      this.player.gainExperience(expGain);
      this.player.gold += goldGain;
      console.log(`Gained ${expGain} EXP and ${goldGain} gold!`);
    } else {
      console.log(`\n${Colors.RED}You have been defeated!${Colors.END}`);
      this.player.hp = Math.floor(this.player.maxHp / 2);
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
