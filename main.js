/**
 * Our Legacy - Text-Based Browser Fantasy RPG Game
 * Main entry point for browser version
 * Ported from main.py
 */

import { Colors, SettingsManager, ModManager } from "./utilities_js/settings.js";
import { Character } from "./utilities_js/character.js";
import { BattleSystem } from "./utilities_js/battle.js";
import { SpellCastingSystem } from "./utilities_js/spellcasting.js";
import { SaveLoadSystem } from "./utilities_js/save_load.js";
import { MarketAPI } from "./utilities_js/market.js";
import { LanguageManager } from "./utilities_js/language.js";
import { DungeonSystem } from "./utilities_js/dungeons.js";
import { Enemy, Boss } from "./utilities_js/entities.js";
import {
  createProgressBar,
  createSeparator,
  createSectionHeader,
  displayWelcomeScreen,
  displayMainMenu,
} from "./utilities_js/UI.js";
import { visit_specific_shop, visit_general_shop as visit_general_shop } from "./utilities_js/shop.js";
import { visit_alchemy } from "./utilities_js/crafting.js";
import {
  build_home,
  build_structures,
  farm,
  training,
} from "./utilities_js/building.js";

// Global color toggle - using let to allow reassignment like Python's global
let COLORS_ENABLED = true;

// Export COLORS_ENABLED for utilities
export { COLORS_ENABLED };

/**
 * Display a loading indicator
 * @param {Object} game - Game instance
 * @param {string} message - Loading message
 */
export async function loadingIndicator(game, message = "Loading") {
  game.print(`\n${Colors.wrap(message, Colors.YELLOW)}`);
  // Simulate loading dots
  for (let i = 0; i < 3; i++) {
    game.delay(500);
    game.print(".");
  }
  game.print("");
}

/**
 * Get the color for an item rarity
 * @param {string} rarity - Item rarity
 * @returns {string} Color code
 */
export function getRarityColor(rarity) {
  const rarityColors = {
    common: Colors.COMMON,
    uncommon: Colors.UNCOMMON,
    rare: Colors.RARE,
    epic: Colors.EPIC,
    legendary: Colors.LEGENDARY,
  };
  return rarityColors[rarity?.toLowerCase()] || Colors.WHITE;
}

/**
 * Format item name with rarity color
 * @param {string} itemName - Item name
 * @param {string} rarity - Item rarity
 * @returns {string} Formatted item name
 */
export function formatItemName(itemName, rarity = "common") {
  const color = getRarityColor(rarity);
  return Colors.wrap(itemName, color);
}

/**
 * Ask the player for input with optional validation
 * @param {Object} game - Game instance
 * @param {string} prompt - Prompt message
 * @param {Array} validChoices - List of valid choices
 * @param {boolean} allowEmpty - Allow empty input
 * @param {boolean} caseSensitive - Case sensitive comparison
 * @param {boolean} suggest - Show suggestions for invalid input
 * @returns {Promise<string>} User response
 */
export async function ask(
  game,
  prompt,
  validChoices = null,
  allowEmpty = true,
  caseSensitive = false,
  suggest = true,
) {
  const lang = game.lang;

  while (true) {
    const response = await game.ask(prompt);
    const resp = response.trim();

    // Normalize for comparison if case-insensitive
    let cmpResp = resp;
    if (!caseSensitive) {
      cmpResp = resp.toLowerCase();
    }

    // Ensure cmp_choices is always a list for safe membership checks
    let cmpChoices = [];
    if (validChoices) {
      cmpChoices = validChoices.map((c) =>
        caseSensitive ? c : c.toLowerCase(),
      );
    }

    // Empty handling
    if (!resp && allowEmpty) {
      return resp;
    }
    if (!resp && !allowEmpty) {
      continue;
    }

    // If no validation requested, accept
    if (!validChoices) {
      if (game.clear) game.clear();
      return resp;
    }

    // Exact match
    if (cmpChoices.includes(cmpResp)) {
      if (game.clear) game.clear();
      return resp;
    }

    // If suggestions enabled, show closest matches
    if (suggest && cmpChoices.length > 0) {
      const close = getCloseMatches(cmpResp, cmpChoices, 3, 0.4);
      if (close.length > 0) {
        game.print(
          lang
            .get("did_you_mean_msg", "Did you mean one of these? {close}")
            .replace("{close}", close.join(", ")),
        );
      } else {
        game.print(
          lang
            .get(
              "invalid_input_choices_msg",
              "Invalid input. Allowed choices: {choices}",
            )
            .replace("{choices}", cmpChoices.join(", ")),
        );
      }
    } else {
      game.print(
        lang
          .get(
            "invalid_input_choices_msg",
            "Invalid input. Allowed choices: {choices}",
          )
          .replace("{choices}", cmpChoices.join(", ")),
      );
    }
  }
}

/**
 * Simple implementation of difflib.get_close_matches
 * @param {string} word - Word to match
 * @param {Array} possibilities - Possible matches
 * @param {number} n - Number of matches to return
 * @param {number} cutoff - Cutoff score
 * @returns {Array} Close matches
 */
function getCloseMatches(word, possibilities, n = 3, cutoff = 0.4) {
  if (word.length < 4) {
    return possibilities.filter((p) => p.startsWith(word)).slice(0, n);
  }

  const matches = [];
  for (const pos of possibilities) {
    const score = similarity(word, pos);
    if (score >= cutoff) {
      matches.push({ word: pos, score: score });
    }
  }

  matches.sort((a, b) => b.score - a.score);
  return matches.slice(0, n).map((m) => m.word);
}

/**
 * Calculate similarity between two strings
 * @param {string} s1 - First string
 * @param {string} s2 - Second string
 * @returns {number} Similarity score 0-1
 */
function similarity(s1, s2) {
  const longer = s1.length > s2.length ? s1 : s2;
  const shorter = s1.length > s2.length ? s2 : s1;

  if (longer.length === 0) return 1.0;

  const costs = [];
  for (let i = 0; i <= shorter.length; i++) {
    let lastValue = i;
    for (let j = 0; j <= longer.length; j++) {
      if (i === 0) {
        costs[j] = j;
      } else if (j > 0) {
        let newValue = costs[j - 1];
        if (shorter.charAt(i - 1) !== longer.charAt(j - 1)) {
          newValue = Math.min(Math.min(newValue, lastValue), costs[j]) + 1;
        }
        costs[j - 1] = lastValue;
        lastValue = newValue;
      }
    }
    if (i > 0) costs[longer.length] = lastValue;
  }

  return (longer.length - costs[longer.length]) / longer.length;
}

// Market API URL and cooldown (set by Game class when game starts)
let gameApi = null;

// Export gameApi getter/setter
export function setGameApi(api) {
  gameApi = api;
}

export function getGameApi() {
  return gameApi;
}

/**
 * Main Game Class
 * Ported from main.py Game class
 */
export class Game {
  constructor(gameInstance = null) {
    // Reference to the actual game instance (browser game handler)
    this.game = gameInstance;

    this.player = null;
    this.currentArea = "starting_village";
    this.visitedAreas = new Set(); // Track visited areas for cutscenes
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
    this.missionProgress = {}; // mission_id -> {current_count, target_count, completed, type}
    this.completedMissions = [];
    this.marketApi = null;
    this.craftingData = {};
    this.weeklyChallengesData = {};
    this.housingData = {};
    this.shopsData = {};
    this.farmingData = {};
    this.petsData = {};

    // Challenge tracking
    this.challengeProgress = {}; // challenge_id -> progress count
    this.completedChallenges = [];

    // Dungeon state tracking
    this.currentDungeon = null;
    this.dungeonProgress = 0;
    this.dungeonRooms = [];
    this.dungeonState = {};

    this.lang = new LanguageManager(
      (key, defaultValue) => this.settingsManager ? this.settingsManager.get(key, defaultValue) : defaultValue,
      (key, value) => this.settingsManager ? this.settingsManager.set(key, value) : null
    );

    // Set up settings manager synchronously (already imported at top level)
    this.settingsManager = settingsManager;
    // Initialize ModManager synchronously
    this.modManager = new ModManager(this.settingsManager.settings, this.lang, this);

    // Initialize Market API
    this.marketApi = new MarketAPI({ lang: this.lang, colors: Colors });

    // Initialize Dungeon System
    this.dungeonSystem = null;
  }

  /**
   * Print to game output
   * @param {string} message - Message to print
   * @param {string} end - End character (for compatibility)
   */
  print(message) {
    if (this.game && typeof this.game.print === "function") {
      this.game.print(message);
    } else {
      console.log(message);
    }
  }

  /**
   * Ask for user input
   * @param {string} prompt - Prompt message
   * @returns {Promise<string>} User response
   */
  async ask(prompt) {
    if (this.game && typeof this.game.ask === "function") {
      return await this.game.ask(prompt);
    }
    return prompt;
  }

  /**
   * Create HP/MP bar
   * @param {number} current - Current value
   * @param {number} maximum - Maximum value
   * @param {number} width - Bar width
   * @param {string} color - Color
   * @returns {string} Formatted bar
   */
  createHpMpBar(current, maximum, width = 20, color = Colors.RED) {
    if (maximum <= 0) {
      return "[" + " ".repeat(width) + "]";
    }
    const filledWidth = Math.floor((current / maximum) * width);
    const filled = "█".repeat(filledWidth);
    const empty = "░".repeat(width - filledWidth);
    return `[${Colors.wrap(filled, color)}${empty}]`;
  }

  /**
   * Create boss HP bar
   * @param {number} current - Current HP
   * @param {number} maximum - Maximum HP
   * @returns {string} Boss HP bar
   */
  createBossHpBar(current, maximum) {
    const barWidth = 40;
    if (maximum <= 0) {
      return "[" + "=".repeat(barWidth) + "]";
    }
    const filledWidth = Math.floor((current / maximum) * barWidth);
    const filled = "=".repeat(filledWidth);
    const empty = "-".repeat(barWidth - filledWidth);
    return `[${Colors.wrap(filled, Colors.RED)}${empty}] ${current}/${maximum}`;
  }

