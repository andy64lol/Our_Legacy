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
    console.log(game.lang.get("no_character") || "No character created yet.");
    return;
  }

  if (!game.player.housingOwned || game.player.housingOwned.length === 0) {
    console.log(`${Colors.YELLOW}You haven't purchased any housing items yet! Visit the Housing Shop first.${Colors.END}`);
    await askFunc("Press Enter to continue...");
    return;
  }

  while (true) {
    console.clear();
    console.log(`\n${Colors.BOLD}${Colors.CYAN}=== BUILD STRUCTURES ===${Colors.END}`);
    console.log(`${Colors.YELLOW}Manage your buildings and customize your property${Colors.END}\n`);

    console.log(`Comfort Points: ${Colors.CYAN}${game.player.comfortPoints}${Colors.END}\n`);

    // Display building categories
    const buildingTypes = {
      "house": { label: "House", slots: 3 },
      "decoration": { label: "Decoration", slots: 10 },
      "fencing": { label: "Fencing", slots: 1 },
      "garden": { label: "Garden", slots: 3 },
      "farm": { label: "Farm", slots: 2 },
      "farming": { label: "Farming", slots: 2 },
      "training_place": { label: "Training Place", slots: 3 }
    };

    for (const [bType, info] of Object.entries(buildingTypes)) {
      console.log(`${Colors.BOLD}${info.label} Slots:${Colors.END}`);
      for (let i = 1; i <= info.slots; i++) {
        const slot = `${bType}_${i}`;
        const itemId = game.player.buildingSlots ? game.player.buildingSlots[slot] : null;
        if (itemId && game.housingData && game.housingData[itemId]) {
          const item = game.housingData[itemId];
          const rarityColor = getRarityColor(item.get('rarity', 'common'));
          console.log(`  ${slot}: ${rarityColor}${item.get('name', itemId)}${Colors.END}`);
        } else {
          console.log(`  ${slot}: ${Colors.GRAY}Empty${Colors.END}`);
        }
      }
      console.log();
    }

    console.log("1. Place item in slot");
    console.log("2. Remove item from slot");
    console.log("3. View home status");
    console.log("B. Back");

    const choice = (await askFunc(`\n${Colors.CYAN}Choose option: ${Colors.END}`)).trim().toUpperCase();

    if (choice === 'B') {
      break;
    } else if (choice === '1') {
      await placeHousingItem(game, askFunc);
    } else if (choice === '2') {
      await removeHousingItem(game, askFunc);
    } else if (choice === '3') {
      await viewHomeStatus(game, askFunc);
    } else {
      console.log("Invalid choice. Please try again.");
      await new Promise(resolve => setTimeout(resolve, 1000));
    }
  }
}

/**
 * Place a housing item in a slot
 * @param {Object} game - Game instance
 * @param {Function} askFunc - Ask function for input
 * @returns {Promise<void>}
 */
