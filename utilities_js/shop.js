/**
 * Shop Module for Our Legacy (Browser Version)
 * Shop functionality for buying and selling items
 * Ported from utilities/shop.py
 */

import { Colors } from './settings.js';

/**
 * Get the color for an item rarity
 * @param {string} rarity - Item rarity
 * @returns {string} Color code
 */
function getRarityColor(rarity) {
  const rarityColors = {
    "common": Colors.COMMON,
    "uncommon": Colors.UNCOMMON,
    "rare": Colors.RARE,
    "epic": Colors.EPIC,
    "legendary": Colors.LEGENDARY
  };
  return rarityColors[rarity.toLowerCase()] || Colors.WHITE;
}

/**
 * Visit a general shop
 * @param {Object} game - Game instance
 * @param {Object} shopData - Shop data
 * @param {Function} askFunc - Ask function for input
 * @returns {Promise<void>}
 */
async function visitGeneralShop(game, shopData, askFunc) {
  if (!game.player) {
    game.print(game.lang.get("no_character") || "No character created yet.");
    return;
  }

  const shopName = shopData.name || "Shop";
  const welcomeMsg = shopData.welcome_message || `Welcome to ${shopName}!`;
  const items = shopData.items || [];
  const maxBuy = shopData.max_buy || 99;

  game.print(`\n${Colors.BOLD}=== ${shopName.toUpperCase()} ===${Colors.END}`);
  game.print(welcomeMsg);
  game.print(`Your gold: ${Colors.GOLD}${game.player.gold}${Colors.END}`);

  if (!items || items.length === 0) {
    game.print(game.lang.get('ui_shop_no_items') || "This shop has no items for sale.");
    return;
  }

  // Group items by type for better display
  const itemDetails = [];
  for (const itemId of items) {
    if (game.itemsData[itemId]) {
      const item = game.itemsData[itemId];
      itemDetails.push({
        'id': itemId,
        'name': item.name || itemId,
        'type': item.type || 'misc',
        'rarity': item.rarity || 'common',
        'price': item.price || 0,
        'description': item.description || ''
      });
    }
  }

  if (itemDetails.length === 0) {
    game.print(game.lang.get('ui_no_valid_items_shop') || "No valid items in this shop.");
    return;
  }

  const pageSize = 8;
  let currentPage = 0;

  while (true) {
    const start = currentPage * pageSize;
    const end = start + pageSize;
    const pageItems = itemDetails.slice(start, end);

    game.print(`\n--- Items (Page ${currentPage + 1}) ---`);
    for (let i = 0; i < pageItems.length; i++) {
      const item = pageItems[i];
      const rarityColor = getRarityColor(item.rarity);
      const ownedCount = game.player.inventory.filter(x => x === item.id).length;
      const canBuyMore = ownedCount < maxBuy;

      let status = "";
      if (!canBuyMore) {
        status = ` ${Colors.RED}(Max owned: ${maxBuy})${Colors.END}`;
      } else if (ownedCount > 0) {
        status = ` ${Colors.YELLOW}(Owned: ${ownedCount})${Colors.END}`;
      }

      game.print(`${start + i + 1}. ${rarityColor}${item.name}${Colors.END} - ${Colors.GOLD}${item.price}g${Colors.END}${status}`);
      game.print(`   ${item.description}`);
    }

    const totalPages = Math.ceil(itemDetails.length / pageSize);
    game.print(`\nPage ${currentPage + 1}/${totalPages}`);

    if (totalPages > 1) {
      if (currentPage > 0) {
        game.print(`P. Previous Page`);
      }
      if (currentPage < totalPages - 1) {
        game.print(`N. Next Page`);
      }
    }
    game.print(`S. Sell Items`);
    game.print(`B. Back`);

    const choice = (await askFunc("\nChoose item to buy or option: ")).trim().toUpperCase();

    if (choice === 'B') {
      break;
    } else if (choice === 'S') {
      await shopSell(game, askFunc);
      game.print(`\nYour gold: ${Colors.GOLD}${game.player.gold}${Colors.END}`);
    } else if (choice === 'N' && currentPage < totalPages - 1) {
      currentPage += 1;
    } else if (choice === 'P' && currentPage > 0) {
      currentPage -= 1;
    } else if (choice && /^\d+$/.test(choice)) {
      const itemIdx = parseInt(choice) - 1;
      if (itemIdx >= 0 && itemIdx < itemDetails.length) {
        const item = itemDetails[itemIdx];
        const ownedCount = game.player.inventory.filter(x => x === item.id).length;

        if (ownedCount >= maxBuy) {
          game.print(`${Colors.RED}You already own the maximum amount (${maxBuy}) of this item.${Colors.END}`);
          continue;
        }

        if (game.player.gold >= item.price) {
          game.player.gold -= item.price;
          game.player.inventory.push(item.id);
          game.print(`${Colors.GREEN}Purchased ${item.name} for ${item.price} gold!${Colors.END}`);
          game.updateMissionProgress('collect', item.id);
        } else {
          game.print(`${Colors.RED}Not enough gold! Need ${item.price}, have ${game.player.gold}.${Colors.END}`);
        }
      } else {
        game.print("Invalid item number.");
      }
    } else {
      game.print("Invalid choice.");
    }
  }
}

