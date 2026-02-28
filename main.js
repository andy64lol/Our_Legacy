/**
 * Our Legacy - Browser-Based Fantasy RPG Game
 * Ported from main.py for browser use
 * Andy64lol
 */

// Import utility modules
import { Character } from './utilities_js/character.js';
import { BattleSystem, create_hp_mp_bar, create_boss_hp_bar } from './utilities_js/battle.js';
import { SpellCastingSystem } from './utilities_js/spellcasting.js';
import { SaveLoadSystem } from './utilities_js/save_load.js';
import { LanguageManager } from './utilities_js/language.js';
import { SettingsManager, Colors, ModManager } from './utilities_js/settings.js';
import { Enemy, Boss } from './utilities_js/entities.js';
import { Dice } from './utilities_js/dice.js';

// Game API URL for market
let gameApi = null;

// Add isDigit helper to String prototype
if (!String.prototype.isDigit) {
    String.prototype.isDigit = function() {
        return /^\d+$/.test(this);
    };
}

// Add contains helper
if (!String.prototype.contains) {
    String.prototype.contains = function(str) {
        return this.indexOf(str) !== -1;
    };
}

/**
 * Main Game class for browser
 */
export class Game {
    constructor() {
        this.player = null;
        this.currentArea = "starting_village";
        this.visitedAreas = new Set();
        
        // Game data objects
        this.enemiesData = {};
        this.areasData = {};
        this.itemsData = {};
        this.missionsData = {};
        this.bossesData = {};
        this.classesData = {};
        this.spellsData = {};
        this.effectsData = {};
        this.companionsData = {};
        this.dialoguesData = {};
        this.dungeonsData = {};
        this.cutscenesData = {};
        this.craftingData = {};
        this.weeklyChallengesData = {};
        this.housingData = {};
        this.shopsData = {};
        this.farmingData = {};
        this.petsData = {};
        this.weatherData = {};
        this.timesData = {};
        
        // Mission progress
        this.missionProgress = {};
        this.completedMissions = [];
        
        // Challenge tracking
        this.challengeProgress = {};
        this.completedChallenges = [];
        
        // Dungeon state
        this.currentDungeon = null;
        this.dungeonProgress = 0;
        this.dungeonRooms = [];
        this.dungeonState = {};
        
        // Initialize systems
        this.settingsManager = new SettingsManager();
        this.lang = new LanguageManager(
            (key) => this.settingsManager.get(key),
            (key, value) => this.settingsManager.set(key, value)
        );
        
        // Initialize mod manager
        this.modManager = new ModManager(
            (key) => this.lang.get(key),
            "game_mod_settings"
        );
        
        // Game systems
        this.battleSystem = null;
        this.spellCastingSystem = null;
        this.saveLoadSystem = null;
        this.diceUtil = new Dice();
        
        // UI callback for browser input
        this.inputCallback = null;
        this.resolveInput = null;
    }
    
    /**
     * Initialize the game - load all data
     */
    async init() {
        console.log(`%cOur Legacy - Browser RPG%c`, Colors.CYAN + Colors.BOLD, Colors.END);
        console.log("Loading game data...");
        
        await this.loadGameData();
        this.loadConfig();
        
        // Initialize systems that need game instance
        this.battleSystem = new BattleSystem(this);
        this.spellCastingSystem = new SpellCastingSystem(this);
        this.saveLoadSystem = new SaveLoadSystem(this);
        
        console.log("%cGame loaded successfully!%c", Colors.GREEN, Colors.END);
    }
    
    /**
     * Load all game data from JSON files
     */
    async loadGameData() {
        const loadPromises = [];
        
        // Load core data files
        const dataFiles = [
            { key: 'enemiesData', file: 'data/enemies.json' },
            { key: 'areasData', file: 'data/areas.json' },
            { key: 'itemsData', file: 'data/items.json' },
            { key: 'missionsData', file: 'data/missions.json' },
            { key: 'bossesData', file: 'data/bosses.json' },
            { key: 'classesData', file: 'data/classes.json' },
            { key: 'spellsData', file: 'data/spells.json' },
            { key: 'effectsData', file: 'data/effects.json' },
            { key: 'companionsData', file: 'data/companions.json', optional: true },
            { key: 'craftingData', file: 'data/crafting.json', optional: true },
            { key: 'dialoguesData', file: 'data/dialogues.json', optional: true },
            { key: 'cutscenesData', file: 'data/cutscenes.json', optional: true },
            { key: 'weatherData', file: 'data/weather.json', optional: true },
            { key: 'timesData', file: 'data/times.json', optional: true },
            { key: 'dungeonsData', file: 'data/dungeons.json', optional: true },
            { key: 'weeklyChallengesData', file: 'data/weekly_challenges.json', optional: true },
            { key: 'housingData', file: 'data/housing.json', optional: true },
            { key: 'shopsData', file: 'data/shops.json', optional: true },
            { key: 'farmingData', file: 'data/farming.json', optional: true },
            { key: 'petsData', file: 'data/pets.json', optional: true }
        ];
        
        for (const { key, file, optional } of dataFiles) {
            loadPromises.push(
                fetch(file)
                    .then(response => {
                        if (!response.ok) {
                            if (optional) return [key, {}];
                            throw new Error(`Failed to load ${file}`);
                        }
                        return response.json().then(data => [key, data]);
                    })
                    .catch(err => {
                        if (optional) return [key, {}];
                        console.warn(`Warning: ${file} not found`);
                        return [key, {}];
                    })
            );
        }
        
        const results = await Promise.all(loadPromises);
        for (const [key, data] of results) {
            this[key] = data;
        }
        
        // Apply mod data
        await this.loadModData();
        
        // Initialize challenge progress
        if (this.weeklyChallengesData.challenges) {
            for (const challenge of this.weeklyChallengesData.challenges) {
                this.challengeProgress[challenge.id] = 0;
            }
        }
    }
    
    /**
     * Load and merge mod data
     */
    async loadModData() {
        // Discover mods
        await this.modManager.discoverMods();
        
        const enabledMods = this.modManager.getEnabledMods();
        if (!enabledMods || enabledMods.length === 0) return;
        
        console.log("%cLoading mods...%c", Colors.YELLOW, Colors.END);
        
        const modDataTypes = [
            'areas.json', 'enemies.json', 'items.json', 'missions.json',
            'bosses.json', 'companions.json', 'classes.json', 'spells.json',
            'effects.json', 'crafting.json', 'dungeons.json', 'dialogues.json',
            'cutscenes.json', 'weekly_challenges.json', 'housing.json',
            'shops.json', 'weather.json', 'times.json'
        ];
        
        for (const fileName of modDataTypes) {
            const modData = await this.modManager.loadModData(fileName);
            if (modData && Object.keys(modData).length > 0) {
                const attrName = this.getAttrNameFromFile(fileName);
                if (attrName && this[attrName]) {
                    Object.assign(this[attrName], modData);
                }
            }
        }
    }
    