export async function placeHousingItem(game, askFunc) {
  if (!game.player) {
    return;
  }

  if (!game.player.housingOwned || game.player.housingOwned.length === 0) {
    console.log(`${Colors.YELLOW}You have no housing items to place.${Colors.END}`);
    await askFunc("Press Enter to continue...");
    return;
  }

  console.log("\n=== AVAILABLE ITEMS ===");
  for (let i = 0; i < game.player.housingOwned.length; i++) {
    const itemId = game.player.housingOwned[i];
    if (game.housingData && game.housingData[itemId]) {
      const item = game.housingData[itemId];
      const rarityColor = getRarityColor(item.get('rarity', 'common'));
      console.log(`${i + 1}. ${rarityColor}${item.get('name', itemId)}${Colors.END} (${item.get('type', 'misc')})`);
    }
  }

  const choice = (await askFunc(`\nChoose item (1-${game.player.housingOwned.length}) or press Enter to cancel: `)).trim();

  if (!choice) {
    return;
  }

  if (!/^\d+$/.test(choice)) {
    console.log("Invalid choice.");
    return;
  }

  const idx = parseInt(choice) - 1;
  if (idx < 0 || idx >= game.player.housingOwned.length) {
    console.log("Invalid item number.");
    return;
  }

  const itemId = game.player.housingOwned[idx];
  const item = game.housingData ? game.housingData[itemId] : null;

  if (!item) {
    console.log("Item data not found.");
    return;
  }

  const itemType = item.get('type', 'decoration');

  // Find available slots for this item type
  let availableSlots = [];
  if (itemType === 'house') {
    availableSlots = [`house_1`, `house_2`, `house_3`];
  } else if (itemType === 'decoration') {
    availableSlots = [];
    for (let i = 1; i <= 10; i++) availableSlots.push(`decoration_${i}`);
  } else if (itemType === 'fencing') {
    availableSlots = ['fencing_1'];
  } else if (itemType === 'garden') {
    availableSlots = [];
    for (let i = 1; i <= 3; i++) availableSlots.push(`garden_${i}`);
  } else if (itemType === 'training_place') {
    availableSlots = [];
    for (let i = 1; i <= 3; i++) availableSlots.push(`training_place_${i}`);
  } else if (itemType === 'farming' || itemType === 'farm') {
    availableSlots = [`farm_1`, `farm_2`];
  } else if (itemType === 'crafting') {
    availableSlots = ['crafting_1'];
  } else if (itemType === 'storage') {
    availableSlots = ['storage_1'];
  } else {
    // Default to decoration slots
    availableSlots = [];
    for (let i = 1; i <= 10; i++) availableSlots.push(`decoration_${i}`);
  }

  // Filter to slots that are empty
  const emptySlots = availableSlots.filter(slot => {
    return !game.player.buildingSlots || game.player.buildingSlots[slot] === null;
  });

  if (emptySlots.length === 0) {
    console.log(`No available slots for ${itemType} items.`);
    await askFunc("Press Enter to continue...");
    return;
  }

  console.log(`\nAvailable slots for ${itemType}:`);
  for (let i = 0; i < emptySlots.length; i++) {
    console.log(`${i + 1}. ${emptySlots[i]}`);
  }

  const slotChoice = (await askFunc(`\nChoose slot (1-${emptySlots.length}) or press Enter to cancel: `)).trim();

  if (!slotChoice) {
    return;
  }

  if (!/^\d+$/.test(slotChoice)) {
    console.log("Invalid choice.");
    return;
  }

  const slotIdx = parseInt(slotChoice) - 1;
  if (slotIdx < 0 || slotIdx >= emptySlots.length) {
    console.log("Invalid slot number.");
    return;
  }

  const targetSlot = emptySlots[slotIdx];

  // Initialize buildingSlots if needed
  if (!game.player.buildingSlots) {
    game.player.buildingSlots = {};
  }

  // Place the item
  game.player.buildingSlots[targetSlot] = itemId;

  // Update comfort
  const comfortPoints = item.get('comfort_points', 0);
  game.player.comfortPoints = (game.player.comfortPoints || 0) + comfortPoints;

  console.log(`${Colors.GREEN}Placed ${item.get('name', itemId)} in ${targetSlot}!${Colors.END}`);
  await askFunc("Press Enter to continue...");
}

/**
 * Remove a housing item from a slot
 * @param {Object} game - Game instance
 * @param {Function} askFunc - Ask function for input
 * @returns {Promise<void>}
 */
export async function removeHousingItem(game, askFunc) {
  if (!game.player) {
    return;
  }

  // Get occupied slots
  const occupiedSlots = [];
  if (game.player.buildingSlots) {
    for (const [slot, itemId] of Object.entries(game.player.buildingSlots)) {
      if (itemId !== null && itemId !== undefined) {
        occupiedSlots.push({ slot, itemId });
      }
    }
  }

  if (occupiedSlots.length === 0) {
    console.log("\nNo items to remove.");
    await askFunc("Press Enter to continue...");
    return;
  }

  console.log("\n=== PLACED ITEMS ===");
  for (let i = 0; i < occupiedSlots.length; i++) {
    const { slot, itemId } = occupiedSlots[i];
    if (game.housingData && game.housingData[itemId]) {
      const item = game.housingData[itemId];
      const rarityColor = getRarityColor(item.get('rarity', 'common'));
      console.log(`${i + 1}. ${slot}: ${rarityColor}${item.get('name', itemId)}${Colors.END}`);
    }
  }

  const choice = (await askFunc(`\nChoose item to remove (1-${occupiedSlots.length}) or press Enter to cancel: `)).trim();

  if (!choice) {
    return;
  }

  if (!/^\d+$/.test(choice)) {
    console.log("Invalid choice.");
    return;
  }

  const idx = parseInt(choice) - 1;
  if (idx < 0 || idx >= occupiedSlots.length) {
    console.log("Invalid item number.");
    return;
  }

  const targetSlot = occupiedSlots[idx].slot;
  const itemId = occupiedSlots[idx].itemId;

  // Remove the item
  game.player.buildingSlots[targetSlot] = null;

  // Update comfort
  if (itemId && game.housingData && game.housingData[itemId]) {
    const item = game.housingData[itemId];
    const comfortPoints = item.get('comfort_points', 0);
    game.player.comfortPoints = Math.max(0, (game.player.comfortPoints || 0) - comfortPoints);
  }

  console.log(`${Colors.YELLOW}Removed item from ${targetSlot}.${Colors.END}`);
  await askFunc("Press Enter to continue...");
}