/**
 * Visit a specific shop by ID
 * @param {Object} game - Game instance
 * @param {string} shopId - Shop ID
 * @param {Function} askFunc - Ask function for input
 * @returns {Promise<void>}
 */
async function visitSpecificShop(game, shopId, askFunc) {
  if (!game.player) {
    game.print(game.lang.get("no_character") || "No character created yet.");
    return;
  }

  const shopData = game.shopsData && game.shopsData[shopId] ? game.shopsData[shopId] : {};
  if (!shopData || Object.keys(shopData).length === 0) {
    game.print(`Shop ${shopId} not found.`);
    return;
  }

  await visitGeneralShop(game, shopData, askFunc);
}

/**
 * Sell items from the player's inventory
 * @param {Object} game - Game instance
 * @param {Function} askFunc - Ask function for input
 * @returns {Promise<void>}
 */
async function shopSell(game, askFunc) {
  if (!game.player) {
    return;
  }

  const sellable = [...game.player.inventory];
  if (sellable.length === 0) {
    game.print("You have nothing to sell.");
    return;
  }

  game.print(`\nYour Inventory:`);
  for (let i = 0; i < sellable.length; i++) {
    let equipMarker = '';
    for (const slot of Object.keys(game.player.equipment)) {
      if (game.player.equipment[slot] === sellable[i]) {
        equipMarker = ' (equipped)';
        break;
      }
    }
    const itemData = game.itemsData[sellable[i]] || {};
    const price = itemData.price || 0;
    const sellPrice = price > 0 ? Math.floor(price / 2) : 0;
    game.print(`${i + 1}. ${sellable[i]}${equipMarker} - Sell for ${sellPrice} gold`);
  }

  const choice = (await askFunc(`Choose item to sell (1-${sellable.length}) or press Enter to cancel: `)).trim();
  if (!choice || !/^\d+$/.test(choice)) {
    return;
  }
  
  const idx = parseInt(choice) - 1;
  if (!(idx >= 0 && idx < sellable.length)) {
    game.print("Invalid selection.");
    return;
  }

  const item = sellable[idx];
  // Prevent selling equipped items
  const isEquipped = Object.values(game.player.equipment).some(eq => eq === item);
  if (isEquipped) {
    game.print("Unequip this item before selling.");
    return;
  }

  const itemData = game.itemsData[item] || {};
  const price = itemData.price || 0;
  const sellPrice = price > 0 ? Math.floor(price / 2) : 0;
  
  const itemIndex = game.player.inventory.indexOf(item);
  if (itemIndex > -1) {
    game.player.inventory.splice(itemIndex, 1);
  }
  game.player.gold += sellPrice;
  game.print(`Sold ${item} for ${sellPrice} gold.`);
}

export { getRarityColor, visitGeneralShop as visit_general_shop, visitSpecificShop as visit_specific_shop, shopSell as shop_sell };
export default {
  getRarityColor,
  visitGeneralShop,
  visitSpecificShop,
  shopSell,
  visit_specific_shop: visitSpecificShop,
  visit_general_shop: visitGeneralShop,
  shop_sell: shopSell
};
