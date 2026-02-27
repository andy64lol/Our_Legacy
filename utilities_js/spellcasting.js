// spellcasting.js
// Spell casting utility for browser, separated from main game logic
// Progressing through decentralisation...
// Andy64lol

import { Dice } from './dice.js';
import { Colors } from './settings.js';

/**
 * SpellCastingSystem class for handling spell casting
 * Ported from utilities/spellcasting.py
 */
export class SpellCastingSystem {
  /**
   * @param {Object} gameInstance - The game instance with player, lang, data references
   */
  constructor(gameInstance) {
    this.game = gameInstance;
    this.player = gameInstance.player;
    this.lang = gameInstance.lang;
    this.spellsData = gameInstance.spellsData;
    this.effectsData = gameInstance.effectsData;
    this.itemsData = gameInstance.itemsData;
    this.diceUtil = new Dice();
  }

  /**
   * Get available spells for a weapon
   * @param {string} weaponName - The weapon name to check
   * @returns {Array} Array of [spellName, spellData] tuples
   */
  getAvailableSpells(weaponName) {
    if (!weaponName) {
      return [];
    }

    const available = [];
    for (const [sname, sdata] of Object.entries(this.spellsData)) {
      const allowed = sdata.allowedWeapons || sdata.allowed_weapons || [];
      if (allowed.includes(weaponName)) {
        available.push([sname, sdata]);
      }
    }
    return available;
  }

  /**
   * Check if a weapon can cast spells
   * @param {string} weaponName - The weapon name to check
   * @returns {boolean} True if weapon can cast spells
   */
  canCastSpells(weaponName) {
    if (!weaponName) return false;
    const weaponData = this.itemsData[weaponName] || {};
    return Boolean(weaponData.magicWeapon || weaponData.magic_weapon);
  }

  /**
   * Cast a spell on an enemy
   * @param {Object} enemy - The enemy to cast spell on
   * @param {string} spellName - The name of the spell to cast
   * @param {Object} spellData - The spell data
   * @returns {Object} Result of the spell cast
   */
  castSpell(enemy, spellName, spellData) {
    if (!this.player) {
      return { success: false, error: 'No player' };
    }

    const cost = spellData.mpCost || spellData.mp_cost || 0;
    
    if (this.player.mp < cost) {
      console.log(this.lang.get("not_enough_mp", "Not enough MP!"));
      return { success: false, error: 'Not enough MP' };
    }

    // Pay cost
    this.player.mp -= cost;

    const spellType = spellData.type;
    const result = { success: true, type: spellType, spellName };

    switch (spellType) {
      case 'damage':
        this._castDamageSpell(enemy, spellName, spellData, result);
        break;
      case 'heal':
        this._castHealSpell(spellName, spellData, result);
        break;
      case 'buff':
        this._castBuffSpell(spellName, spellData, result);
        break;
      case 'debuff':
        this._castDebuffSpell(enemy, spellName, spellData, result);
        break;
      default:
        console.log(`Unknown spell type: ${spellType}`);
        // Refund MP for unknown spell types
        this.player.mp += cost;
        result.success = false;
        result.error = 'Unknown spell type';
    }

    // Check for cast cutscene
    const castCutscene = spellData.castCutscene || spellData.cast_cutscene;
    if (castCutscene && this.game.cutscenesData && this.game.cutscenesData[castCutscene]) {
      if (typeof this.game.playCutscene === 'function') {
        this.game.playCutscene(castCutscene);
      }
    }

    return result;
  }

  /**
   * Cast a damage spell
   * @private
   */
  _castDamageSpell(enemy, spellName, spellData, result) {
    const power = spellData.power || 0;
    const baseDamage = power + Math.floor(this.player.getEffectiveAttack() / 2);
    
    const roll = this.diceUtil.roll_1d(20);
    
    if (roll === 1) {
      const memeKey = `roll_1_meme_${Math.floor(Math.random() * 3) + 1}`;
      console.log(this.lang.get(memeKey));
    } else if (roll === 20) {
      const memeKey = `roll_20_meme_${Math.floor(Math.random() * 3) + 1}`;
      console.log(this.lang.get(memeKey));
    } else {
      console.log(this.lang.get("roll_msg", { roll: roll }));
    }

    const damage = Math.floor(baseDamage * roll / 10);
    const actual = enemy.takeDamage(damage);
    
    console.log(`You cast ${spellName} for ${actual} damage!`);
    result.damage = actual;

    // Apply effects if any
    const effects = spellData.effects || [];
    for (const effectName of effects) {
      const effectData = this.effectsData[effectName] || {};
      const effectType = effectData.type || '';

      if (effectType === 'damage_over_time') {
        console.log(`%c${enemy.name} is afflicted with ${effectName}!%c`, Colors.RED, Colors.END);
      } else if (effectType === 'stun') {
        if (Math.random() < (effectData.chance || 0.5)) {
          console.log(`%c${enemy.name} is stunned!%c`, Colors.YELLOW, Colors.END);
        }
      } else if (effectType === 'mixed_effect') {
        if (Math.random() < (effectData.chance || 0.5)) {
          console.log(`%c${enemy.name} is frozen!%c`, Colors.CYAN, Colors.END);
        }
      }
    }
  }

  /**
   * Cast a heal spell
   * @private
   */
  _castHealSpell(spellName, spellData, result) {
    const healAmount = spellData.power || 0;
    const oldHp = this.player.hp;
    this.player.heal(healAmount);
    const healed = this.player.hp - oldHp;
    
    console.log(`You cast ${spellName} and healed ${healed} HP!`);
    result.healed = healed;

    // Apply healing effects if any
    const effects = spellData.effects || [];
    for (const effectName of effects) {
      const effectData = this.effectsData[effectName] || {};
      if (effectData.type === 'healing_over_time') {
        console.log(`%cYou are affected by regeneration!%c`, Colors.GREEN, Colors.END);
      }
    }
  }

