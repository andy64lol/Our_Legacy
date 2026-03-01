/**
 * Character and Stats Management for Our Legacy (Browser Version)
 * Centralized Character class and related logic
 * Ported from utilities/character.py
 */

import { Colors } from './settings.js';

/**
 * Mock language class for when no language manager is provided
 */
export class MockLangCharacterAttr {
  get(key, defaultValue = null, params = {}) {
    return key;
  }
}

/**
 * Player character class
 * Ported from utilities/character.py
 */
export class Character {
  /**
   * @param {string} name - Character name
   * @param {string} characterClass - Character class name
   * @param {Object} classesData - Classes data object
   * @param {string} playerUuid - Optional player UUID
   * @param {Object} lang - Optional language manager
   */
  constructor(name, characterClass, classesData = null, playerUuid = null, lang = null) {
    this.name = name;
    this.characterClass = characterClass;
    this.uuid = playerUuid || this._generateUUID();

    // Language manager
    this.lang = lang || new MockLangCharacterAttr();

    // Rank system based on level
    this.rank = "F tier adventurer";
    this.level = 1;
    this.experience = 0;
    this.experienceToNext = 100;
    this.classData = {};
    this.levelUpBonuses = {};

    // Load class data if provided
    if (classesData && characterClass in classesData) {
      this.classData = classesData[characterClass];
      const stats = this.classData.base_stats || {};
      this.levelUpBonuses = this.classData.level_up_bonuses || {};
      this.maxHp = stats.hp || 100;
      this.hp = this.maxHp;
      this.maxMp = stats.mp || 50;
      this.mp = this.maxMp;
      this.attack = stats.attack || 10;
      this.defense = stats.defense || 8;
      this.speed = stats.speed || 10;
    } else {
      // Fallback defaults
      this.maxHp = 100;
      this.hp = this.maxHp;
      this.maxMp = 50;
      this.mp = this.maxMp;
      this.attack = 10;
      this.defense = 8;
      this.speed = 10;
    }
    this.defending = false;

    // Equipment slots
    this.equipment = {
      weapon: null,
      armor: null,
      offhand: null,
      accessory_1: null,
      accessory_2: null,
      accessory_3: null
    };

    // Legacy compatibility slots
    this.weapon = null;
    this.armor = null;
    this.offhand = null;
    this.accessory = null;

    // Inventory and gold
    this.inventory = [];
    this.gold = 100;
    this.companions = [];
    this.activeBuffs = [];
    this.bossesKilled = {};

    // Housing and Building
    this.housingOwned = [];
    this.comfortPoints = 0;
    this.buildingSlots = {
      house_1: null,
      house_2: null,
      house_3: null,
      decoration_1: null,
      decoration_2: null,
      decoration_3: null,
      decoration_4: null,
      decoration_5: null,
      decoration_6: null,
      decoration_7: null,
      decoration_8: null,
      decoration_9: null,
      decoration_10: null,
      fencing_1: null,
      garden_1: null,
      garden_2: null,
      garden_3: null,
      farm_1: null,
      farm_2: null,
      training_place_1: null,
      training_place_2: null,
      training_place_3: null,
    };
    this.farmPlots = {
      farm_1: [],
      farm_2: [],
    };

    // Time and Weather
    this.day = 1;
    this.hour = 8.0;
    this.maxHours = 24;
    this.currentArea = "starting_village";
    this.currentWeather = "sunny";
    this.weatherData = {};
    this.timesData = {};

    // Stats tracking
    this.baseMaxHp = this.maxHp;
    this.baseMaxMp = this.maxMp;
    this.baseAttack = this.attack;
    this.baseDefense = this.defense;
    this.baseSpeed = this.speed;

    this.activePet = null;
    this.petsOwned = [];
    this.petsData = {};
    this._loadPetsData();
    this._syncEquipmentSlots();
  }

