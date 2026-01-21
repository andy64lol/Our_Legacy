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
            if (!fs.existsSync(ACTIVITIES_FILE)) {
                return false;
            }
            var data = fs.readFileSync(ACTIVITIES_FILE, 'utf8');
            if (!data) return false;
            var parsed = JSON.parse(data);
            
            // Load state
            if (parsed.player) global.playerState = parsed.player;
            if (parsed.location) global.locationState = parsed.location;
            if (parsed.enemy) global.enemyState = parsed.enemy;
            if (parsed.battle) global.battleState = parsed.battle;
            if (parsed.missions) global.missionsState = parsed.missions;
            if (parsed.system) global.systemState = parsed.system;
            if (parsed.effects) global.effectsState = parsed.effects;
            if (parsed.activities) activities = parsed.activities;
            
            return true;
        } catch (e) {
            return false;
        }
    }
    return false;
}

// Save activities to file
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
            return true;
        } catch (e) {
            return false;
        }
    }
    return false;
}

// Initialize global state
if (typeof global !== 'undefined') {
    if (!global.playerState) global.playerState = { health: 100, maxHealth: 100, mp: 50, maxMP: 50, level: 1, gold: 100, inventory: [], companions: [], equipped: {} };
    if (!global.locationState) global.locationState = { id: "starting_village", connections: [] };
    if (!global.enemyState) global.enemyState = { hp: 0 };
    if (!global.battleState) global.battleState = { active: false };
    if (!global.missionsState) global.missionsState = { finished: [], ongoing: [], notAccepted: [] };
    if (!global.systemState) global.systemState = {};
    if (!global.effectsState) global.effectsState = [];
}

if (typeof require !== 'undefined') loadActivities();

// APIs
var player = {
    uuid: function() { return global.playerState.uuid || ''; },
    name: function() { return global.playerState.name || ''; },
    class: function() { return global.playerState.class || ''; },
    changeName: function(n) { activities.push({type:'changeName', name:n}); global.playerState.name=n; saveActivities(); },
    changeClass: function(c) { activities.push({type:'changeClass', class:c}); global.playerState.class=c; saveActivities(); },
    getHealth: function() { return global.playerState.health || 0; },
    getMaxHealth: function() { return global.playerState.maxHealth || 0; },
    setHealth: function(v) { global.playerState.health=v; saveActivities(); },
    addHealth: function(a) { global.playerState.health=(global.playerState.health||0)+a; saveActivities(); },
    getMP: function() { return global.playerState.mp || 0; },
    setMP: function(v) { global.playerState.mp=v; saveActivities(); },
    addMP: function(a) { global.playerState.mp=(global.playerState.mp||0)+a; saveActivities(); },
    hasEffect: function(id) { return global.effectsState.indexOf(id)!==-1; },
    addEffect: function(id) { if(global.effectsState.indexOf(id)===-1){global.effectsState.push(id);saveActivities();} },
    location: function() { return { id: global.locationState.id, name: global.locationState.name }; },
    setLocation: function(id) { global.locationState.id=id; saveActivities(); },
    level: { set: function(v) { global.playerState.level=v; saveActivities(); }, add: function(a) { global.playerState.level=(global.playerState.level||1)+a; saveActivities(); } },
    exp: { set: function(v) { global.playerState.exp=v; saveActivities(); }, add: function(a) { global.playerState.exp=(global.playerState.exp||0)+a; saveActivities(); } },
    gold: function() { return global.playerState.gold || 0; },
    giveGold: function(a) { global.playerState.gold=(global.playerState.gold||0)+(a||0); saveActivities(); },
    deleteGold: function(a) { global.playerState.gold=Math.max(0, (global.playerState.gold||0)-(a||0)); saveActivities(); },
    inventory: function() { return global.playerState.inventory || []; },
    addItem: function(id, a) { activities.push({type:'addItem', id:id, amount:a||1}); saveActivities(); },
    removeItem: function(id, a) { activities.push({type:'removeItem', id:id, amount:a||1}); saveActivities(); },
    companions: function() { return global.playerState.companions || []; }
};

var enemy = {
    id: function() { return global.enemyState.id || ''; },
    hp: function() { return global.enemyState.hp || 0; },
    setCurrentHP: function(v) { global.enemyState.hp=v; saveActivities(); }
};

var battle = {
    start: function(id) { activities.push({type:'battle.start', id:id}); saveActivities(); },
    win: function() { activities.push({type:'battle.win'}); saveActivities(); }
};

var menu = {
    addButton: function(id, label, action) { print('__ADD_BUTTON__' + JSON.stringify({id:id, label:label, action:action})); },
    removeButton: function(id) { print('__REMOVE_BUTTON__' + id); },
    hide: function() { print('__HIDE_MENU__'); },
    show: function() { print('__SHOW_MENU__'); }
};

function tellraw(msg) { print('__RAW_OUTPUT__' + msg); }
function print(msg) { console.log(msg); }
function log(msg) { console.log("[" + new Date().toISOString() + "] " + msg); }

if (typeof exports !== 'undefined') {
    exports.player = player; exports.enemy = enemy; exports.battle = battle;
    exports.menu = menu; exports.tellraw = tellraw; exports.print = print; exports.log = log;
}