  /**
   * Load game data
   */
  async loadGameData() {
    try {
      let response = await fetch("data/enemies.json");
      if (response.ok) this.enemiesData = await response.json();

      response = await fetch("data/areas.json");
      if (response.ok) this.areasData = await response.json();

      response = await fetch("data/items.json");
      if (response.ok) this.itemsData = await response.json();

      response = await fetch("data/missions.json");
      if (response.ok) this.missionsData = await response.json();

      response = await fetch("data/bosses.json");
      if (response.ok) this.bossesData = await response.json();

      response = await fetch("data/classes.json");
      if (response.ok) this.classesData = await response.json();

      response = await fetch("data/spells.json");
      if (response.ok) this.spellsData = await response.json();

      response = await fetch("data/effects.json");
      if (response.ok) this.effectsData = await response.json();

      // Optional companions data
      response = await fetch("data/companions.json");
      if (response.ok) this.companionsData = await response.json();

      // Optional crafting data
      response = await fetch("data/crafting.json");
      if (response.ok) this.craftingData = await response.json();

      // Load dialogues data
      response = await fetch("data/dialogues.json");
      if (response.ok) this.dialoguesData = await response.json();

      // Load cutscenes data
      response = await fetch("data/cutscenes.json");
      if (response.ok) this.cutscenesData = await response.json();

      // Load weather and times data
      response = await fetch("data/weather.json");
      if (response.ok) this.weatherData = await response.json();

      response = await fetch("data/times.json");
      if (response.ok) this.timesData = await response.json();

      // Apply mod data
      if (this.modManager) {
        const modEnemies = await this.modManager.loadModData("enemies.json");
        this.enemiesData = { ...this.enemiesData, ...modEnemies };

        const modAreas = await this.modManager.loadModData("areas.json");
        this.areasData = { ...this.areasData, ...modAreas };

        const modItems = await this.modManager.loadModData("items.json");
        this.itemsData = { ...this.itemsData, ...modItems };

        const modMissions = await this.modManager.loadModData("missions.json");
        this.missionsData = { ...this.missionsData, ...modMissions };

        const modBosses = await this.modManager.loadModData("bosses.json");
        this.bossesData = { ...this.bossesData, ...modBosses };

        const modSpells = await this.modManager.loadModData("spells.json");
        this.spellsData = { ...this.spellsData, ...modSpells };

        const modEffects = await this.modManager.loadModData("effects.json");
        this.effectsData = { ...this.effectsData, ...modEffects };
      }
    } catch (e) {
      this.print(`Error loading game data: ${e}`);
      this.print(this.lang.get("ensure_data_files"));
    }

    // Load dungeons data
    try {
      const response = await fetch("data/dungeons.json");
      if (response.ok) this.dungeonsData = await response.json();
    } catch {
      this.dungeonsData = {};
    }

    // Load weekly challenges data
    try {
      const response = await fetch("data/weekly_challenges.json");
      if (response.ok) {
        this.weeklyChallengesData = await response.json();
        // Initialize challenge progress
        for (const challenge of this.weeklyChallengesData.challenges || []) {
          this.challengeProgress[challenge.id] = 0;
        }
      }
    } catch {
      this.weeklyChallengesData = {};
    }

    // Load housing data
    try {
      const response = await fetch("data/housing.json");
      if (response.ok) this.housingData = await response.json();
    } catch {
      this.housingData = {};
    }

    // Load shops data
    try {
      const response = await fetch("data/shops.json");
      if (response.ok) this.shopsData = await response.json();
    } catch {
      this.shopsData = {};
    }

    // Load farming data
    try {
      const response = await fetch("data/farming.json");
      if (response.ok) this.farmingData = await response.json();
    } catch {
      this.farmingData = {};
    }

    // Load pets data
    try {
      const response = await fetch("data/pets.json");
      if (response.ok) this.petsData = await response.json();
    } catch {
      this.petsData = {};
    }

    // Load mod data
    await this.loadModData();
  }

  /**
   * Load mod data
   */
  async loadModData() {
    if (!this.modManager) return;

    // Discover available mods
    await this.modManager.discoverMods();

    // Get enabled mods
    const enabledMods = this.modManager.getEnabledMods();

    if (!enabledMods || enabledMods.length === 0) return;

    this.print(this.lang.get("loading_mods"));

    const modDataTypes = [
      ["areas.json", "areasData"],
      ["enemies.json", "enemiesData"],
      ["items.json", "itemsData"],
      ["missions.json", "missionsData"],
      ["bosses.json", "bossesData"],
      ["companions.json", "companionsData"],
      ["classes.json", "classesData"],
      ["spells.json", "spellsData"],
      ["effects.json", "effectsData"],
      ["crafting.json", "craftingData"],
      ["dungeons.json", "dungeonsData"],
      ["dialogues.json", "dialoguesData"],
      ["cutscenes.json", "cutscenesData"],
      ["weekly_challenges.json", "weeklyChallengesData"],
      ["housing.json", "housingData"],
      ["shops.json", "shopsData"],
      ["weather.json", "weatherData"],
      ["times.json", "timesData"],
    ];

    for (const [fileName, attrName] of modDataTypes) {
      const modData = await this.modManager.loadModData(fileName);
      if (modData && Object.keys(modData).length > 0) {
        const baseData = this[attrName];
        if (baseData) {
          // Special handling for dungeons
          if (fileName === "dungeons.json") {
            if (modData.dungeons) {
              if (!baseData.dungeons) baseData.dungeons = [];
              baseData.dungeons.push(...modData.dungeons);
            }
            if (modData.challenge_templates) {
              if (!baseData.challenge_templates)
                baseData.challenge_templates = {};
              Object.assign(
                baseData.challenge_templates,
                modData.challenge_templates,
              );
            }
            if (modData.chest_templates) {
              if (!baseData.chest_templates) baseData.chest_templates = {};
              Object.assign(baseData.chest_templates, modData.chest_templates);
            }
          } else if (fileName === "weekly_challenges.json") {
            if (modData.challenges) {
              if (!baseData.challenges) baseData.challenges = [];
              baseData.challenges.push(...modData.challenges);
              // Initialize progress tracking for new challenges
              for (const challenge of modData.challenges) {
                this.challengeProgress[challenge.id] = 0;
              }
            }
          } else {
            Object.assign(baseData, modData);
          }
        }
        this.print(
          `  Loaded ${Object.keys(modData).length} entries from mods for ${fileName}`,
        );
      }
    }

    this.print(this.lang.get("mod_loading_complete_1"));
  }

