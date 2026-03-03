/**
 * Building Module for Our Legacy (Browser Version)
 * Building and farming functionality
 * Ported from utilities/building.py
 */

import { Colors } from './settings.js';
import { getRarityColor } from './shop.js';

/**
 * Build and manage structures on your land
 * @param {Object} game - Game instance
 * @param {Function} askFunc - Ask function for input
 * @returns {Promise<void>}
 */
export async function buildHome(game, askFunc) {
  if (!game.player) {
    game.print(game.lang?.get("no_character") || "No character created yet.");
    return;
  }

  if (!game.player.housingOwned || game.player.housingOwned.length === 0) {
    game.print(`${Colors.YELLOW}You haven't purchased any housing items yet! Visit the Housing Shop first.${Colors.END}`);
    await askFunc("Press Enter to continue...");
    return;
  }

  while (true) {
    game.clear();
    game.print(`\n${Colors.BOLD}${Colors.CYAN}=== BUILD STRUCTURES ===${Colors.END}`);
    game.print(`${Colors.YELLOW}Manage your buildings and customize your property${Colors.END}\n`);
    game.print(`Comfort Points: ${Colors.CYAN}${game.player.comfortPoints || 0}${Colors.END}\n`);

    const buildingTypes = {
      "house": { label: "House", slots: 3 },
      "decoration": { label: "Decoration", slots: 10 },
      "fencing": { label: "Fencing", slots: 1 },
      "garden": { label: "Garden", slots: 3 },
      "farm": { label: "Farm", slots: 2 },
      "training_place": { label: "Training Place", slots: 3 }
    };

    for (const [bType, info] of Object.entries(buildingTypes)) {
      game.print(`${Colors.BOLD}${info.label} Slots:${Colors.END}`);
      for (let i = 1; i <= info.slots; i++) {
        const slot = `${bType}_${i}`;
        const itemId = game.player.buildingSlots ? game.player.buildingSlots[slot] : null;
        if (itemId && game.housingData && game.housingData[itemId]) {
          const item = game.housingData[itemId];
          const rarityColor = getRarityColor(item.rarity || 'common');
          game.print(`  ${slot}: ${rarityColor}${item.name || itemId}${Colors.END}`);
        } else {
          game.print(`  ${slot}: ${Colors.GRAY}Empty${Colors.END}`);
        }
      }
      game.print();
    }

    game.print("1. Place item in slot");
    game.print("2. Remove item from slot");
    game.print("3. View home status");
    game.print("B. Back");

    const choice = (await askFunc(`\n${Colors.CYAN}Choose option: ${Colors.END}`)).trim().toUpperCase();

    if (choice === 'B') break;
    else if (choice === '1') await placeHousingItem(game, askFunc);
    else if (choice === '2') await removeHousingItem(game, askFunc);
    else if (choice === '3') await viewHomeStatus(game, askFunc);
  }
}

