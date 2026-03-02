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
    console.log(game.lang.get("no_character") || "No character created yet.");
    return;
  }

  if (!game.craftingData || !game.craftingData.get('recipes')) {
    console.log(game.lang.get('ui_no_crafting_recipes') || "No crafting recipes available.");
    return;
  }

  console.log(`\n${Colors.MAGENTA}${Colors.BOLD}=== ALCHEMY WORKSHOP ===${Colors.END}`);
  console.log("Welcome to the Alchemy Workshop! Here you can craft potions, elixirs, and items.");
  console.log(`\nYour gold: ${Colors.GOLD}${game.player.gold}${Colors.END}`);

  // Display available materials from inventory
  displayCraftingMaterials(game);

  while (true) {
    console.clear();
    console.log("=== ALCHEMY WORKSHOP ===");
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

/**
 * Display materials available in player's inventory
 * @param {Object} game - Game instance
 */
export function displayCraftingMaterials(game) {
  if (!game.player) {
    return;
  }

  console.log("\n=== Your Materials ===");

  // Get all material categories
  const materialCategories = game.craftingData.get('material_categories', {});

  // Collect all possible materials
  const allMaterials = new Set();
  for (const materials of Object.values(materialCategories)) {
    for (const mat of materials) {
      allMaterials.add(mat);
    }
  }

  // Count materials in inventory
  const materialCounts = {};
  for (const item of game.player.inventory) {
    if (allMaterials.has(item)) {
      materialCounts[item] = (materialCounts[item] || 0) + 1;
    }
  }

  if (Object.keys(materialCounts).length === 0) {
    console.log("You have no crafting materials.");
    console.log("Materials can be found as drops from enemies or purchased from shops.");
    return;
  }

  console.log(`${'Material'.padEnd(25)} ${'Quantity'.padEnd(10)}`);
  console.log("-".repeat(35));
  for (const [material, count] of Object.entries(materialCounts).sort()) {
    console.log(`${material.padEnd(25)} ${count.toString().padEnd(10)}`);
  }
}

/**
 * Display recipes filtered by category
 * @param {Object} game - Game instance
 * @param {string} category - Category name
 * @param {Function} askFunc - Ask function for input
 * @returns {Promise<void>}
 */
export async function displayRecipesByCategory(game, category, askFunc) {
  if (!game.craftingData) {
    return;
  }

  const recipes = game.craftingData.get('recipes', {});
  const categoryRecipes = Object.entries(recipes).filter(([_, rdata]) => rdata.get('category') === category);

  if (categoryRecipes.length === 0) {
    console.log(`No recipes for ${category}.`);
    return;
  }

  console.log(`\n${Colors.BOLD}=== ${category.toUpperCase()} ===${Colors.END}`);
  for (let i = 0; i < categoryRecipes.length; i++) {
    const [rid, rdata] = categoryRecipes[i];
    const name = rdata.get('name', rid);
    const rarity = rdata.get('rarity', 'common');
    const rarityColor = getRarityColor(rarity);
    console.log(`${i + 1}. ${rarityColor}${name}${Colors.END}`);
  }
}

/**
 * Display all available recipes
 * @param {Object} game - Game instance
 * @param {Function} askFunc - Ask function for input
 * @returns {Promise<void>}
 */
export async function displayAllRecipes(game, askFunc) {
  if (!game.craftingData) {
    return;
  }

  const recipes = game.craftingData.get('recipes', {});
  if (!recipes || Object.keys(recipes).length === 0) {
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
      const name = rdata.get('name', rid);
      const category = rdata.get('category', 'Unknown');
      const rarity = rdata.get('rarity', 'common');
      const rarityColor = getRarityColor(rarity);
      console.log(`${start + i + 1}. ${rarityColor}${name}${Colors.END} (${category})`);
    }

    const totalPages = Math.ceil(recipeList.length / pageSize);
    console.log(`\nPage ${currentPage + 1}/${totalPages}`);

    if (totalPages > 1) {
      if (currentPage > 0) {
        console.log("P. Previous Page");
      }
      if (currentPage < totalPages - 1) {
        console.log("N. Next Page");
      }
    }
    console.log("C. Craft Option");
    console.log("B. Back");

    const choice = (await askFunc("\nChoose an option: ")).trim().toUpperCase();

    if (choice === 'B') {
      break;
    } else if (choice === 'N' && currentPage < totalPages - 1) {
      currentPage += 1;
    } else if (choice === 'P' && currentPage > 0) {
      currentPage -= 1;
    } else if (choice === 'C') {
      await craftItem(game, askFunc);
    } else {
      console.log("Invalid choice.");
    }
  }
}

