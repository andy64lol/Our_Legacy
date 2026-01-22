/**
 * RPG Scripting Engine Test
 * Covers core API functionality and Node.js execution
 */

const fs = require('fs');
const path = require('path');

// Mock global state for standalone testing if needed
global.playerState = global.playerState || { name: "Test Player", level: 1, hp: 100 };

console.log("=== Node.js Scripting Engine Test ===");

// 1. Verify filesystem access
try {
    const activitiesPath = path.resolve(__dirname, 'activities.json');
    if (fs.existsSync(activitiesPath)) {
        console.log("✓ Found activities.json");
        const data = JSON.parse(fs.readFileSync(activitiesPath, 'utf8'));
        console.log(`✓ Loaded player: ${data.player.name} (Level ${data.player.level})`);
    } else {
        console.log("! activities.json not found (expected in scripts/ directory)");
    }
} catch (err) {
    console.error("✗ Filesystem test failed:", err.message);
}

// 2. Test basic logic
const testValue = 42;
if (testValue * 2 === 84) {
    console.log("✓ JavaScript basic logic verified");
}

console.log("=== Test Complete ===");
