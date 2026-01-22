// Camp Script - Allows camping in restricted areas
// Cost: 20 gold
// Requirements: Level 5+, location must have can_rest: false
// Benefits: +10 Max Health, +5 Max MP, Full Health & MP restore

import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Helper for output
const tellraw = (msg) => console.log('__RAW_OUTPUT__' + msg);

async function run() {
    try {
        // Activities file path
        const activitiesPath = path.join(__dirname, '..', 'activities.json');
        if (!fs.existsSync(activitiesPath)) {
            tellraw('Error: activities.json not found');
            return;
        }

        const data = JSON.parse(fs.readFileSync(activitiesPath, 'utf8'));
        const player = data.player || {};
        const location = data.location || {};

        const playerLevel = player.level || 1;
        const playerGold = player.gold || 0;
        const maxHealth = player.maxHealth || 100;
        const maxMP = player.maxMP || 50;
        const canRest = location.canRest === true;

        // Check requirements
        if (playerLevel < 5) {
            tellraw('You must be at least level 5 to camp here. Your current level is ' + playerLevel + '.');
            return;
        } 
        
        if (canRest === true) {
            tellraw('This location is too safe for camping. Find a more dangerous area.');
            return;
        } 
        
        if (playerGold < 20) {
            tellraw('You need 20 gold to set up camp. You only have ' + playerGold + ' gold.');
            return;
        }

        // Perform camping
        player.gold = playerGold - 20;
        const newMaxHealth = maxHealth + 10;
        const newMaxMP = maxMP + 5;
        
        player.maxHealth = newMaxHealth;
        player.health = newMaxHealth;
        player.maxMP = newMaxMP;
        player.mp = newMaxMP;

        // Update data object
        data.player = player;
        data.last_updated = new Date().toISOString();

        // Save back to activities.json
        fs.writeFileSync(activitiesPath, JSON.stringify(data, null, 2));

        tellraw('You set up camp and rest for the night.');
        tellraw('- 20 gold spent');
        tellraw('- Max Health increased from ' + maxHealth + ' to ' + newMaxHealth);
        tellraw('- Max MP increased from ' + maxMP + ' to ' + newMaxMP);
        tellraw('- Health and MP fully restored!');

    } catch (e) {
        tellraw('Error in camp script: ' + e.message);
    }
}

run();