/**
 * View detailed home status and statistics
 * @param {Object} game - Game instance
 * @param {Function} askFunc - Ask function for input
 * @returns {Promise<void>}
 */
export async function viewHomeStatus(game, askFunc) {
  if (!game.player) {
    return;
  }

  console.log("\n=== HOME DETAILS ===");
  console.log(`\nComfort Points: ${Colors.CYAN}${game.player.comfortPoints || 0}${Colors.END}`);

  const placedItems = [];
  if (game.player.buildingSlots) {
    for (const itemId of Object.values(game.player.buildingSlots)) {
      if (itemId !== null && itemId !== undefined) {
        placedItems.push(itemId);
      }
    }
  }

  console.log(`Total Items Placed: ${placedItems.length}`);
  console.log(`Unique Items Placed: ${new Set(placedItems).size}`);

  // Calculate comfort distribution
  console.log("\n=== ITEM BREAKDOWN ===");
  const itemComforts = {};
  for (const itemId of placedItems) {
    const itemData = game.housingData ? game.housingData.get(itemId, {}) : {};
    const name = itemData.get("name", itemId);
    const comfort = itemData.get("comfort_points", 0);

    if (!itemComforts[name]) {
      itemComforts[name] = { count: 0, total_comfort: 0 };
    }
    itemComforts[name].count += 1;
    itemComforts[name].total_comfort += comfort;
  }

  // Sort by total comfort contribution
  const sortedItems = Object.entries(itemComforts).sort((a, b) => b[1].total_comfort - a[1].total_comfort);

  let displayed = 0;
  for (const [name, info] of sortedItems.slice(0, 10)) {
    console.log(`  ${name}: x${info.count} = +${info.total_comfort} comfort`);
    displayed++;
  }

  if (sortedItems.length > 10) {
    const remainingComfort = sortedItems.slice(10).reduce((sum, [, info]) => sum + info.total_comfort, 0);
    console.log(`  ... and ${sortedItems.length - 10} more items (+${remainingComfort} comfort)`);
  }

  await askFunc("\nPress Enter to continue...");
}

/**
 * Farm crops on your land
 * @param {Object} game - Game instance
 * @param {Function} askFunc - Ask function for input
 * @returns {Promise<void>}
 */