    /**
     * Get attribute name from JSON filename
     */
    getAttrNameFromFile(fileName) {
        const mapping = {
            'areas.json': 'areasData',
            'enemies.json': 'enemiesData',
            'items.json': 'itemsData',
            'missions.json': 'missionsData',
            'bosses.json': 'bossesData',
            'companions.json': 'companionsData',
            'classes.json': 'classesData',
            'spells.json': 'spellsData',
            'effects.json': 'effectsData',
            'crafting.json': 'craftingData',
            'dungeons.json': 'dungeonsData',
            'dialogues.json': 'dialoguesData',
            'cutscenes.json': 'cutscenesData',
            'weekly_challenges.json': 'weeklyChallengesData',
            'housing.json': 'housingData',
            'shops.json': 'shopsData',
            'weather.json': 'weatherData',
            'times.json': 'timesData'
        };
        return mapping[fileName];
    }
    
    /**
     * Load configuration
     */
    loadConfig() {
        // Initialize settings
        this.settingsManager.loadSettings();
        
        // Set up language
        const savedLang = this.settingsManager.get('language', 'en');
        if (savedLang && savedLang !== this.lang.currentLanguage) {
            this.lang.changeLanguage(savedLang);
        }
    }
    
    /**
     * Display welcome screen
     */
    async displayWelcome() {
        console.clear();
        console.log(`%c${'='.repeat(60)}%c`, Colors.CYAN, Colors.END);
        console.log(`%c       ${this.lang.get('game_title_display', 'Our Legacy')}%c`, Colors.CYAN + Colors.BOLD, Colors.END);
        console.log(`%c       ${this.lang.get('game_subtitle_display', 'A Text-Based RPG')}%c`, Colors.YELLOW, Colors.END);
        console.log(`%c${'='.repeat(60)}%c`, Colors.CYAN, Colors.END);
        console.log();
        console.log(this.lang.get('welcome_message', 'Welcome to Our Legacy!'));
        console.log('Choose your path wisely, for every decision shapes your destiny.');
        console.log();
        
        console.log(`%c=== ${this.lang.get('main_menu', 'MAIN MENU')} ===%c`, Colors.CYAN + Colors.BOLD, Colors.END);
        console.log(`${Colors.CYAN}1.${Colors.END} ${this.lang.get('new_game', 'New Game')}`);
        console.log(`${Colors.CYAN}2.${Colors.END} ${this.lang.get('load_game', 'Load Game')}`);
        console.log(`${Colors.CYAN}3.${Colors.END} ${this.lang.get('settings', 'Settings')}`);
        console.log(`${Colors.CYAN}4.${Colors.END} ${this.lang.get('mods', 'Mods')}`);
        console.log(`${Colors.CYAN}5.${Colors.END} ${this.lang.get('quit', 'Quit')}`);
        console.log();
        
        const choice = await this.ask(`${Colors.CYAN}Choose an option (1-5): ${Colors.END}`);
        
        if (choice === "1") {
            return "new_game";
        } else if (choice === "2") {
            return "load_game";
        } else if (choice === "3") {
            await this.settingsWelcome();
            return await this.displayWelcome();
        } else if (choice === "4") {
            await this.modsWelcome();
            return await this.displayWelcome();
        } else if (choice === "5") {
            console.log(this.lang.get('thank_exit', 'Thank you for playing!'));
            return "quit";
        } else {
            console.log(this.lang.get('invalid_choice', 'Invalid choice'));
            return await this.displayWelcome();
        }
    }
    
    /**
     * Settings menu
     */
    async settingsWelcome() {
        console.log(`\n%c=== SETTINGS ===%c`, Colors.CYAN + Colors.BOLD, Colors.END);
        
        const modsEnabled = this.modManager.settings.mods_enabled;
        
        console.log(`\n1. Mod System: ${modsEnabled ? Colors.GREEN + 'Enabled' + Colors.END : Colors.RED + 'Disabled' + Colors.END}`);
        console.log(`2. Language`);
        console.log(`3. ${this.lang.get('back', 'Back')}`);
        
        const choice = await this.ask("\nChoose an option: ");
        
        if (choice === "1") {
            this.modManager.toggleModsSystem();
            console.log(`Mod system ${this.modManager.settings.mods_enabled ? 'enabled' : 'disabled'}!`);
        } else if (choice === "2") {
            await this.changeLanguageMenu();
        }
    }
    
    /**
     * Change language menu
     */
    async changeLanguageMenu() {
        console.log(`\n%c=== LANGUAGE ===%c`, Colors.CYAN + Colors.BOLD, Colors.END);
        
        const available = this.lang.config.available_languages || { en: "English" };
        const langs = Object.entries(available);
        
        for (let i = 0; i < langs.length; i++) {
            const [code, name] = langs[i];
            console.log(`${Colors.CYAN}${i + 1}.${Colors.END} ${name}`);
        }
        console.log(`${Colors.CYAN}${langs.length + 1}.${Colors.END} Back`);
        
        const choice = await this.ask(`${Colors.CYAN}Choose a language: ${Colors.END}`);
        
        if (choice.isDigit()) {
            const idx = parseInt(choice) - 1;
            if (idx >= 0 && idx < langs.length) {
                await this.lang.changeLanguage(langs[idx][0]);
                console.log(`Language changed to ${langs[idx][1]}!`);
            }
        }
    }
    
