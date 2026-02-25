// battle.js
// Battle system for browser, ported from battle.py
// Andy64lol

import { Dice } from './dice.js';
import { Colors } from './settings.js';
import { SpellCastingSystem } from './spellcasting.js';

/**
 * Create an HP/MP bar string for display
 * @param {number} current - Current value
 * @param {number} maximum - Maximum value
 * @param {number} width - Bar width (default 15)
 * @param {string} color - Color style (default Colors.RED)
 * @returns {string} Formatted bar string
 */
export function createHpMpBar(current, maximum, width = 15, color = Colors.RED) {
  if (maximum <= 0) {
    return "[" + " ".repeat(width) + "]";
  }
  const filledWidth = Math.floor((current / maximum) * width);
  const filled = "█".repeat(filledWidth);
  const empty = "░".repeat(width - filledWidth);
  return `[${filled}${empty}] ${current}/${maximum}`;
}

/**
 * Create a boss HP bar with special formatting
 * @param {number} current - Current HP
 * @param {number} maximum - Maximum HP
 * @param {number} width - Bar width (default 40)
 * @param {string} color - Color style (default Colors.RED)
 * @returns {string} Formatted boss HP bar
 */
export function createBossHpBar(current, maximum, width = 40, color = Colors.RED) {
  if (maximum <= 0) {
    return "[" + " ".repeat(width) + "]";
  }
  const filledWidth = Math.floor((current / maximum) * width);
  const filled = "█".repeat(filledWidth);
  const empty = "░".repeat(width - filledWidth);
  const percentage = ((current / maximum) * 100).toFixed(1);
  const bossLabel = "%cBOSS HP%c";
  const bar = `[${filled}${empty}]`;
  const percentText = `%c${percentage}%`;
  return `${bossLabel} ${bar} ${percentText} (${current}/${maximum})`;
}

/**
 * Battle system class for handling turn-based combat
 */
export class BattleSystem {
  /**
   * @param {Object} gameInstance - The game instance with player, lang, data references
   */
  constructor(gameInstance) {
    this.game = gameInstance;
    this.player = gameInstance.player;
    this.lang = gameInstance.lang;
    this.itemsData = gameInstance.itemsData;
    this.companionsData = gameInstance.companionsData;
    this.spellsData = gameInstance.spellsData;
    this.effectsData = gameInstance.effectsData;
    this.diceUtil = new Dice();
    this.spellCasting = new SpellCastingSystem(gameInstance);
  }