  /**
   * Generate a UUID v4
   * @returns {string} UUID string
   * @private
   */
  _generateUUID() {
    return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
      const r = Math.random() * 16 | 0;
      const v = c === 'x' ? r : (r & 0x3 | 0x8);
      return v.toString(16);
    });
  }

  /**
   * Sync legacy equipment slots for compatibility
   * @private
   */
  _syncEquipmentSlots() {
    this.weapon = this.equipment.weapon;
    this.armor = this.equipment.armor;
    this.accessory = this.equipment.accessory_1;
    this.offhand = this.equipment.offhand;
  }

  /**
   * Update legacy equipment slots when equipment dictionary changes
   * @private
   */
  _updateEquipmentSlots() {
    this.weapon = this.equipment.weapon;
    this.armor = this.equipment.armor;
    this.accessory = this.equipment.accessory_1;
    this.offhand = this.equipment.offhand;
  }

  /**
   * Load pet data from data/pets.json
   * @private
   */
  async _loadPetsData() {
    try {
      const response = await fetch('data/pets.json');
      this.petsData = await response.json();
    } catch (e) {
      this.petsData = {};
    }
  }

  /**
   * Get the current pet's boost for a given stat, scaled by land comfort.
   * @param {string} stat - Stat name (attack, defense, speed)
   * @returns {number} Boost value
   */
  getPetBoost(stat) {
    if (!this.activePet || !this.petsData[this.activePet]) {
      return 0.0;
    }

    const pet = this.petsData[this.activePet];
    const boosts = pet.boosts || {};
    const baseBoost = boosts[stat] || 0.0;
    const comfortMultiplier = 1.0 + (this.comfortPoints / 1000.0);
    return baseBoost * comfortMultiplier;
  }

  /**
   * Check if character is alive
   * @returns {boolean} True if hp > 0
   */
  isAlive() {
    return this.hp > 0;
  }

  /**
   * Apply damage to character, return actual damage taken
   * @param {number} damage - Damage amount
   * @returns {number} Actual damage taken
   */
  takeDamage(damage) {
    const baseDamage = Math.max(1, damage - this.getEffectiveDefense());
    let remaining = baseDamage;

    for (const buff of [...this.activeBuffs]) {
      const mods = buff.modifiers || {};
      if (remaining <= 0) break;
      if (mods.absorb_amount > 0) {
        const avail = mods.absorb_amount;
        const use = Math.min(avail, remaining);
        remaining -= use;
        mods.absorb_amount = avail - use;
        // Remove buff if all modifiers are 0 or non-numeric
        const allZero = Object.values(mods).every(v => 
          typeof v !== 'number' || v === 0
        );
        if (allZero) {
          const idx = this.activeBuffs.indexOf(buff);
          if (idx > -1) this.activeBuffs.splice(idx, 1);
        }
      }
    }

    const damageTaken = Math.max(0, remaining);
    this.hp = Math.max(0, this.hp - damageTaken);
    return damageTaken;
  }

  /**
   * Heal character
   * @param {number} amount - Heal amount
   */
  heal(amount) {
    this.hp = Math.min(this.maxHp, this.hp + amount);
  }

  /**
   * Gain experience and level up if needed
   * @param {number} exp - Experience amount
   */
  gainExperience(exp) {
    this.experience += exp;
    while (this.experience >= this.experienceToNext) {
      this.levelUp();
    }
  }

  /**
   * Level up the character
   */
  levelUp() {
    this.level += 1;
    this.experience -= this.experienceToNext;
    this.experienceToNext = Math.floor(this.experienceToNext * 1.5);

    if (this.levelUpBonuses) {
      this.maxHp += this.levelUpBonuses.hp || 0;
      this.maxMp += this.levelUpBonuses.mp || 0;
      this.attack += this.levelUpBonuses.attack || 0;
      this.defense += this.levelUpBonuses.defense || 0;
      this.speed += this.levelUpBonuses.speed || 0;
    }
    this.hp = this.maxHp;
    this._updateRank();
  }

  /**
   * Simple rank tiers based on level
   * @private
   */
  _updateRank() {
    if (this.level >= 100) {
      this.rank = "SSR tier adventurer";
    } else if (this.level >= 90) {
      this.rank = "SR tier adventurer";
    } else if (this.level >= 80) {
      this.rank = "SSS tier adventurer";
    } else if (this.level >= 70) {
      this.rank = "SS tier adventurer";
    } else if (this.level >= 50) {
      this.rank = "S tier adventurer";
    } else if (this.level >= 30) {
      this.rank = "A tier adventurer";
    } else if (this.level >= 20) {
      this.rank = "B tier adventurer";
    } else if (this.level >= 15) {
      this.rank = "C tier adventurer";
    } else if (this.level >= 10) {
      this.rank = "D tier adventurer";
    } else if (this.level >= 5) {
      this.rank = "E tier adventurer";
    } else {
      this.rank = "F tier adventurer";
    }
  }

  /**
   * Get current time period
   * @returns {string} Time period name
   */
  getTimePeriod() {
    if (!this.timesData) return "unknown";
    for (const [period, data] of Object.entries(this.timesData)) {
      if (data.start_hour <= this.hour && this.hour <= data.end_hour) {
        return period;
      }
    }
    return "unknown";
  }

  /**
   * Get translated time description
   * @param {Object} languageManager - Language manager instance
   * @returns {string} Translated description
   */
  getTimeDescription(languageManager) {
    const period = this.getTimePeriod();
    if (period === "unknown") {
      return "The passage of time is strange here...";
    }
    const periodData = this.timesData[period] || {};
    return languageManager.get(periodData.description || "");
  }

  /**
   * Get translated weather description
   * @param {Object} languageManager - Language manager instance
   * @returns {string} Translated description
   */
  getWeatherDescription(languageManager) {
    const weatherInfo = this.weatherData[this.currentWeather] || {};
    const descKey = weatherInfo.description || `weather_${this.currentWeather}_desc`;
    const isNight = this.hour < 6 || this.hour >= 18;
    if (isNight) {
      const nightDescKey = `${descKey}_night`;
      const nightDesc = languageManager.get(nightDescKey);
      if (nightDesc !== nightDescKey) {
        return nightDesc;
      }
    }
    return languageManager.get(descKey, this.currentWeather.charAt(0).toUpperCase() + this.currentWeather.slice(1));
  }

  /**
   * Advance game time
   * @param {number} minutes - Real minutes to advance (default 10)
   */
  advanceTime(minutes = 10.0) {
    const gameMinutes = minutes / 2.0;
    this.hour += gameMinutes / 60.0;
    while (this.hour >= 24) {
      this.hour -= 24;
      this.day += 1;
    }
  }

  /**
   * Update current weather based on area data and probabilities.
   * @param {Object} areaData - Area data with weather chances
   */
  updateWeather(areaData) {
    const weatherChances = areaData.weather_chances || { sunny: 1.0 };
    const weathers = Object.keys(weatherChances);
    const weights = Object.values(weatherChances);
    if (weathers.length > 0) {
      // Weighted random selection
      const totalWeight = weights.reduce((a, b) => a + b, 0);
      let random = Math.random() * totalWeight;
      for (let i = 0; i < weathers.length; i++) {
        random -= weights[i];
        if (random <= 0) {
          this.currentWeather = weathers[i];
          return;
        }
      }
      this.currentWeather = weathers[weathers.length - 1];
    }
  }

  /**
   * Calculate attack with all bonuses
   * @returns {number} Effective attack
   */
  getEffectiveAttack() {
    const bonus = this.activeBuffs.reduce((sum, b) => 
      sum + (b.modifiers?.attack_bonus || 0), 0
    );
    const petBoost = this.getPetBoost('attack');
    return Math.floor((this.attack + bonus) * (1.0 + petBoost));
  }

  /**
   * Calculate defense with all bonuses
   * @returns {number} Effective defense
   */
  getEffectiveDefense() {
    const bonus = this.activeBuffs.reduce((sum, b) => 
      sum + (b.modifiers?.defense_bonus || 0), 0
    );
    const petBoost = this.getPetBoost('defense');
    const baseDef = (this.defense + bonus) * (1.0 + petBoost);
    return this.defending ? Math.floor(baseDef * 1.5) : Math.floor(baseDef);
  }

  /**
   * Calculate speed with all bonuses
   * @returns {number} Effective speed
   */
  getEffectiveSpeed() {
    const bonus = this.activeBuffs.reduce((sum, b) => 
      sum + (b.modifiers?.speed_bonus || 0), 0
    );
    const petBoost = this.getPetBoost('speed');
    return Math.floor((this.speed + bonus) * (1.0 + petBoost));
  }

  /**
   * Display character stats
   * @param {Function} createHpMpBar - Optional function to create HP/MP bars
   */
  displayStats(printFunc = null) {
    const output = printFunc || ((text) => {});
    output(`\n--- ${this.name} (${this.characterClass}) ---`);
    output(`Level: ${this.level} (${this.rank})`);
    
    output(`HP: ${this.hp}/${this.maxHp}`);
    output(`MP: ${this.mp}/${this.maxMp}`);
    
    output(`EXP: ${this.experience}/${this.experienceToNext}`);
    output(`Gold: ${this.gold}`);
    output(`Attack: ${this.getEffectiveAttack()} (Base: ${this.attack})`);
    output(`Defense: ${this.getEffectiveDefense()} (Base: ${this.defense})`);
    output(`Speed: ${this.getEffectiveSpeed()} (Base: ${this.speed})`);
    
    if (this.equipment && Object.values(this.equipment).some(v => v !== null)) {
      output("\nEquipment:");
      for (const [slot, item] of Object.entries(this.equipment)) {
        if (item) {
          output(`  ${slot.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}: ${item}`);
        }
      }
    }
  }

  /**
   * Update character stats based on current equipment and companions
   * @param {Object} itemsData - Items data object
   * @param {Object} companionsData - Companions data object
   */
  updateStatsFromEquipment(itemsData, companionsData = null) {
    // Reset to base stats
    this.attack = this.baseAttack;
    this.defense = this.baseDefense;
    this.speed = this.baseSpeed;
    this.maxHp = this.baseMaxHp;
    this.maxMp = this.baseMaxMp;

    // Apply equipment bonuses
    for (const [slot, itemName] of Object.entries(this.equipment)) {
      if (itemName && itemsData[itemName]) {
        const item = itemsData[itemName];
        const stats = item.stats || {};
        this.attack += stats.attack || 0;
        this.defense += stats.defense || 0;
        this.speed += stats.speed || 0;
        this.maxHp += stats.hp || 0;
        this.maxMp += stats.mp || 0;
      }
    }

    // Apply companion bonuses
    if (companionsData && this.companions) {
      for (const companion of this.companions) {
        const compName = companion.name || companion;
        const compData = Object.values(companionsData).find(c => c.name === compName);
        if (compData) {
          this.attack += compData.attack_bonus || 0;
          this.defense += compData.defense_bonus || 0;
          this.speed += compData.speed_bonus || 0;
        }
      }
    }
  }

  /**
   * Apply a buff to the character
   * @param {string} name - Buff name
   * @param {number} duration - Duration in turns
   * @param {Object} modifiers - Stat modifiers
   */
  applyBuff(name, duration, modifiers) {
    this.activeBuffs.push({
      name: name,
      duration: duration,
      modifiers: { ...modifiers }
    });
  }

  /**
   * Equip an item from inventory
   * @param {string} itemName - Item name to equip
   * @param {Object} itemsData - Items data object
   * @returns {boolean} True if equipped successfully
   */
  equip(itemName, itemsData) {
    if (!this.inventory.includes(itemName)) {
      return false;
    }

    const item = itemsData[itemName];
    if (!item) {
      return false;
    }

    const slot = item.type;
    if (!this.equipment.hasOwnProperty(slot)) {
      return false;
    }

    // Unequip existing if any
    this.unequip(slot, itemsData);

    this.equipment[slot] = itemName;
    const idx = this.inventory.indexOf(itemName);
    if (idx > -1) this.inventory.splice(idx, 1);
    
    this._updateEquipmentSlots();
    this.updateStatsFromEquipment(itemsData);
    return true;
  }

  /**
   * Unequip an item from a slot
   * @param {string} slot - Equipment slot
   * @param {Object} itemsData - Items data object
   * @returns {boolean} True if unequipped successfully
   */
  unequip(slot, itemsData) {
    if (!this.equipment.hasOwnProperty(slot)) {
      return false;
    }

    const itemName = this.equipment[slot];
    if (!itemName) {
      return false;
    }

    this.equipment[slot] = null;
    this.inventory.push(itemName);
    this._updateEquipmentSlots();
    this.updateStatsFromEquipment(itemsData);
    return true;
  }

  /**
   * Tick active buffs, return True if any expired or changed stats
   * @returns {boolean} True if any buffs expired
   */
  tickBuffs() {
    let changed = false;
    for (let i = this.activeBuffs.length - 1; i >= 0; i--) {
      const buff = this.activeBuffs[i];
      buff.duration -= 1;
      if (buff.duration <= 0) {
        this.activeBuffs.splice(i, 1);
        changed = true;
      }
    }
    return changed;
  }
}

export default Character;