    /**
     * Mods menu
     */
    async modsWelcome() {
        console.log(`\n%c=== MODS ===%c`, Colors.CYAN + Colors.BOLD, Colors.END);
        
        await this.modManager.discoverMods();
        const modsList = this.modManager.getModList();
        
        if (!modsList || modsList.length === 0) {
            console.log(`\n%c${this.lang.get('no_mods_found', 'No mods found')}%c`, Colors.YELLOW, Colors.END);
            console.log(this.lang.get('place_mods_instruction', 'Place mods in the mods/ folder'));
            await this.ask("\nPress Enter to go back...");
            return;
        }
        
        const modsSystemEnabled = this.modManager.settings.mods_enabled;
        const statusColor = modsSystemEnabled ? Colors.GREEN : Colors.RED;
        console.log(`\nMod System Status: ${statusColor}${modsSystemEnabled ? 'Enabled' : 'Disabled'}${Colors.END}`);
        
        console.log(`\n%cInstalled Mods (${modsList.length}):%c`, Colors.CYAN, Colors.END);
        
        for (let i = 0; i < modsList.length; i++) {
            const mod = modsList[i];
            const status = mod.enabled ? Colors.GREEN + '[ENABLED]' + Colors.END : Colors.RED + '[DISABLED]' + Colors.END;
            console.log(`\n${i + 1}. %c${mod.name || mod.folder_name}%c ${status}`);
            console.log(`   Version: ${mod.version || '1.0'}`);
            console.log(`   Author: ${mod.author || 'Unknown'}`);
            if (mod.description) {
                console.log(`   ${mod.description.substring(0, 100)}`);
            }
        }
        
        console.log(`\nOptions:`);
        console.log(`1-${modsList.length}. Toggle Mod`);
        console.log(`B. Back`);
        
        const choice = await this.ask("\nChoose an option: ");
        
        if (choice.toUpperCase() === 'B') return;
        
        if (choice.isDigit()) {
            const idx = parseInt(choice) - 1;
            if (idx >= 0 && idx < modsList.length) {
                const mod = modsList[idx];
                this.modManager.toggleMod(mod.folder_name);
                console.log(`Mod "${mod.name}" toggled. Changes take effect on restart.`);
            }
        }
    }
    
    /**
     * Create a new character
     */
    async createCharacter() {
        console.log(`%c${this.lang.get('character_creation', '=== CHARACTER CREATION ===')}%c`, Colors.BOLD, Colors.END);
        console.log('-'.repeat(30));
        
        const name = await this.ask(this.lang.get('enter_name', 'Enter your name: '));
        const playerName = name.trim() || "Hero";
        
        // Display available classes
        console.log(`\n${this.lang.get('ui_choose_class', 'Available Classes:')}`);
        
        const colorMap = [Colors.RED, Colors.BLUE, Colors.GREEN, Colors.YELLOW, Colors.MAGENTA, Colors.CYAN];
        const classEntries = Object.entries(this.classesData);
        
        for (let i = 0; i < classEntries.length; i++) {
            const [className, classData] = classEntries[i];
            const color = colorMap[i % colorMap.length];
            const description = classData.description || "No description available";
            console.log(`${color}${i + 1}. ${className}${Colors.END} - ${description}`);
        }
        
        const choice = await this.ask(`\nEnter class choice (1-${classEntries.length}): `);
        let selectedClass = null;
        
        if (choice.isDigit()) {
            const idx = parseInt(choice) - 1;
            if (idx >= 0 && idx < classEntries.length) {
                selectedClass = classEntries[idx][0];
            }
        }
        
        // Fallback to first class if invalid
        if (!selectedClass) {
            selectedClass = classEntries[0][0];
        }
        
        // Create character
        this.player = new Character(playerName, selectedClass, this.classesData, null, this.lang);
        
        // Set weather and times data
        this.player.weatherData = this.weatherData;
        this.player.timesData = this.timesData;
        
        // Give starting items
        this.giveStartingItems(selectedClass);
        
        console.log(`\n%c${this.lang.get('welcome_adventurer', `Welcome, ${playerName} the ${selectedClass}!`)}%c`, Colors.GREEN, Colors.END);
        
        this.displayPlayerStats();
    }
    
    /**
     * Give starting items based on class
     */
    giveStartingItems(characterClass) {
        if (!this.player || !this.classesData[characterClass]) return;
        
        const classInfo = this.classesData[characterClass];
        const items = classInfo.starting_items || [];
        const startingGold = classInfo.starting_gold || 100;
        
        for (const item of items) {
            this.player.inventory.push(item);
        }
        
        this.player.gold = startingGold;
        
        if (items.length > 0) {
            console.log(`%cYou received starting equipment:%c`, Colors.YELLOW, Colors.END);
            for (const item of items) {
                console.log(`  - ${item}`);
            }
            
            // Auto-equip first weapon and armor
            for (const slot of ["weapon", "armor"]) {
                for (const item of items) {
                    const itemType = this.itemsData[item]?.type;
                    if (itemType === slot) {
                        this.player.equip(item, this.itemsData);
                        console.log(`Equipped: ${item}`);
                        break;
                    }
                }
            }
        }
    }
    
    /**
     * Display player stats
     */
    displayPlayerStats() {
        if (!this.player) {
            console.log(this.lang.get('no_character', 'No character created'));
            return;
        }
        
        console.log(`\n%c=== ${this.player.name} - Level ${this.player.level} ${this.player.rank} ===%c`, Colors.CYAN + Colors.BOLD, Colors.END);
        console.log(`HP: ${create_hp_mp_bar(this.player.hp, this.player.maxHp, 15, Colors.RED)} ${this.player.hp}/${this.player.maxHp}`);
        console.log(`MP: ${create_hp_mp_bar(this.player.mp, this.player.maxMp, 15, Colors.BLUE)} ${this.player.mp}/${this.player.maxMp}`);
        console.log(`Attack: ${this.player.attack} | Defense: ${this.player.defense} | Speed: ${this.player.speed}`);
        console.log(`Gold: ${Colors.GOLD}${this.player.gold}${Colors.END}`);
        console.log(`Level: ${this.player.level} | XP: ${this.player.experience}/${this.player.experienceToNext}`);
    }
    
    /**
     * Main game loop
     */
    async run() {
        const choice = await this.displayWelcome();
        
        if (choice === "new_game") {
            await this.createCharacter();
        } else if (choice === "load_game") {
            await this.loadGame();
            if (!this.player) {
                console.log(this.lang.get('ui_no_game_loaded', 'No game loaded'));
                await this.createCharacter();
            }
        } else if (choice === "quit") {
            console.log("Thanks for playing!");
            return;
        }
        
        // Main game loop
        while (true) {
            await this.mainMenu();
        }
    }
    