export async function farm(game, askFunc) {
  if (!game.player) {
    console.log(game.lang.get("no_character") || "No character created yet.");
    return;
  }

  // Check if player has any farm buildings
  let hasFarm = false;
  if (game.player.buildingSlots) {
    for (let i = 1; i <= 2; i++) {
      if (game.player.buildingSlots[`farm_${i}`]) {
        hasFarm = true;
        break;
      }
    }
  }

  if (!hasFarm) {
    console.log(`\n${Colors.YELLOW}You need to build a farm first! Use the 'Build Structures' option.${Colors.END}`);
    await askFunc("Press Enter to continue...");
    return;
  }

  while (true) {
    console.clear();
    console.log(`\n${Colors.BOLD}${Colors.CYAN}=== FARMING ===${Colors.END}`);
    console.log(`${Colors.YELLOW}Tend to your crops and harvest your bounty${Colors.END}\n`);

    // Get farming data
    const cropsData = game.farmingData ? game.farmingData.get("crops", {}) : {};

    console.log("=== AVAILABLE CROPS TO PLANT ===\n");
    const cropsList = Object.entries(cropsData);
    for (let idx = 0; idx < cropsList.length; idx++) {
      const [cropId, cropData] = cropsList[idx];
      const name = cropData.get("name", cropId);
      const description = cropData.get("description", "");
      const growthTime = cropData.get("growth_time", 0);
      const harvest = cropData.get("harvest_amount", 0);
      console.log(`${Colors.CYAN}${idx + 1}.${Colors.END} ${Colors.BOLD}${name}${Colors.END}`);
      console.log(`   ${description}`);
      console.log(`   Growth: ${Colors.YELLOW}${growthTime} days${Colors.END} | Harvest: ${Colors.GREEN}+${harvest}${Colors.END}\n`);
    }

    console.log("=== FARM STATUS ===\n");

    // Show farm plot status
    for (let farmIdx = 1; farmIdx <= 2; farmIdx++) {
      const farmSlot = `farm_${farmIdx}`;
      const hasBuilding = game.player.buildingSlots && game.player.buildingSlots[farmSlot] !== null;

      if (hasBuilding) {
        console.log(`${Colors.GOLD}Farm Plot ${farmIdx}:${Colors.END} ${Colors.GREEN}✓ Active${Colors.END}`);
        const plots = game.player.farmPlots ? game.player.farmPlots[farmSlot] : [];
        if (plots && plots.length > 0) {
          for (let plantIdx = 0; plantIdx < plots.length; plantIdx++) {
            const plant = plots[plantIdx];
            const cropName = (cropsData.get(plant.get("crop"), {}) || {}).get("name", plant.get("crop"));
            const daysLeft = plant.get("days_left", 0);
            if (daysLeft > 0) {
              console.log(`  ${plantIdx + 1}. ${cropName} - ${Colors.YELLOW}${daysLeft} days${Colors.END} until ready`);
            } else {
              console.log(`  ${plantIdx + 1}. ${cropName} - ${Colors.GREEN}Ready to harvest!${Colors.END}`);
            }
          }
        } else {
          console.log(`  ${Colors.GRAY}Empty - Ready to plant${Colors.END}`);
        }
      } else {
        console.log(`Farm Plot ${farmIdx}: ${Colors.DARK_GRAY}Not built${Colors.END}`);
      }
      console.log();
    }

    console.log(`1-${cropsList.length}. Plant a crop`);
    console.log("H. Harvest crops");
    console.log("V. View inventory");
    console.log("B. Back");

    const choice = (await askFunc(`\n${Colors.CYAN}Choose action: ${Colors.END}`)).trim().toUpperCase();

    if (choice === 'B') {
      break;
    } else if (choice === 'H') {
      await harvestCrops(game, askFunc);
    } else if (choice === 'V') {
      await viewFarmingInventory(game, askFunc);
    } else if (/^\d+$/.test(choice)) {
      const cropIdx = parseInt(choice) - 1;
      if (cropIdx >= 0 && cropIdx < cropsList.length) {
        await plantCrop(game, askFunc, cropsList[cropIdx]);
      }
    }
  }
}

/**
 * Plant a specific crop in an available farm plot
 * @param {Object} game - Game instance
 * @param {Function} askFunc - Ask function for input
 * @param {Array} cropTuple - [cropId, cropData]
 * @returns {Promise<void>}
 */
export async function plantCrop(game, askFunc, cropTuple) {
  if (!game.player) {
    return;
  }

  const [cropId, cropData] = cropTuple;
  const cropName = cropData.get("name", cropId);
  const growthTime = cropData.get("growth_time", 0);

  // Select which farm to plant in
  console.clear();
  console.log(`\n${Colors.BOLD}${Colors.CYAN}=== PLANT ${cropName.toUpperCase()} ===${Colors.END}\n`);
  console.log("Select farm plot:");

  const farmChoices = [];
  for (let farmIdx = 1; farmIdx <= 2; farmIdx++) {
    const farmSlot = `farm_${farmIdx}`;
    const hasBuilding = game.player.buildingSlots && game.player.buildingSlots[farmSlot] !== null;

    if (hasBuilding) {
      const plots = game.player.farmPlots ? game.player.farmPlots[farmSlot] : [];
      const plantCount = plots ? plots.length : 0;
      const maxPlots = game.farmingData ? game.farmingData.get("max_plots_per_farm", 3) : 3;

      console.log(`${farmChoices.length + 1}. Farm Plot ${farmIdx} - ${Colors.GREEN}${plantCount}/${maxPlots} plants${Colors.END}`);
      farmChoices.push(farmSlot);
    }
  }

  if (farmChoices.length === 0) {
    console.log("No active farms available.");
    await askFunc("Press Enter to continue...");
    return;
  }

  const choice = (await askFunc(`\nChoose farm (1-${farmChoices.length}) or press Enter to cancel: `)).trim();

  if (!choice || !/^\d+$/.test(choice)) {
    return;
  }

  const farmChoiceIdx = parseInt(choice) - 1;
  if (farmChoiceIdx < 0 || farmChoiceIdx >= farmChoices.length) {
    console.log("Invalid choice.");
    return;
  }

  const farmSlot = farmChoices[farmChoiceIdx];

  // Initialize farmPlots if needed
  if (!game.player.farmPlots) {
    game.player.farmPlots = {};
  }
  if (!game.player.farmPlots[farmSlot]) {
    game.player.farmPlots[farmSlot] = [];
  }

  const maxPlots = game.farmingData ? game.farmingData.get("max_plots_per_farm", 3) : 3;
  if (game.player.farmPlots[farmSlot].length < maxPlots) {
    game.player.farmPlots[farmSlot].push({
      "crop": cropId,
      "days_left": growthTime
    });
    console.log(`\n${Colors.GREEN}✓ Planted ${cropName} in ${farmSlot}!${Colors.END}`);
    console.log(`It will be ready to harvest in ${Colors.YELLOW}${growthTime} days${Colors.END}`);
  } else {
    console.log(`\n${Colors.YELLOW}This farm plot is full! (${maxPlots}/${maxPlots} plants)${Colors.END}`);
  }

  await askFunc("Press Enter to continue...");
}

