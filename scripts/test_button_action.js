/**
 * Test button action script
 * This script is executed when the "Test File Button" is clicked
 */

print("\n=== File-based Button Action ===");
print("This script was executed from a file-based button!");

// Give the player some gold
player.gold.add(100);
print("Added 100 gold to your wallet!");

// Give a random item
var items = ["Potion", "Mana Potion", "Antidote", "Torch"];
var randomItem = items[Math.floor(Math.random() * items.length)];
player.addItem(randomItem, 1);
print("Received: " + randomItem);

// Display current gold
print("\nCurrent gold: " + player.gold());
print("Current inventory: " + player.inventory().join(", "));

print("\n=== Action Complete ===");

