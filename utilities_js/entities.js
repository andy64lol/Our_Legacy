/**
 * Entities module for Our Legacy (Browser Version)
 * Enemy and Boss classes for battle system
 * Ported from utilities/entities.py
 */

/**
 * Enemy class for battle system
 * Ported from utilities/entities.py
 */
export class Enemy {
  /**
   * @param {Object} enemyData - Enemy data object
   */
  constructor(enemyData) {
    this.name = enemyData.name || "Unknown Enemy";
    this.maxHp = enemyData.hp || 50;
    this.hp = this.maxHp;
    this.attack = enemyData.attack || 5;
    this.defense = enemyData.defense || 2;
    this.speed = enemyData.speed || 5;
    this.experienceReward = enemyData.experience_reward || enemyData.exp_reward || 20;
    this.goldReward = enemyData.gold_reward || 10;
    this.lootTable = enemyData.loot_table || enemyData.drops || [];
    
    // Flag to identify regular enemies (not bosses)
    this.isBoss = false;
  }

  /**
   * Check if enemy is alive
   * @returns {boolean} True if hp > 0
   */
  isAlive() {
    return this.hp > 0;
  }

  /**
   * Apply damage to enemy
   * @param {number} damage - Damage amount
   * @returns {number} Actual damage taken
   */
  takeDamage(damage) {
    const damageTaken = Math.max(1, damage - this.defense);
    this.hp = Math.max(0, this.hp - damageTaken);
    return damageTaken;
  }
}

/**
 * Boss class with additional logic
 * Extends Enemy class
 * Ported from utilities/entities.py
 */
export class Boss extends Enemy {
  /**
   * @param {Object} bossData - Boss data object
   * @param {Object} dialoguesData - Dialogues data object
   */
  constructor(bossData, dialoguesData = {}) {
    super(bossData);
    
    // Override isBoss flag
    this.isBoss = true;
    
    // Boss-specific properties
    this.dialogue = (dialoguesData && dialoguesData[bossData.id]) || bossData.dialogue || {};
    this.lootTable = bossData.loot_table || bossData.drops || [];
    this.description = bossData.description || "A powerful foe.";
    this.experienceReward = bossData.experience_reward || bossData.exp_reward || 100;
    
    // Additional boss properties for enhanced battle system
    this.specialAbilities = bossData.special_abilities || bossData.abilities || [];
    this.cooldowns = {};
    this.phases = bossData.phases || [];
    this.currentPhaseIndex = bossData.current_phase_index || 0;
    this.maxMp = bossData.max_mp || bossData.mp || 100;
    this.mp = this.maxMp;
    
    // Initialize cooldowns for special abilities
    if (this.specialAbilities) {
      for (const ability of this.specialAbilities) {
        if (ability.name) {
          this.cooldowns[ability.name] = 0;
        }
      }
    }
  }

  /**
   * Get dialogue by key
   * @param {string} key - Dialogue key (e.g., 'intro', 'defeat', 'victory')
   * @returns {string|null} Dialogue text or null if not found
   */
  getDialogue(key) {
    return this.dialogues[key] || null;
  }

  /**
   * Get all available dialogues
   * @returns {Object} All dialogues for this boss
   */
  getAllDialogues() {
    return { ...this.dialogues };
  }

  /**
   * Check if boss has dialogue for a specific key
   * @param {string} key - Dialogue key
   * @returns {boolean} True if dialogue exists
   */
  hasDialogue(key) {
    return key in this.dialogues;
  }

  /**
   * Get current phase data
   * @returns {Object|null} Current phase data or null
   */
  getCurrentPhase() {
    if (this.phases && this.currentPhaseIndex >= 0 && this.currentPhaseIndex < this.phases.length) {
      return this.phases[this.currentPhaseIndex];
    }
    return null;
  }

  /**
   * Advance to next phase
   * @returns {boolean} True if advanced to new phase
   */
  advancePhase() {
    if (this.currentPhaseIndex < this.phases.length - 1) {
      this.currentPhaseIndex++;
      return true;
    }
    return false;
  }

  /**
   * Get available special abilities (not on cooldown, enough MP)
   * @returns {Array} Array of available abilities
   */
  getAvailableAbilities() {
    return this.specialAbilities.filter(ability => {
      const cooldown = this.cooldowns[ability.name] || 0;
      const mpCost = ability.mp_cost || 0;
      return cooldown === 0 && this.mp >= mpCost;
    });
  }

  /**
   * Use a special ability
   * @param {string} abilityName - Name of the ability to use
   * @returns {Object|null} Ability data if used, null if not available
   */
  useAbility(abilityName) {
    const ability = this.specialAbilities.find(a => a.name === abilityName);
    if (!ability) return null;
    
    const cooldown = this.cooldowns[abilityName] || 0;
    const mpCost = ability.mp_cost || 0;
    
    if (cooldown > 0 || this.mp < mpCost) {
      return null;
    }
    
    // Deduct MP and set cooldown
    this.mp -= mpCost;
    this.cooldowns[abilityName] = ability.cooldown || 0;
    
    return ability;
  }

  /**
   * Tick cooldowns at the end of turn
   */
  tickCooldowns() {
    for (const abilityName in this.cooldowns) {
      if (this.cooldowns[abilityName] > 0) {
        this.cooldowns[abilityName]--;
      }
    }
  }

  /**
   * Regenerate MP
   * @param {number} amount - Amount to regenerate
   */
  regenerateMp(amount) {
    this.mp = Math.min(this.maxMp, this.mp + amount);
  }

  /**
   * Get boss info summary
   * @returns {Object} Boss information
   */
  getInfo() {
    return {
      name: this.name,
      description: this.description,
      hp: this.hp,
      maxHp: this.maxHp,
      mp: this.mp,
      maxMp: this.maxMp,
      attack: this.attack,
      defense: this.defense,
      speed: this.speed,
      phase: this.currentPhaseIndex + 1,
      totalPhases: this.phases.length,
      isBoss: true
    };
  }
}