/**
 * Harvest ready crops from farm plots
 * @param {Object} game - Game instance
 * @param {Function} askFunc - Ask function for input
 * @returns {Promise<void>}
 */
export async function harvestCrops(game, askFunc) {
  if (!game.player) {
    return;
  }

  console.clear();
  console.log(`\n${Colors.BOLD}${Colors.CYAN}=== HARVEST CROPS ===${Colors.END}\n`);

  let harvested = false;
  const cropsData = game.farmingData ? game.farmingData.get("crops", {}) : {};

  for (let farmIdx = 1; farmIdx <= 2; farmIdx++) {
    const farmSlot = `farm_${farmIdx}`;
    const plots = game.player.farmPlots ? game.player.farmPlots[farmSlot] : [];

    if (!plots || plots.length === 0) {
      continue;
    }

    const cropsToRemove = [];
    for (let plantIdx = 0; plantIdx < plots.length; plantIdx++) {
      const plant = plots[plantIdx];
      const cropId = plant.get("crop");
      const daysLeft = plant.get("days_left", 0);

      if (daysLeft <= 0) {
        const cropData = cropsData.get(cropId, {});
        const cropName = cropData.get("name", cropId);
        const harvestAmount = cropData.get("harvest_amount", 1);

        // Add crops to inventory
        for (let i = 0; i < harvestAmount; i++) {
          game.player.inventory.push(cropName);
        }

        console.log(`${Colors.GREEN}✓ Harvested ${Colors.BOLD}${harvestAmount}x ${cropName}${Colors.END}${Colors.GREEN} from ${farmSlot}!${Colors.END}`);
        cropsToRemove.push(plantIdx);
        harvested = true;
      }
    }

    // Remove harvested crops (in reverse to maintain indices)
    for (let idx = cropsToRemove.length - 1; idx >= 0; idx--) {
      plots.splice(cropsToRemove[idx], 1);
    }
  }

  if (!harvested) {
    console.log(`${Colors.YELLOW}No crops are ready to harvest yet.${Colors.END}`);
  }

  await askFunc("Press Enter to continue...");
}

/**
 * View crops in inventory
 * @param {Object} game - Game instance
 * @param {Function} askFunc - Ask function for input
 * @returns {Promise<void>}
 */
export async function viewFarmingInventory(game, askFunc) {
  if (!game.player) {
    return;
  }

  console.clear();
  console.log(`\n${Colors.BOLD}${Colors.CYAN}=== FARMING INVENTORY ===${Colors.END}\n`);

  const cropsData = game.farmingData ? game.farmingData.get("crops", {}) : {};
  const cropNames = {};
  for (const [cropId, cropData] of Object.entries(cropsData)) {
    cropNames[cropData.get("name")] = cropId;
  }

  // Count crops in inventory
  const cropCounts = {};
  for (const item of game.player.inventory) {
    if (cropNames[item]) {
      cropCounts[item] = (cropCounts[item] || 0) + 1;
    }
  }

  if (Object.keys(cropCounts).length > 0) {
    console.log("=== CROPS IN INVENTORY ===\n");
    for (const [cropName, count] of Object.entries(cropCounts)) {
      const cropId = cropNames[cropName];
      const cropData = cropsData.get(cropId, {});
      const sellPrice = cropData.get("sell_price", 0);

      console.log(`${Colors.GREEN}✓${Colors.END} ${Colors.BOLD}${cropName}${Colors.END} x${count}`);
      console.log(`  Sell price: ${Colors.GOLD}${sellPrice}g${Colors.END} each | Total: ${Colors.GOLD}${sellPrice * count}g${Colors.END}\n`);
    }

    console.log("S. Sell crops");
    console.log("B. Back");

    const choice = (await askFunc(`\n${Colors.CYAN}Choose action: ${Colors.END}`)).trim().toUpperCase();

    if (choice === 'S') {
      await sellCrops(game, askFunc);
    }
  } else {
    console.log(`${Colors.YELLOW}You have no crops in your inventory yet.${Colors.END}`);
    await askFunc("Press Enter to continue...");
  }
}