  /**
   * Handle turn-based battle
   * @param {Object} enemy - The enemy to battle
   * @returns {Promise<boolean>} Resolves when battle ends
   */
  async battle(enemy) {
    if (!this.player) {
      return;
    }

    console.log(this.lang.get("n_battle"));
    console.log(`VS ${enemy.name}`);

    let playerFled = false;
    const playerFirst = this.player.getEffectiveSpeed() >= enemy.speed;

    while (this.player.isAlive() && enemy.isAlive()) {
      if (playerFirst) {
        const continueBattle = await this.playerTurn(enemy);
        if (!continueBattle) {
          playerFled = true;
          break;
        }
        if (enemy.isAlive() && this.player.companions) {
          this.companionsAct(enemy);
        }
        if (enemy.isAlive()) {
          this.enemyTurn(enemy);
        }
      } else {
        this.enemyTurn(enemy);
        if (this.player.isAlive()) {
          const continueBattle = await this.playerTurn(enemy);
          if (!continueBattle) {
            playerFled = true;
            break;
          }
          if (enemy.isAlive() && this.player.companions) {
            this.companionsAct(enemy);
          }
        }
      }

      // Display current HP/MP
      const playerHpBar = createHpMpBar(this.player.hp, this.player.maxHp, 20, Colors.RED);
      const playerMpBar = createHpMpBar(this.player.mp, this.player.maxMp, 20, Colors.BLUE);

      let enemyHpBar;
      if (enemy.isBoss) {
        enemyHpBar = createBossHpBar(enemy.hp, enemy.maxHp);
      } else {
        enemyHpBar = createHpMpBar(enemy.hp, enemy.maxHp, 20, Colors.RED);
      }

      console.log(`\n%c${this.player.name}%c`, Colors.BOLD, Colors.END);
      console.log(`HP: ${playerHpBar} ${this.player.hp}/${this.player.maxHp}`);
      console.log(`MP: ${playerMpBar} ${this.player.mp}/${this.player.maxMp}`);

      console.log(`\n%c${enemy.name}%c`, Colors.BOLD, Colors.END);
      if (enemy.isBoss) {
        console.log(enemyHpBar);
      } else {
        console.log(`HP: ${enemyHpBar} ${enemy.hp}/${enemy.maxHp}`);
      }

      if (this.player.tickBuffs()) {
        this.player.updateStatsFromEquipment(this.itemsData, this.companionsData);
      }
    }

    if (playerFled) {
      console.log(this.lang.get("nyou_fled_from_the_battle", "You fled from the battle!"));
      return;
    }

    if (this.player.isAlive()) {
      console.log(`\n%c${this.lang.get('defeat_enemy_msg', 'You defeated the {enemy_name}!').replace('{enemy_name}', enemy.name)}%c`, Colors.GREEN, Colors.END);
      
      if (enemy.isBoss) {
        this.player.bossesKilled[enemy.name] = new Date().toISOString();
      }

      let expReward = enemy.experienceReward;
      let goldReward = enemy.goldReward;

      if (this.player.currentWeather === "sunny") {
        expReward = Math.floor(expReward * 1.1);
        console.log(`%c${this.lang.get('sunny_weather_bonus', 'Sunny weather bonus: +10% EXP!')}%c`, Colors.YELLOW, Colors.END);
      } else if (this.player.currentWeather === "stormy") {
        goldReward = Math.floor(goldReward * 1.2);
        console.log(`%c${this.lang.get('stormy_weather_bonus', 'Stormy weather bonus: +20% Gold (hazardous conditions)!')}%c`, Colors.CYAN, Colors.END);
      }

      console.log(this.lang.get('gain_exp_msg', 'Gained {exp_reward} experience').replace('{exp_reward}', expReward).replace('{Colors.MAGENTA}', '').replace('{Colors.END}', ''));
      console.log(this.lang.get('gain_gold_msg', 'Gained {gold_reward} gold').replace('{gold_reward}', goldReward).replace('{Colors.GOLD}', '').replace('{Colors.END}', ''));

      this.player.gainExperience(expReward);
      this.player.gold += goldReward;
      this.game.updateMissionProgress('kill', enemy.name);
      this.game.updateChallengeProgress('kill_count');

      if (enemy.lootTable && Math.random() < 0.5) {
        const loot = enemy.lootTable[Math.floor(Math.random() * enemy.lootTable.length)];
        this.player.inventory.push(loot);
        console.log(`%c${this.lang.get('loot_acquired_msg', 'Loot acquired: {loot}!').replace('{loot}', loot)}%c`, Colors.YELLOW, Colors.END);
        this.game.updateMissionProgress('collect', loot);
      }

      if (this.player.companions) {
        for (const companion of this.player.companions) {
          let compName, compId;
          if (typeof companion === 'object' && companion !== null) {
            compName = companion.name;
            compId = companion.id;
          } else {
            compName = companion;
            compId = null;
          }

          let compData = null;
          for (const [cid, cdata] of Object.entries(this.companionsData)) {
            if (cdata.name === compName || cid === compId) {
              compData = cdata;
              break;
            }
          }

          if (compData && compData.postBattleHeal) {
            const amt = parseInt(compData.postBattleHeal) || 0;
            if (amt > 0) {
              this.player.heal(amt);
              console.log(`%c${this.lang.get('companion_heal_msg', '{comp_name} restores {amt} HP after battle!').replace('{comp_name}', compData.name).replace('{amt}', amt)}%c`, Colors.GREEN, Colors.END);
            }
          }
        }
      }
    } else {
      console.log(`\n%c${this.lang.get('defeat_player_msg', 'You were defeated by the {enemy_name}...').replace('{enemy_name}', enemy.name)}%c`, Colors.RED, Colors.END);
      this.player.hp = Math.floor(this.player.maxHp / 2);
      this.player.mp = Math.floor(this.player.maxMp / 2);
      console.log(this.lang.get("respawn"));
      this.game.currentArea = "starting_village";
    }
  }

