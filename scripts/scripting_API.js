/**
 * Our Legacy - Scripting API
 * This file provides the JavaScript API for scripting functionality in the game.
 * All functions are designed to work with Node.js and read/write to activities.json.
 */

// Activity tracking
var activities = [];
var lastActivityTime = 0;

// Path to activities file (relative to script location)
var ACTIVITIES_FILE = 'scripts/activities.json';

// Initialize Date.now() equivalent for environments that don't have it
var _nowTimestamp = (typeof Date !== 'undefined' && Date.now) ? Date.now() : Math.floor(new Date().getTime());
if (typeof Date === 'undefined' || typeof Date.now === 'undefined') {
    Date = {
        now: function() {
            return _nowTimestamp;
        }
    };
}

// Helper to get current timestamp
function getTimestamp() {
    if (typeof Date !== 'undefined' && Date.now) {
        return Date.now();
    }
    return Math.floor(new Date().getTime());
}

// Helper for JSON stringify (QuickJS compatibility)
if (typeof JSON === 'undefined' || typeof JSON.stringify === 'undefined') {
    JSON = {
        stringify: function(obj) {
            if (obj === null) return 'null';
            if (obj === undefined) return 'undefined';
            if (typeof obj === 'number') return String(obj);
            if (typeof obj === 'boolean') return String(obj);
            if (typeof obj === 'string') return '"' + obj.replace(/"/g, '\\"') + '"';
            if (Array.isArray(obj)) {
                return '[' + obj.map(function(x) { return JSON.stringify(x); }).join(',') + ']';
            }
            if (typeof obj === 'object') {
                var keys = Object.keys(obj);
                var pairs = keys.map(function(k) { return JSON.stringify(k) + ':' + JSON.stringify(obj[k]); });
                return '{' + pairs.join(',') + '}';
            }
            return 'undefined';
        },
        parse: function(str) {
            try {
                return eval('(' + str + ')');
            } catch (e) {
                return null;
            }
        }
    };
}

// Load activities from file using Node.js fs
function loadActivities() {
    if (typeof require !== 'undefined') {
        var fs = require('fs');
        try {
            var data = fs.readFileSync(ACTIVITIES_FILE, 'utf8');
            var parsed = JSON.parse(data);
            
            // Load player state
            if (parsed.player) {
                global.playerState = parsed.player;
            }
            
            // Load location state
            if (parsed.location) {
                global.locationState = parsed.location;
            }
            
            // Load enemy state
            if (parsed.enemy) {
                global.enemyState = parsed.enemy;
            }
            
            // Load battle state
            if (parsed.battle) {
                global.battleState = parsed.battle;
            }
            
            // Load missions state
            if (parsed.missions) {
                global.missionsState = parsed.missions;
            }
            
            // Load system state
            if (parsed.system) {
                global.systemState = parsed.system;
            }
            
            // Load effects
            if (parsed.effects) {
                global.effectsState = parsed.effects;
            }
            
            // Load activities history
            if (parsed.activities) {
                activities = parsed.activities;
            }
            
            log("Activities loaded from " + ACTIVITIES_FILE);
            return true;
        } catch (e) {
            print("Error loading activities: " + e.message);
            return false;
        }
    }
    return false;
}

// Save activities to file using Node.js fs
function saveActivities() {
    if (typeof require !== 'undefined') {
        var fs = require('fs');
        try {
            var data = {
                version: "2.0",
                last_updated: new Date().toISOString(),
                activities: activities,
                player: global.playerState || {},
                location: global.locationState || {},
                enemy: global.enemyState || {},
                battle: global.battleState || {},
                missions: global.missionsState || {},
                system: global.systemState || {},
                effects: global.effectsState || []
            };
            
            fs.writeFileSync(ACTIVITIES_FILE, JSON.stringify(data, null, 2));
            log("Activities saved to " + ACTIVITIES_FILE);
            return true;
        } catch (e) {
            print("Error saving activities: " + e.message);
            return false;
        }
    }
    return false;
}

// Initialize global state if not exists
if (typeof global !== 'undefined') {
    if (!global.playerState) {
        global.playerState = {
            uuid: "",
            name: "",
            class: "",
            health: 100,
            maxHealth: 100,
            mp: 50,
            maxMP: 50,
            level: 1,
            exp: 0,
            gold: 100,
            inventory: [],
            companions: [],
            equipped: {
                weapon: null,
                offhand: null,
                armor: null,
                accessory: null
            },
            lastItemConsumed: null,
            lastItemObtained: null
        };
    }
    
    if (!global.locationState) {
        global.locationState = {
            id: "starting_village",
            name: "Starting Village",
            connections: [],
            canRest: true,
            restCost: 10,
            difficulty: 1
        };
    }
    
    if (!global.enemyState) {
        global.enemyState = {
            id: "",
            name: "",
            isBoss: false,
            hp: 0,
            maxHp: 0
        };
    }
    
    if (!global.battleState) {
        global.battleState = {
            active: false,
            enemyId: null,
            bossId: null
        };
    }
    
    if (!global.missionsState) {
        global.missionsState = {
            finished: [],
            ongoing: [],
            notAccepted: []
        };
    }
    
    if (!global.systemState) {
        global.systemState = {
            latestSave: null
        };
    }
    
    if (!global.effectsState) {
        global.effectsState = [];
    }
}

// Auto-load activities on initialization (Node.js)
if (typeof require !== 'undefined') {
    loadActivities();
}

// Player API object
var player = {
    // Player info
    uuid: function() { 
        activities.push({ type: 'uuid', time: getTimestamp() }); 
        return global.playerState.uuid || '';
    },
    name: function() { 
        activities.push({ type: 'name', time: getTimestamp() }); 
        return global.playerState.name || '';
    },
    class: function() { 
        activities.push({ type: 'class', time: getTimestamp() }); 
        return global.playerState.class || '';
    },
    
    // Player modifications
    changeName: function(newName) { 
        activities.push({ type: 'changeName', newName: newName, time: getTimestamp() }); 
        global.playerState.name = newName;
        saveActivities();
        return "Name change requested: " + newName;
    },
    changeClass: function(newClass) { 
        activities.push({ type: 'changeClass', newClass: newClass, time: getTimestamp() }); 
        global.playerState.class = newClass;
        saveActivities();
        return "Class change requested: " + newClass;
    },
    
    // Health management
    getHealth: function() { 
        activities.push({ type: 'getHealth', time: getTimestamp() }); 
        return global.playerState.health || 0;
    },
    getMaxHealth: function() { 
        activities.push({ type: 'getMaxHealth', time: getTimestamp() }); 
        return global.playerState.maxHealth || 0;
    },
    setHealth: function(value) { 
        activities.push({ type: 'setHealth', value: value, time: getTimestamp() }); 
        global.playerState.health = value;
        saveActivities();
        return value;
    },
    setMaxHealth: function(value) { 
        activities.push({ type: 'setMaxHealth', value: value, time: getTimestamp() }); 
        global.playerState.maxHealth = value;
        saveActivities();
        return value;
    },
    addHealth: function(amount) { 
        activities.push({ type: 'addHealth', amount: amount, time: getTimestamp() }); 
        global.playerState.health = (global.playerState.health || 0) + amount;
        saveActivities();
        return amount;
    },
    addMaxHealth: function(amount) { 
        activities.push({ type: 'addMaxHealth', amount: amount, time: getTimestamp() }); 
        global.playerState.maxHealth = (global.playerState.maxHealth || 0) + amount;
        saveActivities();
        return amount;
    },
    
    // MP management
    getMP: function() { 
        activities.push({ type: 'getMP', time: getTimestamp() }); 
        return global.playerState.mp || 0;
    },
    getMaxMP: function() { 
        activities.push({ type: 'getMaxMP', time: getTimestamp() }); 
        return global.playerState.maxMP || 0;
    },
    setMP: function(value) { 
        activities.push({ type: 'setMP', value: value, time: getTimestamp() }); 
        global.playerState.mp = value;
        saveActivities();
        return value;
    },
    setMaxMP: function(value) { 
        activities.push({ type: 'setMaxMP', value: value, time: getTimestamp() }); 
        global.playerState.maxMP = value;
        saveActivities();
        return value;
    },
    addMP: function(amount) { 
        activities.push({ type: 'addMP', amount: amount, time: getTimestamp() }); 
        global.playerState.mp = (global.playerState.mp || 0) + amount;
        saveActivities();
        return amount;
    },
    addMaxMP: function(amount) { 
        activities.push({ type: 'addMaxMP', amount: amount, time: getTimestamp() }); 
        global.playerState.maxMP = (global.playerState.maxMP || 0) + amount;
        saveActivities();
        return amount;
    },
    
    // Effects
    hasEffect: function(effectId) { 
        activities.push({ type: 'hasEffect', effectId: effectId, time: getTimestamp() }); 
        return global.effectsState && global.effectsState.indexOf(effectId) !== -1;
    },
    addEffect: function(effectId) { 
        activities.push({ type: 'addEffect', effectId: effectId, time: getTimestamp() }); 
        if (!global.effectsState) global.effectsState = [];
        if (global.effectsState.indexOf(effectId) === -1) {
            global.effectsState.push(effectId);
            saveActivities();
        }
        return effectId;
    },
    
    // Location
    location: function() { 
        activities.push({ type: 'location', time: getTimestamp() }); 
        return { 
            id: global.locationState.id || '', 
            name: global.locationState.name || '' 
        };
    },
    setLocation: function(locationId) { 
        activities.push({ type: 'setLocation', locationId: locationId, time: getTimestamp() }); 
        global.locationState.id = locationId;
        saveActivities();
        return locationId;
    },
    locationsConnectedToCurrent: function() { 
        activities.push({ type: 'locationsConnectedToCurrent', time: getTimestamp() }); 
        return global.locationState.connections || [];
    },
    
    // Level
    level: {
        set: function(value) { 
            activities.push({ type: 'level.set', value: value, time: getTimestamp() }); 
            global.playerState.level = value;
            saveActivities();
            return value;
        },
        add: function(amount) { 
            activities.push({ type: 'level.add', amount: amount, time: getTimestamp() }); 
            global.playerState.level = (global.playerState.level || 1) + amount;
            saveActivities();
            return amount;
        }
    },
    
    // Experience
    exp: {
        set: function(value) { 
            activities.push({ type: 'exp.set', value: value, time: getTimestamp() }); 
            global.playerState.exp = value;
            saveActivities();
            return value;
        },
        add: function(amount) { 
            activities.push({ type: 'exp.add', amount: amount, time: getTimestamp() }); 
            global.playerState.exp = (global.playerState.exp || 0) + amount;
            saveActivities();
            return amount;
        }
    },
    
    // Inventory
    hasItem: function(itemId, amount) { 
        if (amount === undefined) amount = 1;
        activities.push({ type: 'hasItem', itemId: itemId, amount: amount, time: getTimestamp() }); 
        var count = 0;
        var inventory = global.playerState.inventory || [];
        for (var i = 0; i < inventory.length; i++) {
            if (inventory[i] === itemId) count++;
        }
        return count >= amount;
    },
    addItem: function(itemId, amount) { 
        if (amount === undefined) amount = 1;
        activities.push({ type: 'addItem', itemId: itemId, amount: amount, time: getTimestamp() }); 
        if (!global.playerState.inventory) global.playerState.inventory = [];
        for (var i = 0; i < amount; i++) {
            global.playerState.inventory.push(itemId);
        }
        global.playerState.lastItemObtained = itemId;
        saveActivities();
        return { itemId: itemId, amount: amount };
    },
    removeItem: function(itemId, amount) { 
        if (amount === undefined) amount = 1;
        activities.push({ type: 'removeItem', itemId: itemId, amount: amount, time: getTimestamp() }); 
        var removed = 0;
        if (global.playerState.inventory) {
            for (var i = global.playerState.inventory.length - 1; i >= 0 && removed < amount; i--) {
                if (global.playerState.inventory[i] === itemId) {
                    global.playerState.inventory.splice(i, 1);
                    removed++;
                }
            }
        }
        saveActivities();
        return { itemId: itemId, amount: removed };
    },
    
    inventory: function() { 
        activities.push({ type: 'inventory', time: getTimestamp() }); 
        return global.playerState.inventory || [];
    },
    
    // Gold
    gold: function() { 
        activities.push({ type: 'gold', time: getTimestamp() }); 
        return global.playerState.gold || 0;
    },
    giveGold: function() { 
        activities.push({ type: 'giveGold', time: getTimestamp() }); 
        return 0;
    },
    deleteGold: function() { 
        activities.push({ type: 'deleteGold', time: getTimestamp() }); 
        return 0;
    },
    
    // Companions
    companions: function() { 
        activities.push({ type: 'companions', time: getTimestamp() }); 
        return global.playerState.companions || [];
    },
    companionSlot: function(slotNumber) { 
        activities.push({ type: 'companionSlot', slotNumber: slotNumber, time: getTimestamp() }); 
        var companions = global.playerState.companions || [];
        if (slotNumber >= 0 && slotNumber < companions.length) {
            return companions[slotNumber];
        }
        return null;
    },
    
    joinCompanion: function(companionId) { 
        activities.push({ type: 'joinCompanion', companionId: companionId, time: getTimestamp() }); 
        if (!global.playerState.companions) global.playerState.companions = [];
        global.playerState.companions.push(companionId);
        saveActivities();
        return companionId;
    },
    disbandCompanion: function(companionId) { 
        activities.push({ type: 'disbandCompanion', companionId: companionId, time: getTimestamp() }); 
        if (global.playerState.companions) {
            var idx = global.playerState.companions.indexOf(companionId);
            if (idx !== -1) {
                global.playerState.companions.splice(idx, 1);
                saveActivities();
            }
        }
        return companionId;
    },
    
    // Equipment
    getEquipped: function() { 
        activities.push({ type: 'getEquipped', time: getTimestamp() }); 
        return global.playerState.equipped || { weapon: null, offhand: null, armor: null, accessory: null };
    },
    
    equip: function(itemId) { 
        activities.push({ type: 'equip', itemId: itemId, time: getTimestamp() }); 
        global.playerState.equipped = global.playerState.equipped || { weapon: null, offhand: null, armor: null, accessory: null };
        // Determine slot based on item type (simplified)
        global.playerState.equipped.weapon = itemId;
        saveActivities();
        return itemId;
    },
    unequip: function(itemId) { 
        activities.push({ type: 'unequip', itemId: itemId, time: getTimestamp() }); 
        if (global.playerState.equipped) {
            if (global.playerState.equipped.weapon === itemId) global.playerState.equipped.weapon = null;
            if (global.playerState.equipped.armor === itemId) global.playerState.equipped.armor = null;
            if (global.playerState.equipped.accessory === itemId) global.playerState.equipped.accessory = null;
            saveActivities();
        }
        return itemId;
    },
    
    hasItemEquipped: function(itemId) { 
        activities.push({ type: 'hasItemEquipped', itemId: itemId, time: getTimestamp() }); 
        var equipped = global.playerState.equipped || {};
        return equipped.weapon === itemId || equipped.armor === itemId || equipped.accessory === itemId;
    },
    
    // Last items
    lastItemConsumed: function() { 
        activities.push({ type: 'lastItemConsumed', time: getTimestamp() }); 
        return global.playerState.lastItemConsumed || null;
    },
    lastItemObtained: function() { 
        activities.push({ type: 'lastItemObtained', time: getTimestamp() }); 
        return global.playerState.lastItemObtained || null;
    }
};

// Enemy API object
var enemy = {
    id: function() { 
        activities.push({ type: 'enemy.id', time: getTimestamp() }); 
        return global.enemyState.id || '';
    },
    isBoss: function() { 
        activities.push({ type: 'enemy.isBoss', time: getTimestamp() }); 
        return global.enemyState.isBoss || false;
    },
    
    hp: function() { 
        activities.push({ type: 'enemy.hp', time: getTimestamp() }); 
        return global.enemyState.hp || 0;
    },
    setCurrentHP: function(value) { 
        activities.push({ type: 'enemy.setCurrentHP', value: value, time: getTimestamp() }); 
        global.enemyState.hp = value;
        saveActivities();
        return value;
    },
    addCurrentHP: function(amount) { 
        activities.push({ type: 'enemy.addCurrentHP', amount: amount, time: getTimestamp() }); 
        global.enemyState.hp = (global.enemyState.hp || 0) + amount;
        saveActivities();
        return amount;
    }
};

// Battle API object
var battle = {
    start: function(enemyId) { 
        activities.push({ type: 'battle.start', enemyId: enemyId, time: getTimestamp() }); 
        global.battleState.active = true;
        global.battleState.enemyId = enemyId;
        global.battleState.bossId = null;
        saveActivities();
        return enemyId;
    },
    bossfightStart: function(bossId) { 
        activities.push({ type: 'battle.bossfightStart', bossId: bossId, time: getTimestamp() }); 
        global.battleState.active = true;
        global.battleState.bossId = bossId;
        global.battleState.enemyId = null;
        saveActivities();
        return bossId;
    },
    
    flee: function() { 
        activities.push({ type: 'battle.flee', time: getTimestamp() }); 
        global.battleState.active = false;
        saveActivities();
        return true;
    },
    lose: function() { 
        activities.push({ type: 'battle.lose', time: getTimestamp() }); 
        global.battleState.active = false;
        saveActivities();
        return true;
    },
    win: function() { 
        activities.push({ type: 'battle.win', time: getTimestamp() }); 
        global.battleState.active = false;
        saveActivities();
        return true;
    }
};

// Map API object
var map = {
    getAvalaibleMaterials: function() { 
        activities.push({ type: 'map.getAvalaibleMaterials', time: getTimestamp() }); 
        return [];
    },
    getAvalaibleBoss: function() { 
        activities.push({ type: 'map.getAvalaibleBoss', time: getTimestamp() }); 
        return [];
    },
    getAvalaibleMonster: function() { 
        activities.push({ type: 'map.getAvalaibleMonster', time: getTimestamp() }); 
        return [];
    },
    getAvalaibleShops: function() { 
        activities.push({ type: 'map.getAvalaibleShops', time: getTimestamp() }); 
        return [];
    },
    getAvalaibleConnections: function() { 
        activities.push({ type: 'map.getAvalaibleConnections', time: getTimestamp() }); 
        return global.locationState.connections || [];
    },
    
    getCanRest: function() { 
        activities.push({ type: 'map.getCanRest', time: getTimestamp() }); 
        return global.locationState.canRest || false;
    },
    getCanRestCosts: function() { 
        activities.push({ type: 'map.getCanRestCosts', time: getTimestamp() }); 
        return global.locationState.restCost || 0;
    },
    getDifficulty: function() { 
        activities.push({ type: 'map.getDifficulty', time: getTimestamp() }); 
        return global.locationState.difficulty || 1;
    }
};

// Missions API object
var missions = {
    getFinished: function() { 
        activities.push({ type: 'missions.getFinished', time: getTimestamp() }); 
        return global.missionsState.finished || [];
    },
    getOngoing: function() { 
        activities.push({ type: 'missions.getOngoing', time: getTimestamp() }); 
        return global.missionsState.ongoing || [];
    },
    getNotAccepted: function() { 
        activities.push({ type: 'missions.getNotAccepted', time: getTimestamp() }); 
        return global.missionsState.notAccepted || [];
    },
    
    accept: function(missionId) { 
        activities.push({ type: 'missions.accept', missionId: missionId, time: getTimestamp() }); 
        if (!global.missionsState.ongoing) global.missionsState.ongoing = [];
        if (global.missionsState.notAccepted) {
            var idx = global.missionsState.notAccepted.indexOf(missionId);
            if (idx !== -1) global.missionsState.notAccepted.splice(idx, 1);
        }
        global.missionsState.ongoing.push(missionId);
        saveActivities();
        return missionId;
    },
    finish: function(missionId) { 
        activities.push({ type: 'missions.finish', missionId: missionId, time: getTimestamp() }); 
        if (global.missionsState.ongoing) {
            var idx = global.missionsState.ongoing.indexOf(missionId);
            if (idx !== -1) global.missionsState.ongoing.splice(idx, 1);
        }
        if (!global.missionsState.finished) global.missionsState.finished = [];
        global.missionsState.finished.push(missionId);
        saveActivities();
        return missionId;
    },
    
    deleteFromOngoing: function(missionId) { 
        activities.push({ type: 'missions.deleteFromOngoing', missionId: missionId, time: getTimestamp() }); 
        if (global.missionsState.ongoing) {
            var idx = global.missionsState.ongoing.indexOf(missionId);
            if (idx !== -1) global.missionsState.ongoing.splice(idx, 1);
            saveActivities();
        }
        return missionId;
    },
    deleteFromFinished: function(missionId) { 
        activities.push({ type: 'missions.deleteFromFinished', missionId: missionId, time: getTimestamp() }); 
        if (global.missionsState.finished) {
            var idx = global.missionsState.finished.indexOf(missionId);
            if (idx !== -1) global.missionsState.finished.splice(idx, 1);
            saveActivities();
        }
        return missionId;
    }
};

// System API object
var system = {
    latest_save: function() { 
        activities.push({ type: 'system.latest_save', time: getTimestamp() }); 
        return global.systemState.latestSave || null;
    },
    saveGame: function() { 
        activities.push({ type: 'system.saveGame', time: getTimestamp() }); 
        saveActivities();
        return true;
    },
    deleteSaveFile: function() { 
        activities.push({ type: 'system.deleteSaveFile', time: getTimestamp() }); 
        return true;
    },
    hideMenu: function() {
        // Clears the terminal screen
        activities.push({ type: 'system.hideMenu', time: getTimestamp() });
        if (typeof console !== 'undefined' && console.log) {
            console.log("__HIDE_MENU__");
        }
    },
    showMenu: function() {
        // Shows the game menu again
        activities.push({ type: 'system.showMenu', time: getTimestamp() });
        if (typeof console !== 'undefined' && console.log) {
            console.log("__SHOW_MENU__");
        }
    }
};

// Events system
var events = {
    listeners: {},
    
    on: function(eventName, callback) {
        if (!this.listeners[eventName]) {
            this.listeners[eventName] = [];
        }
        this.listeners[eventName].push(callback);
        activities.push({ type: 'events.on', eventName: eventName, time: getTimestamp() });
    },
    
    emit: function(eventName, data) {
        activities.push({ type: 'events.emit', eventName: eventName, time: getTimestamp() });
        if (this.listeners[eventName]) {
            for (var i = 0; i < this.listeners[eventName].length; i++) {
                try {
                    this.listeners[eventName][i](data);
                } catch (e) {
                    print("Error in event handler: " + e);
                }
            }
        }
    }
};

// Utility functions
function print(message) {
    // This will be replaced with actual print function from the game
    if (typeof globalPrint !== 'undefined') {
        globalPrint(message);
    } else if (typeof console !== 'undefined' && console.log) {
        console.log(message);
    }
}

// tellraw - display raw text on screen without [script] prefix
// Uses a special marker that the game engine detects to print without prefix
function tellraw(message) {
    if (typeof globalPrint !== 'undefined') {
        globalPrint("__RAW_OUTPUT__" + message);
    } else if (typeof console !== 'undefined' && console.log) {
        console.log("__RAW_OUTPUT__" + message);
    }
}

function log(message) {
    activities.push({ type: 'log', message: message, time: getTimestamp() });
}

function getActivities() {
    return activities;
}

function clearActivities() {
    activities = [];
}

function getActivityCount() {
    return activities.length;
}

// Export for QuickJS and Node.js
// For QuickJS: use globalThis (or just assign to the global object)
// For Node.js: use global
var _exportTarget = (typeof globalThis !== 'undefined') ? globalThis : (typeof global !== 'undefined') ? global : this;

_exportTarget.player = player;
_exportTarget.enemy = enemy;
_exportTarget.battle = battle;
_exportTarget.map = map;
_exportTarget.missions = missions;
_exportTarget.system = system;
_exportTarget.events = events;
_exportTarget.getActivities = getActivities;
_exportTarget.clearActivities = clearActivities;
_exportTarget.getActivityCount = getActivityCount;
_exportTarget.log = log;
_exportTarget.print = print;
_exportTarget.tellraw = tellraw;
_exportTarget.Date = Date;
_exportTarget.JSON = JSON;
_exportTarget.activities = activities;
_exportTarget.loadActivities = loadActivities;
_exportTarget.saveActivities = saveActivities;

// Also export for ES modules
export {
    player,
    enemy,
    battle,
    map,
    missions,
    system,
    events,
    getActivities,
    clearActivities,
    getActivityCount,
    log,
    print,
    tellraw,
    activities,
    loadActivities,
    saveActivities
};

// For ES modules in Node.js, also assign to globalThis explicitly
if (typeof globalThis !== 'undefined') {
    globalThis.player = player;
    globalThis.enemy = enemy;
    globalThis.battle = battle;
    globalThis.map = map;
    globalThis.missions = missions;
    globalThis.system = system;
    globalThis.events = events;
    globalThis.getActivities = getActivities;
    globalThis.clearActivities = clearActivities;
    globalThis.getActivityCount = getActivityCount;
    globalThis.log = log;
    globalThis.print = print;
    globalThis.activities = activities;
    globalThis.loadActivities = loadActivities;
    globalThis.saveActivities = saveActivities;
}

