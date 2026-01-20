/**
 * Example Script for Our Legacy
 * This script demonstrates various features of the scripting API
 */

// Import the scripting API first
import { player, enemy, battle, map, missions, system, events, getActivities, clearActivities, getActivityCount, log, print, activities, loadActivities, saveActivities } from './scripting_API.js';

// Welcome message
print("=== Example Script Loaded ===");
print("This script demonstrates the scripting API capabilities.");
log("Example script executed at: " + Date.now());

// Demonstrate player API
print("\n--- Player Information ---");
print("Player UUID: " + player.uuid());
print("Player Name: " + player.name());
print("Player Class: " + player.class());
print("Player Level: " + player.level);

// Demonstrate level modification (for testing)
print("\n--- Level Modification Demo ---");
print("Adding 100 experience...");
player.exp.add(100);
print("Current experience added count: " + getActivityCount());

// Demonstrate inventory API
print("\n--- Inventory Demo ---");
print("Current inventory: " + JSON.stringify(player.inventory()));
print("Checking for 'Potion'...");
player.hasItem("Potion");
print("Adding 'Potion' to inventory...");
player.addItem("Potion", 3);
print("Added 'Gold' to inventory...");
player.addItem("Gold", 50);

// Demonstrate gold API
print("\n--- Gold Demo ---");
print("Current gold: " + player.gold());
print("Giving 100 gold...");
player.giveGold();

// Demonstrate location API
print("\n--- Location Demo ---");
var currentLocation = player.location();
print("Current location: " + currentLocation.name);
print("Available connections: " + JSON.stringify(player.locationsConnectedToCurrent()));

// Demonstrate map API
print("\n--- Map Demo ---");
print("Map difficulty: " + map.getDifficulty());
print("Can rest here: " + map.getCanRest());
print("Rest cost: " + map.getCanRestCosts());

// Demonstrate enemy API
print("\n--- Enemy Demo ---");
print("Enemy ID: " + enemy.id());
print("Is boss: " + enemy.isBoss());
print("Enemy HP: " + enemy.hp());

// Demonstrate battle API
print("\n--- Battle Demo ---");
print("Battle functions available: flee, win, lose");
battle.start("Goblin");
battle.bossfightStart("Dragon");

// Demonstrate missions API
print("\n--- Missions Demo ---");
print("Finished missions: " + JSON.stringify(missions.getFinished()));
print("Ongoing missions: " + JSON.stringify(missions.getOngoing()));
print("Available missions: " + JSON.stringify(missions.getNotAccepted()));

// Demonstrate companions API
print("\n--- Companions Demo ---");
print("Current companions: " + JSON.stringify(player.companions()));

// Demonstrate events system
print("\n--- Events Demo ---");
events.on("testEvent", function(data) {
    print("Test event triggered with data: " + JSON.stringify(data));
});
events.emit("testEvent", { message: "Hello from script!" });

// Demonstrate effects
print("\n--- Effects Demo ---");
print("Checking for effect 'poison'...");
player.hasEffect("poison");
print("Adding effect 'regeneration'...");
player.addEffect("regeneration");

// Summary
print("\n=== Script Execution Complete ===");
print("Total API calls made: " + getActivityCount());
print("Activities logged: " + JSON.stringify(getActivities()));

// Clear activities for next run
clearActivities();
print("Activities cleared for next script execution.");