  /**
   * Player's turn in battle
   * @param {Object} enemy - The enemy being fought
   * @returns {Promise<boolean>} True to continue battle, false if fled
   */
  async playerTurn(enemy) {
    if (!this.player) {
      return true;
    }

    console.log(this.lang.get("nyour_turn"));
    console.log(`1. ${this.lang.get('attack')}`);
    console.log(`2. ${this.lang.get('use_item')}`);
    console.log(`3. ${this.lang.get('defend')}`);
    console.log(`4. ${this.lang.get('flee')}`);

    const weaponName = this.player.equipment?.weapon;
    const weaponData = weaponName ? this.itemsData[weaponName] : {};
    const canCast = Boolean(weaponData.magicWeapon);
    if (canCast) {
      console.log(`5. ${this.lang.get('cast_spell')}`);
    }

    // In browser, we need to get input asynchronously
    const choice = await this.game.ask(canCast ? "Choose action (1-5): " : "Choose action (1-4): ");

    if (choice === "1") {
      const baseDamage = this.player.getEffectiveAttack();
      const roll = this.diceUtil.roll1d(20);
      if (roll === 1) {
        console.log(this.lang.get(`roll_1_meme_${Math.floor(Math.random() * 3) + 1}`));
      } else if (roll === 20) {
        console.log(this.lang.get(`roll_20_meme_${Math.floor(Math.random() * 3) + 1}`));
      } else {
        console.log(this.lang.get("roll_msg", { roll: roll }));
      }

      const damage = Math.floor(baseDamage * roll / 10);
      const actualDamage = enemy.takeDamage(damage);
      console.log(this.lang.get("player_attack_msg", "You attack for {damage} damage!").replace("{damage}", actualDamage));
    } else if (choice === "2") {
      await this.game.useItemInBattle();
    } else if (choice === "5" && canCast) {
      const selectedSpell = await this.spellCasting.selectSpell(weaponName);
      if (selectedSpell) {
        this.spellCasting.castSpell(enemy, selectedSpell.name, selectedSpell.data);
      }
    } else if (choice === "3") {
      console.log(`%c${this.lang.get("you_defend", "You defend!")}%c`, Colors.BLUE, Colors.END);
      this.player.defending = true;
    } else if (choice === "4") {
      const fleeChance = this.player.getEffectiveSpeed() > enemy.speed ? 0.7 : 0.4;
      if (Math.random() < fleeChance) {
        console.log(this.lang.get("you_successfully_fled", "You successfully fled!"));
        return false;
      } else {
        console.log(this.lang.get("failed_to_flee", "Failed to flee!"));
        return true;
      }
    } else {
      console.log(this.lang.get("invalid_choice_turn_lost", "Invalid choice, turn lost!"));
    }

    return true;
  }

