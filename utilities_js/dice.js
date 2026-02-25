// dice.js
// Dice rolling utility, made by andy64lol
// First step porting...

export class Dice {
  // Roll a single die with `sides` sides
  roll1d(sides) {
    return Math.floor(Math.random() * sides) + 1;
  }

  // Roll `numDice` dice with `sides` sides, return array
  roll(numDice, sides) {
    const results = [];
    for (let i = 0; i < numDice; i++) {
      results.push(this.roll1d(sides));
    }
    return results;
  }

  // Roll dice and return [min, max]
  rollMinMax(numDice, sides) {
    const rolls = this.roll(numDice, sides);
    return [Math.min(...rolls), Math.max(...rolls)];
  }
}