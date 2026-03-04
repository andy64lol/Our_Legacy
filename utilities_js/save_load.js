// save_load.js
// Save/Load system for browser, ported from save_load.py
// Progressing through decentralisation...
// Andy64lol

import { Colors } from './settings.js';
import { Character } from './character.js';

/**
 * SaveLoadSystem class for handling game saves in browser
 * Ported from utilities/save_load.py
 */
export class SaveLoadSystem {
  /**
   * @param {Object} gameInstance - The game instance with player, lang, data references
   */
  constructor(gameInstance) {
    this.game = gameInstance;
    this.player = gameInstance.player;
    this.lang = gameInstance.lang;
    this.itemsData = gameInstance.itemsData;
    this.classesData = gameInstance.classesData;
    this.companionsData = gameInstance.companionsData;
    this.missionsData = gameInstance.missionsData;
    this.storageKey = "game_saves";
  }

  /**
   * Save the game with an optional filename prefix
   * @param {string} filenamePrefix - Optional prefix for the save name
   * @returns {boolean} True if save was successful
   */
  save_game(filenamePrefix = "") {
    if (!this.game.player) {
      this.game.print(this.lang.get('no_character_save'));
      return false;
    }

    const p = this.game.player;
    const saveData = {
      player: {
        name: p.name,
        uuid: p.uuid,
        characterClass: p.characterClass,
        level: p.level,
        experience: p.experience,
        experienceToNext: p.experienceToNext,
        maxHp: p.maxHp,
        hp: p.hp,
        maxMp: p.maxMp,
        mp: p.mp,
        attack: p.attack,
        defense: p.defense,
        speed: p.speed,
        inventory: p.inventory,
        gold: p.gold,
        equipment: p.equipment,
        companions: p.companions,
        baseStats: {
          baseMaxHp: p.baseMaxHp,
          baseMaxMp: p.baseMaxMp,
          baseAttack: p.baseAttack,
          baseDefense: p.baseDefense,
          baseSpeed: p.baseSpeed
        },
        classData: p.classData,
        rank: p.rank,
        activeBuffs: p.activeBuffs,
        housingOwned: p.housingOwned || [],
        comfortPoints: p.comfortPoints || 0,
        buildingSlots: p.buildingSlots || {},
        farmPlots: p.farmPlots || {},
        hour: p.hour || 8,
        day: p.day || 1,
        currentWeather: p.currentWeather || "sunny",
        activePet: p.activePet || null,
        petsOwned: p.petsOwned || []
      },
      currentArea: this.game.currentArea,
      visitedAreas: Array.from(this.game.visitedAreas || []),
      missionProgress: this.game.missionProgress || {},
      completedMissions: this.game.completedMissions || [],
      achievements: this.game.achievements || [],
      saveVersion: "3.1",
      saveTime: new Date().toISOString(),
      bossesKilled: p.bossesKilled || {},
      hour: p.hour || 8,
      day: p.day || 1,
      currentWeather: p.currentWeather || "sunny"
    };

    const safePrefix = (filenamePrefix || "").replace(/\//g, '_');
    const overwriteByUuid = this.game.modManager?.settings?.overwriteSaveByUuid || false;

    let saves = this._getAllSaves();

    if (overwriteByUuid && !filenamePrefix) {
      // Find existing save by UUID
      const existingSaveKey = Object.keys(saves).find(key => 
        key.includes(p.uuid.substring(0, 8)) && !key.startsWith('err_save')
      );

      if (existingSaveKey) {
        saves[existingSaveKey] = saveData;
      } else {
        const timestamp = new Date().toISOString().replace(/[:.]/g, '-').substring(0, 19);
        const saveKey = `${safePrefix}${p.name}_${p.uuid.substring(0, 8)}_save_${timestamp}_${p.characterClass}_${p.level}`;
        saves[saveKey] = saveData;
      }
    } else {
      const timestamp = new Date().toISOString().replace(/[:.]/g, '-').substring(0, 19);
      const saveKey = `${safePrefix}${p.name}_${p.uuid.substring(0, 8)}_save_${timestamp}_${p.characterClass}_${p.level}`;
      saves[saveKey] = saveData;
    }

    try {
      localStorage.setItem(this.storageKey, JSON.stringify(saves));
      const saveName = Object.keys(saves).pop();
      this.game.print(this.lang.get("game_saved_success", "Game saved successfully: {filename}").replace("{filename}", saveName));
      
      // Local download
      const json = JSON.stringify(saveData, null, 2);
      const blob = new Blob([json], { type: 'application/json' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `${saveName}.json`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
      
      return true;
    } catch (e) {
      console.error("Error saving game:", e);
      return false;
    }
  }

  /**
   * Load a saved game
   * @returns {Promise<boolean>} True if load was successful
   */
  async load_game() {
    this.game.print("1. Load from Browser Storage");
    this.game.print("2. Upload Save File (.json)");
    
    const methodChoice = await this.game.ask("Choose loading method (1-2): ");
    
    if (methodChoice === "2") {
        return new Promise((resolve) => {
            const input = document.createElement('input');
            input.type = 'file';
            input.accept = '.json';
            input.onchange = (e) => {
                const file = e.target.files[0];
                if (!file) {
                    resolve(false);
                    return;
                }
                const reader = new FileReader();
                reader.onload = (e) => {
                    try {
                        const saveData = JSON.parse(e.target.result);
                        this._load_save_data_internal(saveData);
                        resolve(true);
                    } catch (err) {
                        this.game.print("Error reading save file: " + err.message);
                        resolve(false);
                    }
                };
                reader.readAsText(file);
            };
            input.click();
        });
    }

    const saves = this._getAllSaves();
    const saveKeys = Object.keys(saves);

    if (saveKeys.length === 0) {
      this.game.print(this.lang.get('no_save_files', "No save files found."));
      return false;
    }

    this.game.print(this.lang.get('available_save_files', "Available save files:"));
    saveKeys.forEach((key, i) => {
      this.game.print(`${i + 1}. ${key.replace('_save.json', '')}`);
    });

    const choice = await this.game.ask(
      this.lang.get("load_save_prompt", "Load save (1-{count}) or press Enter to cancel: ").replace("{count}", saveKeys.length)
    );

    if (choice && !isNaN(parseInt(choice))) {
      const idx = parseInt(choice) - 1;
      if (idx >= 0 && idx < saveKeys.length) {
        const saveKey = saveKeys[idx];
        const saveData = saves[saveKey];
        try {
          this._load_save_data_internal(saveData);
          return true;
        } catch (e) {
          this.game.print(this.lang.get("error_loading_save", "Error loading save file: {error}").replace("{error}", e.message));
          return false;
        }
      }
    }
    return false;
  }

  /**
   * Load save data internally
   * @param {Object} saveData - The save data to load
   * @private
   */
  _load_save_data_internal(saveData) {
    const saveVersion = saveData.saveVersion || "1.0";
    const playerData = saveData.player;

    // Create new character
    this.game.player = new Character(
      playerData.name,
      playerData.characterClass,
      this.game.classesData,
      playerData.uuid,
      this.game.lang
    );

    const p = this.game.player;
    p.level = playerData.level;
    p.experience = playerData.experience;
    p.experienceToNext = playerData.experienceToNext;
    p.maxHp = playerData.maxHp;
    p.hp = playerData.hp;
    p.maxMp = playerData.maxMp;
    p.mp = playerData.mp;
    p.attack = playerData.attack;
    p.defense = playerData.defense;
    p.speed = playerData.speed;
    p.inventory = playerData.inventory || [];
    p.gold = playerData.gold;
    p.rank = playerData.rank || p.rank;
    p.activeBuffs = playerData.activeBuffs || p.activeBuffs;
    p.companions = playerData.companions || [];
    p.housingOwned = playerData.housingOwned || [];
    p.comfortPoints = playerData.comfortPoints || 0;
    p.buildingSlots = playerData.buildingSlots || {};
    p.farmPlots = playerData.farmPlots || { farm_1: [], farm_2: [] };
    p.activePet = playerData.activePet || null;
    p.petsOwned = playerData.petsOwned || [];
    p.bossesKilled = saveData.bossesKilled || {};
    p.hour = saveData.hour || playerData.hour || 8;
    p.day = saveData.day || playerData.day || 1;
    p.currentWeather = saveData.currentWeather || playerData.currentWeather || "sunny";

    this._load_equipment_data(playerData, saveVersion);

    this.game.currentArea = saveData.currentArea;
    this.game.visitedAreas = new Set(saveData.visitedAreas || []);
    this.game.missionProgress = saveData.missionProgress || {};
    this.game.completedMissions = saveData.completedMissions || [];
    this.game.achievements = saveData.achievements || [];

    // Handle legacy mission format
    if (!this.game.missionProgress && saveData.currentMissions) {
      for (const mid of saveData.currentMissions) {
        const mission = this.missionsData[mid];
        if (mission) {
          const mtype = mission.type || 'kill';
          const tcount = mission.targetCount || 1;
          if (mtype === 'collect' && typeof tcount === 'object') {
            this.game.missionProgress[mid] = {
              currentCounts: Object.fromEntries(Object.keys(tcount).map(item => [item, 0])),
              targetCounts: tcount,
              completed: false,
              type: mtype
            };
          } else {
            this.game.missionProgress[mid] = {
              currentCount: 0,
              targetCount: tcount,
              completed: false,
              type: mtype
            };
          }
        }
      }
    }

    try {
      if (typeof p._updateRank === 'function') {
        p._updateRank();
      }
    } catch (e) {
      // Ignore rank update errors
    }

    if (typeof p.updateStatsFromEquipment === 'function') {
      p.updateStatsFromEquipment(this.game.itemsData, this.game.companionsData);
    }

    this.game.print(
      this.lang.get("game_loaded_welcome", "Game loaded successfully! Welcome back, {player_name}!").replace("{player_name}", p.name)
    );

    if (typeof p.displayStats === 'function') {
      p.displayStats((c, m, w, col) => this.game.print(create_hp_mp_bar(c, m, w, col)));
    }
  }

  /**
   * Validate and fix equipment
   * @private
   */
  _validate_and_fix_equipment() {
    const p = this.game.player;
    const invalid = [];

    for (const slot of ["weapon", "armor", "accessory"]) {
      const itemName = p.equipment?.[slot];
      if (!itemName) {
        continue;
      }

      if (!this.game.itemsData[itemName]) {
        invalid.push([slot, itemName, "Item no longer exists"]);
        p.equipment[slot] = null;
        continue;
      }

      const it = this.game.itemsData[itemName];
      if (it.type !== slot) {
        invalid.push([slot, itemName, "Item type mismatch"]);
        p.equipment[slot] = null;
        continue;
      }

      const reqs = it.requirements || {};
      const lreq = reqs.level || 0;
      const creq = reqs.class;

      if (p.level < lreq) {
        invalid.push([slot, itemName, `Level ${lreq} required`]);
        p.equipment[slot] = null;
      } else if (creq && creq !== p.characterClass) {
        invalid.push([slot, itemName, `${creq} class required`]);
        p.equipment[slot] = null;
      }
    }

    if (invalid.length > 0) {
      this.game.print(this.lang.get('invalid_items_unequipped', 'Some items were auto-unequipped:'));
      for (const [s, n, r] of invalid) {
        this.game.print(`  - ${s.charAt(0).toUpperCase() + s.slice(1)}: ${n} (${r})`);
      }
    }
  }

  /**
   * Load equipment data from save
   * @param {Object} playerData - Player data from save
   * @param {string} saveVersion - Version of the save
   * @private
   */
  _load_equipment_data(playerData, saveVersion) {
    const p = this.game.player;

    if (saveVersion >= "2.0") {
      p.equipment = playerData.equipment || {
        weapon: null,
        armor: null,
        accessory: null
      };

      const bs = playerData.baseStats || {};
      if (Object.keys(bs).length > 0) {
        p.baseMaxHp = bs.baseMaxHp || p.baseMaxHp;
        p.baseMaxMp = bs.baseMaxMp || p.baseMaxMp;
        p.baseAttack = bs.baseAttack || p.baseAttack;
        p.baseDefense = bs.baseDefense || p.baseDefense;
        p.baseSpeed = bs.baseSpeed || p.baseSpeed;
      }

      const cd = playerData.classData || {};
      if (Object.keys(cd).length > 0) {
        p.classData = cd;
        p.levelUpBonuses = cd.levelUpBonuses || {};
      }
    } else {
      this.game.print(this.lang.get('legacy_save_warning', 'Loading legacy save. Equipment may not be restored.'));

      const eq = { weapon: null, armor: null, accessory: null };
      for (const item of (playerData.inventory || [])) {
        const it = this.game.itemsData[item] || {};
        const itype = it.type;
        if (itype in eq && !eq[itype]) {
          eq[itype] = item;
        }
      }
      p.equipment = eq;
    }

    this._validate_and_fix_equipment();

    if (typeof p.updateStatsFromEquipment === 'function') {
      p.updateStatsFromEquipment(this.game.itemsData);
    }
  }

  /**
   * Get all saves from localStorage
   * @returns {Object} Object with save keys and data
   * @private
   */
  _getAllSaves() {
    try {
      const saved = localStorage.getItem(this.storageKey);
      return saved ? JSON.parse(saved) : {};
    } catch (e) {
      console.error("Error loading saves:", e);
      return {};
    }
  }

  /**
   * Delete a specific save
   * @param {string} saveKey - The key of the save to delete
   * @returns {boolean} True if deletion was successful
   */
  delete_save(saveKey) {
    const saves = this._getAllSaves();
    if (saves[saveKey]) {
      delete saves[saveKey];
      try {
        localStorage.setItem(this.storageKey, JSON.stringify(saves));
        this.game.print(`Save deleted: ${saveKey}`);
        return true;
      } catch (e) {
        console.error("Error deleting save:", e);
        return false;
      }
    }
    return false;
  }

  /**
   * Get list of all save names
   * @returns {string[]} Array of save keys
   */
  list_saves() {
    return Object.keys(this._getAllSaves());
  }

  /**
   * Export save data to JSON string (for download)
   * @param {string} saveKey - The key of the save to export
   * @returns {string|null} JSON string or null if save not found
   */
  export_save_to_json(saveKey) {
    const saves = this._getAllSaves();
    if (saves[saveKey]) {
      return JSON.stringify(saves[saveKey], null, 2);
    }
    return null;
  }

  /**
   * Import save data from JSON string
   * @param {string} saveKey - The key to save under
   * @param {string} jsonData - The JSON string to import
   * @returns {boolean} True if import was successful
   */
  import_save_from_json(saveKey, jsonData) {
    try {
      const saveData = JSON.parse(jsonData);
      const saves = this._getAllSaves();
      saves[saveKey] = saveData;
      localStorage.setItem(this.storageKey, JSON.stringify(saves));
      return true;
    } catch (e) {
      console.error("Error importing save:", e);
      return false;
    }
  }
}