/**
 * Sell crops for gold
 * @param {Object} game - Game instance
 * @param {Function} askFunc - Ask function for input
 * @returns {Promise<void>}
 */
export async function sellCrops(game, askFunc) {
  if (!game.player) {
    return;
  }

  console.clear();
  console.log(`\n=== SELL CROPS ===\n`);

  const cropsData = game.farmingData ? game.farmingData.get("crops", {}) : {};
  const cropNames = {};
  for (const [cropId, cropData] of Object.entries(cropsData)) {
    cropNames[cropData.get("name")] = cropId;
  }

  // Count crops
  const cropCounts = {};
  for (const item of game.player.inventory) {
    if (cropNames[item]) {
      cropCounts[item] = (cropCounts[item] || 0) + 1;
    }
  }

  let totalGold = 0;
  for (const [cropName, count] of Object.entries(cropCounts)) {
    const cropId = cropNames[cropName];
    const cropData = cropsData.get(cropId, {});
    const sellPrice = cropData.get("sell_price", 0);
    const subtotal = sellPrice * count;

    console.log(`${cropName} x${count}: ${Colors.GOLD}${subtotal}g${Colors.END}`);

    // Remove from inventory
    for (let i = 0; i < count; i++) {
      const idx = game.player.inventory.indexOf(cropName);
      if (idx > -1) {
        game.player.inventory.splice(idx, 1);
      }
    }
    
    totalGold += subtotal;
  }

  game.player.gold = (game.player.gold || 0) + totalGold;
  console.log(`\n${Colors.GREEN}✓ Sold all crops for ${Colors.GOLD}${totalGold} gold${Colors.END}${Colors.GREEN}!${Colors.END}`);
  console.log(`Total gold: ${Colors.GOLD}${game.player.gold}${Colors.END}`);
  await askFunc("Press Enter to continue...");
}

/**
 * Training system for improving stats using training_place buildings
 * @param {Object} game - Game instance
 * @param {Function} askFunc - Ask function for input
 * @returns {Promise<void>}
 */