    /**
     * Main menu
     */
    async mainMenu() {
        // Advance time
        if (this.player) {
            this.player.advanceTime(10);
        }
        
        // Check mission progress
        this.updateMissionProgress('check', '');
        
        // Check challenges
        if (this.player) {
            this.updateChallengeProgress('level_reach', this.player.level);
        }
        
        console.log(`\n%c=== ${this.lang.get('main_menu', 'MAIN MENU')} ===%c`, Colors.BOLD, Colors.END);
        
        // Show current location
        const areaData = this.areasData[this.currentArea] || {};
        const areaName = areaData.name || this.currentArea;
        console.log(this.lang.get('current_location', `Location: ${areaName}`));
        
        // Display time and weather
        if (this.player) {
            const displayHour = Math.floor(this.player.hour);
            const displayMinute = Math.floor((this.player.hour - displayHour) * 60);
            const timeStr = `${String(displayHour).padStart(2, '0')}:${String(displayMinute).padStart(2, '0')}`;
            const dayStr = `Day ${this.player.day}`;
            const weatherDesc = this.player.getWeatherDescription ? this.player.getWeatherDescription(this.lang) : this.player.currentWeather;
            
            console.log(`${Colors.YELLOW}${timeStr} | ${dayStr}${Colors.END}`);
            console.log(`${Colors.CYAN}${weatherDesc}${Colors.END}`);
        }
        
        console.log(`${Colors.CYAN}1.${Colors.END} ${this.lang.get('explore', 'Explore')}`);
        console.log(`${Colors.CYAN}2.${Colors.END} ${this.lang.get('view_character', 'View Character')}`);
        console.log(`${Colors.CYAN}3.${Colors.END} ${this.lang.get('travel', 'Travel')}`);
        console.log(`${Colors.CYAN}4.${Colors.END} ${this.lang.get('inventory', 'Inventory')}`);
        console.log(`${Colors.CYAN}5.${Colors.END} ${this.lang.get('missions', 'Missions')}`);
        console.log(`${Colors.CYAN}6.${Colors.END} ${this.lang.get('fight_boss', 'Fight Boss')}`);
        console.log(`${Colors.CYAN}7.${Colors.END} ${this.lang.get('tavern', 'Tavern')}`);
        console.log(`${Colors.CYAN}8.${Colors.END} ${this.lang.get('shop', 'Shop')}`);
        console.log(`${Colors.CYAN}9.${Colors.END} ${this.lang.get('rest', 'Rest')}`);
        console.log(`${Colors.CYAN}10.${Colors.END} ${this.lang.get('companions', 'Companions')}`);
        
        if (this.currentArea === "your_land") {
            console.log(`${Colors.CYAN}11.${Colors.END} ${this.lang.get('pet_shop', 'Pet Shop')}`);
            console.log(`${Colors.CYAN}12.${Colors.END} ${this.lang.get('build_home', 'Build Home')}`);
            console.log(`${Colors.CYAN}13.${Colors.END} ${this.lang.get('save_game', 'Save Game')}`);
            console.log(`${Colors.CYAN}14.${Colors.END} ${this.lang.get('load_game', 'Load Game')}`);
            console.log(`${Colors.CYAN}15.${Colors.END} ${this.lang.get('quit', 'Quit')}`);
        } else {
            console.log(`${Colors.CYAN}11.${Colors.END} ${this.lang.get('save_game', 'Save Game')}`);
            console.log(`${Colors.CYAN}12.${Colors.END} ${this.lang.get('load_game', 'Load Game')}`);
            console.log(`${Colors.CYAN}13.${Colors.END} ${this.lang.get('quit', 'Quit')}`);
        }
        
        const maxChoice = this.currentArea === "your_land" ? "15" : "13";
        const choice = await this.ask(`${Colors.CYAN}Choose an option (1-${maxChoice}): ${Colors.END}`);
        
        switch (choice) {
            case "1": await this.explore(); break;
            case "2": this.displayPlayerStats(); break;
            case "3": await this.travel(); break;
            case "4": await this.viewInventory(); break;
            case "5": await this.viewMissions(); break;
            case "6": await this.fightBossMenu(); break;
            case "7": await this.visitTavern(); break;
            case "8": await this.visitShop(); break;
            case "9": await this.rest(); break;
            case "10": await this.manageCompanions(); break;
            case "11":
                if (this.currentArea === "your_land") {
                    await this.petShop();
                } else {
                    await this.saveGame();
                }
                break;
            case "12":
                if (this.currentArea === "your_land") {
                    await this.buildHome();
                } else {
                    await this.loadGame();
                }
                break;
            case "13":
                if (this.currentArea === "your_land") {
                    await this.saveGame();
                } else {
                    console.log(this.lang.get('thank_exit', 'Thanks for playing!'));
                    return;
                }
                break;
            case "14":
                if (this.currentArea === "your_land") {
                    await this.loadGame();
                }
                break;
            case "15":
                if (this.currentArea === "your_land") {
                    console.log(this.lang.get('thank_exit', 'Thanks for playing!'));
                    return;
                }
                break;
            default:
                console.log(this.lang.get('invalid_choice', 'Invalid choice'));
        }
    }
    
    /**
     * Explore current area
     */
    async explore() {
        if (!this.player) {
            console.log(this.lang.get('no_character_created', 'No character created'));
            return;
        }
        
        this.player.advanceTime(5);
        this.updateMissionProgress('check', '');
        
        const areaData = this.areasData[this.currentArea] || {};
        const areaName = areaData.name || "Unknown Area";
        
        console.log(this.lang.get('exploring_area_msg', `Exploring ${areaName}...`));
        
        // 70% chance of encounter
        if (Math.random() < 0.7) {
            await this.randomEncounter();
        } else {
            console.log(this.lang.get('explore_nothing_found', 'You explore the area but find nothing.'));
            
            // Small chance to find gold
            if (Math.random() < 0.3) {
                const foundGold = Math.floor(Math.random() * 15) + 5;
                this.player.gold += foundGold;
                console.log(this.lang.get('found_gold_msg', `You found ${foundGold} gold!`));
            }
        }
    }
    
    /**
     * Random encounter
     */
    async randomEncounter() {
        if (!this.player) return;
        
        const areaData = this.areasData[this.currentArea] || {};
        const possibleEnemies = areaData.possible_enemies || [];
        
        if (possibleEnemies.length === 0) {
            console.log(this.lang.get('no_enemies_in_area', 'No enemies in this area'));
            return;
        }
        
        const enemyName = possibleEnemies[Math.floor(Math.random() * possibleEnemies.length)];
        const enemyData = this.enemiesData[enemyName];
        
        if (enemyData) {
            const enemy = new Enemy(enemyData);
            console.log(`\n%cA wild ${enemy.name} appears!%c`, Colors.RED + Colors.BOLD, Colors.END);
            await this.battle(enemy);
        }
    }
    
    /**
     * Battle system
     */
    async battle(enemy) {
        await this.battleSystem.battle(enemy);
    }
    
