// Spawn Thief Script
// This script initiates a battle with a Thief enemy

import { battle, tellraw } from './scripting_API.js';

async function run() {
    tellraw('A thief jumps out from the shadows!');
    tellraw('"Hand over your gold!"');
    
    // Initiate battle with the 'thief' enemy ID from enemies.json
    console.log('__RAW_OUTPUT__Starting battle...');
    await battle.start('thief');
    console.log('__RAW_OUTPUT__Battle command sent.');
}

run();
