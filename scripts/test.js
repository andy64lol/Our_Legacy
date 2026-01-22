/**
 * RPG Scripting Engine Comprehensive Test
 * Tests every function in the Scripting API
 */

import { player, enemy, battle, menu, print, log, tellraw } from './scripting_API.js';

console.log("=== RPG SCRIPTING API FULL TEST ===");

async function runTests() {
    try {
        // 1. Player API Tests
        log("Testing Player API...");
        print(`Name: ${player.name()}`);
        print(`Class: ${player.class()}`);
        print(`UUID: ${player.uuid()}`);
        
        const initialHP = player.getHealth();
        await player.addHealth(10);
        print(`HP changed: ${initialHP} -> ${player.getHealth()}`);
        
        await player.addMP(5);
        print(`MP: ${player.getMP()}`);
        
        await player.giveGold(50);
        print(`Gold: ${player.gold()}`);
        
        await player.addItem('Health Potion', 1);
        print(`Inventory contains ${player.inventory().length} items`);
        
        await player.addEffect('Blessed');
        print(`Has 'Blessed' effect: ${player.hasEffect('Blessed')}`);
        
        const loc = player.location();
        print(`Current Location: ${loc.name} (${loc.id})`);

        // 2. Enemy API Tests
        log("Testing Enemy API...");
        print(`Enemy ID: ${enemy.id()}`);
        print(`Enemy HP: ${enemy.hp()}`);
        await enemy.setCurrentHP(50);

        // 3. Battle API Tests
        log("Testing Battle API...");
        await battle.start('goblin_scout');
        await battle.win();

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
}

runTests().then(() => {
    console.log("=== TEST COMPLETE ===");
});