  /**
   * Perform an action for a specific companion
   * @param {Object|string} companion - Companion data or name
   * @param {Object} enemy - The enemy being fought
   */
  companionActionFor(companion, enemy) {
    if (!this.player) {
      return;
    }

    let compName, compId;
    if (typeof companion === 'object' && companion !== null) {
      compName = companion.name;
      compId = companion.id;
    } else {
      compName = companion;
      compId = null;
    }

    let compData = null;
    for (const [cid, cdata] of Object.entries(this.companionsData)) {
      if (cdata.name === compName || cid === compId) {
        compData = cdata;
        break;
      }
    }

    if (!compData) {
      return;
    }

    const abilities = compData.abilities || [];
    let usedAbility = false;

    for (const ability of abilities) {
      const chance = ability.chance;
      let triggered = false;
      if (chance === null || chance === undefined) {
        triggered = true;
      } else {
        if (typeof chance === 'number' && chance >= 0 && chance <= 1) {
          triggered = Math.random() < chance;
        } else {
          try {
            triggered = Math.floor(Math.random() * 100) + 1 <= parseInt(chance);
          } catch (e) {
            triggered = false;
          }
        }
      }

      if (!triggered) {
        continue;
      }

      usedAbility = true;
      const atype = ability.type;

      if (['attack_boost', 'rage', 'crit_boost'].includes(atype)) {
        const bonus = parseInt(ability.attackBonus || ability.critDamageBonus || 0);
        const companionDamage = Math.floor(this.player.getEffectiveAttack() * 0.6 + (compData.attackBonus || 0) + bonus);
        const actualDamage = enemy.takeDamage(companionDamage);
        console.log(`%c${this.lang.get('companion_ability_attack_msg', '{comp_name} uses {ability_name} for {damage} damage!').replace('{comp_name}', compName).replace('{ability_name}', ability.name).replace('{damage}', actualDamage)}%c`, Colors.CYAN, Colors.END);
      } else if (atype === 'taunt') {
        const dur = parseInt(ability.duration) || 1;
        const dbonus = parseInt(ability.defenseBonus || compData.defenseBonus || 0);
        this.player.applyBuff(ability.name, dur, { defenseBonus: dbonus });
        console.log(`%c${this.lang.get('companion_taunt_msg', '{comp_name} uses {ability_name} and draws enemy attention!').replace('{comp_name}', compName).replace('{ability_name}', ability.name)}%c`, Colors.BLUE, Colors.END);
      } else if (atype === 'heal') {
        const healAmt = parseInt(ability.healing || ability.heal || compData.healingBonus || 0) || 0;
        this.player.heal(healAmt);
        console.log(`%c${this.lang.get('companion_ability_heal_msg', '{comp_name} uses {ability_name} and heals you for {heal_amt} HP!').replace('{comp_name}', compName).replace('{ability_name}', ability.name).replace('{heal_amt}', healAmt)}%c`, Colors.GREEN, Colors.END);
      } else if (atype === 'mp_regen') {
        const dur = parseInt(ability.duration) || 3;
        const mpPer = parseInt(ability.mpPerTurn) || 0;
        if (mpPer > 0) {
          this.player.applyBuff(ability.name, dur, { mpPerTurn: mpPer });
          console.log(`%c${this.lang.get('companion_mp_regen_msg', '{comp_name} grants {mp_per} MP/turn for {dur} turns!').replace('{comp_name}', compName).replace('{mp_per}', mpPer).replace('{dur}', dur)}%c`, Colors.CYAN, Colors.END);
        }
      } else if (atype === 'spell_power') {
        const dur = parseInt(ability.duration) || 3;
        const sp = parseInt(ability.spellPowerBonus) || 0;
        if (sp) {
          this.player.applyBuff(ability.name, dur, { spellPowerBonus: sp });
          console.log(`%c${this.lang.get('companion_spell_power_msg', '{comp_name} increases spell power by {sp} for {dur} turns!').replace('{comp_name}', compName).replace('{sp}', sp).replace('{dur}', dur)}%c`, Colors.CYAN, Colors.END);
        }
      } else if (atype === 'party_buff') {
        const dur = parseInt(ability.duration) || 3;
        const mods = {};
        for (const k of ['attackBonus', 'defenseBonus', 'speedBonus']) {
          if (ability[k] !== undefined && ability[k] !== null) {
            mods[k] = parseInt(ability[k]);
          }
        }
        if (Object.keys(mods).length > 0) {
          this.player.applyBuff(ability.name, dur, mods);
          console.log(`%c${this.lang.get('companion_party_buff_msg', '{comp_name} uses {ability_name}, granting party buffs: {mods}!').replace('{comp_name}', compName).replace('{ability_name}', ability.name).replace('{mods}', JSON.stringify(mods))}%c`, Colors.CYAN, Colors.END);
        }
      }
      break;
    }

    if (!usedAbility) {
      const actionType = ['attack', 'defend', 'heal'][Math.floor(Math.random() * 3)];
      if (actionType === 'attack' && (compData.attackBonus || 0) > 0) {
        const companionDamage = Math.floor(this.player.getEffectiveAttack() * 0.6 + (compData.attackBonus || 0));
        const actualDamage = enemy.takeDamage(companionDamage);
        console.log(`%c${this.lang.get('companion_attack_msg', '{comp_name} attacks for {damage} damage!').replace('{comp_name}', compName).replace('{damage}', actualDamage)}%c`, Colors.CYAN, Colors.END);
      } else if (actionType === 'heal' && (compData.healingBonus || 0) > 0) {
        const healAmount = compData.healingBonus || 0;
        this.player.heal(healAmount);
        console.log(`%c${this.lang.get('companion_heal_msg_simple', '{comp_name} heals you for {heal_amount} HP!').replace('{comp_name}', compName).replace('{heal_amount}', healAmount)}%c`, Colors.GREEN, Colors.END);
      } else if (actionType === 'defend' && (compData.defenseBonus || 0) > 0) {
        console.log(`%c${this.lang.get('companion_defend_msg', '{comp_name} helps you defend, reducing incoming damage!').replace('{comp_name}', compName)}%c`, Colors.BLUE, Colors.END);
        this.player.defending = true;
      }
    }
  }

  /**
   * Each companion has a chance to act on their own each turn
   * @param {Object} enemy - The enemy being fought
   */
  companionsAct(enemy) {
    if (!this.player) {
      return;
    }
    for (const companion of [...this.player.companions]) {
      let chance = 0.5;
      if (typeof companion === 'object' && companion !== null && companion.actionChance) {
        chance = companion.actionChance || 0.5;
      }
      if (Math.random() < chance) {
        this.companionActionFor(companion, enemy);
      }
    }
  }

