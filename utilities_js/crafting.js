/**
 * Crafting Module for Our Legacy (Browser Version)
 * Alchemy and crafting functionality
 * Ported from utilities/crafting.py
 */

import { Colors } from './settings.js';
import { getRarityColor } from './shop.js';

/**
 * Visit the Alchemy workshop
 * @param {Object} game - Game instance
 * @param {Function} askFunc - Ask function for input
 * @returns {Promise<void>}
 */
export async function visitAlchemy(game, askFunc) {
  if (!game.player) {
    console.log(game.lang?.get("no_character") || "No character created yet.");
    return;
  }

  const recipes = game.craftingData?.recipes || {};
  if (!recipes || Object.keys(recipes).length === 0) {
    console.log(game.lang?.get('ui_no_crafting_recipes') || "No crafting recipes available.");
    return;
  }

  console.log(`\n${Colors.MAGENTA}${Colors.BOLD}=== ALCHEMY WORKSHOP ===${Colors.END}`);
  console.log("Welcome to the Alchemy Workshop! Here you can craft potions, elixirs, and items.");
  console.log(`\nYour gold: ${Colors.GOLD}${game.player.gold}${Colors.END}`);

  displayCraftingMaterials(game);

  while (true) {
    console.log("\n=== ALCHEMY WORKSHOP ===");
    console.log("Categories: [P]otions, [E]lixirs, [N]chantments, [U]tility, [A]ll");
    console.log("[C]raft item, [M]aterials, [B]ack");

    const choice = (await askFunc("\nChoose an option: ")).trim().toUpperCase();

    if (choice === 'B' || !choice) {
      break;
    } else if (choice === 'P') {
      await displayRecipesByCategory(game, 'Potions', askFunc);
    } else if (choice === 'E') {
      console.log("Elixirs or Enchantments? [E/N]:");
      const sub = (await askFunc("Choose (E/N): ")).trim().toUpperCase();
      if (sub === 'E') {
        await displayRecipesByCategory(game, 'Elixirs', askFunc);
      } else if (sub === 'N') {
        await displayRecipesByCategory(game, 'Enchantments', askFunc);
      }
    } else if (choice === 'U') {
      await displayRecipesByCategory(game, 'Utility', askFunc);
    } else if (choice === 'A') {
      await displayAllRecipes(game, askFunc);
    } else if (choice === 'C') {
      await craftItem(game, askFunc);
    } else if (choice === 'M') {
      displayCraftingMaterials(game);
    } else {
      console.log("Invalid choice.");
    }
  }
}

export function displayCraftingMaterials(game) {
  if (!game.player) return;

  console.log("\n=== Your Materials ===");
  const materialCategories = game.craftingData?.material_categories || {};
  const allMaterials = new Set();
  for (const materials of Object.values(materialCategories)) {
    for (const mat of materials) allMaterials.add(mat);
  }

  const materialCounts = {};
  for (const item of game.player.inventory) {
    if (allMaterials.has(item)) {
      materialCounts[item] = (materialCounts[item] || 0) + 1;
    }
  }

  if (Object.keys(materialCounts).length === 0) {
    console.log("You have no crafting materials.");
    return;
  }

  console.log(`${'Material'.padEnd(25)} ${'Quantity'.padEnd(10)}`);
  console.log("-".repeat(35));
  for (const [material, count] of Object.entries(materialCounts).sort()) {
    console.log(`${material.padEnd(25)} ${count.toString().padEnd(10)}`);
  }
}

export async function displayRecipesByCategory(game, category, askFunc) {
  const recipes = game.craftingData?.recipes || {};
  const categoryRecipes = Object.entries(recipes).filter(([_, rdata]) => rdata.category === category);

  if (categoryRecipes.length === 0) {
    console.log(`No recipes for ${category}.`);
    return;
  }

  console.log(`\n${Colors.BOLD}=== ${category.toUpperCase()} ===${Colors.END}`);
  for (let i = 0; i < categoryRecipes.length; i++) {
    const [rid, rdata] = categoryRecipes[i];
    const name = rdata.name || rid;
    const rarity = rdata.rarity || 'common';
    const rarityColor = getRarityColor(rarity);
    console.log(`${i + 1}. ${rarityColor}${name}${Colors.END}`);
  }
}