export async function placeHousingItem(game, askFunc) {
  if (!game.player.housingOwned || game.player.housingOwned.length === 0) return;

  game.print("\n=== AVAILABLE ITEMS ===");
  game.player.housingOwned.forEach((itemId, i) => {
    const item = game.housingData?.[itemId];
    if (item) {
      const rarityColor = getRarityColor(item.rarity || 'common');
      game.print(`${i + 1}. ${rarityColor}${item.name || itemId}${Colors.END} (${item.type || 'misc'})`);
    }
  });

  const choice = (await askFunc(`\nChoose item (1-${game.player.housingOwned.length}) or Enter: `)).trim();
  if (!choice || !/^\d+$/.test(choice)) return;

  const idx = parseInt(choice) - 1;
  const itemId = game.player.housingOwned[idx];
  const item = game.housingData?.[itemId];
  if (!item) return;

  const itemType = item.type || 'decoration';
  let availableSlots = [];
  if (itemType === 'house') availableSlots = ['house_1', 'house_2', 'house_3'];
  else if (itemType === 'decoration') for (let i = 1; i <= 10; i++) availableSlots.push(`decoration_${i}`);
  else if (itemType === 'fencing') availableSlots = ['fencing_1'];
  else if (itemType === 'garden') for (let i = 1; i <= 3; i++) availableSlots.push(`garden_${i}`);
  else if (itemType === 'training_place') for (let i = 1; i <= 3; i++) availableSlots.push(`training_place_${i}`);
  else if (itemType === 'farming' || itemType === 'farm') availableSlots = ['farm_1', 'farm_2'];
  else if (itemType === 'crafting') availableSlots = ['crafting_1'];
  else if (itemType === 'storage') availableSlots = ['storage_1'];
  else for (let i = 1; i <= 10; i++) availableSlots.push(`decoration_${i}`);

  const emptySlots = availableSlots.filter(slot => !game.player.buildingSlots?.[slot]);
  if (emptySlots.length === 0) {
    game.print(`No slots for ${itemType}.`);
    return;
  }

  game.print(`\nAvailable slots for ${itemType}:`);
  emptySlots.forEach((s, i) => game.print(`${i + 1}. ${s}`));

  const slotChoice = (await askFunc(`\nChoose slot (1-${emptySlots.length}) or Enter: `)).trim();
  if (!slotChoice || !/^\d+$/.test(slotChoice)) return;

  const targetSlot = emptySlots[parseInt(slotChoice) - 1];
  if (!game.player.buildingSlots) game.player.buildingSlots = {};
  game.player.buildingSlots[targetSlot] = itemId;
  game.player.comfortPoints = (game.player.comfortPoints || 0) + (item.comfort_points || 0);

  game.print(`${Colors.GREEN}Placed ${item.name || itemId} in ${targetSlot}!${Colors.END}`);
  await askFunc("Press Enter to continue...");
}

export async function removeHousingItem(game, askFunc) {
  const occupiedSlots = [];
  if (game.player.buildingSlots) {
    for (const [slot, itemId] of Object.entries(game.player.buildingSlots)) {
      if (itemId) occupiedSlots.push({ slot, itemId });
    }
  }

  if (occupiedSlots.length === 0) {
    game.print("\nNo items to remove.");
    return;
  }

  game.print("\n=== PLACED ITEMS ===");
  occupiedSlots.forEach((obj, i) => {
    const item = game.housingData?.[obj.itemId];
    game.print(`${i + 1}. ${obj.slot}: ${getRarityColor(item?.rarity || 'common')}${item?.name || obj.itemId}${Colors.END}`);
  });

  const choice = (await askFunc(`\nRemove (1-${occupiedSlots.length}) or Enter: `)).trim();
  if (!choice || !/^\d+$/.test(choice)) return;

  const { slot, itemId } = occupiedSlots[parseInt(choice) - 1];
  game.player.buildingSlots[slot] = null;
  if (itemId && game.housingData?.[itemId]) {
    game.player.comfortPoints = Math.max(0, (game.player.comfortPoints || 0) - (game.housingData[itemId].comfort_points || 0));
  }
  game.print(`${Colors.YELLOW}Removed item from ${slot}.${Colors.END}`);
  await askFunc("Press Enter to continue...");
}

export async function viewHomeStatus(game, askFunc) {
  game.print("\n=== HOME DETAILS ===");
  game.print(`\nComfort Points: ${Colors.CYAN}${game.player.comfortPoints || 0}${Colors.END}`);

  const placedItems = Object.values(game.player.buildingSlots || {}).filter(id => id);
  game.print(`Total Items Placed: ${placedItems.length}`);

  game.print("\n=== ITEM BREAKDOWN ===");
  const itemComforts = {};
  for (const itemId of placedItems) {
    const itemData = game.housingData?.[itemId] || {};
    const name = itemData.name || itemId;
    const comfort = itemData.comfort_points || 0;
    if (!itemComforts[name]) itemComforts[name] = { count: 0, total_comfort: 0 };
    itemComforts[name].count++;
    itemComforts[name].total_comfort += comfort;
  }

  Object.entries(itemComforts).sort((a, b) => b[1].total_comfort - a[1].total_comfort).slice(0, 10).forEach(([name, info]) => {
    game.print(`  ${name}: x${info.count} = +${info.total_comfort} comfort`);
  });
  await askFunc("\nPress Enter to continue...");
}