/**
 * Craft an item using materials from inventory
 * @param {Object} game - Game instance
 * @param {Function} askFunc - Ask function for input
 * @returns {Promise<void>}
 */
export async function craftItem(game, askFunc) {
  if (!game.player || !game.craftingData) {
    console.log("Cannot craft.");
    return;
  }

  const recipes = game.craftingData.get('recipes', {});

  // Show all recipes for selection
  console.log("\n=== Craft Item ===");
  const recipeNames = Object.keys(recipes);

  for (let i = 0; i < recipeNames.length; i++) {
    const rid = recipeNames[i];
    const rdata = recipes[rid];
    const name = rdata.get('name', rid);
    const rarity = rdata.get('rarity', 'common');
    const rarityColor = getRarityColor(rarity);
    console.log(`${i + 1}. ${rarityColor}${name}${Colors.END}`);
  }

  const choice = (await askFunc(`\nChoose recipe (1-${recipeNames.length}) or press Enter to cancel: `)).trim();

  if (!choice) {
    return;
  }

  if (!/^\d+$/.test(choice)) {
    console.log("Invalid choice.");
    return;
  }

  const idx = parseInt(choice) - 1;
  if (!(idx >= 0 && idx < recipeNames.length)) {
    console.log("Invalid recipe number.");
    return;
  }

  const recipeId = recipeNames[idx];
  const recipe = recipes[recipeId];

  // Check skill requirement
  const skillReq = recipe.get('skill_requirement', 1);
  if (game.player.level < skillReq) {
    console.log(`\n${Colors.RED}You need at least level ${skillReq} to craft this item.${Colors.END}`);
    return;
  }

  // Get materials required
  const materialsNeeded = recipe.get('materials', {});

  // Check if player has materials
  const missingMaterials = [];
  for (const [material, quantity] of Object.entries(materialsNeeded)) {
    const inInventory = game.player.inventory.filter(x => x === material).length;
    if (inInventory < quantity) {
      missingMaterials.push(`${material} (need ${quantity}, have ${inInventory})`);
    }
  }

  if (missingMaterials.length > 0) {
    console.log("\nMissing materials:");
    for (const m of missingMaterials) {
      console.log(`  - ${m}`);
    }
    console.log("\nGather more materials first.");
    return;
  }

  // Show craft confirmation
  const outputItems = recipe.get('output', {});
  console.log("\n=== Craft Confirmation ===");
  console.log(`Recipe: ${recipe.get('name')}`);
  console.log(`Output: ${Object.entries(outputItems).map(([item, qty]) => `${qty}x ${item}`).join(', ')}`);
  console.log("\nMaterials will be consumed:");
  for (const [material, quantity] of Object.entries(materialsNeeded)) {
    console.log(`  - ${quantity}x ${material}`);
  }

  const confirm = (await askFunc("\nCraft this item? (y/n): ")).trim().toLowerCase();
  if (confirm !== 'y') {
    console.log("Crafting cancelled.");
    return;
  }

  // Consume materials
  for (const [material, quantity] of Object.entries(materialsNeeded)) {
    for (let i = 0; i < quantity; i++) {
      const idx = game.player.inventory.indexOf(material);
      if (idx > -1) {
        game.player.inventory.splice(idx, 1);
      }
    }
  }

  // Add crafted items to inventory
  for (const [item, quantity] of Object.entries(outputItems)) {
    for (let i = 0; i < quantity; i++) {
      game.player.inventory.push(item);
      game.updateMissionProgress('collect', item);
    }
  }

  console.log(`\n${Colors.GREEN}Successfully crafted ${recipe.get('name')}!${Colors.END}`);
  for (const [item, quantity] of Object.entries(outputItems)) {
    console.log(`Received: ${quantity}x ${item}`);
  }
}

export default {
  visitAlchemy,
  displayCraftingMaterials,
  displayRecipesByCategory,
  displayAllRecipes,
  craftItem
};