  /**
   * Enemy's turn in battle
   * @param {Object} enemy - The enemy taking their turn
   */
  enemyTurn(enemy) {
    if (!this.player) {
      return;
    }

    if (enemy.isBoss) {
      // Handle boss cooldowns
      for (const abil in enemy.cooldowns) {
        if (enemy.cooldowns[abil] > 0) {
          enemy.cooldowns[abil]--;
        }
      }

      let availableAbilities = enemy.specialAbilities.filter(a => 
        (enemy.cooldowns[a.name] || 0) === 0 && enemy.mp >= (a.mpCost || 0)
      );

      const currentPhase = enemy.currentPhaseIndex >= 0 ? enemy.phases[enemy.currentPhaseIndex] : {};
      const unlocked = currentPhase.specialAbilitiesUnlocked || [];
      if (unlocked.length > 0) {
        availableAbilities = availableAbilities.filter(a => unlocked.includes(a.name));
      }

      if (availableAbilities.length > 0 && Math.random() < 0.4) {
        const ability = availableAbilities[Math.floor(Math.random() * availableAbilities.length)];
        console.log(`\n%c${this.lang.get('enemy_ability_msg', '{enemy_name} uses {ability_name}!').replace('{enemy_name}', enemy.name).replace('{ability_name}', ability.name)}%c`, Colors.RED, Colors.END);
        console.log(`%c${ability.description}%c`, Colors.DARK_GRAY || 'color: #666', Colors.END);

        enemy.mp -= ability.mpCost || 0;
        enemy.cooldowns[ability.name] = ability.cooldown || 0;

        if (ability.damage) {
          let dmg = ability.damage;
          if (this.player.defending) {
            dmg = Math.floor(dmg / 2);
          }
          const actual = this.player.takeDamage(dmg);
          console.log(this.lang.get("enemy_ability_damage_msg", "It deals {damage} damage!").replace("{damage}", actual));
        }

        if (ability.stunChance && Math.random() < ability.stunChance) {
          console.log(`%c${this.lang.get('stun_msg', 'You are stunned and skip your next turn!')}%c`, Colors.YELLOW, Colors.END);
          this.player.applyBuff("Stunned", 1, { speedBonus: -999 });
        }

        if (ability.healAmount) {
          const heal = ability.healAmount;
          enemy.hp = Math.min(enemy.maxHp, enemy.hp + heal);
          console.log(this.lang.get("enemy_heal_msg", "{enemy_name} heals for {heal} HP!").replace("{enemy_name}", enemy.name).replace("{heal}", heal));
        }
        return;
      }
    }

    const baseDamage = enemy.attack;
    const roll = this.diceUtil.roll1d(Math.max(1, this.player.level));
    console.log(this.lang.get("enemy_roll_msg", "{enemy_name} rolls the dice...").replace("{enemy_name}", enemy.name));
    console.log(this.lang.get("enemy_rolled_val_msg", "{enemy_name} rolled a {roll}!").replace("{enemy_name}", enemy.name).replace("{roll}", roll));

    let damage = Math.floor(baseDamage * roll / 10);
    if (this.player.defending) {
      damage = Math.floor(damage / 2);
      this.player.defending = false;
    }

    const actualDamage = this.player.takeDamage(damage);
    console.log(this.lang.get("enemy_attack_msg", "{enemy_name} attacks for {damage} damage!").replace("{enemy_name}", enemy.name).replace("{damage}", actualDamage));

    if (this.player.companions) {
      let companionDefenseBonus = 0;
      for (const companion of this.player.companions) {
        let compName, compId;
        if (typeof companion === 'object' && companion !== null) {
          compName = companion.name;
          compId = companion.id;
        } else {
          compName = companion;
          compId = null;
        }

        for (const [cid, cdata] of Object.entries(this.companionsData)) {
          if (cdata.name === compName || cid === compId) {
            companionDefenseBonus += cdata.defenseBonus || 0;
            break;
          }
        }
      }

      if (companionDefenseBonus > 0) {
        const damageReduction = Math.floor(companionDefenseBonus * 0.5);
        this.player.heal(damageReduction);
        console.log(`%c${this.lang.get('companions_mitigate_msg', 'Companions mitigate {damage} damage!').replace('{damage}', damageReduction)}%c`, Colors.BLUE, Colors.END);
      }
    }
  }
}