export async function farm(game, askFunc) {
  if (!game.player) return;
  let hasFarm = false;
  if (game.player.buildingSlots) {
    for (let i = 1; i <= 2; i++) if (game.player.buildingSlots[`farm_${i}`]) hasFarm = true;
  }

  if (!hasFarm) {
    game.print(`\n${Colors.YELLOW}Build a farm first!${Colors.END}`);
    await askFunc("Press Enter to continue...");
    return;
  }

  while (true) {
    game.clear();
    game.print(`\n${Colors.BOLD}${Colors.CYAN}=== FARMING ===${Colors.END}`);
    const cropsData = game.farmingData?.crops || {};
    const cropsList = Object.entries(cropsData);

    game.print("=== FARM STATUS ===");
    for (let i = 1; i <= 2; i++) {
      const slot = `farm_${i}`;
      if (game.player.buildingSlots?.[slot]) {
        game.print(`Farm Plot ${i}: Active`);
        const plots = game.player.farmPlots?.[slot] || [];
        plots.forEach((p, pi) => {
          const cName = cropsData[p.crop]?.name || p.crop;
          game.print(`  ${pi + 1}. ${cName} - ${p.days_left > 0 ? p.days_left + ' days left' : 'READY'}`);
        });
      }
    }

    game.print("\n1-N. Plant, H. Harvest, B. Back");
    const choice = (await askFunc("Action: ")).trim().toUpperCase();
    if (choice === 'B') break;
    else if (choice === 'H') await harvestCrops(game, askFunc);
    else if (/^\d+$/.test(choice)) {
      const idx = parseInt(choice) - 1;
      if (cropsList[idx]) await plantCrop(game, askFunc, cropsList[idx]);
    }
  }
}

async function plantCrop(game, askFunc, [cropId, cropData]) {
  const farmChoices = [];
  for (let i = 1; i <= 2; i++) if (game.player.buildingSlots?.[`farm_${i}`]) farmChoices.push(`farm_${i}`);

  game.print("Select plot:");
  farmChoices.forEach((f, i) => game.print(`${i+1}. ${f}`));
  const choice = await askFunc("Plot: ");
  const fSlot = farmChoices[parseInt(choice)-1];
  if (!fSlot) return;

  if (!game.player.farmPlots) game.player.farmPlots = {};
  if (!game.player.farmPlots[fSlot]) game.player.farmPlots[fSlot] = [];

  if (game.player.farmPlots[fSlot].length < (game.farmingData?.max_plots_per_farm || 3)) {
    game.player.farmPlots[fSlot].push({ crop: cropId, days_left: cropData.growth_time || 0 });
    game.print(`Planted ${cropData.name}!`);
  }
  await askFunc("Press Enter to continue...");
}

async function harvestCrops(game, askFunc) {
  const cropsData = game.farmingData?.crops || {};
  for (let i = 1; i <= 2; i++) {
    const slot = `farm_${i}`;
    const plots = game.player.farmPlots?.[slot] || [];
    const remaining = [];
    for (const p of plots) {
      if (p.days_left <= 0) {
        const cData = cropsData[p.crop] || {};
        for (let j = 0; j < (cData.harvest_amount || 1); j++) game.player.inventory.push(cData.name || p.crop);
        game.print(`Harvested ${cData.name || p.crop}!`);
      } else remaining.push(p);
    }
    game.player.farmPlots[slot] = remaining;
  }
  await askFunc("Press Enter to continue...");
}
