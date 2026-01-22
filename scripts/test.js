/**
 * RPG Scripting Engine Comprehensive Test
 * Tests every function in the Scripting API
 */

const { player, enemy, battle, menu, print, log, tellraw } = require('./scripting_API.js');

console.log("=== RPG SCRIPTING API FULL TEST ===");

try {
    // 1. Player API Tests
    log("Testing Player API...");
    print(`Name: ${player.name()}`);
    print(`Class: ${player.class()}`);
    print(`UUID: ${player.uuid()}`);
    
    const initialHP = player.getHealth();
    player.addHealth(10);
    print(`HP changed: ${initialHP} -> ${player.getHealth()}`);
    
    player.addMP(5);
    print(`MP: ${player.getMP()}`);
    
    player.giveGold(50);
    print(`Gold: ${player.gold()}`);
    
    player.addItem('Health Potion', 1);
    print(`Inventory contains ${player.inventory().length} items`);
    
    player.addEffect('Blessed');
    print(`Has 'Blessed' effect: ${player.hasEffect('Blessed')}`);
    
    const loc = player.location();
    print(`Current Location: ${loc.name} (${loc.id})`);

    // 2. Enemy API Tests
    log("Testing Enemy API...");
    print(`Enemy ID: ${enemy.id()}`);
    print(`Enemy HP: ${enemy.hp()}`);
    enemy.setCurrentHP(50);

    // 3. Battle API Tests
    log("Testing Battle API...");
    battle.start('goblin_scout');
    battle.win();

    // 4. Menu API Tests (Visual verification)
    log("Testing Menu API...");
    menu.hide();
    menu.show();

    // 5. Output API Tests
    tellraw("Custom RAW message test");

    console.log("\n✓ ALL API FUNCTIONS EXECUTED SUCCESSFULLY");
} catch (err) {
    console.error("\n✗ TEST FAILED:");
    console.error(err.stack);
    process.exit(1);
}

console.log("=== TEST COMPLETE ===");