    /**
     * Travel to connected areas
     */
    async travel() {
        if (!this.player) {
            console.log(this.lang.get('no_character', 'No character'));
            return;
        }
        
        const areaData = this.areasData[this.currentArea] || {};
        const connections = areaData.connections || [];
        
        console.log(`\n%c=== TRAVEL ===%c`, Colors.CYAN + Colors.BOLD, Colors.END);
        console.log(`Current location: ${areaData.name || this.currentArea}`);
        
        if (connections.length === 0) {
            console.log(this.lang.get('no_connected_areas', 'No connected areas'));
            return;
        }
        
        console.log(this.lang.get('ui_connected_areas', 'Connected areas:'));
        for (let i = 0; i < connections.length; i++) {
            const area = this.areasData[connections[i]] || {};
            console.log(`${i + 1}. ${area.name || connections[i]} - ${area.description || ''}`);
        }
        
        const choice = await this.ask(`\nTravel to (1-${connections.length}) or press Enter to cancel: `);
        
        if (choice.isDigit()) {
            const idx = parseInt(choice) - 1;
            if (idx >= 0 && idx < connections.length) {
                const newArea = connections[idx];
                this.currentArea = newArea;
                this.player.updateWeather(newArea);
                console.log(`Traveling to ${this.areasData[newArea]?.name || newArea}...`);
                
                // Random encounter on travel
                if (Math.random() < 0.3) {
                    await this.randomEncounter();
                }
            }
        }
    }
    
    /**
     * View inventory
     */
    async viewInventory() {
        if (!this.player) {
            console.log(this.lang.get('no_character', 'No character'));
            return;
        }
        
        console.log(`\n%c=== INVENTORY ===%c`, Colors.CYAN + Colors.BOLD, Colors.END);
        console.log(`Gold: ${Colors.GOLD}${this.player.gold}${Colors.END}`);
        
        if (this.player.inventory.length === 0) {
            console.log(this.lang.get('inventory_empty', 'Your inventory is empty'));
            return;
        }
        
        // Group by type
        const itemsByType = {};
        for (const item of this.player.inventory) {
            const itemType = this.itemsData[item]?.type || "unknown";
            if (!itemsByType[itemType]) itemsByType[itemType] = [];
            itemsByType[itemType].push(item);
        }
        
        for (const [type, items] of Object.entries(itemsByType)) {
            console.log(`\n${Colors.CYAN}${type.charAt(0).toUpperCase() + type.slice(1)}:${Colors.END}`);
            for (const item of items) {
                const itemData = this.itemsData[item] || {};
                console.log(`  - ${item}`);
                if (itemData.description) {
                    console.log(`    ${itemData.description}`);
                }
            }
        }
    }
    
    /**
     * View missions
     */
    async viewMissions() {
        if (!this.player) {
            console.log(this.lang.get('no_character', 'No character'));
            return;
        }
        
        console.log(`\n%c=== MISSIONS ===%c`, Colors.CYAN + Colors.BOLD, Colors.END);
        
        const activeMissions = Object.keys(this.missionProgress).filter(
            mid => !this.missionProgress[mid]?.completed
        );
        
        if (activeMissions.length === 0) {
            console.log(this.lang.get('no_active_missions', 'No active missions'));
            console.log(`${Colors.CYAN}A.${Colors.END} Available Missions`);
            console.log(`B. Back`);
            
            const choice = await this.ask("\nChoose an option: ");
            if (choice.toUpperCase() === 'A') {
                await this.availableMissionsMenu();
            }
            return;
        }
        
        console.log(this.lang.get('n_active_missions', 'Active Missions:'));
        for (let i = 0; i < activeMissions.length; i++) {
            const mid = activeMissions[i];
            const mission = this.missionsData[mid] || {};
            const progress = this.missionProgress[mid];
            const target = progress.target_count || 1;
            const current = progress.current_count || 0;
            
            console.log(`${i + 1}. ${mission.name || mid} - ${current}/${target}`);
            console.log(`   ${mission.description || ''}`);
        }
    }
    
    /**
     * Available missions menu
     */
    async availableMissionsMenu() {
        console.log(`\n%c=== AVAILABLE MISSIONS ===%c`, Colors.CYAN + Colors.BOLD, Colors.END);
        
        const availableMissions = Object.keys(this.missionsData).filter(
            mid => !this.missionProgress[mid] && !this.completedMissions.includes(mid)
        );
        
        if (availableMissions.length === 0) {
            console.log(this.lang.get('no_new_missions', 'No new missions available'));
            return;
        }
        
        for (let i = 0; i < availableMissions.length; i++) {
            const mid = availableMissions[i];
            const mission = this.missionsData[mid] || {};
            console.log(`${i + 1}. ${Colors.BOLD}${mission.name || mid}${Colors.END}`);
            console.log(`   ${mission.description || ''}`);
            
            const levelReq = mission.unlock_level;
            if (levelReq) {
                const hasLevel = this.player.level >= levelReq;
                console.log(`   Level required: ${hasLevel ? Colors.GREEN : Colors.RED}${levelReq}${Colors.END}`);
            }
        }
        
        const choice = await this.ask(`\nAccept mission (1-${availableMissions.length}) or Enter to cancel: `);
        
        if (choice.isDigit()) {
            const idx = parseInt(choice) - 1;
            if (idx >= 0 && idx < availableMissions.length) {
                const missionId = availableMissions[idx];
                await this.acceptMission(missionId);
            }
        }
    }
    
    /**
     * Accept a mission
     */
    async acceptMission(missionId) {
        if (this.missionProgress[missionId]) {
            console.log(this.lang.get('mission_already_accepted', 'Mission already accepted'));
            return;
        }
        
        const mission = this.missionsData[missionId];
        if (!mission) {
            console.log(this.lang.get('mission_data_not_found', 'Mission not found'));
            return;
        }
        
        const missionType = mission.type || 'kill';
        const targetCount = mission.target_count || 1;
        
        this.missionProgress[missionId] = {
            current_count: 0,
            target_count: targetCount,
            completed: false,
            type: missionType
        };
        
        console.log(`Mission accepted: ${mission.name || missionId}`);
    }
    
    /**
     * Fight boss menu
     */
    async fightBossMenu() {
        if (!this.player) {
            console.log(this.lang.get('no_character', 'No character'));
            return;
        }
        
        const areaData = this.areasData[this.currentArea] || {};
        const possibleBosses = areaData.possible_bosses || [];
        
        if (possibleBosses.length === 0) {
            console.log(`No bosses in ${areaData.name || this.currentArea}`);
            return;
        }
        
        console.log(`\n%c=== BOSSES IN ${(areaData.name || this.currentArea).toUpperCase()} ===%c`, Colors.RED + Colors.BOLD, Colors.END);
        
        for (let i = 0; i < possibleBosses.length; i++) {
            const bossName = possibleBosses[i];
            const bossData = this.bossesData[bossName] || {};
            let status = "";
            
            if (this.player.bossesKilled && this.player.bossesKilled[bossName]) {
                status = ` ${Colors.YELLOW}(Recently defeated)${Colors.END}`;
            }
            
            console.log(`${i + 1}. ${bossData.name || bossName}${status}`);
        }
        
        const choice = await this.ask(`\nChoose a boss (1-${possibleBosses.length}) or Enter to cancel: `);
        
        if (choice.isDigit()) {
            const idx = parseInt(choice) - 1;
            if (idx >= 0 && idx < possibleBosses.length) {
                const bossName = possibleBosses[idx];
                const bossData = this.bossesData[bossName];
                
                if (bossData) {
                    const boss = new Boss(bossData, this.dialoguesData);
                    console.log(`\n%cChallenge accepted!%c`, Colors.RED + Colors.BOLD, Colors.END);
                    await this.battle(boss);
                }
            }
        }
    }
    