  /**
   * Cast a buff spell
   * @private
   */
  _castBuffSpell(spellName, spellData, result) {
    const power = spellData.power || 0;
    const effects = spellData.effects || [];

    for (const effectName of effects) {
      const effectData = this.effectsData[effectName] || {};
      const effectType = effectData.type || '';

      // Collect numeric modifiers from effect_data
      const modifiers = {};
      for (const [k, v] of Object.entries(effectData)) {
        if (typeof v === 'number' && (
          k.endsWith('_bonus') || k.endsWith('Bonus') ||
          ['hp_bonus', 'mp_bonus', 'absorb_amount', 'critical_bonus'].includes(k)
        )) {
          modifiers[k] = Math.floor(v);
        }
      }

      const duration = Math.floor(effectData.duration || Math.max(3, power || 3));
      
      // Apply as temporary buff
      if (Object.keys(modifiers).length > 0) {
        this.player.applyBuff(effectName, duration, modifiers);
        const modStr = Object.entries(modifiers).map(([k, v]) => `${v} ${k}`).join(', ');
        console.log(`%cApplied buff: ${effectName} (+${modStr}) for ${duration} turns%c`, Colors.GREEN, Colors.END);
      } else {
        // Non-numeric effects still applied as a marker buff
        this.player.applyBuff(effectName, duration, {});
        if (effectType === 'damage_absorb') {
          console.log(`%cYou create a magical shield!%c`, Colors.BLUE, Colors.END);
        } else if (effectType === 'reconnaissance') {
          console.log(`%cYou can see enemy weaknesses!%c`, Colors.CYAN, Colors.END);
        }
      }
    }
    
    result.buffsApplied = effects.length;
  }

  /**
   * Cast a debuff spell
   * @private
   */
  _castDebuffSpell(enemy, spellName, spellData, result) {
    const power = spellData.power || 0;
    const effects = spellData.effects || [];

    for (const effectName of effects) {
      const effectData = this.effectsData[effectName] || {};
      const effectType = effectData.type || '';

      if (effectType === 'action_block') {
        if (Math.random() < (effectData.chance || 0.5)) {
          console.log(`%c${enemy.name} is stunned and cannot act!%c`, Colors.YELLOW, Colors.END);
        }
      } else if (effectType === 'accuracy_reduction') {
        console.log(`%c${enemy.name}'s accuracy is reduced!%c`, Colors.RED, Colors.END);
      } else if (effectType === 'speed_reduction') {
        console.log(`%c${enemy.name} is slowed!%c`, Colors.YELLOW, Colors.END);
      } else if (effectType === 'stat_reduction') {
        console.log(`%c${enemy.name}'s stats are cursed!%c`, Colors.RED, Colors.END);
      }
    }
    
    result.debuffsApplied = effects.length;
  }

  /**
   * Display spell selection menu (for CLI/browser use)
   * @param {string} weaponName - The weapon to get spells for
   * @returns {Promise<Object|null>} Selected spell or null if cancelled
   */
  async selectSpell(weaponName) {
    const available = this.getAvailableSpells(weaponName);
    
    if (available.length === 0) {
      console.log(this.lang.get("no_spells_available", "No spells available for this weapon."));
      return null;
    }

    let page = 0;
    const perPage = 10;

    while (true) {
      const totalPages = Math.max(1, Math.ceil(available.length / perPage));
      const startIdx = page * perPage;
      const endIdx = startIdx + perPage;
      const currentSpells = available.slice(startIdx, endIdx);

      console.log(`\n%c=== SPELLS (Page ${page + 1}/${totalPages}) ===%c`, Colors.BOLD, Colors.END);
      console.log(`MP: %c${this.player.mp}/${this.player.maxMp}%c\n`, Colors.BLUE, Colors.END);

      for (let i = 0; i < currentSpells.length; i++) {
        const [sname, sdata] = currentSpells[i];
        const cost = sdata.mpCost || sdata.mp_cost || 0;
        const mpColor = this.player.mp >= cost ? Colors.BLUE : Colors.RED;
        console.log(`${i + 1}. %c${sname}%c - Cost: %c${cost} MP%c`, Colors.CYAN, Colors.END, mpColor, Colors.END);
        console.log(`   ${sdata.description || ''}`);
      }

      console.log("\nOptions:");
      if (totalPages > 1) {
        if (page > 0) console.log("P. Previous Page");
        if (page < totalPages - 1) console.log("N. Next Page");
      }
      console.log(`1-${currentSpells.length}. Cast Spell`);
      console.log("B. Back");

      // In browser, this would use a prompt or UI element
      const choice = await this.game.ask("Choose an option: ");
      const upperChoice = choice.toUpperCase();

      if (upperChoice === 'B' || !choice) {
        return null;
      } else if (upperChoice === 'N' && page < totalPages - 1) {
        page++;
      } else if (upperChoice === 'P' && page > 0) {
        page--;
      } else if (!isNaN(parseInt(choice))) {
        const idx = parseInt(choice) - 1;
        if (idx >= 0 && idx < currentSpells.length) {
          const [sname, sdata] = currentSpells[idx];
          return { name: sname, data: sdata };
        } else {
          console.log(this.lang.get('invalid_selection', "Invalid selection"));
        }
      } else {
        console.log(this.lang.get("invalid_choice", "Invalid choice"));
      }
    }
  }
}

export { SpellCastingSystem };
export default SpellCastingSystem;
