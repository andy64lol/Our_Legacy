// dice.js
// Dice rolling utility, made by andy64lol
// First step porting...

/**
 * Dice rolling utility class
 * Ported from utilities/dice.py
 */
export class Dice {
  /**
   * Roll a single die with `sides` sides
   * @param {number} sides - Number of sides on the die
   * @returns {number} Result of the roll (1 to sides)
   */
  roll_1d(sides) {
    return Math.floor(Math.random() * sides) + 1;
  }

  /**
   * Roll `num_dice` dice with `sides` sides, return array
   * @param {number} num_dice - Number of dice to roll
   * @param {number} sides - Number of sides on each die
   * @returns {number[]} Array of roll results
   */
  roll(num_dice, sides) {
    const results = [];
    for (let i = 0; i < num_dice; i++) {
      results.push(this.roll_1d(sides));
    }
    return results;
  }

  /**
   * Roll dice and return [min, max]
   * @param {number} num_dice - Number of dice to roll
   * @param {number} sides - Number of sides on each die
   * @returns {number[]} Array with [min, max] values
   */
  roll_min_max(num_dice, sides) {
    const rolls = this.roll(num_dice, sides);
    return [Math.min(...rolls), Math.max(...rolls)];
  }
}

export default Dice;