  /**
   * Weighted random choice helper
   */
  weightedRandomChoice(items, weights) {
    const totalWeight = weights.reduce((sum, w) => sum + w, 0);
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
   * Load configuration
   */
  loadConfig() {
    // Set global color toggle to True by default - using globalThis for browser compatibility
    globalThis.COLORS_ENABLED = true;
    COLORS_ENABLED = true;

    // Initialize systems
    this.marketApi = new MarketAPI({ colors: Colors, lang: this.lang });
    this.battleSystem = new BattleSystem(this);
    this.spellCastingSystem = new SpellCastingSystem(this);
    this.saveLoadSystem = new SaveLoadSystem(this);
    this.dungeonSystem = new DungeonSystem(this);
  }

  /**
   * Update current weather
   */
  updateWeather() {
    if (!this.player) return;

    const areaData = this.areasData[this.player.currentArea] || {};
    const weatherProbs = areaData.weather_probabilities || { sunny: 1.0 };

    const weathers = Object.keys(weatherProbs);
    const probs = Object.values(weatherProbs);

    const newWeather = this.weightedRandomChoice(weathers, probs);
    this.player.currentWeather = newWeather;
  }

  /**
   * Play a cutscene by ID
   * @param {string} cutsceneId - Cutscene ID
   */
  async playCutscene(cutsceneId) {
    if (!this.cutscenesData[cutsceneId]) {
      this.print(
        this.lang
          .get("cutscene_not_found_msg")
          .replace("{cutscene_id}", cutsceneId),
      );
      return;
    }

    const cutscene = this.cutscenesData[cutsceneId];
    await this.playCutsceneContent(cutscene.content);
  }

  /**
   * Play cutscene content recursively
   * @param {Object} content - Cutscene content
   */
  async playCutsceneContent(content) {
    // Display text
    if (content.text) {
      this.print(`\n${Colors.CYAN}${content.text}${Colors.END}`);
    }

    // Wait
    if (content.wait) {
      for (let i = 0; i < content.wait; i++) {
        this.print(".", "");
        await this.delay(1000);
      }
      this.print("");
    }

    // Handle choices
    if (content.choice) {
      const choices = content.choice;
      const choiceKeys = Object.keys(choices);
      if (choiceKeys.length > 0) {
        this.print(this.lang.get("choose_your_response"));
        for (let i = 0; i < choiceKeys.length; i++) {
          this.print(`${i + 1}. ${choiceKeys[i]}`);
        }

        const choice = (
          await this.ask("Your choice (or press Enter to skip): ")
        ).trim();
        if (choice && !isNaN(choice)) {
          const idx = parseInt(choice) - 1;
          if (idx >= 0 && idx < choiceKeys.length) {
            const selectedChoice = choiceKeys[idx];
            const nextContent = choices[selectedChoice];
            if (typeof nextContent === "object") {
              await this.playCutsceneContent(nextContent);
            }
          }
        }
      }
    }
  }

  /**
   * Delay helper
   * @param {number} ms - Milliseconds to delay
   * @returns {Promise} Promise that resolves after delay
   */
  delay(ms) {
    return new Promise((resolve) => setTimeout(resolve, ms));
  }

  /**
   * Display welcome screen
   * @returns {Promise<string>} User choice
   */
  async displayWelcome() {
    return await displayWelcomeScreen(this.lang, this, this.ask.bind(this));
  }

  /**
   * Settings menu
   */
  async settingsWelcome() {
    while (true) {
      if (this.clear) this.clear();
      this.print(this.lang.get("settings"));

      const modsEnabled = this.modManager?.settings?.mods_enabled ?? true;

      this.print(
        `\n1. Mod System: ${modsEnabled ? Colors.wrap("Enabled", Colors.GREEN) : Colors.wrap("Disabled", Colors.RED)}`,
      );
      this.print(this.lang.get("mod_menu_goback"));

      const choice = (await this.ask("\nChoose an option: ")).trim();

      if (choice === "1") {
        this.modManager.toggleModsSystem();
        if (this.modManager.settings.mods_enabled) {
          this.print(this.lang.get("mod_system_enabled_1"));
        } else {
          this.print(this.lang.get("mod_system_disabled"));
        }
        this.print(
          `${Colors.YELLOW}Note: Changes take effect on game restart.${Colors.END}`,
        );
        await this.ask("\nPress Enter to continue...");
      } else if (choice === "2" || !choice) {
        break;
      } else {
        this.print(this.lang.get("invalid_choice"));
      }
    }
  }

  /**
   * Mods menu
   */
  async modsWelcome() {
    while (true) {
      if (this.clear) this.clear();
      this.print(this.lang.get("mods"));

      await this.modManager.discoverMods();
      const modsList = this.modManager.getModList();

      if (!modsList || modsList.length === 0) {
        this.print(
          `\n${Colors.YELLOW}${this.lang.get("no_mods_found")}${Colors.END}`,
        );
        this.print(this.lang.get("place_mods_instruction"));
        await this.ask("\nPress Enter to go back...");
        break;
      }

      const modsSystemEnabled = this.modManager.settings.mods_enabled;
      const statusColor = modsSystemEnabled ? Colors.GREEN : Colors.RED;
      const statusText = modsSystemEnabled ? "Enabled" : "Disabled";
      this.print(
        `\nMod System Status: ${statusColor}${statusText}${Colors.END}`,
      );

      this.print(
        `\n${Colors.CYAN}Installed Mods (${modsList.length}):${Colors.END}`,
      );

      for (let i = 0; i < modsList.length; i++) {
        const mod = modsList[i];
        const name = mod.name || mod.folder_name || "Unknown";
        const description = mod.description || "";
        const author = mod.author || "Unknown";
        const version = mod.version || "1.0";
        const enabled = mod.enabled;

        const status = enabled
          ? `${Colors.GREEN}[ENABLED]${Colors.END}`
          : `${Colors.RED}[DISABLED]${Colors.END}`;
        this.print(`\n${i + 1}. ${Colors.BOLD}${name}${Colors.END} ${status}`);
        this.print(`   Version: ${version}`);
        this.print(`   Author: ${author}`);
        if (description) {
          const desc =
            description.length > 100
              ? description.substring(0, 100) + "..."
              : description;
          this.print(`   ${desc}`);
        }
      }

      this.print(this.lang.get("options"));
      this.print(`1-${modsList.length}. Toggle Mod`);
      this.print(`R. ${this.lang.get("ui_refresh_mod_list")}`);
      this.print(`B. ${this.lang.get("ui_back_to_main_menu")}`);

      const choice = (await this.ask("\nChoose an option: "))
        .trim()
        .toUpperCase();

      if (choice === "B" || !choice) {
        break;
      } else if (choice === "R") {
        await this.modManager.discoverMods();
        this.print(this.lang.get("mod_list_refreshed"));
        await this.delay(500);
      } else if (!isNaN(choice)) {
        const idx = parseInt(choice) - 1;
        if (idx >= 0 && idx < modsList.length) {
          const mod = modsList[idx];
          const folderName = mod.folder_name;
          if (folderName) {
            this.modManager.toggleMod(folderName);
            this.print(
              `${Colors.YELLOW}Note: Changes take effect on game restart.${Colors.END}`,
            );
            await this.ask("\nPress Enter to continue...");
          }
        } else {
          this.print(this.lang.get("invalid_mod_number"));
          await this.delay(1000);
        }
      } else {
        this.print(this.lang.get("invalid_choice"));
        await this.delay(1000);
      }
    }
  }

  /**
   * Create a new character
   */
  createCharacter() {
    this.player = new Character(
      "Hero",
      "Warrior",
      this.classesData,
      null,
      this.lang,
    );
    this.player.weatherData = this.weatherData || {};
    this.player.timesData = this.timesData || {};
    this.player.createCharacter(this.classesData, this.itemsData, this.lang);
    this.visitedAreas.add(this.player.currentArea);
    this.updateWeather();
  }

  /**
   * Change language menu
   */
  async changeLanguageMenu() {
    this.print(
      `\n${Colors.CYAN}${Colors.BOLD}=== ${this.lang.get("settings", "SETTINGS")} ===${Colors.END}`,
    );
    const available = this.lang.config?.available_languages || {
      en: "English",
    };

    const langs = Object.entries(available);
    for (let i = 0; i < langs.length; i++) {
      this.print(`${Colors.CYAN}${i + 1}.${Colors.END} ${langs[i][1]}`);
    }
    this.print(
      `${Colors.CYAN}${langs.length + 1}.${Colors.END} ${this.lang.get("back", "Back")}`,
    );

    const choice = await this.ask(
      `${Colors.CYAN}Choose a language: ${Colors.END}`,
    );

    if (!isNaN(choice)) {
      const idx = parseInt(choice) - 1;
      if (idx >= 0 && idx < langs.length) {
        this.lang.changeLanguage(langs[idx][0]);
      } else if (idx === langs.length) {
        return;
      }
    }
    this.print(createSeparator());
  }

  /**
   * Main menu
   */
  async mainMenu() {
    // Advance time by 5 to 10 minutes each menu loop
    if (this.player) {
      this.player.advanceTime(10.0);
    }

    // Continuous mission check on every main menu return
    this.updateMissionProgress("check", "");

    // Check level-based challenges
    if (this.player) {
      this.updateChallengeProgress("level_reach", this.player.level);
    }

    // Show current location
    const areaData = this.areasData[this.currentArea] || {};
    const areaName = areaData.name || this.currentArea;

    const menuMax = this.currentArea === "your_land" ? "24" : "20";

    const menuOutput = displayMainMenu(
      this.lang,
      this.player,
      areaName,
      menuMax,
    );
    this.print(menuOutput);

    let choice = await this.ask(
      `${Colors.CYAN}Choose an option (1-${menuMax}): ${Colors.END}`,
      null,
      false,
    );

    // Normalize textual shortcuts
    const shortcutMap = {
      explore: "1",
      e: "1",
      view: "2",
      v: "2",
      travel: "3",
      t: "3",
      inventory: "4",
      i: "4",
      missions: "5",
      m: "5",
      boss: "6",
      tavern: "7",
      shop: "8",
      s: "8",
      alchemy: "9",
      alc: "9",
      craft: "9",
      crafting: "9",
      market: "10",
      mkt: "10",
      elite: "10",
      rest: "11",
      r: "11",
      companions: "12",
      comp: "12",
      pet_shop: "15",
      settings: "16",
      lang: "16",
      language: "16",
      build_home: "17",
      furnish_home: "17",
      build_land: "18",
      build_structures: "18",
      land: "18",
      farm: "19",
      training: "20",
      train: "20",
      save: this.currentArea === "your_land" ? "21" : "17",
      load: this.currentArea === "your_land" ? "22" : "18",
      l: this.currentArea === "your_land" ? "22" : "18",
      claim: this.currentArea === "your_land" ? "23" : "19",
      c: this.currentArea === "your_land" ? "23" : "19",
      quit: this.currentArea === "your_land" ? "24" : "20",
      q: this.currentArea === "your_land" ? "24" : "20",
    };

    const normalized = choice.toLowerCase().trim();
    if (shortcutMap[normalized]) {
      choice = shortcutMap[normalized];
    }

    switch (choice) {
      case "1":
        await this.explore();
        break;
      case "2":
        if (this.player) {
          this.player.displayStats(this.print.bind(this));
        } else {
          this.print(this.lang.get("no_character"));
        }
        break;
      case "3":
        await this.travel();
        break;
      case "4":
        await this.viewInventory();
        break;
      case "5":
        await this.viewMissions();
        break;
      case "6":
        await this.fightBossMenu();
        break;
      case "7":
        await this.visitTavern();
        break;
      case "8":
        await this.visitShop();
        break;
      case "9":
        await visit_alchemy(this);
        break;
      case "10":
        await this.visitMarket();
        break;
      case "11":
        await this.rest();
        break;
      case "12":
        await this.manageCompanions();
        break;
      case "13":
        await this.dungeonSystem.visitDungeons();
        break;
      case "14":
        await this.viewChallenges();
        break;
      case "15":
        if (this.currentArea === "your_land") {
          await this.petShop();
        }
        break;
      case "16":
        await this.changeLanguageMenu();
        break;
      case "17":
        if (this.currentArea === "your_land") {
          await build_home(this);
        } else {
          await this.saveGame();
        }
        break;
      case "18":
        if (this.currentArea === "your_land") {
          await build_structures(this);
        } else {
          await this.loadGame();
        }
        break;
      case "19":
        if (this.currentArea === "your_land") {
          await farm(this);
        } else {
          await this.claimRewards();
        }
        break;
      case "20":
        if (this.currentArea === "your_land") {
          await training(this);
        } else {
          await this.quitGame();
        }
        break;
      case "21":
        if (this.currentArea === "your_land") {
          await this.saveGame();
        }
        break;
      case "22":
        if (this.currentArea === "your_land") {
          await this.loadGame();
        }
        break;
      case "23":
        if (this.currentArea === "your_land") {
          await this.claimRewards();
        }
        break;
      case "24":
        if (this.currentArea === "your_land") {
          await this.quitGame();
        }
        break;
      default:
        this.print(this.lang.get("invalid_choice"));
    }
  }

  /**
   * Fight boss menu
   */
  async fightBossMenu() {
    if (!this.player) {
      this.print(this.lang.get("no_character"));
      return;
    }

    const areaData = this.areasData[this.currentArea] || {};
    const possibleBosses = areaData.possible_bosses || [];

    if (!possibleBosses || possibleBosses.length === 0) {
      this.print(
        `There are no bosses in ${areaData.name || this.currentArea}.`,
      );
      return;
    }

    this.print(
      `\n${Colors.RED}${Colors.BOLD}=== BOSSES IN ${(areaData.name || this.currentArea).toUpperCase()} ===${Colors.END}`,
    );

    for (let i = 0; i < possibleBosses.length; i++) {
      const bossName = possibleBosses[i];
      const bossData = this.bossesData[bossName] || {};
      let status = "";

      if (this.player.bossesKilled && this.player.bossesKilled[bossName]) {
        const lastKilledStr = this.player.bossesKilled[bossName];
        try {
          const lastKilledDt = new Date(lastKilledStr);
          const diff = Date.now() - lastKilledDt.getTime();
          if (diff < 28800000) {
            // 8 hours in ms
            status = ` ${Colors.YELLOW}(Cooldown: ${Math.floor((28800000 - diff) / 60000)}m left)${Colors.END}`;
          }
        } catch {
          // Ignore date parsing errors
        }
      }
      this.print(`${i + 1}. ${bossData.name || bossName}${status}`);
    }

    const choice = await this.ask(
      `Choose a boss (1-${possibleBosses.length}) or Enter to cancel: `,
    );
    if (choice && !isNaN(choice)) {
      const idx = parseInt(choice) - 1;
      if (idx >= 0 && idx < possibleBosses.length) {
        const bossName = possibleBosses[idx];

        // Cooldown check
        if (this.player.bossesKilled && this.player.bossesKilled[bossName]) {
          const lastKilledStr = this.player.bossesKilled[bossName];
          try {
            const lastKilledDt = new Date(lastKilledStr);
            if (Date.now() - lastKilledDt.getTime() < 28800000) {
              this.print(`${bossName} is still recovering. Try again later.`);
              return;
            }
          } catch {
            // Ignore date parsing errors
          }
        }

        const bossData = this.bossesData[bossName];
        if (bossData) {
          const boss = new Boss(bossData, this.dialoguesData);
          this.print(
            `\n${Colors.RED}${Colors.BOLD}Challenge accepted!${Colors.END}`,
          );

          const startDialogue = boss.getDialogue("on_start_battle");
          if (startDialogue) {
            this.print(
              `\n${Colors.CYAN}${boss.name}:${Colors.END} ${startDialogue}`,
            );
          }

          await this.battle(boss);
        }
      } else {
        this.print(this.lang.get("invalid_choice"));
      }
    }
  }

  /**
   * Explore current area
   */
  async explore() {
    if (this.player) {
      this.player.advanceTime(5.0);
    }
    if (!this.player) {
      this.print(this.lang.get("no_character_created"));
      return;
    }

    // Continuous mission check
    this.updateMissionProgress("check", "");

    const areaData = this.areasData[this.currentArea] || {};
    const areaName = areaData.name || "Unknown Area";

    this.print(
      this.lang.get("exploring_area_msg").replace("{area_name}", areaName),
    );

    // Random encounter chance
    if (Math.random() < 0.7) {
      await this.randomEncounter();
    } else {
      this.print(this.lang.get("explore_nothing_found"));

      // Small chance to find materials
      if (Math.random() < 0.4) {
        await this.gatherMaterials();
      }

      // Small chance to find gold
      if (Math.random() < 0.3) {
        const foundGold = Math.floor(Math.random() * 16) + 5;
        this.player.gold += foundGold;
        this.print(
          this.lang.get("found_gold_msg").replace("{gold}", foundGold),
        );
      }
    }
  }

  /**
   * Random encounter
   */
  async randomEncounter() {
    if (!this.player) return;

    const areaData = this.areasData[this.currentArea] || {};
    const possibleEnemies = areaData.possible_enemies || [];

    if (!possibleEnemies || possibleEnemies.length === 0) {
      const msg = this.lang.get("no_enemies_in_area");
      this.print(msg.replace(/\\n/g, "\n").replace(/\\033/g, "\x1b"));
      return;
    }

    const enemyName =
      possibleEnemies[Math.floor(Math.random() * possibleEnemies.length)];
    const enemyData = this.enemiesData[enemyName];

    if (enemyData) {
      const enemy = new Enemy(enemyData);
      const msg = `\nA wild ${enemy.name} appears!`;
      this.print(Colors.wrap(msg, Colors.RED));
      await this.battle(enemy);
    } else {
      const msg = this.lang.get("explore_no_enemies");
      this.print(msg.replace(/\\n/g, "\n").replace(/\\033/g, "\x1b"));
    }
  }

  /**
   * Update challenge progress
   * @param {string} challengeType - Challenge type
   * @param {number} value - Progress value
   */
  updateChallengeProgress(challengeType, value = 1) {
    if (!this.player) return;

    const challenges = this.weeklyChallengesData.challenges || [];
    for (const challenge of challenges) {
      if (this.completedChallenges.includes(challenge.id)) continue;

      if (challenge.type === challengeType) {
        this.challengeProgress[challenge.id] += value;

        // Show progress bar
        const bar = createProgressBar(
          this.challengeProgress[challenge.id],
          challenge.target,
          20,
          Colors.YELLOW,
        );
        this.print(
          `${Colors.CYAN}[Challenge Progress] ${challenge.name}: ${bar} ${this.challengeProgress[challenge.id]}/${challenge.target}${Colors.END}`,
        );

        // Check completion
        if (this.challengeProgress[challenge.id] >= challenge.target) {
          this.completeChallenge(challenge);
        }
      }
    }
  }

  /**
   * Complete a challenge
   * @param {Object} challenge - Challenge object
   */
  completeChallenge(challenge) {
    if (!this.player) return;

    const challengeId = challenge.id;
    this.completedChallenges.push(challengeId);

    const rewardExp = challenge.reward_exp || 0;
    const rewardGold = challenge.reward_gold || 0;

    this.player.gainExperience(rewardExp);
    this.player.gold += rewardGold;

    this.print(
      `\n${Colors.CYAN}${Colors.BOLD}✓ Challenge Completed: ${challenge.name}!${Colors.END}`,
    );
    this.print(`  Reward: ${rewardExp} EXP + ${rewardGold} Gold`);
  }

  /**
   * View challenges
   */
  async viewChallenges() {
    if (!this.player) return;

    this.print(
      `\n${Colors.CYAN}${Colors.BOLD}=== WEEKLY CHALLENGES ===${Colors.END}`,
    );

    const challenges = this.weeklyChallengesData.challenges || [];
    for (const challenge of challenges) {
      const challengeId = challenge.id;
      const isCompleted = this.completedChallenges.includes(challengeId);
      const progress = this.challengeProgress[challengeId] || 0;
      const target = challenge.target;

      const status = isCompleted ? "✓" : `${progress}/${target}`;
      const completedText = isCompleted
        ? `${Colors.GREEN}COMPLETED${Colors.END}`
        : status;

      this.print(`\n${Colors.BOLD}${challenge.name}${Colors.END}`);
      this.print(`  ${challenge.description}`);
      this.print(`  Status: ${completedText}`);
      this.print(
        `  Reward: ${challenge.reward_exp} EXP + ${challenge.reward_gold} Gold`,
      );
    }
  }

  /**
   * Battle wrapper
   * @param {Object} enemy - Enemy to battle
   */
  async battle(enemy) {
    await this.battleSystem.battle(enemy);
  }

  /**
   * Player turn wrapper
   * @param {Object} enemy - Enemy
   * @returns {Promise<boolean>} Continue battle
   */
  async playerTurn(enemy) {
    return await this.battleSystem.playerTurn(enemy);
  }

  /**
   * Companion action
   * @param {Object} companion - Companion
   * @param {Object} enemy - Enemy
   */
  companionActionFor(companion, enemy) {
    this.battleSystem.companionActionFor(companion, enemy);
  }

  /**
   * Companions act
   * @param {Object} enemy - Enemy
   */
  companionsAct(enemy) {
    this.battleSystem.companionsAct(enemy);
  }

  /**
   * Enemy turn
   * @param {Object} enemy - Enemy
   */
  enemyTurn(enemy) {
    this.battleSystem.enemyTurn(enemy);
  }

  /**
   * Use item in battle
   */
  async useItemInBattle() {
    if (!this.player) return;

    const consumables = this.player.inventory.filter(
      (item) =>
        this.itemsData[item] && this.itemsData[item].type === "consumable",
    );

    if (!consumables || consumables.length === 0) {
      const msg = this.lang.get("no_consumable_items");
      this.print(msg.replace(/\\n/g, "\n").replace(/\\033/g, "\x1b"));
      return;
    }

    const msg = this.lang.get("available_consumables");
    this.print(msg.replace(/\\n/g, "\n").replace(/\\033/g, "\x1b"));

    for (let i = 0; i < consumables.length; i++) {
      const item = consumables[i];
      const itemData = this.itemsData[item] || {};
      this.print(
        `${i + 1}. ${item} - ${itemData.description || "Unknown effect"}`,
      );
    }

    const choice = await this.ask(`Choose item (1-${consumables.length}): `);
    const idx = parseInt(choice) - 1;
    if (!isNaN(idx) && idx >= 0 && idx < consumables.length) {
      const item = consumables[idx];
      await this.useItem(item);
      const itemIndex = this.player.inventory.indexOf(item);
      if (itemIndex > -1) {
        this.player.inventory.splice(itemIndex, 1);
      }
    } else {
      this.print(this.lang.get("invalid_choice"));
    }
  }

  /**
   * Cast spell
   * @param {Object} enemy - Enemy target
   * @param {string} weaponName - Weapon name
   */
  async castSpell(enemy, weaponName = null) {
    if (!this.player) return;

    const selected = await this.spellCastingSystem.selectSpell(weaponName);
    if (selected) {
      const [spellName, spellData] = selected;
      this.spellCastingSystem.castSpell(enemy, spellName, spellData);
    }
  }

  /**
   * Use an item
   * @param {string} item - Item name
   */
  async useItem(item) {
    if (!this.player) return;

    const itemData = this.itemsData[item] || {};
    const itemType = itemData.type;

    if (itemType === "consumable") {
      if (itemData.effect === "heal") {
        const healAmount = itemData.value || 0;
        const oldHp = this.player.hp;
        this.player.heal(healAmount);
        this.print(`Used ${item}, healed ${this.player.hp - oldHp} HP!`);
      } else if (itemData.effect === "mp_restore") {
        const mpAmount = itemData.value || 0;
        const oldMp = this.player.mp;
        this.player.mp = Math.min(this.player.maxMp, this.player.mp + mpAmount);
        this.print(`Used ${item}, restored ${this.player.mp - oldMp} MP!`);
      }
    }
  }

  /**
   * View inventory
   */
  async viewInventory() {
    if (!this.player) {
      this.print(this.lang.get("no_character"));
      return;
    }

    this.print(this.lang.get("inventory"));
    this.print(`Gold: ${Colors.GOLD}${this.player.gold}${Colors.END}`);

    if (!this.player.inventory || this.player.inventory.length === 0) {
      this.print(this.lang.get("inventory_empty"));
      return;
    }

    // Group items by type
    const itemsByType = {};
    for (const item of this.player.inventory) {
      const itemType = (this.itemsData[item] || {}).type || "unknown";
      if (!itemsByType[itemType]) {
        itemsByType[itemType] = [];
      }
      itemsByType[itemType].push(item);
    }

    for (const [itemType, items] of Object.entries(itemsByType)) {
      this.print(
        `\n${Colors.CYAN}${itemType.charAt(0).toUpperCase() + itemType.slice(1)}:${Colors.END}`,
      );
      for (const item of items) {
        const itemData = this.itemsData[item] || {};
        this.print(`  - ${item}`);
        if (itemData.description) {
          this.print(`    ${itemData.description}`);
        }
      }
    }

    // Get consumable items
    const consumables = this.player.inventory.filter(
      (it) => (this.itemsData[it] || {}).type === "consumable",
    );

    // Offer equip/unequip options
    const equipable = this.player.inventory.filter(
      (it) =>
        (this.itemsData[it] || {}).type in
        ["weapon", "armor", "accessory", "offhand"],
    );

    if (equipable.length > 0 || consumables.length > 0) {
      this.print(this.lang.get("equipment_options"));
      if (equipable.length > 0) {
        this.print(this.lang.get("equip_from_inventory"));
        this.print(this.lang.get("unequip_slot"));
      }
      if (consumables.length > 0) {
        this.print(
          this.lang.get("use_consumable_option", "  C. Use a consumable item"),
        );
      }

      const choice = (
        await this.ask("Choose option (E/U/C) or press Enter to return: ")
      ).toLowerCase();

      if (choice === "e" && equipable.length > 0) {
        this.print(this.lang.get("equipable_items"));
        for (let i = 0; i < equipable.length; i++) {
          const item = equipable[i];
          this.print(
            `${i + 1}. ${item} - ${(this.itemsData[item] || {}).description || ""}`,
          );
        }
        const sel = await this.ask(
          `Choose item to equip (1-${equipable.length}) or press Enter: `,
        );
        if (sel && !isNaN(sel)) {
          const idx = parseInt(sel) - 1;
          if (idx >= 0 && idx < equipable.length) {
            const itemName = equipable[idx];
            const ok = this.player.equip(itemName, this.itemsData);
            if (ok) {
              this.print(`Equipped ${itemName}.`);
            } else {
              this.print(`Cannot equip ${itemName} (requirements not met).`);
            }
          }
        }
      } else if (choice === "u") {
        this.print(this.lang.get("currently_equipped"));
        const slots = [
          "weapon",
          "armor",
          "offhand",
          "accessory_1",
          "accessory_2",
          "accessory_3",
        ];
        for (const slot of slots) {
          this.print(
            `${slot.charAt(0).toUpperCase() + slot.slice(1)}: ${this.player.equipment[slot] || "None"}`,
          );
        }
        const slotChoice = await this.ask(
          "Enter slot to unequip or press Enter: ",
        );
        const validSlots = [
          "weapon",
          "armor",
          "offhand",
          "accessory_1",
          "accessory_2",
          "accessory_3",
        ];
        if (validSlots.includes(slotChoice)) {
          const removed = this.player.unequip(slotChoice, this.itemsData);
          if (removed) {
            this.print(`Unequipped ${removed} from ${slotChoice}.`);
          } else {
            this.print(this.lang.get("nothing_to_unequip"));
          }
        }
      } else if (choice === "c" && consumables.length > 0) {
        this.print(
          `\n${this.lang.get("consumable_items_header", "Consumable items:")}`,
        );
        for (let i = 0; i < consumables.length; i++) {
          const item = consumables[i];
          const itemData = this.itemsData[item] || {};
          this.print(`${i + 1}. ${item} - ${itemData.description || ""}`);
        }
        const sel = await this.ask(
          `Choose item to use (1-${consumables.length}) or press Enter: `,
        );
        if (sel && !isNaN(sel)) {
          const idx = parseInt(sel) - 1;
          if (idx >= 0 && idx < consumables.length) {
            const itemName = consumables[idx];
            await this.useItem(itemName);
            const itemIndex = this.player.inventory.indexOf(itemName);
            if (itemIndex > -1) {
              this.player.inventory.splice(itemIndex, 1);
            }
            this.print(`Used ${itemName}.`);
          }
        }
      }
    }
  }

  /**
   * View missions
   */
  async viewMissions() {
    while (true) {
      if (this.clear) this.clear();
      this.print(createSectionHeader("MISSIONS"));

      // Active Missions
      const activeMissions = Object.keys(this.missionProgress).filter(
        (mid) => !this.missionProgress[mid]?.completed,
      );

      if (activeMissions.length > 0) {
        this.print(this.lang.get("active_missions"));

        for (let i = 0; i < activeMissions.length; i++) {
          const mid = activeMissions[i];
          const mission = this.missionsData[mid] || {};
          const progress = this.missionProgress[mid];

          let status;
          if (progress.type === "kill") {
            if (progress.currentCounts) {
              status = Object.entries(progress.targetCounts)
                .map(([t, c]) => `${t}: ${progress.currentCounts[t] || 0}/${c}`)
                .join(", ");
            } else {
              status = `${progress.currentCount}/${progress.targetCount}`;
            }
          } else {
            if (progress.currentCounts) {
              status = Object.entries(progress.targetCounts)
                .map(([t, c]) => `${t}: ${progress.currentCounts[t] || 0}/${c}`)
                .join(", ");
            } else {
              status = `${progress.currentCount}/${progress.targetCount}`;
            }
          }

          this.print(`${i + 1}. ${mission.name} - ${status}`);
          this.print(
            `   ${Colors.DARK_GRAY}${mission.description || ""}${Colors.END}`,
          );
        }

        this.print(`\n${this.lang.get("options_available_cancel_back")}`);
      } else {
        this.print(this.lang.get("no_active_missions"));
        this.print(`\n${this.lang.get("options_available_missions_back")}`);
      }

      const choice = (await this.ask("\nChoose an option: ")).toUpperCase();

      if (choice === "B") {
        break;
      } else if (choice === "A") {
        await this.availableMissionsMenu();
      } else if (choice === "C" && activeMissions.length > 0) {
        const idxStr = await this.ask("Enter mission number to cancel: ");
        if (!isNaN(idxStr)) {
          const idx = parseInt(idxStr) - 1;
          if (idx >= 0 && idx < activeMissions.length) {
            const mId = activeMissions[idx];
            const mName = this.missionsData[mId]?.name;
            const confirm = (
              await this.ask(
                `Are you sure you want to cancel '${mName}'? (y/n): `,
              )
            ).toLowerCase();
            if (confirm === "y") {
              delete this.missionProgress[mId];
              this.print(`Mission '${mName}' cancelled.`);
              await this.delay(1000);
            }
          } else {
            this.print(this.lang.get("invalid_mission_number"));
            await this.delay(1000);
          }
        }
      }
    }
  }

  /**
   * Available missions menu
   */
  async availableMissionsMenu() {
    let page = 0;
    const perPage = 10;

    while (true) {
      if (this.clear) this.clear();
      this.print(createSectionHeader("AVAILABLE MISSIONS"));

      const availableMissions = Object.keys(this.missionsData).filter(
        (mid) =>
          !this.missionProgress[mid] && !this.completedMissions.includes(mid),
      );

      if (availableMissions.length === 0) {
        this.print(this.lang.get("no_new_missions"));
        await this.ask("\nPress Enter to go back...");
        break;
      }

      const totalPages = Math.ceil(availableMissions.length / perPage);
      const startIdx = page * perPage;
      const endIdx = Math.min(startIdx + perPage, availableMissions.length);
      const currentPageMissions = availableMissions.slice(startIdx, endIdx);

      for (let i = 0; i < currentPageMissions.length; i++) {
        const missionId = currentPageMissions[i];
        const mission = this.missionsData[missionId] || {};
        this.print(
          `${i + 1}. ${Colors.BOLD}${mission.name || "Unknown"}${Colors.END}`,
        );
        this.print(`   ${mission.description || ""}`);

        // Requirements
        const reqs = [];
        if (mission.unlock_level) {
          const levelReq = mission.unlock_level;
          const hasLevel = this.player ? this.player.level >= levelReq : false;
          const color = hasLevel ? Colors.GREEN : Colors.RED;
          reqs.push(`Level ${color}${levelReq}${Colors.END}`);
        }
        if (mission.prerequisites) {
          for (const prereqId of mission.prerequisites) {
            const prereqName =
              (this.missionsData[prereqId] || {}).name || prereqId;
            const color = this.completedMissions.includes(prereqId)
              ? Colors.GREEN
              : Colors.RED;
            reqs.push(`Requires: ${color}${prereqName}${Colors.END}`);
          }
        }
        if (reqs.length > 0) {
          this.print(`   Requirements: ${reqs.join(", ")}`);
        }
      }

      this.print(`\nPage ${page + 1}/${totalPages}`);
      if (totalPages > 1) {
        if (page > 0) this.print(`P. ${this.lang.get("ui_previous_page")}`);
        if (page < totalPages - 1)
          this.print(`N. ${this.lang.get("ui_next_page")}`);
      }

      if (currentPageMissions.length > 0) {
        this.print(`1-${currentPageMissions.length}. Accept Mission`);
      }
      this.print(`B. ${this.lang.get("back")}`);

      const choice = (await this.ask("\nChoose an option: ")).toUpperCase();

      if (choice === "B") {
        break;
      } else if (choice === "N" && page < totalPages - 1) {
        page += 1;
      } else if (choice === "P" && page > 0) {
        page -= 1;
      } else if (!isNaN(choice)) {
        const idx = parseInt(choice) - 1;
        if (idx >= 0 && idx < currentPageMissions.length) {
          const missionId = currentPageMissions[idx];
          await this.acceptMission(missionId);
        } else {
          this.print(this.lang.get("invalid_mission_number"));
          await this.delay(1000);
        }
      }
    }
  }

  /**
   * Accept a mission
   * @param {string} missionId - Mission ID
   */
  async acceptMission(missionId) {
    if (this.missionProgress[missionId]) {
      this.print(this.lang.get("mission_already_accepted"));
      await this.delay(1000);
      return;
    }

    const mission = this.missionsData[missionId];
    if (!mission) {
      this.print(this.lang.get("mission_data_not_found"));
      await this.delay(1000);
      return;
    }

    // Initialize progress tracking
    const missionType = mission.type || "kill";
    const targetCount = mission.target_count || 1;

    if (missionType === "collect" && typeof targetCount === "object") {
      this.missionProgress[missionId] = {
        currentCounts: Object.fromEntries(
          Object.keys(targetCount).map((k) => [k, 0]),
        ),
        targetCounts: targetCount,
        completed: false,
        type: missionType,
      };
    } else {
      this.missionProgress[missionId] = {
        currentCount: 0,
        targetCount: targetCount,
        completed: false,
        type: missionType,
      };
    }

    this.print(`Mission accepted: ${mission.name || "Unknown"}`);

    // Check for accept cutscene
    const acceptCutscene = mission.accept_cutscene;
    if (acceptCutscene && this.cutscenesData[acceptCutscene]) {
      await this.playCutscene(acceptCutscene);
    }

    await this.delay(1000);
  }

  /**
   * Update mission progress
   * @param {string} updateType - Update type
   * @param {string} target - Target
   * @param {number} count - Count
   */
  updateMissionProgress(updateType, target, count = 1) {
    // Always check inventory-based collect missions
    if (this.player) {
      for (const [mid, progress] of Object.entries(this.missionProgress)) {
        if (progress.completed) continue;

        const mission = this.missionsData[mid];
        if (progress.type === "collect") {
          if (progress.currentCounts) {
            for (const item of Object.keys(progress.targetCounts)) {
              const invCount = this.player.inventory.filter(
                (i) => i === item,
              ).length;
              progress.currentCounts[item] = invCount;
            }

            const allCollected = Object.keys(progress.targetCounts).every(
              (item) =>
                progress.currentCounts[item] >= progress.targetCounts[item],
            );
            if (allCollected) {
              this.completeMission(mid);
            }
          } else {
            const targetItem = mission?.target || "";
            const invCount = this.player.inventory.filter(
              (i) => i === targetItem,
            ).length;
            progress.currentCount = invCount;
            if (progress.currentCount >= progress.targetCount) {
              this.completeMission(mid);
            }
          }
        }
      }
    }

    // Standard update logic
    for (const [mid, progress] of Object.entries(this.missionProgress)) {
      if (progress.completed) continue;

      const mission = this.missionsData[mid];

      if (progress.type === "kill" && updateType === "kill") {
        const targetEnemy = (mission?.target || "").toLowerCase();
        if (targetEnemy === target.toLowerCase()) {
          progress.currentCount += count;
          const bar = createProgressBar(
            progress.currentCount,
            progress.targetCount,
            20,
            Colors.CYAN,
          );
          this.print(
            `${Colors.CYAN}[Mission Progress] ${mission.name}: ${bar} ${progress.currentCount}/${progress.targetCount}${Colors.END}`,
          );

          if (progress.currentCount >= progress.targetCount) {
            this.completeMission(mid);
          }
        }
      } else if (progress.type === "collect" && updateType === "collect") {
        if (progress.currentCounts && target in progress.currentCounts) {
          progress.currentCounts[target] += count;
          const bar = createProgressBar(
            progress.currentCounts[target],
            progress.targetCounts[target],
            20,
            Colors.CYAN,
          );
          this.print(
            `${Colors.CYAN}[Mission Progress] ${mission.name} - ${target}: ${bar} ${progress.currentCounts[target]}/${progress.targetCounts[target]}${Colors.END}`,
          );

          const allCollected = Object.keys(progress.targetCounts).every(
            (item) =>
              progress.currentCounts[item] >= progress.targetCounts[item],
          );
          if (allCollected) {
            this.completeMission(mid);
          }
        } else if (!progress.currentCounts) {
          const targetItem = mission?.target || "";
          if (targetItem === target) {
            progress.currentCount += count;
            const bar = createProgressBar(
              progress.currentCount,
              progress.targetCount,
              20,
              Colors.CYAN,
            );
            this.print(
              `${Colors.CYAN}[Mission Progress] ${mission.name}: ${bar} ${progress.currentCount}/${progress.targetCount}${Colors.END}`,
            );

            if (progress.currentCount >= progress.targetCount) {
              this.completeMission(mid);
            }
          }
        }
      }
    }
  }

  /**
   * Complete a mission
   * @param {string} missionId - Mission ID
   */
  completeMission(missionId) {
    if (this.missionProgress[missionId]) {
      this.missionProgress[missionId].completed = true;
      const mission = this.missionsData[missionId] || {};
      this.print(
        `\n${Colors.GOLD}${Colors.BOLD}!!! MISSION COMPLETE: ${mission.name || "Unknown"} !!!${Colors.END}`,
      );
      this.print(
        `${Colors.YELLOW}You can now claim your rewards from the menu.${Colors.END}`,
      );

      // Check for complete cutscene
      const completeCutscene = mission.complete_cutscene;
      if (completeCutscene && this.cutscenesData[completeCutscene]) {
        this.playCutscene(completeCutscene);
      }

      setTimeout(() => {}, 2000);
    }
  }

  /**
   * Claim rewards
   */
  async claimRewards() {
    if (!this.player) {
      this.print(this.lang.get("no_character"));
      return;
    }

    const completedMissions = Object.keys(this.missionProgress).filter(
      (mid) => this.missionProgress[mid]?.completed,
    );

    if (completedMissions.length === 0) {
      this.print(this.lang.get("no_completed_missions"));
      return;
    }

    this.print(this.lang.get("claim_rewards"));
    this.print(this.lang.get("completed_missions_header"));

    for (let i = 0; i < completedMissions.length; i++) {
      const mid = completedMissions[i];
      const mission = this.missionsData[mid] || {};
      const reward = mission.reward || {};
      const exp = reward.experience || 0;
      const gold = reward.gold || 0;
      const items = reward.items || [];
      this.print(
        `${i + 1}. ${mission.name || "Unknown"} - Exp: ${exp}, Gold: ${gold}, Items: ${items.length > 0 ? items.join(", ") : "None"}`,
      );
    }

    const choice = await this.ask(
      `Claim rewards for mission (1-${completedMissions.length}) or press Enter to cancel: `,
    );
    if (choice && !isNaN(choice)) {
      const idx = parseInt(choice) - 1;
      if (idx >= 0 && idx < completedMissions.length) {
        const missionId = completedMissions[idx];
        const mission = this.missionsData[missionId] || {};
        const reward = mission.reward || {};

        const exp = reward.experience || 0;
        const gold = reward.gold || 0;
        const items = reward.items || [];

        this.player.gainExperience(exp);
        this.player.gold += gold;
        for (const item of items) {
          this.player.inventory.push(item);
        }

        delete this.missionProgress[missionId];
        this.completedMissions.push(missionId);

        this.print(this.lang.get("rewards_claimed"));
        this.print(`Gained ${Colors.MAGENTA}${exp} experience${Colors.END}`);
        this.print(`Gained ${Colors.GOLD}${gold} gold${Colors.END}`);
        if (items.length > 0) {
          this.print(`Received items: ${items.join(", ")}`);
        }
      } else {
        this.print(this.lang.get("invalid_choice"));
      }
    }
  }

  /**
   * Visit shop
   */
  async visitShop() {
    if (!this.player) {
      this.print(this.lang.get("no_character"));
      return;
    }

    const areaData = this.areasData[this.currentArea] || {};
    const areaShops = areaData.shops || [];

    const availableShops = [...areaShops];
    if (this.currentArea === "your_land") {
      availableShops.push("housing_shop");
    }

    if (availableShops.length === 0) {
      this.print(
        `\n${Colors.RED}There are no shops in ${areaData.name || this.currentArea}.${Colors.END}`,
      );
      return;
    }

    let selectedShop;
    if (availableShops.length > 1) {
      this.print(
        `\n${Colors.BOLD}=== SHOPS IN ${(areaData.name || this.currentArea).toUpperCase()} ===${Colors.END}`,
      );
      this.print(`Your gold: ${Colors.GOLD}${this.player.gold}${Colors.END}\n`);

      for (let i = 0; i < availableShops.length; i++) {
        const shopId = availableShops[i];
        let shopName;
        if (shopId === "housing_shop") {
          shopName = "Housing Shop";
        } else {
          const shopData = this.shopsData[shopId] || {};
          shopName =
            shopData.name ||
            shopId.replace(/_/g, " ").replace(/\b\w/g, (l) => l.toUpperCase());
        }
        this.print(`${i + 1}. ${shopName}`);
      }

      this.print(this.lang.get("leave_option"));
      const choice = await this.ask("Which shop would you like to visit? ");

      if (choice === "0" || !choice || isNaN(choice)) {
        return;
      }

      const shopIdx = parseInt(choice) - 1;
      if (shopIdx >= 0 && shopIdx < availableShops.length) {
        selectedShop = availableShops[shopIdx];
      } else {
        this.print(this.lang.get("invalid_choice"));
        return;
      }
    } else {
      selectedShop = availableShops[0];
    }

    // Now visit the selected shop
    if (selectedShop === "housing_shop") {
      await this.visitHousingShopInline();
    } else {
      await visit_specific_shop(this, selectedShop);
    }
  }

  /**
   * Visit the housing shop in your_land to buy housing items
   */
  async visitHousingShopInline() {
    if (!this.player) {
      this.print(this.lang.get("no_character"));
      return;
    }

    this.print(this.lang.get("housing_shop"));
    this.print(
      `${Colors.YELLOW}Welcome to the Housing Shop! Build your dream home with these items.${Colors.END}`,
    );
    this.print(`\nYour gold: ${Colors.GOLD}${this.player.gold}${Colors.END}`);
    this.print(
      `Comfort Points: ${Colors.CYAN}${this.player.comfortPoints || 0}${Colors.END}`,
    );
    this.print(
      `Items owned: ${Colors.MAGENTA}${(this.player.housingOwned || []).length}${Colors.END}`,
    );

    // Get all housing items
    const housingItems = Object.entries(this.housingData);
    if (!housingItems || housingItems.length === 0) {
      this.print(this.lang.get("no_housing_items_available"));
      return;
    }

    const pageSize = 8;
    let currentPage = 0;

    while (true) {
      const start = currentPage * pageSize;
      const end = start + pageSize;
      const pageItems = housingItems.slice(start, end);

      if (!pageItems || pageItems.length === 0) {
        this.print(this.lang.get("no_more_items"));
        break;
      }

      this.print(
        `\n${Colors.CYAN}--- Page ${currentPage + 1} of ${Math.ceil(housingItems.length / pageSize)} ---${Colors.END}`,
      );
      for (let i = 0; i < pageItems.length; i++) {
        const [itemId, itemData] = pageItems[i];
        const name = itemData.name || itemId;
        const price = itemData.price || 0;
        const comfort = itemData.comfort_points || 0;
        const desc = itemData.description || "";
        const owned = (this.player.housingOwned || []).includes(itemId)
          ? "✓"
          : " ";

        // Color price based on affordability
        const priceColor =
          this.player.gold >= price ? Colors.GREEN : Colors.RED;
        // Color owned indicator
        const ownedColor = owned === "✓" ? Colors.GREEN : Colors.RED;

        this.print(
          `\n${Colors.CYAN}${i + 1}.${Colors.END} [${ownedColor}${owned}${Colors.END}] ${Colors.BOLD}${Colors.YELLOW}${name}${Colors.END}`,
        );
        this.print(`   ${desc}`);
        this.print(
          `   Price: ${priceColor}${price} gold${Colors.END} | Comfort: ${Colors.CYAN}+${comfort}${Colors.END}`,
        );
      }

      this.print(this.lang.get("options_2"));
      this.print(
        `${Colors.CYAN}1-${pageItems.length}.${Colors.END} Buy/Add Housing Item`,
      );
      if (housingItems.length > pageSize) {
        this.print(this.lang.get("n_next_page"));
        this.print(this.lang.get("p_previous_page"));
      }
      this.print(this.lang.get("b_furnishview_home"));
      this.print(this.lang.get("enter_leave_shop"));

      const choice = (await this.ask("\nChoose action: ")).trim().toUpperCase();

      if (!choice) {
        break;
      } else if (choice === "N" && housingItems.length > pageSize) {
        if (end < housingItems.length) {
          currentPage += 1;
        }
      } else if (choice === "P" && housingItems.length > pageSize) {
        if (currentPage > 0) {
          currentPage -= 1;
        }
      } else if (choice === "B") {
        await build_home(this);
      } else if (!isNaN(choice)) {
        const itemIdx = parseInt(choice) - 1;
        if (itemIdx >= 0 && itemIdx < pageItems.length) {
          const [itemId, itemData] = pageItems[itemIdx];
          const name = itemData.name || itemId;
          const price = itemData.price || 0;
          const comfort = itemData.comfort_points || 0;

          // Check if already owned
          if ((this.player.housingOwned || []).includes(itemId)) {
            const confirm = (
              await this.ask(
                `\n${Colors.YELLOW}You already own this. Buy another copy for ${Colors.GOLD}${price} gold${Colors.YELLOW}? (y/n): ${Colors.END}`,
              )
            )
              .trim()
              .toLowerCase();
            if (confirm !== "y") continue;
          }

          // Check if can afford
          if (this.player.gold >= price) {
            this.player.gold -= price;
            if (!this.player.housingOwned) this.player.housingOwned = [];
            this.player.housingOwned.push(itemId);
            this.player.comfortPoints =
              (this.player.comfortPoints || 0) + comfort;
            this.print(
              `\n${Colors.GREEN}✓ Purchased ${Colors.BOLD}${name}${Colors.END}${Colors.GREEN}!${Colors.END}`,
            );
            this.print(
              `${Colors.CYAN}Comfort points: +${comfort} (Total: ${this.player.comfortPoints})${Colors.END}`,
            );
          } else {
            this.print(
              `\n${Colors.RED}✗ Not enough gold! Need ${Colors.BOLD}${price}${Colors.END}${Colors.RED}, have ${this.player.gold}.${Colors.END}`,
            );
          }
        } else {
          this.print(this.lang.get("invalid_selection_1"));
        }
      }
    }
  }

  /**
   * Visit the tavern to hire companions
   */
  async visitTavern() {
    if (!this.player) {
      this.print(this.lang.get("no_character"));
      return;
    }

    this.print(this.lang.get("tavern"));
    this.print(
      "Welcome to The Rusty Tankard. Here you can hire companions to join your party.",
    );
    this.print(`Your gold: ${Colors.GOLD}${this.player.gold}${Colors.END}`);

    const companions = Object.entries(this.companionsData);
    if (!companions || companions.length === 0) {
      this.print(this.lang.get("no_companions_available"));
      return;
    }

    const pageSize = 6;
    let currentPage = 0;

    while (true) {
      const start = currentPage * pageSize;
      const end = start + pageSize;
      const pageItems = companions.slice(start, end);

      this.print(
        `\n--- Page ${currentPage + 1} of ${Math.ceil(companions.length / pageSize)} ---`,
      );
      for (let i = 0; i < pageItems.length; i++) {
        const [cid, cdata] = pageItems[i];
        const price = cdata.price || "?";
        const desc = cdata.description || "";
        this.print(
          `${i + 1}. ${cdata.name || cid} - ${Colors.GOLD}${price} gold${Colors.END}`,
        );
        this.print(`   ${desc}`);
      }

      this.print(this.lang.get("ui_shortcuts_nav"));
      const choice = await this.ask(
        `\nHire companion (1-${pageItems.length}) or press Enter to leave: `,
      );

      if (!choice) {
        break;
      } else if (choice.toLowerCase() === "n") {
        if (end < companions.length) {
          currentPage += 1;
        } else {
          this.print(this.lang.get("ui_no_more_pages"));
        }
      } else if (choice.toLowerCase() === "p") {
        if (currentPage > 0) {
          currentPage -= 1;
        } else {
          this.print(this.lang.get("ui_already_first_page"));
        }
      } else if (!isNaN(choice)) {
        const idx = parseInt(choice) - 1;
        if (idx >= 0 && idx < pageItems.length) {
          const [cid, cdata] = pageItems[idx];
          const price = cdata.price || 0;
          if (this.player.gold >= price) {
            if ((this.player.companions || []).length >= 4) {
              this.print(
                "You already have the maximum number of companions (4).",
              );
              continue;
            }
            this.player.gold -= price;
            // Create companion data with equipment and level
            const companionData = {
              id: cid,
              name: cdata.name || cid,
              level: 1,
              equipment: {
                weapon: null,
                armor: null,
                accessory: null,
              },
            };
            if (!this.player.companions) this.player.companions = [];
            this.player.companions.push(companionData);
            this.print(`Hired ${cdata.name || cid} for ${price} gold!`);
            // Recalculate stats with new companion bonus
            this.player.updateStatsFromEquipment(
              this.itemsData,
              this.companionsData,
            );
          } else {
            this.print(this.lang.get("not_enough_gold"));
          }
        } else {
          this.print(this.lang.get("invalid_choice"));
        }
      }
    }
  }

  /**
   * Visit the Elite Market - browse and buy items from the API at 50% off
   */
  async visitMarket() {
    if (!this.player) {
      this.print(this.lang.get("no_character"));
      return;
    }

    if (!this.marketApi) {
      this.print(this.lang.get("market_api_not_available"));
      return;
    }

    this.print(
      `\n${Colors.MAGENTA}${Colors.BOLD}=== ELITE MARKET ===${Colors.END}`,
    );
    this.print(this.lang.get("welcome_elite_market"));
    if (this.player) {
      this.print(`\nYour gold: ${Colors.GOLD}${this.player.gold}${Colors.END}`);
    }

    // Check cooldown
    const remaining = this.marketApi.getCooldownRemaining();
    if (remaining && remaining.totalSeconds && remaining.totalSeconds() > 0) {
      const mins = Math.floor(remaining.totalSeconds() / 60);
      const secs = Math.floor(remaining.totalSeconds() % 60);
      this.print(
        `\n${Colors.YELLOW}Market cooldown: ${mins}m ${secs}s remaining${Colors.END}`,
      );
    }

    // Fetch market data
    const marketData = await this.marketApi.fetchMarketData();
    if (!marketData || !marketData.ok) {
      this.print(
        `\n${Colors.RED}${Colors.BOLD}Market is currently closed!${Colors.END}`,
      );
      this.print(
        `${Colors.YELLOW}Merchants have travelled to another distant far place!${Colors.END}`,
      );
      this.print(
        `${Colors.YELLOW}Please wait until the merchants arrive!${Colors.END}`,
      );
      return;
    }

    let items = this.marketApi.getAllItems();
    if (!items || items.length === 0) {
      this.print(this.lang.get("no_items_available_market"));
      return;
    }

    // Get filter options from player
    this.print(this.lang.get("browse_items"));
    this.print(this.lang.get("ui_filters_available"));
    this.print(this.lang.get("filter_all_items"));
    this.print(this.lang.get("filter_by_type_desc"));
    this.print(this.lang.get("filter_by_rarity_desc"));
    this.print(this.lang.get("filter_by_class_desc"));
    this.print(this.lang.get("filter_by_max_price_desc"));
    this.print(`  R. ${this.lang.get("filter_refresh_market")}`);

    const choice = (
      await this.ask("\nChoose filter (1-5, R) or press Enter to browse all: ")
    )
      .trim()
      .toUpperCase();

    let filteredItems = items;

    if (choice === "1" || !choice) {
      // All items
    } else if (choice === "2") {
      this.print(
        "\nItem types: weapon, armor, consumable, accessory, material, offhand",
      );
      const itemType = (await this.ask("Enter type: ")).trim().toLowerCase();
      filteredItems = this.marketApi.filterItems({ itemType: itemType });
    } else if (choice === "3") {
      this.print(`\n${this.lang.get("rarities_list")}`);
      const rarity = (await this.ask("Enter rarity: ")).trim().toLowerCase();
      filteredItems = this.marketApi.filterItems({ rarity: rarity });
    } else if (choice === "4") {
      this.print(`\n${this.lang.get("classes_list")}`);
      const classReq = (await this.ask("Enter class: ")).trim();
      filteredItems = this.marketApi.filterItems({ classReq: classReq });
    } else if (choice === "5") {
      try {
        const maxPrice = parseInt((await this.ask("Enter max price: ")).trim());
        filteredItems = this.marketApi.filterItems({ maxPrice: maxPrice });
      } catch {
        // Keep filtered items on error
        this.print(this.lang.get("invalid_price_showing_all"));
      }
    } else if (choice === "R") {
      // Force refresh
      await this.marketApi.fetchMarketData({ forceRefresh: true });
      filteredItems = this.marketApi.getAllItems();
    }

    if (!filteredItems || filteredItems.length === 0) {
      this.print(this.lang.get("no_items_match_filters"));
      return;
    }

    // Sort by market price by default
    filteredItems.sort((a, b) => (a.marketPrice || 0) - (b.marketPrice || 0));

    // Paginate and display items
    const pageSize = 8;
    let currentPage = 0;

    while (true) {
      const start = currentPage * pageSize;
      const end = start + pageSize;
      const pageItems = filteredItems.slice(start, end);

      if (!pageItems || pageItems.length === 0) {
        this.print(this.lang.get("no_more_items"));
        break;
      }

      this.print(
        `\n--- Page ${currentPage + 1} of ${Math.ceil(filteredItems.length / pageSize)} ---`,
      );

      for (let i = 0; i < pageItems.length; i++) {
        const item = pageItems[i];
        const name = item.name || "Unknown";
        const itemType = item.type || "unknown";
        const rarity = item.rarity || "common";
        const originalPrice = item.originalPrice || 0;
        const marketPrice = item.marketPrice || 0;
        const desc = (item.description || "").substring(0, 60);
        const reqs = item.requirements;
        const classReq = reqs ? reqs.class : null;
        const levelReq = reqs ? reqs.level : 1;

        // Color by rarity
        const rarityColor = getRarityColor(rarity);
        const priceColor =
          marketPrice <= (this.player?.gold || 0) ? Colors.GREEN : Colors.RED;

        this.print(
          `\n${i + 1}. ${rarityColor}${name}${Colors.END} (${itemType})`,
        );
        this.print(`   ${Colors.DARK_GRAY}${desc}${Colors.END}`);
        this.print(
          `   ${rarityColor}${rarity.charAt(0).toUpperCase() + rarity.slice(1)}${Colors.END} | Level ${levelReq}` +
            (classReq ? ` | ${Colors.CYAN}${classReq}${Colors.END}` : ""),
        );
        this.print(
          `   ${priceColor}${marketPrice}${Colors.END} gold (was ${originalPrice})`,
        );
      }

      this.print(this.lang.get("options_3"));
      this.print(`1-${pageItems.length}. Buy Item`);
      if (filteredItems.length > pageSize) {
        this.print(`N. ${this.lang.get("ui_next_page")}`);
        this.print(`P. ${this.lang.get("ui_previous_page")}`);
      }
      this.print(`F. ${this.lang.get("ui_filter_items")}`);
      this.print(`Enter. ${this.lang.get("ui_return_to_main_menu")}`);

      const actionChoice = (await this.ask("\nChoose action: "))
        .trim()
        .toUpperCase();

      if (!actionChoice) {
        break;
      } else if (actionChoice === "N" && filteredItems.length > pageSize) {
        if (end < filteredItems.length) {
          currentPage += 1;
        }
      } else if (actionChoice === "P" && filteredItems.length > pageSize) {
        if (currentPage > 0) {
          currentPage -= 1;
        }
      } else if (actionChoice === "F") {
        // Apply filter
        this.print(`\n${this.lang.get("ui_refine_search")}`);
        this.print(this.lang.get("filter_by_type"));
        this.print(this.lang.get("filter_by_rarity"));
        this.print(this.lang.get("filter_by_class"));
        this.print(this.lang.get("filter_by_max_price"));
        const subChoice = (await this.ask("Choose filter: ")).trim();
        if (subChoice === "1") {
          const itemType = (await this.ask("Enter type: "))
            .trim()
            .toLowerCase();
          filteredItems = filteredItems.filter(
            (it) => (it.type || "").toLowerCase() === itemType,
          );
        } else if (subChoice === "2") {
          const rarity = (await this.ask("Enter rarity: "))
            .trim()
            .toLowerCase();
          filteredItems = filteredItems.filter(
            (it) => (it.rarity || "").toLowerCase() === rarity,
          );
        } else if (subChoice === "3") {
          const classReq = (await this.ask("Enter class: ")).trim();
          filteredItems = filteredItems.filter(
            (it) =>
              ((it.requirements || {}).class || "").toLowerCase() ===
              classReq.toLowerCase(),
          );
        } else if (subChoice === "4") {
          try {
            const maxPrice = parseInt(
              (await this.ask("Enter max price: ")).trim(),
            );
            filteredItems = filteredItems.filter(
              (it) => (it.marketPrice || 0) <= maxPrice,
            );
          } catch {
            // Keep filtered items on error
          }
        }
        currentPage = 0;
      } else if (!isNaN(actionChoice)) {
        const itemIdx = parseInt(actionChoice) - 1;
        if (itemIdx >= 0 && itemIdx < pageItems.length) {
          const item = pageItems[itemIdx];
          const name = item.name || "";
          const marketPrice = item.marketPrice || 0;

          if (this.player.gold >= marketPrice) {
            this.player.gold -= marketPrice;
            this.player.inventory.push(name);
            this.print(
              `\n${Colors.GREEN}Purchased ${name} for ${marketPrice} gold!${Colors.END}`,
            );
            this.updateMissionProgress("collect", name);
          } else {
            this.print(
              `\n${Colors.RED}Not enough gold! Need ${marketPrice}, have ${this.player.gold}.${Colors.END}`,
            );
          }
        } else {
          this.print(this.lang.get("invalid_selection"));
        }
      }
    }
  }

  /**
   * Manage hired companions
   */
  async manageCompanions() {
    if (!this.player) {
      this.print(this.lang.get("no_character"));
      return;
    }

    while (true) {
      this.print(this.lang.get("companions"));
      this.print(
        `Active companions: ${(this.player.companions || []).length}/4`,
      );

      if (!this.player.companions || this.player.companions.length === 0) {
        this.print(
          "You have no companions yet. Visit the tavern to hire some!",
        );
        return;
      }

      // Display active companions
      for (let i = 0; i < this.player.companions.length; i++) {
        const companion = this.player.companions[i];
        let compName, compLevel;
        if (typeof companion === "object") {
          compName = companion.name;
          compLevel = companion.level || 1;
        } else {
          compName = companion;
          compLevel = 1;
        }

        // Find companion data to show bonuses
        let compData = null;
        for (const [, cdata] of Object.entries(this.companionsData)) {
          if (cdata.name === compName) {
            compData = cdata;
            break;
          }
        }

        this.print(
          `\n${i + 1}. ${Colors.CYAN}${compName}${Colors.END} (Level ${compLevel})`,
        );
        if (compData) {
          const bonuses = [];
          if (compData.attack_bonus)
            bonuses.push(`+${compData.attack_bonus} ATK`);
          if (compData.defense_bonus)
            bonuses.push(`+${compData.defense_bonus} DEF`);
          if (compData.speed_bonus)
            bonuses.push(`+${compData.speed_bonus} SPD`);
          if (compData.healing_bonus)
            bonuses.push(`+${compData.healing_bonus} Healing`);
          if (compData.mp_bonus) bonuses.push(`+${compData.mp_bonus} MP`);

          if (bonuses.length > 0) {
            this.print(`   Bonuses: ${bonuses.join(", ")}`);
          }
          this.print(`   ${compData.description || ""}`);
        }
      }

      this.print(`\n${this.lang.get("ui_options")}`);
      this.print(this.lang.get("ui_dismiss_companion"));
      this.print(this.lang.get("ui_equip_companion"));
      this.print(this.lang.get("ui_enter_return"));

      const choice = (await this.ask("Choose action: ")).trim().toLowerCase();

      if (!choice) {
        break;
      } else if (choice === "d") {
        // Dismiss companion
        if (this.player.companions && this.player.companions.length > 0) {
          try {
            const idx =
              parseInt(
                await this.ask(
                  `Dismiss which companion (1-${this.player.companions.length})? `,
                ),
              ) - 1;
            if (idx >= 0 && idx < this.player.companions.length) {
              const dismissed = this.player.companions.splice(idx, 1)[0];
              if (typeof dismissed === "object") {
                this.print(
                  `${Colors.RED}Dismissed ${dismissed.get("name")}.${Colors.END}`,
                );
              } else {
                this.print(`${Colors.RED}Dismissed ${dismissed}.${Colors.END}`);
              }
              // Recalculate stats after dismissal
              this.player.updateStatsFromEquipment(
                this.itemsData,
                this.companionsData,
              );
            } else {
              this.print(this.lang.get("invalid_selection"));
            }
          } catch {
            this.print(this.lang.get("invalid_input"));
          }
        }
      } else if (choice === "e") {
        // Equip item on companion
        this.print(this.lang.get("ui_companion_equip_soon"));
        // TODO: Implement companion equipment
      } else {
        this.print(this.lang.get("invalid_choice"));
      }
    }
  }

  /**
   * Travel to connected areas from the current area
   */
  async travel() {
    if (!this.player) {
      this.print(this.lang.get("no_character"));
      return;
    }

    const current = this.currentArea;
    const areaData = this.areasData[current] || {};
    const connections = areaData.connections || [];

    this.print(this.lang.get("travel"));
    this.print(`Current location: ${areaData.name || current}`);
    if (!connections || connections.length === 0) {
      this.print(this.lang.get("no_connected_areas"));
      return;
    }

    this.print(this.lang.get("ui_connected_areas"));
    for (let i = 0; i < connections.length; i++) {
      const aid = connections[i];
      const a = this.areasData[aid] || {};
      this.print(`${i + 1}. ${a.name || aid} - ${a.description || ""}`);
    }

    const choice = await this.ask(
      `Travel to (1-${connections.length}) or press Enter to cancel: `,
    );
    if (choice && !isNaN(choice)) {
      const idx = parseInt(choice) - 1;
      if (idx >= 0 && idx < connections.length) {
        const newArea = connections[idx];
        this.currentArea = newArea;
        this.player.currentArea = newArea;
        if (this.player.updateWeather) {
          this.player.updateWeather(newArea);
        }
        const newAreaData = this.areasData[newArea] || {};
        this.print(`Traveling to ${newAreaData.name || newArea}...`);

        // Check for area cutscene
        const cutsceneId = newAreaData.first_time_enter_cutscene;
        if (cutsceneId && this.cutscenesData[cutsceneId]) {
          const cutscene = this.cutscenesData[cutsceneId];
          const isIterable = cutscene.iterable || false;
          if (isIterable || !this.visitedAreas.has(newArea)) {
            await this.playCutscene(cutsceneId);
            if (!isIterable) {
              this.visitedAreas.add(newArea);
            }
          }
        }

        // Small chance encounter on travel
        if (Math.random() < 0.3) {
          await this.randomEncounter();
        }
      }
    }
  }

  /**
   * Rest in a safe area to recover HP and MP for gold
   */
  async rest() {
    if (!this.player) {
      this.print(this.lang.get("no_character"));
      return;
    }

    const areaData = this.areasData[this.currentArea] || {};
    const areaName = areaData.name || "Unknown Area";
    const canRest = areaData.can_rest || false;
    const restCost = areaData.rest_cost || 0;

    if (!canRest) {
      this.print(
        `\n${Colors.RED}You cannot rest in ${areaName}. It's too dangerous!${Colors.END}`,
      );
      return;
    }

    this.print(
      `\n${Colors.CYAN}=== REST IN ${areaName.toUpperCase()} ===${Colors.END}`,
    );
    this.print(`Rest Cost: ${Colors.GOLD}${restCost} gold${Colors.END}`);
    this.print(
      `Current HP: ${Colors.RED}${this.player.hp}/${this.player.maxHp}${Colors.END}`,
    );
    this.print(
      `Current MP: ${Colors.BLUE}${this.player.mp}/${this.player.maxMp}${Colors.END}`,
    );

    if (this.player.gold < restCost) {
      this.print(
        `\n${Colors.RED}You don't have enough gold to rest! Need ${restCost}, have ${this.player.gold}.${Colors.END}`,
      );
      return;
    }

    const choice = await this.ask(`Rest for ${restCost} gold? (y/n): `);
    if (choice.toLowerCase() !== "y") {
      this.print(this.lang.get("decide_not_rest"));
      return;
    }

    // Deduct gold and restore HP/MP
    this.player.gold -= restCost;
    const oldHp = this.player.hp;
    const oldMp = this.player.mp;
    this.player.hp = this.player.maxHp;
    this.player.mp = this.player.maxMp;

    this.print(
      `\n${Colors.GREEN}You rest and recover your strength...${Colors.END}`,
    );
    this.print(
      `HP restored: ${oldHp} → ${Colors.GREEN}${this.player.hp}${Colors.END}`,
    );
    this.print(
      `MP restored: ${oldMp} → ${Colors.GREEN}${this.player.mp}${Colors.END}`,
    );
    this.print(
      `Gold remaining: ${Colors.GOLD}${this.player.gold}${Colors.END}`,
    );
  }

  /**
   * Menu for buying and managing pets
   */
  async petShop() {
    if (!this.player) {
      this.print(this.lang.get("no_character"));
      return;
    }

    if (!this.player.petsOwned) this.player.petsOwned = [];
    if (!this.player.activePet) this.player.activePet = null;
    if (!this.player.petsData) this.player.petsData = this.petsData || {};

    while (true) {
      if (this.clear) this.clear();
      if (!this.player) break;
      this.print(
        createSectionHeader(this.lang.get("pet_shop_header", "PET SHOP")),
      );
      this.print(
        `${this.lang.get("your_gold", "Your Gold")}: ${Colors.GOLD}${this.player.gold}g${Colors.END}`,
      );

      // Using localized pet names if possible, else fallback
      let activePetName = "None";
      if (this.player.activePet) {
        activePetName =
          (this.player.petsData[this.player.activePet] || {}).name ||
          this.player.activePet;
      }

      this.print(
        `Current Pet: ${Colors.MAGENTA}${activePetName}${Colors.END}\n`,
      );

      this.print(`${Colors.CYAN}1.${Colors.END} Buy Pet`);
      this.print(`${Colors.CYAN}2.${Colors.END} Manage Pets`);
      this.print(`${Colors.CYAN}3.${Colors.END} Back`);

      const choice = await this.ask("Select an option: ");

      if (choice === "1") {
        this.print("\nAvailable Pets:");
        const available = [];
        for (const [petId, pet] of Object.entries(this.player.petsData)) {
          if (!(this.player.petsOwned || []).includes(petId)) {
            this.print(`- ${pet.name} (${pet.price}g): ${pet.description}`);
            available.push(petId);
          }
        }

        if (available.length === 0) {
          this.print("You already own all available pets!");
          await this.ask("Press Enter to continue...");
          continue;
        }

        const petInput = (
          await this.ask("\nEnter pet name to buy or press Enter to cancel: ")
        )
          .toLowerCase()
          .trim()
          .replace(/ /g, "_");
        if (!petInput) continue;

        if (
          this.player.petsData[petInput] &&
          !(this.player.petsOwned || []).includes(petInput)
        ) {
          const price = this.player.petsData[petInput].price;
          if (this.player.gold >= price) {
            this.player.gold -= price;
            if (!this.player.petsOwned) this.player.petsOwned = [];
            this.player.petsOwned.push(petInput);
            this.print(`You bought a ${this.player.petsData[petInput].name}!`);
          } else {
            this.print("Not enough gold!");
          }
        } else {
          this.print("Invalid pet or already owned.");
        }
        await this.ask("Press Enter to continue...");
      } else if (choice === "2") {
        if (!this.player.petsOwned || this.player.petsOwned.length === 0) {
          this.print("You don't own any pets yet.");
          await this.ask("Press Enter to continue...");
          continue;
        }

        this.print("\nYour Pets:");
        for (let i = 0; i < this.player.petsOwned.length; i++) {
          const petId = this.player.petsOwned[i];
          const petName = (this.player.petsData[petId] || {}).name || petId;
          const status = petId === this.player.activePet ? "(Active)" : "";
          this.print(`${i + 1}. ${petName} ${status}`);
        }

        const sel = await this.ask(
          `Select pet to activate (1-${this.player.petsOwned.length}) or press Enter: `,
        );
        if (sel && !isNaN(sel)) {
          const idx = parseInt(sel) - 1;
          if (idx >= 0 && idx < this.player.petsOwned.length) {
            this.player.activePet = this.player.petsOwned[idx];
            this.print(
              `${this.player.petsData[this.player.activePet].name} is now active!`,
            );
            await this.ask("Press Enter to continue...");
          }
        }
      } else if (choice === "3") {
        break;
      }
    }
  }

  /**
   * Save the game
   */
  async saveGame(filenamePrefix = "") {
    if (this.saveLoadSystem) {
      await this.saveLoadSystem.save_game(filenamePrefix);
    } else {
      this.print("Save system not initialized");
    }
  }

  /**
   * Load the game
   */
  async loadGame() {
    if (this.saveLoadSystem) {
      await this.saveLoadSystem.load_game();
    } else {
      this.print("Save system not initialized");
    }
  }

  /**
   * Gather materials based on current area's difficulty and theme
   */
  async gatherMaterials() {
    if (!this.player) return;

    const areaData = this.areasData[this.currentArea] || {};
    const difficulty = areaData.difficulty || 1;

    // Define material pools by difficulty tier
    // Tier 1: Basic materials (difficulty 1-2)
    const tier1Materials = [
      "Herb",
      "Spring Water",
      "Leather",
      "Leather Strip",
      "Hardwood",
      "Stone Block",
      "Coal",
      "Iron Ore",
      "Goblin Ear",
      "Wolf Fang",
      "Bone Fragment",
    ];

    // Tier 2: Uncommon materials (difficulty 3)
    const tier2Materials = [
      "Mana Herb",
      "Gold Nugget",
      "Steel Ingot",
      "Orc Tooth",
      "Serpent Tail",
      "Crystal Shard",
      "Venom Sac",
      "Swamp Scale",
      "Ancient Relic",
      "Wind Elemental Essence",
      "Demon Blood",
    ];

    // Tier 3: Rare materials (difficulty 4)
    const tier3Materials = [
      "Dark Crystal",
      "Ice Crystal",
      "Void Crystal",
      "Shadow Essence",
      "Fire Essence",
      "Ice Essence",
      "Starlight Shard",
      "Eternal Essence",
      "Poison Crystal",
      "Lightning Crystal",
    ];

    // Tier 4: Legendary materials (difficulty 5-6)
    const tier4Materials = [
      "Dragon Scale",
      "Dragon Bone",
      "Phoenix Feather",
      "Fire Gem",
      "Soul Fragment",
      "Demon Heart",
      "Golem Core",
      "Storm Elemental Core",
      "Zephyr's Scale",
      "Wind Dragon's Heart",
      "Eternal Feather",
      "Dragon Heart",
      "Void Heart",
    ];

    // Select materials based on difficulty
    let availableMaterials;
    if (difficulty <= 2) {
      availableMaterials = [...tier1Materials];
      if (Math.random() < 0.3) availableMaterials.push(...tier2Materials);
    } else if (difficulty === 3) {
      availableMaterials = [...tier1Materials, ...tier2Materials];
      if (Math.random() < 0.4) availableMaterials.push(...tier3Materials);
    } else if (difficulty === 4) {
      availableMaterials = [...tier2Materials, ...tier3Materials];
      if (Math.random() < 0.3) availableMaterials.push(...tier4Materials);
    } else {
      availableMaterials = [...tier3Materials, ...tier4Materials];
      if (Math.random() < 0.2) availableMaterials.push(...tier2Materials);
    }

    // Filter to only materials that actually exist in itemsData
    const validMaterials = availableMaterials.filter((m) => this.itemsData[m]);

    if (validMaterials.length === 0) return;

    // Gather 1-3 random materials
    const numMaterials = Math.floor(Math.random() * 3) + 1;
    const gathered = {};

    for (let i = 0; i < numMaterials; i++) {
      const material =
        validMaterials[Math.floor(Math.random() * validMaterials.length)];
      const quantity = Math.floor(Math.random() * 3) + 1;
      gathered[material] = (gathered[material] || 0) + quantity;
    }

    // Add gathered materials to inventory
    const foundText = [];
    for (const [material, qty] of Object.entries(gathered)) {
      for (let i = 0; i < qty; i++) {
        this.player.inventory.push(material);
      }

      // Get material info for display
      const itemData = this.itemsData[material] || {};
      const rarity = itemData.rarity || "common";
      const color = getRarityColor(rarity);
      foundText.push(`${color}${qty}x ${material}${Colors.END}`);
    }

    // Display gathered materials
    this.print(this.lang.get("you_found_materials"));
    for (const text of foundText) {
      this.print(`  - ${text}`);
    }

    // Update mission progress for collected materials
    for (const material of Object.keys(gathered)) {
      this.updateMissionProgress("collect", material);
    }
  }

  /**
   * Quit the game
   */
  async quitGame() {
    this.print(`\n${this.lang.get("ui_have_you_saved")}`);
    const response = (await this.ask(">>> ")).trim().toLowerCase();
    if (response === "no") {
      if (this.clear) this.clear();
      this.print(this.lang.get("ui_saving_progress"));
      await this.saveGame();
      this.print(this.lang.get("ui_progress_saved"));
    }
    this.print(this.lang.get("ui_thank_you_playing"));
    this.print(this.lang.get("ui_legacy_remembered"));
    // In browser, we would handle this differently
    if (typeof window !== "undefined") {
      // Browser game end
    }
  }

  /**
   * Run the main game loop
   */
  async run() {
    const choice = await this.displayWelcome();

    if (choice === "new_game") {
      this.createCharacter();
    } else if (choice === "load_game") {
      await this.loadGame();
      if (!this.player) {
        this.print(this.lang.get("ui_no_game_loaded"));
        this.createCharacter();
      }
    }

    // Ensure player has reference to data and up-to-date stats
    if (this.player) {
      this.player.weatherData = this.weatherData || {};
      this.player.timesData = this.timesData || {};
      this.player.updateStatsFromEquipment(this.itemsData, this.companionsData);
    }

    // Main game loop
    while (true) {
      await this.mainMenu();
    }
  }
}

/**
 * Initialize and start the game (for browser)
 */
export async function initGame(gameInstance) {
  const game = new Game(gameInstance);

  // Set up game reference for I/O
  game.game = gameInstance;

  // Load game data
  await game.loadGameData();
  game.loadConfig();

  // Run the game
  await game.run();

  return game;
}

export async function main() {
  const game = new Game();
  await game.loadGameData();
  game.loadConfig();
  await game.run();
}