export async function training(game, askFunc) {
  if (!game.player) {
    console.log(game.lang.get("no_character") || "No character created yet.");
    return;
  }

  // Check if player has any training_place buildings
  let hasTrainingPlace = false;
  if (game.player.buildingSlots) {
    for (let i = 1; i <= 3; i++) {
      if (game.player.buildingSlots[`training_place_${i}`]) {
        hasTrainingPlace = true;
        break;
      }
    }
  }

  if (!hasTrainingPlace) {
    console.log(`\n${Colors.YELLOW}You need to build a Training Place first! Use the 'Build Structures' option.${Colors.END}`);
    await askFunc("Press Enter to continue...");
    return;
  }

  // Calculate training effectiveness based on buildings
  const trainingBonus = calculateTrainingEffectiveness(game);

  while (true) {
    console.clear();
    console.log(`\n${Colors.BOLD}${Colors.CYAN}=== TRAINING GROUND ===${Colors.END}`);
    console.log(`${Colors.YELLOW}Train to improve your stats! Each training session affects all your stats.${Colors.END}\n`);

    // Show training facility info
    displayTrainingFacilities(game);

    console.log("=== CURRENT STATS ===");
    console.log(`HP: ${Colors.RED}${game.player.maxHp}${Colors.END} | MP: ${Colors.BLUE}${game.player.maxMp}${Colors.END}`);
    console.log(`Attack: ${Colors.RED}${game.player.attack}${Colors.END} | Defense: ${Colors.GREEN}${game.player.defense}${Colors.END} | Speed: ${Colors.YELLOW}${game.player.speed}${Colors.END}\n`);

    console.log("=== TRAINING TYPES ===");
    console.log("1. Morning Training (1d4)");
    console.log(`   ${Colors.GREEN}4: +4%${Colors.END} | ${Colors.YELLOW}3: +2%${Colors.END} | ${Colors.RED}1-2: -1%${Colors.END}`);
    console.log();
    console.log("2. Calm Training (1d6)");
    console.log(`   ${Colors.GREEN}6: +13%${Colors.END} | ${Colors.GREEN}5: +10%${Colors.END} | ${Colors.YELLOW}4: +7%${Colors.END} | ${Colors.YELLOW}3: +1%${Colors.END} | ${Colors.RED}1-2: -3%${Colors.END}`);
    console.log();
    console.log("3. Normal Training (1d8)");
    console.log(`   ${Colors.GREEN}5-8: +10%${Colors.END} | ${Colors.RED}1-3: -7%${Colors.END}`);
    console.log();
    console.log("4. Intense Training (1d20)");
    console.log(`   ${Colors.GREEN}16-20: +20%${Colors.END} | ${Colors.GREEN}11-15: +15%${Colors.END} | ${Colors.YELLOW}10: +10%${Colors.END} | ${Colors.RED}5-9: -10%${Colors.END} | ${Colors.RED}1-4: -20%${Colors.END}`);
    console.log();
    console.log("B. Back");

    const choice = (await askFunc(`\n${Colors.CYAN}Choose training type: ${Colors.END}`)).trim().toUpperCase();

    if (choice === 'B') {
      break;
    }

    if (['1', '2', '3', '4'].includes(choice)) {
      const trainingTypes = {
        '1': { name: 'Morning Training', sides: 4, calc: (roll) => roll === 4 ? 4 : roll === 3 ? 2 : -1 },
        '2': { name: 'Calm Training', sides: 6, calc: (roll) => roll === 6 ? 13 : roll === 5 ? 10 : roll === 4 ? 7 : roll === 3 ? 1 : -3 },
        '3': { name: 'Normal Training', sides: 8, calc: (roll) => roll >= 5 ? 10 : -7 },
        '4': { name: 'Intense Training', sides: 20, calc: (roll) => roll >= 16 ? 20 : roll >= 11 ? 15 : roll === 10 ? 10 : roll >= 5 ? -10 : -20 }
      };

      const { name, sides, calc } = trainingTypes[choice];

      // Roll the dice
      const roll = Math.floor(Math.random() * sides) + 1;
      const baseBonusPercent = calc(roll);

      // Apply training facility bonus
      const finalBonusPercent = baseBonusPercent * trainingBonus;

      console.log(`\n${Colors.BOLD}${Colors.CYAN}=== ${name.toUpperCase()} ===${Colors.END}`);
      console.log(`You rolled a ${Colors.YELLOW}${roll}${Colors.END} on a d${sides}!`);

      let bonusDescription = "";
      if (trainingBonus > 1.0) {
        bonusDescription = ` (x${trainingBonus.toFixed(1)} from facilities)`;
      } else if (trainingBonus < 1.0) {
        bonusDescription = ` (x${trainingBonus.toFixed(1)} from poor facilities)`;
      }

      if (finalBonusPercent > 0) {
        console.log(`${Colors.GREEN}Success!${Colors.END} All stats increase by ${Colors.GREEN}+${finalBonusPercent.toFixed(1)}%${Colors.END}${bonusDescription}`);
      } else if (finalBonusPercent < 0) {
        console.log(`${Colors.RED}Training failed!${Colors.END} All stats decrease by ${Colors.RED}${Math.abs(finalBonusPercent).toFixed(1)}%${Colors.END}${bonusDescription}`);
      } else {
        console.log("No change in stats.");
      }

      // Calculate stat changes
      const oldStats = {
        'maxHp': game.player.maxHp,
        'maxMp': game.player.maxMp,
        'attack': game.player.attack,
        'defense': game.player.defense,
        'speed': game.player.speed
      };

      // Apply percentage changes
      if (finalBonusPercent !== 0) {
        const percentMultiplier = 1 + (finalBonusPercent / 100);

        game.player.maxHp = Math.max(1, Math.floor(game.player.maxHp * percentMultiplier));
        game.player.maxMp = Math.max(1, Math.floor(game.player.maxMp * percentMultiplier));
        game.player.attack = Math.max(1, Math.floor(game.player.attack * percentMultiplier));
        game.player.defense = Math.max(1, Math.floor(game.player.defense * percentMultiplier));
        game.player.speed = Math.max(1, Math.floor(game.player.speed * percentMultiplier));

        // Ensure current HP/MP don't exceed new maxes
        game.player.hp = Math.min(game.player.hp, game.player.maxHp);
        game.player.mp = Math.min(game.player.mp, game.player.maxMp);
      }

      console.log("\n=== STAT CHANGES ===");
      console.log(`HP: ${Colors.RED}${oldStats.maxHp} → ${game.player.maxHp}${Colors.END}`);
      console.log(`MP: ${Colors.BLUE}${oldStats.maxMp} → ${game.player.maxMp}${Colors.END}`);
      console.log(`Attack: ${Colors.RED}${oldStats.attack} → ${game.player.attack}${Colors.END}`);
      console.log(`Defense: ${Colors.GREEN}${oldStats.defense} → ${game.player.defense}${Colors.END}`);
      console.log(`Speed: ${Colors.YELLOW}${oldStats.speed} → ${game.player.speed}${Colors.END}`);

      await askFunc("Press Enter to continue...");
    }
  }
}

