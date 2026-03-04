// battle.js
// Battle system for browser, ported from battle.py
// Andy64lol

import { Dice } from './dice.js';
import { Colors } from './settings.js';
import { SpellCastingSystem } from './spellcasting.js';

/**
 * Battle system class for handling turn-based combat
 * Ported from utilities/battle.py
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

    this.game.print(this.lang.get("n_battle"));
    this.game.print(`VS ${enemy.name}`);

    let playerFled = false;
    const playerFirst = this.player.getEffectiveSpeed() >= enemy.speed;

    while (this.player.isAlive() && enemy.isAlive()) {
      // Display current HP/MP at the start of each turn
      const playerHpBar = this.game.createHpMpBar(this.player.hp, this.player.maxHp, 20, Colors.RED);
      const playerMpBar = this.game.createHpMpBar(this.player.mp, this.player.maxMp, 20, Colors.BLUE);

      let enemyHpBar;
      if (enemy.isBoss) {
        enemyHpBar = this.game.createBossHpBar(enemy.hp, enemy.maxHp);
      } else {
        enemyHpBar = this.game.createHpMpBar(enemy.hp, enemy.maxHp, 20, Colors.RED);
      }

      this.game.print(`\n${this.player.name}`);
      this.game.print(`HP: ${playerHpBar} ${this.player.hp}/${this.player.maxHp}`);
      this.game.print(`MP: ${playerMpBar} ${this.player.mp}/${this.player.maxMp}`);

      this.game.print(`\n${enemy.name}`);
      if (enemy.isBoss) {
        this.game.print(enemyHpBar);
      } else {
        this.game.print(`HP: ${enemyHpBar} ${enemy.hp}/${enemy.maxHp}`);
      }

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

      if (this.player.tickBuffs()) {
        this.player.updateStatsFromEquipment(this.itemsData, this.companionsData);
      }
    }

    if (playerFled) {
      this.game.print(this.lang.get("nyou_fled_from_the_battle", "You fled from the battle!"));
      return;
    }

    if (this.player.isAlive()) {
      this.game.print(`\n${this.lang.get('defeat_enemy_msg', 'You defeated the {enemy_name}!').replace('{enemy_name}', enemy.name)}`);
      
      if (enemy.isBoss) {
        this.player.bossesKilled[enemy.name] = new Date().toISOString();
      }

      let expReward = enemy.experienceReward;
      let goldReward = enemy.goldReward;

      if (this.player.currentWeather === "sunny") {
        expReward = Math.floor(expReward * 1.1);
        this.game.print(this.lang.get('sunny_weather_bonus', 'Sunny weather bonus: +10% EXP!'));
      } else if (this.player.currentWeather === "stormy") {
        goldReward = Math.floor(goldReward * 1.2);
        this.game.print(this.lang.get('stormy_weather_bonus', 'Stormy weather bonus: +20% Gold (hazardous conditions)!'));
      }

      this.game.print(this.lang.get('gain_exp_msg', 'Gained {exp_reward} experience', {exp_reward: expReward}));
      this.game.print(this.lang.get('gain_gold_msg', 'Gained {gold_reward} gold', {gold_reward: goldReward}));

      this.player.gainExperience(expReward);
      this.player.gold += goldReward;
      this.game.updateMissionProgress('kill', enemy.name);
      this.game.updateChallengeProgress('kill_count');

      const lootTable = enemy.lootTable || enemy.drops || [];
      if (lootTable.length > 0 && Math.random() < 0.5) {
        const loot = lootTable[Math.floor(Math.random() * lootTable.length)];
        this.player.inventory.push(loot);
        this.game.print(this.lang.get('loot_acquired_msg', 'Loot acquired: {loot}!').replace('{loot}', loot));
        this.game.updateMissionProgress('collect', loot);
      }
    } else {
      this.game.print(`\n${this.lang.get('defeat_player_msg', 'You were defeated by the {enemy_name}...').replace('{enemy_name}', enemy.name)}`);
      this.player.hp = Math.floor(this.player.maxHp / 2);
      this.player.mp = Math.floor(this.player.maxMp / 2);
      this.game.print(this.lang.get("respawn"));
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

    this.game.print(this.lang.get("nyour_turn"));
    this.game.print(`1. ${this.lang.get('attack')}`);
    this.game.print(`2. ${this.lang.get('use_item')}`);
    this.game.print(`3. ${this.lang.get('defend')}`);
    this.game.print(`4. ${this.lang.get('flee')}`);

    const weaponName = this.player.equipment?.weapon;
    const weaponData = weaponName ? this.itemsData[weaponName] : {};
    const canCast = Boolean(weaponData.magicWeapon);
    if (canCast) {
      this.game.print(`5. ${this.lang.get('cast_spell')}`);
    }

    const choice = await this.game.ask(canCast ? "Choose action (1-5): " : "Choose action (1-4): ");

    if (choice === "1") {
      const baseDamage = this.player.getEffectiveAttack();
      const roll = this.diceUtil.roll_1d(20);
      if (roll === 1) {
        this.game.print(this.lang.get(`roll_1_meme_${Math.floor(Math.random() * 3) + 1}`));
      } else if (roll === 20) {
        this.game.print(this.lang.get(`roll_20_meme_${Math.floor(Math.random() * 3) + 1}`));
      } else {
        this.game.print(this.lang.get("roll_msg", { roll: roll }));
      }

      const damage = Math.floor(baseDamage * roll / 10);
      const actualDamage = enemy.takeDamage(damage);
      this.game.print(this.lang.get("player_attack_msg", "You attack for {damage} damage!").replace("{damage}", actualDamage));
    } else if (choice === "2") {
      await this.game.useItemInBattle();
    } else if (choice === "5" && canCast) {
      const selectedSpell = await this.spellCasting.selectSpell(weaponName);
      if (selectedSpell) {
        this.spellCasting.castSpell(enemy, selectedSpell.name, selectedSpell.data);
      }
    } else if (choice === "3") {
      this.game.print(this.lang.get("you_defend", "You defend!"));
      this.player.defending = true;
    } else if (choice === "4") {
      const fleeChance = this.player.getEffectiveSpeed() > enemy.speed ? 0.7 : 0.4;
      if (Math.random() < fleeChance) {
        this.game.print(this.lang.get("you_successfully_fled", "You successfully fled!"));
        return false;
      } else {
        this.game.print(this.lang.get("failed_to_flee", "Failed to flee!"));
        return true;
      }
    } else {
      this.game.print(this.lang.get("invalid_choice_turn_lost", "Invalid choice, turn lost!"));
    }

    return true;
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
      enemy.tickCooldowns();

      let availableAbilities = enemy.getAvailableAbilities();
      if (availableAbilities.length > 0 && Math.random() < 0.4) {
        const ability = availableAbilities[Math.floor(Math.random() * availableAbilities.length)];
        this.game.print(`\n${this.lang.get('enemy_ability_msg', '{enemy_name} uses {ability_name}!').replace('{enemy_name}', enemy.name).replace('{ability_name}', ability.name)}`);
        this.game.print(`${ability.description}`);

        enemy.useAbility(ability.name);

        if (ability.damage) {
          let dmg = ability.damage;
          if (this.player.defending) {
            dmg = Math.floor(dmg / 2);
          }
          const actual = this.player.takeDamage(dmg);
          this.game.print(this.lang.get("enemy_ability_damage_msg", "It deals {damage} damage!").replace("{damage}", actual));
        }

        if (ability.stun_chance && Math.random() < ability.stun_chance) {
          this.game.print(this.lang.get('stun_msg', 'You are stunned and skip your next turn!'));
          this.player.applyBuff("Stunned", 1, { speedBonus: -999 });
        }

        if (ability.heal_amount) {
          const heal = ability.heal_amount;
          enemy.hp = Math.min(enemy.maxHp, enemy.hp + heal);
          this.game.print(this.lang.get("enemy_heal_msg", "{enemy_name} heals for {heal} HP!").replace("{enemy_name}", enemy.name).replace("{heal}", heal));
        }
        return;
      }
    }

    const baseDamage = enemy.attack;
    const roll = this.diceUtil.roll_1d(Math.max(1, this.player.level));
    this.game.print(this.lang.get("enemy_roll_msg", "{enemy_name} rolls the dice...").replace("{enemy_name}", enemy.name));
    this.game.print(this.lang.get("enemy_rolled_val_msg", "{enemy_name} rolled a {roll}!").replace("{enemy_name}", enemy.name).replace("{roll}", roll));

    let damage = Math.floor(baseDamage * roll / 10);
    if (this.player.defending) {
      damage = Math.floor(damage / 2);
      this.player.defending = false;
    }

    const actualDamage = this.player.takeDamage(damage);
    this.game.print(this.lang.get("enemy_attack_msg", "{enemy_name} attacks for {damage} damage!").replace("{enemy_name}", enemy.name).replace("{damage}", actualDamage));
  }
}