    /**
     * Visit tavern (companions)
     */
    async visitTavern() {
        if (!this.player) {
            console.log(this.lang.get('no_character', 'No character'));
            return;
        }
        
        console.log(`\n%c=== THE TAVERN ===%c`, Colors.CYAN + Colors.BOLD, Colors.END);
        console.log(`Your gold: ${Colors.GOLD}${this.player.gold}${Colors.END}`);
        
        const companions = Object.entries(this.companionsData);
        if (companions.length === 0) {
            console.log(this.lang.get('no_companions_available', 'No companions available'));
            return;
        }
        
        console.log(`\nAvailable Companions:`);
        for (let i = 0; i < companions.length; i++) {
            const [cid, cdata] = companions[i];
            const price = cdata.price || 0;
            console.log(`${i + 1}. ${cdata.name || cid} - ${Colors.GOLD}${price} gold${Colors.END}`);
            console.log(`   ${cdata.description || ''}`);
        }
        
        const choice = await this.ask(`\nHire companion (1-${companions.length}) or Enter to leave: `);
        
        if (choice.isDigit()) {
            const idx = parseInt(choice) - 1;
            if (idx >= 0 && idx < companions.length) {
                const [cid, cdata] = companions[idx];
                const price = cdata.price || 0;
                
                if (this.player.gold >= price) {
                    if (this.player.companions.length >= 4) {
                        console.log("Maximum 4 companions allowed");
                        return;
                    }
                    
                    this.player.gold -= price;
                    this.player.companions.push({
                        id: cid,
                        name: cdata.name || cid,
                        level: 1,
                        equipment: { weapon: null, armor: null, accessory: null }
                    });
                    
                    console.log(`Hired ${cdata.name || cid} for ${price} gold!`);
                    this.player.updateStatsFromEquipment(this.itemsData, this.companionsData);
                } else {
                    console.log(this.lang.get('not_enough_gold', 'Not enough gold'));
                }
            }
        }
    }
    
    /**
     * Visit shop
     */
    async visitShop() {
        if (!this.player) {
            console.log(this.lang.get('no_character', 'No character'));
            return;
        }
        
        const areaData = this.areasData[this.currentArea] || {};
        const areaShops = areaData.shops || [];
        
        if (areaShops.length === 0) {
            console.log(`No shops in ${areaData.name || this.currentArea}`);
            return;
        }
        
        console.log(`\n%c=== SHOPS IN ${(areaData.name || this.currentArea).toUpperCase()} ===%c`, Colors.BOLD, Colors.END);
        console.log(`Your gold: ${Colors.GOLD}${this.player.gold}${Colors.END}\n`);
        
        for (let i = 0; i < areaShops.length; i++) {
            const shopId = areaShops[i];
            const shopData = this.shopsData[shopId] || {};
            console.log(`${i + 1}. ${shopData.name || shopId}`);
        }
        
        const choice = await this.ask("\nWhich shop? ");
        
        if (choice.isDigit()) {
            const idx = parseInt(choice) - 1;
            if (idx >= 0 && idx < areaShops.length) {
                await this.visitSpecificShop(areaShops[idx]);
            }
        }
    }
    
    /**
     * Visit specific shop
     */
    async visitSpecificShop(shopId) {
        const shopData = this.shopsData[shopId];
        if (!shopData) return;
        
        console.log(`\n%c=== ${shopData.name || shopId.toUpperCase()} ===%c`, Colors.CYAN + Colors.BOLD, Colors.END);
        
        const items = shopData.items || [];
        if (items.length === 0) {
            console.log("This shop has no items");
            return;
        }
        
        for (let i = 0; i < items.length; i++) {
            const itemId = items[i];
            const itemData = this.itemsData[itemId] || {};
            const price = itemData.price || 0;
            const rarityColor = this.getRarityColor(itemData.rarity || 'common');
            
            console.log(`${i + 1}. ${rarityColor}${itemData.name || itemId}${Colors.END} - ${Colors.GOLD}${price} gold${Colors.END}`);
            console.log(`   ${itemData.description || ''}`);
        }
        
        const choice = await this.ask(`\nBuy item (1-${items.length}) or Enter to leave: `);
        
        if (choice.isDigit()) {
            const idx = parseInt(choice) - 1;
            if (idx >= 0 && idx < items.length) {
                const itemId = items[idx];
                const itemData = this.itemsData[itemId];
                const price = itemData?.price || 0;
                
                if (this.player.gold >= price) {
                    this.player.gold -= price;
                    this.player.inventory.push(itemId);
                    console.log(`Purchased ${itemData?.name || itemId} for ${price} gold!`);
                } else {
                    console.log(this.lang.get('not_enough_gold', 'Not enough gold'));
                }
            }
        }
    }
    
    /**
     * Get rarity color
     */
    getRarityColor(rarity) {
        const colors = {
            common: Colors.WHITE,
            uncommon: Colors.GREEN,
            rare: Colors.BLUE,
            epic: Colors.MAGENTA,
            legendary: Colors.GOLD
        };
        return colors[rarity?.toLowerCase()] || Colors.WHITE;
    }
    
    /**
     * Rest at inn
     */
    async rest() {
        if (!this.player) {
            console.log(this.lang.get('no_character', 'No character'));
            return;
        }
        
        const areaData = this.areasData[this.currentArea] || {};
        const canRest = areaData.can_rest || false;
        const restCost = areaData.rest_cost || 10;
        
        if (!canRest) {
            console.log(`${Colors.RED}You cannot rest here. It's too dangerous!${Colors.END}`);
            return;
        }
        
        console.log(`\n%c=== REST ===%c`, Colors.CYAN + Colors.BOLD, Colors.END);
        console.log(`Rest Cost: ${Colors.GOLD}${restCost} gold${Colors.END}`);
        console.log(`HP: ${this.player.hp}/${this.player.maxHp}`);
        console.log(`MP: ${this.player.mp}/${this.player.maxMp}`);
        
        if (this.player.gold < restCost) {
            console.log(`${Colors.RED}Not enough gold!${Colors.END}`);
            return;
        }
        
        const choice = await this.ask(`Rest for ${restCost} gold? (y/n): `);
        
        if (choice.toLowerCase() === 'y') {
            this.player.gold -= restCost;
            this.player.hp = this.player.maxHp;
            this.player.mp = this.player.maxMp;
            console.log(`${Colors.GREEN}You rest and recover full health!${Colors.END}`);
        }
    }
    