/**
 * Calculate training effectiveness multiplier based on training facilities
 * @param {Object} game - Game instance
 * @returns {number} Training effectiveness multiplier
 */
function calculateTrainingEffectiveness(game) {
  if (!game.player) {
    return 1.0;
  }

  let totalComfort = 0;
  let facilityCount = 0;
  const rarityMultipliers = {
    'common': 1.0,
    'uncommon': 1.2,
    'rare': 1.4,
    'epic': 1.6,
    'legendary': 1.8
  };

  // Check all training_place slots
  for (let i = 1; i <= 3; i++) {
    const slot = `training_place_${i}`;
    const buildingId = game.player.buildingSlots ? game.player.buildingSlots[slot] : null;

    if (buildingId && game.housingData && game.housingData[buildingId]) {
      const building = game.housingData[buildingId];
      const comfort = building.get('comfort_points', 0);
      const rarity = building.get('rarity', 'common');

      // Apply rarity multiplier to comfort points
      const rarityMult = rarityMultipliers[rarity] || 1.0;
      const effectiveComfort = comfort * rarityMult;

      totalComfort += effectiveComfort;
      facilityCount++;
    }
  }

  if (facilityCount === 0) {
    return 1.0;
  }

  // Calculate average effective comfort
  const avgComfort = totalComfort / facilityCount;

  // Convert comfort to training multiplier
  // Base multiplier of 1.0, +0.1 per 10 comfort points
  const baseMultiplier = 1.0;
  const comfortBonus = avgComfort / 10 * 0.1;

  return baseMultiplier + comfortBonus;
}

/**
 * Display information about the player's training facilities
 * @param {Object} game - Game instance
 */
function displayTrainingFacilities(game) {
  if (!game.player) {
    return;
  }

  console.log("=== TRAINING FACILITIES ===\n");

  const facilities = [];
  for (let i = 1; i <= 3; i++) {
    const slot = `training_place_${i}`;
    const buildingId = game.player.buildingSlots ? game.player.buildingSlots[slot] : null;

    if (buildingId && game.housingData && game.housingData[buildingId]) {
      const building = game.housingData[buildingId];
      const name = building.get('name', buildingId);
      const rarity = building.get('rarity', 'common');
      const comfort = building.get('comfort_points', 0);

      // Color code by rarity
      const rarityColors = {
        'common': Colors.GRAY,
        'uncommon': Colors.GREEN,
        'rare': Colors.BLUE,
        'epic': Colors.MAGENTA,
        'legendary': Colors.GOLD
      };

      const color = rarityColors[rarity] || Colors.WHITE;
      facilities.push(`${color}${name} (${rarity}, ${comfort} comfort)${Colors.END}`);
    }
  }

  if (facilities.length > 0) {
    for (const facility of facilities) {
      console.log(`  • ${facility}`);
    }

    const effectiveness = calculateTrainingEffectiveness(game);
    if (effectiveness > 1.0) {
      console.log(`  ${Colors.GREEN}Training Effectiveness: x${effectiveness.toFixed(1)} (better facilities = better results)${Colors.END}`);
    } else if (effectiveness < 1.0) {
      console.log(`  ${Colors.YELLOW}Training Effectiveness: x${effectiveness.toFixed(1)} (upgrade facilities for better results)${Colors.END}`);
    } else {
      console.log(`  ${Colors.GRAY}Training Effectiveness: x${effectiveness.toFixed(1)}${Colors.END}`);
    }
  } else {
    console.log(`${Colors.YELLOW}No training facilities built.${Colors.END}`);
  }

  console.log();
}

export default {
  buildHome,
  placeHousingItem,
  removeHousingItem,
  viewHomeStatus,
  farm,
  plantCrop,
  harvestCrops,
  viewFarmingInventory,
  sellCrops,
  training
};