export async function displayAllRecipes(game, askFunc) {
  const recipes = game.craftingData?.recipes || {};
  if (Object.keys(recipes).length === 0) {
    console.log("\nNo recipes available.");
    return;
  }

  const pageSize = 10;
  const recipeList = Object.entries(recipes);
  let currentPage = 0;

  while (true) {
    const start = currentPage * pageSize;
    const end = start + pageSize;
    const pageItems = recipeList.slice(start, end);

    console.log("\n=== All Recipes ===");
    for (let i = 0; i < pageItems.length; i++) {
      const [rid, rdata] = pageItems[i];
      const name = rdata.name || rid;
      const category = rdata.category || 'Unknown';
      const rarityColor = getRarityColor(rdata.rarity || 'common');
      console.log(`${start + i + 1}. ${rarityColor}${name}${Colors.END} (${category})`);
    }

    const totalPages = Math.ceil(recipeList.length / pageSize);
    console.log(`\nPage ${currentPage + 1}/${totalPages}`);
    if (currentPage > 0) console.log("P. Previous Page");
    if (currentPage < totalPages - 1) console.log("N. Next Page");
    console.log("C. Craft Option, B. Back");

    const choice = (await askFunc("\nChoose an option: ")).trim().toUpperCase();
    if (choice === 'B') break;
    else if (choice === 'N' && currentPage < totalPages - 1) currentPage++;
    else if (choice === 'P' && currentPage > 0) currentPage--;
    else if (choice === 'C') await craftItem(game, askFunc);
  }
}

export async function craftItem(game, askFunc) {
  const recipes = game.craftingData?.recipes || {};
  const recipeNames = Object.keys(recipes);

  console.log("\n=== Craft Item ===");
  recipeNames.forEach((rid, i) => {
    const rdata = recipes[rid];
    console.log(`${i + 1}. ${getRarityColor(rdata.rarity || 'common')}${rdata.name || rid}${Colors.END}`);
  });

  const choice = (await askFunc(`\nChoose (1-${recipeNames.length}) or Enter: `)).trim();
  if (!choice || !/^\d+$/.test(choice)) return;

  const idx = parseInt(choice) - 1;
  const recipe = recipes[recipeNames[idx]];
  if (!recipe) return;

  if (game.player.level < (recipe.skill_requirement || 1)) {
    console.log(`\n${Colors.RED}Need level ${recipe.skill_requirement || 1}!${Colors.END}`);
    return;
  }

  const materialsNeeded = recipe.materials || {};
  for (const [material, quantity] of Object.entries(materialsNeeded)) {
    if (game.player.inventory.filter(x => x === material).length < quantity) {
      console.log(`Missing ${material}`);
      return;
    }
  }

  const confirm = (await askFunc("\nCraft? (y/n): ")).trim().toLowerCase();
  if (confirm !== 'y') return;

  for (const [material, quantity] of Object.entries(materialsNeeded)) {
    for (let i = 0; i < quantity; i++) {
      game.player.inventory.splice(game.player.inventory.indexOf(material), 1);
    }
  }

  const outputItems = recipe.output || {};
  for (const [item, quantity] of Object.entries(outputItems)) {
    for (let i = 0; i < quantity; i++) {
      game.player.inventory.push(item);
      game.updateMissionProgress('collect', item);
    }
  }
  console.log(`${Colors.GREEN}Crafted ${recipe.name}!${Colors.END}`);
}

export default {
  visitAlchemy,
  displayCraftingMaterials,
  displayRecipesByCategory,
  displayAllRecipes,
  craftItem
};