    /**
     * Manage companions
     */
    async manageCompanions() {
        if (!this.player) {
            console.log(this.lang.get('no_character', 'No character'));
            return;
        }
        
        console.log(`\n%c=== COMPANIONS ===%c`, Colors.CYAN + Colors.BOLD, Colors.END);
        console.log(`Active companions: ${this.player.companions?.length || 0}/4`);
        
        if (!this.player.companions || this.player.companions.length === 0) {
            console.log("You have no companions. Visit the tavern to hire some!");
            return;
        }
        
        for (let i = 0; i < this.player.companions.length; i++) {
            const companion = this.player.companions[i];
            const compName = companion.name || companion;
            const compLevel = companion.level || 1;
            
            // Find companion data for bonuses
            let compData = null;
            for (const [cid, cdata] of Object.entries(this.companionsData)) {
                if (cdata.name === compName) {
                    compData = cdata;
                    break;
                }
            }
            
            console.log(`\n${i + 1}. ${Colors.CYAN}${compName}${Colors.END} (Level ${compLevel})`);
            if (compData) {
                const bonuses = [];
                if (compData.attack_bonus) bonuses.push(`+${compData.attack_bonus} ATK`);
                if (compData.defense_bonus) bonuses.push(`+${compData.defense_bonus} DEF`);
                if (compData.speed_bonus) bonuses.push(`+${compData.speed_bonus} SPD`);
                if (bonuses.length > 0) {
                    console.log(`   Bonuses: ${bonuses.join(', ')}`);
                }
            }
        }
        
        console.log(`\nD. Dismiss Companion`);
        console.log(`B. Back`);
        
        const choice = await this.ask("\nChoose action: ");
        
        if (choice.toUpperCase() === 'D') {
            const dismissChoice = await this.ask(`Dismiss which companion (1-${this.player.companions.length})? `);
            if (dismissChoice.isDigit()) {
                const idx = parseInt(dismissChoice) - 1;
                if (idx >= 0 && idx < this.player.companions.length) {
                    const dismissed = this.player.companions.splice(idx, 1)[0];
                    console.log(`${Colors.RED}Dismissed ${dismissed.name || dismissed}.${Colors.END}`);
                    this.player.updateStatsFromEquipment(this.itemsData, this.companionsData);
                }
            }
        }
    }
    
    /**
     * Pet shop
     */
    async petShop() {
        if (!this.player) {
            console.log(this.lang.get('no_character', 'No character'));
            return;
        }
        
        console.log(`\n%c=== PET SHOP ===%c`, Colors.CYAN + Colors.BOLD, Colors.END);
        console.log(`Your Gold: ${Colors.GOLD}${this.player.gold}${Colors.END}`);
        
        const currentPet = this.player.activePet ? (this.petsData[this.player.activePet]?.name || this.player.activePet) : "None";
        console.log(`Current Pet: ${Colors.MAGENTA}${currentPet}${Colors.END}\n`);
        
        console.log(`${Colors.CYAN}1.${Colors.END} Buy Pet`);
        console.log(`${Colors.CYAN}2.${Colors.END} Manage Pets`);
        console.log(`${Colors.CYAN}3.${Colors.END} Back`);
        
        const choice = await this.ask("Select an option: ");
        
        if (choice === "1") {
            const petEntries = Object.entries(this.petsData);
            console.log("\nAvailable Pets:");
            
            for (let i = 0; i < petEntries.length; i++) {
                const [petId, pet] = petEntries[i];
                const isOwned = this.player.petsOwned?.includes(petId);
                if (!isOwned) {
                    console.log(`- ${pet.name || petId} (${pet.price}g): ${pet.description || ''}`);
                }
            }
            
            const petInput = await this.ask("\nEnter pet name to buy: ");
            const petId = petInput.toLowerCase().replace(/ /g, '_');
            
            if (this.petsData[petId] && !this.player.petsOwned?.includes(petId)) {
                const price = this.petsData[petId].price || 0;
                if (this.player.gold >= price) {
                    this.player.gold -= price;
                    if (!this.player.petsOwned) this.player.petsOwned = [];
                    this.player.petsOwned.push(petId);
                    console.log(`You bought a ${this.petsData[petId].name}!`);
                } else {
                    console.log("Not enough gold!");
                }
            }
        } else if (choice === "2") {
            if (this.player.petsOwned && this.player.petsOwned.length > 0) {
                console.log("\nYour Pets:");
                for (let i = 0; i < this.player.petsOwned.length; i++) {
                    const petId = this.player.petsOwned[i];
                    const petName = this.petsData[petId]?.name || petId;
                    const status = petId === this.player.activePet ? "(Active)" : "";
                    console.log(`${i + 1}. ${petName} ${status}`);
                }
                
                const sel = await this.ask(`\nSelect pet to activate (1-${this.player.petsOwned.length}): `);
                if (sel.isDigit()) {
                    const idx = parseInt(sel) - 1;
                    if (idx >= 0 && idx < this.player.petsOwned.length) {
                        this.player.activePet = this.player.petsOwned[idx];
                        console.log(`${this.petsData[this.player.activePet].name} is now active!`);
                    }
                }
            } else {
                console.log("You don't own any pets yet.");
            }
        }
    }
    
    /**
     * Build home (housing)
     */
    async buildHome() {
        if (!this.player) {
            console.log(this.lang.get('no_character', 'No character'));
            return;
        }
        
        if (!this.player.housingOwned || this.player.housingOwned.length === 0) {
            console.log(`${Colors.YELLOW}You haven't purchased any housing items! Visit the Housing Shop first.${Colors.END}`);
            return;
        }
        
        console.log(`\n%c=== BUILD HOME ===%c`, Colors.CYAN + Colors.BOLD, Colors.END);
        console.log(`Comfort Points: ${Colors.CYAN}${this.player.comfortPoints || 0}${Colors.END}`);
        console.log(`Items owned: ${this.player.housingOwned.length}`);
        
        // Show building slots
        const buildingTypes = {
            house: { label: "House", slots: 3 },
            decoration: { label: "Decoration", slots: 10 },
            fencing: { label: "Fencing", slots: 1 },
            garden: { label: "Garden", slots: 3 },
            farm: { label: "Farm", slots: 2 },
            training_place: { label: "Training Place", slots: 3 }
        };
        
        for (const [bType, info] of Object.entries(buildingTypes)) {
            console.log(`\n${Colors.BOLD}${info.label} Slots:${Colors.END}`);
            for (let i = 1; i <= info.slots; i++) {
                const slot = `${bType}_${i}`;
                const itemId = this.player.buildingSlots?.[slot];
                if (itemId && this.housingData[itemId]) {
                    const item = this.housingData[itemId];
                    const rarityColor = this.getRarityColor(item.rarity);
                    console.log(`  ${slot}: ${rarityColor}${item.name || itemId}${Colors.END}`);
                } else {
                    console.log(`  ${slot}: ${Colors.GRAY}Empty${Colors.END}`);
                }
            }
        }
    }
    
