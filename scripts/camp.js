// Camp Script - Allows camping in restricted areas
// Cost: 20 gold
// Requirements: Level 5+, location must have can_rest: false
// Benefits: +10 Max Health, +5 Max MP, Full Health & MP restore

var tellraw = global.tellraw || function(msg) { print(msg); };
var fs = null;
var path = null;

// Try to require filesystem modules
try {
    fs = require('fs');
    path = require('path');
} catch(e) {
    // Node.js modules not available, use global
    if (typeof global !== 'undefined' && global.fs) {
        fs = global.fs;
    }
    if (typeof global !== 'undefined' && global.path) {
        path = global.path;
    }
}

// Get player info
var playerLevel = global.playerState.level || 1;
var playerGold = global.playerState.gold || 0;
var maxHealth = global.playerState.maxHealth || 100;
var maxMP = global.playerState.maxMP || 50;

// Get current location
var currentLocation = global.locationState || {};
var areaId = currentLocation.id || 'starting_village';

// Load areas data to check can_rest property
var canRest = false;
if (fs && path) {
    try {
        var scriptDir = __dirname || (typeof process !== 'undefined' ? process.cwd() : '.');
        var areasPath = path.join(scriptDir, '..', 'data', 'areas.json');
        if (fs.existsSync(areasPath)) {
            var areasData = JSON.parse(fs.readFileSync(areasPath, 'utf8'));
            var areaInfo = areasData[areaId];
            if (areaInfo) {
                canRest = areaInfo.can_rest === true;
            }
        }
    } catch (e) {
        tellraw('Error loading area data: ' + e.message);
    }
}

// Check requirements
if (playerLevel < 5) {
    tellraw('You must be at least level 5 to camp here. Your current level is ' + playerLevel + '.');
} else if (canRest === true) {
    tellraw('This location is too safe for camping. Find a more dangerous area.');
} else if (playerGold < 20) {
    tellraw('You need 20 gold to set up camp. You only have ' + playerGold + ' gold.');
} else {
    // Perform camping
    global.playerState.gold = playerGold - 20;
    
    // Increase max health by 10
    var newMaxHealth = maxHealth + 10;
    global.playerState.maxHealth = newMaxHealth;
    
    // Increase max MP by 5
    var newMaxMP = maxMP + 5;
    global.playerState.maxMP = newMaxMP;
    
    // Restore health and MP to full
    global.playerState.health = newMaxHealth;
    global.playerState.mp = newMaxMP;
    
    // Save activities
    if (typeof saveActivities === 'function') {
        saveActivities();
    }
    
    tellraw('You set up camp and rest for the night.');
    tellraw('- 20 gold spent');
    tellraw('- Max Health increased from ' + maxHealth + ' to ' + newMaxHealth);
    tellraw('- Max MP increased from ' + maxMP + ' to ' + newMaxMP);
    tellraw('- Health and MP fully restored!');
}

// Register the Camp button in buttons.json for the Others menu
if (fs && path) {
    try {
        var scriptDir = __dirname || (typeof process !== 'undefined' ? process.cwd() : '.');
        var buttonsPath = path.join(scriptDir, 'buttons.json');
        
        // Load existing buttons or create new structure
        var buttonsData = { buttons: {} };
        if (fs.existsSync(buttonsPath)) {
            try {
                var existing = JSON.parse(fs.readFileSync(buttonsPath, 'utf8'));
                if (existing.buttons) {
                    buttonsData = existing;
                }
            } catch (e) {
                // File exists but invalid JSON, use default
            }
        }
        
        // Add Camp button if not already present
        if (!buttonsData.buttons['Camp']) {
            buttonsData.buttons['Camp'] = {
                type: 'file',
                value: 'camp.js',
                script_id: 'camp'
            };
            
            // Save to file
            fs.writeFileSync(buttonsPath, JSON.stringify(buttonsData, null, 2));
            tellraw('Camp option added to Others menu!');
        }
    } catch (e) {
        // Silently fail if we can't write to buttons.json
    }
}

// Output command to add button to current session
print('__ADD_BUTTON__' + JSON.stringify({
    id: 'camp',
    label: 'Camp',
    action: 'camp.js',
    description: 'Set up camp to rest and boost your stats. Only works in dangerous areas.'
}));