    /**
     * Save game
     */
    async saveGame() {
        if (!this.player) {
            console.log(this.lang.get('no_character', 'No character'));
            return;
        }
        
        console.log("\nSaving game...");
        const success = await this.saveLoadSystem.saveGame();
        
        if (success) {
            console.log(`%cGame saved successfully!%c`, Colors.GREEN, Colors.END);
        } else {
            console.log(`%cFailed to save game%c`, Colors.RED, Colors.END);
        }
    }
    
    /**
     * Load game
     */
    async loadGame() {
        console.log("\nLoading game...");
        const saveData = await this.saveLoadSystem.loadGame();
        
        if (saveData) {
            await this.saveLoadSystem.loadSaveDataInternal(saveData);
            this.player = saveData.player;
            this.currentArea = saveData.currentArea || "starting_village";
            console.log(`%cGame loaded successfully!%c`, Colors.GREEN, Colors.END);
        } else {
            console.log("No saved game found");
        }
    }
    
    /**
     * Update mission progress
     */
    updateMissionProgress(updateType, target, count = 1) {
        for (const [mid, progress] of Object.entries(this.missionProgress)) {
            if (progress.completed) continue;
            
            const mission = this.missionsData[mid];
            if (!mission) continue;
            
            if (progress.type === 'kill' && updateType === 'kill') {
                const targetEnemy = (mission.target || '').toLowerCase();
                if (targetEnemy === target.toLowerCase()) {
                    progress.current_count += count;
                    console.log(`${Colors.CYAN}[Mission] ${mission.name}: ${progress.current_count}/${progress.target_count}${Colors.END}`);
                    
                    if (progress.current_count >= progress.target_count) {
                        this.completeMission(mid);
                    }
                }
            } else if (progress.type === 'collect' && updateType === 'collect') {
                if (progress.current_counts && progress.current_counts[target] !== undefined) {
                    progress.current_counts[target] += count;
                    
                    const allCollected = Object.keys(progress.target_counts).every(
                        item => progress.current_counts[item] >= progress.target_counts[item]
                    );
                    
                    if (allCollected) {
                        this.completeMission(mid);
                    }
                }
            }
        }
    }
    
    /**
     * Complete mission
     */
    completeMission(missionId) {
        if (this.missionProgress[missionId]) {
            this.missionProgress[missionId].completed = true;
            const mission = this.missionsData[missionId];
            
            console.log(`\n%c!!! MISSION COMPLETE: ${mission?.name || missionId} !!!%c`, Colors.GOLD + Colors.BOLD, Colors.END);
            console.log(`${Colors.YELLOW}You can now claim your rewards from the menu.${Colors.END}`);
        }
    }
    
    /**
     * Update challenge progress
     */
    updateChallengeProgress(challengeType, value = 1) {
        if (!this.player) return;
        
        for (const challenge of (this.weeklyChallengesData.challenges || [])) {
            if (this.completedChallenges.includes(challenge.id)) continue;
            
            if (challenge.type === challengeType) {
                this.challengeProgress[challenge.id] += value;
                
                if (this.challengeProgress[challenge.id] >= challenge.target) {
                    this.completeChallenge(challenge);
                }
            }
        }
    }
    
    /**
     * Complete challenge
     */
    completeChallenge(challenge) {
        this.completedChallenges.push(challenge.id);
        
        const rewardExp = challenge.reward_exp || 0;
        const rewardGold = challenge.reward_gold || 0;
        
        this.player.gainExperience(rewardExp);
        this.player.gold += rewardGold;
        
        console.log(`\n%c✓ Challenge Completed: ${challenge.name}!%c`, Colors.CYAN + Colors.BOLD, Colors.END);
        console.log(`  Reward: ${rewardExp} EXP + ${rewardGold} Gold`);
    }
    
    /**
     * Use item in battle
     */
    async useItemInBattle() {
        if (!this.player) return;
        
        const consumables = this.player.inventory.filter(
            item => this.itemsData[item]?.type === "consumable"
        );
        
        if (consumables.length === 0) {
            console.log("No consumable items!");
            return;
        }
        
        console.log("\nAvailable Consumables:");
        for (let i = 0; i < consumables.length; i++) {
            const item = consumables[i];
            const itemData = this.itemsData[item];
            console.log(`${i + 1}. ${item} - ${itemData?.description || 'Unknown effect'}`);
        }
        
        const choice = await this.ask(`Choose item (1-${consumables.length}): `);
        
        if (choice.isDigit()) {
            const idx = parseInt(choice) - 1;
            if (idx >= 0 && idx < consumables.length) {
                const item = consumables[idx];
                this.useItem(item);
                this.player.inventory.splice(this.player.inventory.indexOf(item), 1);
            }
        }
    }
    
    /**
     * Use item
     */
    useItem(item) {
        if (!this.player) return;
        
        const itemData = this.itemsData[item];
        if (!itemData) return;
        
        if (itemData.type === "consumable") {
            if (itemData.effect === "heal") {
                const healAmount = itemData.value || 0;
                this.player.heal(healAmount);
                console.log(`Used ${item}, healed ${healAmount} HP!`);
            } else if (itemData.effect === "mp_restore") {
                const mpAmount = itemData.value || 0;
                this.player.mp = Math.min(this.player.maxMp, this.player.mp + mpAmount);
                console.log(`Used ${item}, restored ${mpAmount} MP!`);
            }
        }
    }
    
    /**
     * Ask for user input (browser-compatible)
     */
    ask(prompt) {
        return new Promise((resolve) => {
            this.resolveInput = resolve;
            // Dispatch custom event for UI to handle
            const event = new CustomEvent('gameAsk', { 
                detail: { prompt, game: this } 
            });
            document.dispatchEvent(event);
        });
    }
    
    /**
     * Handle user input from UI
     */
    handleInput(value) {
        if (this.resolveInput) {
            this.resolveInput(value);
            this.resolveInput = null;
        }
    }
}

// Export for use in browser
export default Game;