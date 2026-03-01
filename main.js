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

import MarketAPI from './utilities_js/market.js';

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
        this.marketApi = new MarketAPI(this.lang, Colors);
        this.marketApi.game = this;
        
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
        this.print(`Our Legacy - Browser RPG`);
        this.print("Loading game data...");
        
        await this.loadGameData();
        this.loadConfig();
        
        // Expose classes for SaveLoadSystem
        this.CharacterClass = Character;
        this.EnemyClass = Enemy;
        this.BossClass = Boss;

        // Initialize systems that need game instance
        this.battleSystem = new BattleSystem(this);
        this.spellCastingSystem = new SpellCastingSystem(this);
        this.saveLoadSystem = new SaveLoadSystem(this);
        
        this.print("Game loaded successfully!");
    }

    /**
     * Print text to the game output
     */
    print(text, color = null) {
        if (text === null && color === 'clear') {
            if (this.printCallback) {
                this.printCallback(null, 'clear');
            }
            return;
        }
        if (typeof text === 'string') {
            const areaData = this.areasData[this.currentArea] || {};
            const areaName = areaData.name || this.currentArea;
            text = text.replace(/\{area\}/g, areaName);
        }
        if (this.printCallback) {
            this.printCallback(text, color);
        } else {
            console.log(text);
        }
    }

    /**
     * Ask for user input
     */
    async ask(question) {
        this.print(null, 'clear');
        this.print(question);
        // Clear and focus input for the next question
        const input = document.getElementById('gameInput');
        if (input) {
            input.value = '';
            input.focus();
        }
        return new Promise((resolve) => {
            this.resolveInput = resolve;
            // Dispatch custom event for UI to handle
            const event = new CustomEvent('gameAsk', { 
                detail: { prompt: question, game: this } 
            });
            document.dispatchEvent(event);
        });
    }

    /**
     * Handle input from UI
     */
    handleInput(input) {
        if (this.resolveInput) {
            const resolve = this.resolveInput;
            this.resolveInput = null;
            resolve(input);
        }
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
        
        this.print("Loading mods...");
        
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
     * Create a visual progress bar.
     */
    createProgressBar(current, maximum, width = 20, color = Colors.GREEN) {
        if (maximum <= 0) return "[" + " ".repeat(width) + "]";
        const filledWidth = Math.floor((current / maximum) * width);
        const filled = "█".repeat(filledWidth);
        const empty = "░".repeat(width - filledWidth);
        const percentage = (current / maximum) * 100;
        return `[${Colors.wrap(filled, color)}${empty}] ${percentage.toFixed(1)}%`;
    }

    /**
     * Create a wide, epic visual HP bar for bosses.
     */
    createBossHpBar(current, maximum, width = 40, color = Colors.RED) {
        if (maximum <= 0) return "[" + " ".repeat(width) + "]";
        const filledWidth = Math.floor((current / maximum) * width);
        const filled = "█".repeat(filledWidth);
        const empty = "░".repeat(width - filledWidth);
        const percentage = (current / maximum) * 100;
        const bossLabel = Colors.wrap("BOSS HP", `${Colors.BOLD}${Colors.RED}`);
        const bar = `[${Colors.wrap(filled, color)}${empty}]`;
        const percentText = Colors.wrap(`${percentage.toFixed(1)}%`, Colors.BOLD);
        return `${bossLabel} ${bar} ${percentText} (${current}/${maximum})`;
    }

    /**
     * Create a visual HP/MP bar.
     */
    createHpMpBar(current, maximum, width = 15, color = Colors.RED) {
        if (maximum <= 0) return "[" + " ".repeat(width) + "]";
        const filledWidth = Math.floor((current / maximum) * width);
        const filled = "█".repeat(filledWidth);
        const empty = "░".repeat(width - filledWidth);
        return `[${Colors.wrap(filled, color)}${empty}] ${current}/${maximum}`;
    }

    /**
     * Create a visual separator line.
     */
    createSeparator(char = "=", length = 60) {
        return char.repeat(length);
    }

    /**
     * Create a decorative section header.
     */
    createSectionHeader(title, char = "=", width = 60) {
        const padding = Math.max(0, Math.floor((width - title.length - 2) / 2));
        const headerText = `${char.repeat(padding)} ${title} ${char.repeat(padding)}`;
        return headerText;
    }

    /**
     * Display a loading indicator.
     */
    async loadingIndicator(message = "Loading") {
        this.print(`\n${Colors.wrap(message, Colors.YELLOW)}`, null);
        for (let i = 0; i < 3; i++) {
            await new Promise(resolve => setTimeout(resolve, 500));
            this.print(".", null);
        }
        this.print("");
    }

    /**
     * Get the color for an item rarity.
     */
    getRarityColor(rarity) {
        const rarityColors = {
            "common": Colors.COMMON,
            "uncommon": Colors.UNCOMMON,
            "rare": Colors.RARE,
            "epic": Colors.EPIC,
            "legendary": Colors.LEGENDARY
        };
        return rarityColors[rarity.toLowerCase()] || Colors.WHITE;
    }

    /**
     * Format item name with rarity color.
     */
    formatItemName(itemName, rarity = "common") {
        const color = this.getRarityColor(rarity);
        return Colors.wrap(itemName, color);
    }

    /**
     * Display welcome screen
     */
    async displayWelcome() {
        this.print(null, 'clear');
        this.print(this.createSeparator("=", 60));
        this.print(`       ${this.lang.get('game_title_display', 'Our Legacy')}`);
        this.print(`       ${Colors.wrap(this.lang.get('game_subtitle_display', 'Your game in the browser, portable!'), Colors.CYAN)}`);
        this.print(this.createSeparator("=", 60));
        this.print("");
        this.print(Colors.wrap(this.lang.get('welcome_message', 'Welcome to Our Legacy!'), Colors.CYAN));
        this.print('Choose your path wisely, for every decision shapes your destiny.');
        this.print("");
        
        this.print(this.createSectionHeader(this.lang.get('main_menu', 'MAIN MENU'), "="), `${Colors.CYAN}${Colors.BOLD}`);
        this.print(`1. ${Colors.wrap(this.lang.get('new_game', 'New Game'), Colors.GREEN)}`);
        this.print(`2. ${Colors.wrap(this.lang.get('load_game', 'Load Game'), Colors.BLUE)}`);
        this.print(`3. ${Colors.wrap(this.lang.get('settings', 'Settings'), Colors.YELLOW)}`);
        this.print(`4. ${Colors.wrap(this.lang.get('mods', 'Mods'), Colors.MAGENTA)}`);
        this.print(`5. ${Colors.wrap(this.lang.get('quit', 'Quit'), Colors.RED)}`);
        this.print("");
        
        const choice = await this.ask(`${this.lang.get('choose_option', 'Choose an option')} (1-5): `);
        
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
            this.print(Colors.wrap(this.lang.get('thank_exit', 'Thank you for playing!'), Colors.YELLOW));
            return "quit";
        } else {
            this.print(Colors.wrap(this.lang.get('invalid_choice', 'Invalid choice'), Colors.RED));
            return await this.displayWelcome();
        }
    }
    
    /**
     * Settings menu
     */
    async settingsWelcome() {
        this.print(this.createSectionHeader(this.lang.get('settings', 'SETTINGS'), "="));
        
        const modsEnabled = this.modManager.settings.mods_enabled;
        
        this.print(`\n1. ${this.lang.get('mod_system', 'Mod System')}: ${modsEnabled ? Colors.wrap('Enabled', Colors.GREEN) : Colors.wrap('Disabled', Colors.RED)}`);
        this.print(`2. ${this.lang.get('language', 'Language')}`);
        this.print(`3. ${Colors.wrap(this.lang.get('back', 'Back'), Colors.RED)}`);
        
        const choice = await this.ask(`\n${this.lang.get('choose_option', 'Choose an option')}: `);
        
        if (choice === "1") {
            this.modManager.toggleModsSystem();
            this.print(`${this.lang.get('mod_system', 'Mod system')} ${this.modManager.settings.mods_enabled ? Colors.wrap('enabled', Colors.GREEN) : Colors.wrap('disabled', Colors.RED)}!`);
        } else if (choice === "2") {
            await this.changeLanguageMenu();
        }
    }
    
    /**
     * Change language menu
     */
    async changeLanguageMenu() {
        this.print(this.createSectionHeader(this.lang.get('language', 'LANGUAGE'), "-"));
        
        const available = this.lang.config.available_languages || { en: "English" };
        const langs = Object.entries(available);
        
        for (let i = 0; i < langs.length; i++) {
            const [code, name] = langs[i];
            this.print(`${Colors.wrap((i + 1).toString(), Colors.YELLOW)}. ${name}`);
        }
        this.print(`${Colors.wrap((langs.length + 1).toString(), Colors.YELLOW)}. ${this.lang.get('back', 'Back')}`);
        
        const choice = await this.ask(`${this.lang.get('choose_language_prompt', 'Choose a language')}: `);
        
        if (choice.isDigit()) {
            const idx = parseInt(choice) - 1;
            if (idx >= 0 && idx < langs.length) {
                await this.lang.changeLanguage(langs[idx][0]);
                this.print(`${Colors.wrap(this.lang.get('lang_changed_msg', 'Language changed to {lang}!').replace('{lang}', langs[idx][1]), Colors.GREEN)}`);
            }
        }
    }
    
    /**
     * Mods menu
     */
    async modsWelcome() {
        this.print(this.createSectionHeader(this.lang.get('mods', 'MODS'), "="));
        
        await this.modManager.discoverMods();
        const modsList = this.modManager.getModList();
        
        if (!modsList || modsList.length === 0) {
            this.print(`\n${Colors.wrap(this.lang.get('no_mods_found', 'No mods found'), Colors.GRAY)}`);
            this.print(this.lang.get('place_mods_instruction', 'Place mods in the mods/ folder'));
            await this.ask(`\n${this.lang.get('press_enter_back', 'Press Enter to go back...')}`);
            return;
        }
        
        const modsSystemEnabled = this.modManager.settings.mods_enabled;
        this.print(`\n${this.lang.get('mod_status_label', 'Mod System Status:')} ${modsSystemEnabled ? Colors.wrap('Enabled', Colors.GREEN) : Colors.wrap('Disabled', Colors.RED)}`);
        
        this.print(`\n${Colors.wrap(this.lang.get('installed_mods_label', 'Installed Mods:'), Colors.BOLD)}`);
        
        for (let i = 0; i < modsList.length; i++) {
            const mod = modsList[i];
            const status = mod.enabled ? Colors.wrap('[ENABLED]', Colors.GREEN) : Colors.wrap('[DISABLED]', Colors.RED);
            this.print(`\n${Colors.wrap((i + 1).toString(), Colors.YELLOW)}. ${Colors.wrap(mod.name || mod.folder_name, Colors.BOLD)} ${status}`);
            this.print(`   ${this.lang.get('version_label', 'Version:')} ${mod.version || '1.0'}`);
            this.print(`   ${this.lang.get('author_label', 'Author:')} ${mod.author || 'Unknown'}`);
            if (mod.description) {
                this.print(`   ${Colors.wrap(mod.description.substring(0, 100), Colors.GRAY)}`);
            }
        }
        
        this.print(`\n${Colors.wrap(this.lang.get('options_label', 'Options:'), Colors.BOLD)}`);
        this.print(`1-${modsList.length}. ${this.lang.get('toggle_mod', 'Toggle Mod')}`);
        this.print(`B. ${Colors.wrap(this.lang.get('back', 'Back'), Colors.RED)}`);
        
        const choice = await this.ask(`\n${this.lang.get('choose_option', 'Choose an option')}: `);
        
        if (choice.toUpperCase() === 'B') return;
        
        if (choice.isDigit()) {
            const idx = parseInt(choice) - 1;
            if (idx >= 0 && idx < modsList.length) {
                const mod = modsList[idx];
                this.modManager.toggleMod(mod.folder_name);
                this.print(`${Colors.wrap(this.lang.get('mod_toggled_msg', 'Mod "{name}" toggled. Changes take effect on restart.').replace('{name}', mod.name), Colors.YELLOW)}`);
            }
        }
    }
    
    /**
     * Create character menu
     */
    async createCharacter() {
        this.print(null, 'clear');
        this.print(this.createSectionHeader(this.lang.get('char_creation_title', 'CHARACTER CREATION'), "="), `${Colors.CYAN}${Colors.BOLD}`);
        
        const nameInput = await this.ask(this.lang.get('enter_name', 'Enter your name: '));
        const playerName = nameInput.trim() || "Hero";
        
        // Display available classes
        this.print(null, 'clear');
        this.print(Colors.wrap(this.lang.get('ui_choose_class', 'Choose your class:'), Colors.CYAN));
        
        const classEntries = Object.entries(this.classesData);
        
        for (let i = 0; i < classEntries.length; i++) {
            const [className, classData] = classEntries[i];
            const description = classData.description || "No description available";
            this.print(`${Colors.wrap((i + 1).toString(), Colors.YELLOW)}. ${Colors.wrap(className, Colors.BOLD)} - ${description}`);
        }
        
        const choice = await this.ask(`${this.lang.get('enter_class_choice', 'Enter class choice')} (1-${classEntries.length}): `);
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
        
        this.print(`\n${Colors.wrap(this.lang.get('welcome_adventurer', `Welcome, ${playerName} the ${selectedClass}!`), Colors.GREEN)}`);
        
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
            this.print(`\n${Colors.wrap(this.lang.get('received_starting_equip', 'You received starting equipment:'), Colors.CYAN)}`);
            for (const item of items) {
                const itemData = this.itemsData[item] || {};
                const rarity = itemData.rarity || "common";
                this.print(`  - ${this.formatItemName(itemData.name || item, rarity)}`);
            }
            
            // Auto-equip first weapon and armor
            for (const slot of ["weapon", "armor"]) {
                for (const item of items) {
                    const itemData = this.itemsData[item] || {};
                    const itemType = itemData.type;
                    if (itemType === slot) {
                        this.player.equip(item, this.itemsData);
                        this.print(`${Colors.wrap(this.lang.get('equipped_msg', 'Equipped:'), Colors.GREEN)} ${this.formatItemName(itemData.name || item, itemData.rarity)}`);
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
            this.print(this.createSectionHeader(this.lang.get('no_character', 'No character created'), "!"));
            return;
        }
        
        this.print(this.createSectionHeader(`${this.player.name} - Level ${this.player.level} ${this.player.rank}`, "="));
        
        // Show HP/MP bars in stats
        this.print(`HP: ${this.createHpMpBar(this.player.hp, this.player.maxHp, 25, Colors.RED)}`);
        this.print(`MP: ${this.createHpMpBar(this.player.mp, this.player.maxMp, 25, Colors.BLUE)}`);
        
        const attack = this.player.getEffectiveAttack();
        const defense = this.player.getEffectiveDefense();
        const speed = this.player.getEffectiveSpeed();
        
        this.print(`${Colors.wrap(this.lang.get('ui_stats_attack', 'Attack:'), Colors.RED)} ${attack} | ${Colors.wrap(this.lang.get('ui_stats_defense', 'Defense:'), Colors.BLUE)} ${defense} | ${Colors.wrap(this.lang.get('ui_stats_speed', 'Speed:'), Colors.GREEN)} ${speed}`);
        this.print(`${Colors.wrap(this.lang.get('gold', 'Gold:'), Colors.GOLD)} ${this.player.gold}`);
        
        const xpBar = this.createProgressBar(this.player.experience, this.player.experienceToNext, 30, Colors.YELLOW);
        this.print(`${Colors.wrap('XP:', Colors.YELLOW)} ${xpBar}`);
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
                this.print(this.lang.get('ui_no_game_loaded', 'No game loaded'));
                await this.createCharacter();
            }
        } else if (choice === "quit") {
            this.print("Thanks for playing!");
            return;
        }
        
        // Final check for player before loop
        if (!this.player) {
            this.print("Error: Character creation failed.");
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
        
        this.print(this.createSectionHeader(this.lang.get('main_menu', 'MAIN MENU'), "="));
        
        // Show current location
        const areaData = this.areasData[this.currentArea] || {};
        const areaName = areaData.name || this.currentArea;
        this.print(this.lang.get('current_location', `Location: ${areaName}`));
        
        // Display time and weather
        if (this.player) {
            const displayHour = Math.floor(this.player.hour);
            const displayMinute = Math.floor((this.player.hour - displayHour) * 60);
            const timeStr = `${String(displayHour).padStart(2, '0')}:${String(displayMinute).padStart(2, '0')}`;
            const dayStr = `Day ${this.player.day}`;
            const weatherDesc = this.player.getWeatherDescription ? this.player.getWeatherDescription(this.lang) : this.player.currentWeather;
            
            this.print(Colors.wrap(`${timeStr} | ${dayStr}`, Colors.CYAN));
            this.print(Colors.wrap(`${weatherDesc}`, Colors.YELLOW));
            
            // Show HP/MP bars
            this.print(`HP: ${this.createHpMpBar(this.player.hp, this.player.maxHp, 20, Colors.RED)}`);
            this.print(`MP: ${this.createHpMpBar(this.player.mp, this.player.maxMp, 20, Colors.BLUE)}`);
        }
        
        this.print(`1. ${Colors.wrap(this.lang.get('explore', 'Explore'), Colors.GREEN)}`);
        this.print(`2. ${Colors.wrap(this.lang.get('view_character', 'View Character'), Colors.CYAN)}`);
        this.print(`3. ${Colors.wrap(this.lang.get('travel', 'Travel'), Colors.BLUE)}`);
        this.print(`4. ${Colors.wrap(this.lang.get('inventory', 'Inventory'), Colors.YELLOW)}`);
        this.print(`5. ${Colors.wrap(this.lang.get('missions', 'Missions'), Colors.MAGENTA)}`);
        this.print(`6. ${Colors.wrap(this.lang.get('fight_boss', 'Fight Boss'), Colors.RED)}`);
        this.print(`7. ${Colors.wrap(this.lang.get('tavern', 'Tavern'), Colors.ORANGE)}`);
        this.print(`8. ${Colors.wrap(this.lang.get('shop', 'Shop'), Colors.GOLD)}`);
        this.print(`9. ${Colors.wrap(this.lang.get('rest', 'Rest'), Colors.GREEN)}`);
        this.print(`10. ${Colors.wrap(this.lang.get('companions', 'Companions'), Colors.PURPLE)}`);
        
        if (this.currentArea === "your_land") {
            this.print(`11. ${Colors.wrap(this.lang.get('alchemy', 'Alchemy'), Colors.MAGENTA)}`);
            this.print(`12. ${Colors.wrap(this.lang.get('dungeons', 'Dungeons'), Colors.RED)}`);
            this.print(`13. ${Colors.wrap(this.lang.get('pet_shop', 'Pet Shop'), Colors.CYAN)}`);
            this.print(`14. ${Colors.wrap('Housing', Colors.GREEN)}`);
            this.print(`15. ${Colors.wrap('Farming', Colors.GREEN)}`);
            this.print(`16. ${Colors.wrap('Training', Colors.YELLOW)}`);
            this.print(`17. ${Colors.wrap(this.lang.get('save_game', 'Save Game'), Colors.BLUE)}`);
            this.print(`18. ${Colors.wrap(this.lang.get('load_game', 'Load Game'), Colors.BLUE)}`);
            this.print(`19. ${Colors.wrap(this.lang.get('quit', 'Quit'), Colors.RED)}`);
        } else {
            this.print(`11. ${Colors.wrap(this.lang.get('save_game', 'Save Game'), Colors.BLUE)}`);
            this.print(`12. ${Colors.wrap(this.lang.get('load_game', 'Load Game'), Colors.BLUE)}`);
            this.print(`13. ${Colors.wrap(this.lang.get('quit', 'Quit'), Colors.RED)}`);
        }
        
        const maxChoice = this.currentArea === "your_land" ? "19" : "13";
        const choice = await this.ask(`${this.lang.get('choose_option', 'Choose an option')} (1-${maxChoice}): `);
        
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
                    await this.visitAlchemy();
                } else {
                    await this.saveLoadSystem.save_game();
                }
                break;
            case "12":
                if (this.currentArea === "your_land") {
                    await this.visitDungeons();
                } else {
                    await this.saveLoadSystem.load_game();
                }
                break;
            case "13":
                if (this.currentArea === "your_land") {
                    await this.petShop();
                } else {
                    this.print(Colors.wrap(this.lang.get('thank_exit', 'Thanks for playing!'), Colors.YELLOW));
                    return;
                }
                break;
            case "14":
                if (this.currentArea === "your_land") {
                    await this.buildHome();
                }
                break;
            case "15":
                if (this.currentArea === "your_land") {
                    await this.farmingMenu();
                }
                break;
            case "16":
                if (this.currentArea === "your_land") {
                    await this.trainingMenu();
                }
                break;
            case "17":
                if (this.currentArea === "your_land") {
                    await this.saveLoadSystem.save_game();
                } else {
                    await this.saveLoadSystem.save_game();
                }
                break;
            case "18":
                if (this.currentArea === "your_land") {
                    await this.saveLoadSystem.load_game();
                } else {
                    await this.saveLoadSystem.load_game();
                }
                break;
            case "19":
                if (this.currentArea === "your_land") {
                    this.print(Colors.wrap(this.lang.get('thank_exit', 'Thanks for playing!'), Colors.YELLOW));
                    return;
                }
                break;
            default:
                this.print(Colors.wrap(this.lang.get('invalid_choice', 'Invalid choice'), Colors.RED));
        }
    }
    
    /**
     * Explore current area
     */
    async explore() {
        if (!this.player) {
            this.print(this.lang.get('no_character_created', 'No character created'));
            return;
        }
        
        this.player.advanceTime(5);
        this.updateMissionProgress('check', '');
        
        const areaData = this.areasData[this.currentArea] || {};
        const areaName = areaData.name || "Unknown Area";
        
        this.print(this.lang.get('exploring_area_msg', `Exploring ${areaName}...`));
        
        // 70% chance of encounter
        if (Math.random() < 0.7) {
            await this.randomEncounter();
        } else {
            this.print(this.lang.get('explore_nothing_found', 'You explore the area but find nothing.'));
            
            // Small chance to find gold
            if (Math.random() < 0.3) {
                const foundGold = Math.floor(Math.random() * 15) + 5;
                this.player.gold += foundGold;
                this.print(this.lang.get('found_gold_msg', `You found ${foundGold} gold!`));
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
            this.print(this.lang.get('no_enemies_in_area', 'No enemies in this area'));
            return;
        }
        
        const enemyName = possibleEnemies[Math.floor(Math.random() * possibleEnemies.length)];
        const enemyData = this.enemiesData[enemyName];
        
        if (enemyData) {
            const enemy = new Enemy(enemyData);
            this.print(`\nA wild ${enemy.name} appears!`);
            await this.battle(enemy);
        }
    }
    
    /**
     * Battle system
     */
    async battle(enemy) {
        this.print(this.createSectionHeader(this.lang.get('battle_start', 'BATTLE START'), "!"));
        this.print(`${Colors.wrap(this.player.name, Colors.CYAN)} vs ${Colors.wrap(enemy.name, Colors.RED)}`);
        await this.battleSystem.battle(enemy);
    }
    
    /**
     * Travel to connected areas
     */
    async travel() {
        if (!this.player) {
            this.print(this.lang.get('no_character', 'No character'));
            return;
        }
        
        const areaData = this.areasData[this.currentArea] || {};
        const connections = areaData.connections || [];
        
        this.print(this.createSectionHeader(this.lang.get('travel_title', 'TRAVEL'), "="));
        this.print(`${Colors.wrap(this.lang.get('current_location_label', 'Current location:'), Colors.CYAN)} ${areaData.name || this.currentArea}`);
        
        if (connections.length === 0) {
            this.print(Colors.wrap(this.lang.get('no_connected_areas', 'No connected areas'), Colors.RED));
            return;
        }
        
        this.print(`\n${Colors.wrap(this.lang.get('ui_connected_areas', 'Connected areas:'), Colors.BOLD)}`);
        for (let i = 0; i < connections.length; i++) {
            const area = this.areasData[connections[i]] || {};
            this.print(`${Colors.wrap((i + 1).toString(), Colors.YELLOW)}. ${Colors.wrap(area.name || connections[i], Colors.BOLD)} - ${area.description || ''}`);
        }
        
        const choice = await this.ask(`\n${this.lang.get('travel_to_prompt', 'Travel to')} (1-${connections.length}) ${this.lang.get('or_cancel_prompt', 'or press Enter to cancel')}: `);
        
        if (choice.isDigit()) {
            const idx = parseInt(choice) - 1;
            if (idx >= 0 && idx < connections.length) {
                const newArea = connections[idx];
                const oldAreaName = areaData.name || this.currentArea;
                const newAreaName = this.areasData[newArea]?.name || newArea;
                
                await this.loadingIndicator(`${this.lang.get('traveling_to', 'Traveling to')} ${newAreaName}`);
                
                this.currentArea = newArea;
                this.player.updateWeather(newArea);
                
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
            this.print(this.lang.get('no_character', 'No character'));
            return;
        }
        
        this.print(this.createSectionHeader(this.lang.get('inventory_title', 'INVENTORY'), "="));
        this.print(`${Colors.wrap(this.lang.get('gold', 'Gold:'), Colors.GOLD)} ${this.player.gold}`);
        
        if (this.player.inventory.length === 0) {
            this.print(Colors.wrap(this.lang.get('inventory_empty', 'Your inventory is empty'), Colors.GRAY));
            return;
        }
        
        // Group by type
        const itemsByType = {};
        for (const item of this.player.inventory) {
            const itemData = this.itemsData[item] || {};
            const itemType = itemData.type || "unknown";
            if (!itemsByType[itemType]) itemsByType[itemType] = [];
            itemsByType[itemType].push(item);
        }
        
        for (const [type, items] of Object.entries(itemsByType)) {
            this.print(`\n${Colors.wrap(type.toUpperCase(), Colors.CYAN)}:`);
            for (const item of items) {
                const itemData = this.itemsData[item] || {};
                const rarity = itemData.rarity || "common";
                this.print(`  - ${this.formatItemName(itemData.name || item, rarity)}`);
                if (itemData.description) {
                    this.print(`    ${Colors.wrap(itemData.description, Colors.GRAY)}`);
                }
            }
        }
        
        await this.ask(`\n${this.lang.get('press_enter_back', 'Press Enter to go back...')}`);
    }

    /**
     * View missions
     */
    async viewMissions() {
        if (!this.player) {
            this.print(this.lang.get('no_character', 'No character'));
            return;
        }
        
        this.print(this.createSectionHeader(this.lang.get('missions_title', 'MISSIONS'), "="));
        
        const activeMissions = Object.keys(this.missionProgress).filter(
            mid => !this.missionProgress[mid]?.completed
        );
        
        if (activeMissions.length === 0) {
            this.print(Colors.wrap(this.lang.get('no_active_missions', 'No active missions'), Colors.GRAY));
            this.print(`A. ${Colors.wrap(this.lang.get('available_missions', 'Available Missions'), Colors.GREEN)}`);
            this.print(`B. ${Colors.wrap(this.lang.get('back', 'Back'), Colors.RED)}`);
            
            const choice = await this.ask(`\n${this.lang.get('choose_option', 'Choose an option:')} `);
            if (choice.toUpperCase() === 'A') {
                await this.availableMissionsMenu();
            }
            return;
        }
        
        this.print(`\n${Colors.wrap(this.lang.get('n_active_missions', 'Active Missions:'), Colors.BOLD)}`);
        for (let i = 0; i < activeMissions.length; i++) {
            const mid = activeMissions[i];
            const mission = this.missionsData[mid] || {};
            const progress = this.missionProgress[mid];
            const target = progress.target_count || 1;
            const current = progress.current_count || 0;
            
            this.print(`${Colors.wrap((i + 1).toString(), Colors.YELLOW)}. ${Colors.wrap(mission.name || mid, Colors.BOLD)}`);
            this.print(`   ${this.createProgressBar(current, target, 20, Colors.CYAN)}`);
            this.print(`   ${Colors.wrap(mission.description || '', Colors.GRAY)}`);
        }
        
        await this.ask(`\n${this.lang.get('press_enter_back', 'Press Enter to go back...')}`);
    }
    
    /**
     * Available missions menu
     */
    async availableMissionsMenu() {
        this.print(this.createSectionHeader(this.lang.get('available_missions_title', 'AVAILABLE MISSIONS'), "-"));
        
        const availableMissions = Object.keys(this.missionsData).filter(
            mid => !this.missionProgress[mid] && !this.completedMissions.includes(mid)
        );
        
        if (availableMissions.length === 0) {
            this.print(Colors.wrap(this.lang.get('no_new_missions', 'No new missions available'), Colors.GRAY));
            return;
        }
        
        for (let i = 0; i < availableMissions.length; i++) {
            const mid = availableMissions[i];
            const mission = this.missionsData[mid] || {};
            this.print(`${Colors.wrap((i + 1).toString(), Colors.YELLOW)}. ${Colors.wrap(mission.name || mid, Colors.BOLD)}`);
            this.print(`   ${Colors.wrap(mission.description || '', Colors.GRAY)}`);
            
            const levelReq = mission.unlock_level;
            if (levelReq) {
                const hasLevel = this.player.level >= levelReq;
                const color = hasLevel ? Colors.GREEN : Colors.RED;
                this.print(`   ${Colors.wrap(this.lang.get('level_required', 'Level required:'), color)} ${levelReq}`);
            }
        }
        
        const choice = await this.ask(`\n${this.lang.get('accept_mission_prompt', 'Accept mission')} (1-${availableMissions.length}) ${this.lang.get('or_cancel_prompt', 'or Enter to cancel')}: `);
        
        if (choice.isDigit()) {
            const idx = parseInt(choice) - 1;
            if (idx >= 0 && idx < availableMissions.length) {
                const missionId = availableMissions[idx];
                const mission = this.missionsData[missionId];
                if (mission.unlock_level && this.player.level < mission.unlock_level) {
                    this.print(Colors.wrap(this.lang.get('level_too_low_mission', 'Your level is too low for this mission!'), Colors.RED));
                    return;
                }
                await this.acceptMission(missionId);
            }
        }
    }

    /**
     * Accept a mission
     */
    async acceptMission(missionId) {
        if (this.missionProgress[missionId]) {
            this.print(Colors.wrap(this.lang.get('mission_already_accepted', 'Mission already accepted'), Colors.YELLOW));
            return;
        }
        
        const mission = this.missionsData[missionId];
        if (!mission) {
            this.print(Colors.wrap(this.lang.get('mission_data_not_found', 'Mission not found'), Colors.RED));
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
        
        this.print(`${Colors.wrap(this.lang.get('mission_accepted_msg', 'Mission accepted:'), Colors.GREEN)} ${Colors.wrap(mission.name || missionId, Colors.BOLD)}`);
    }
    
    /**
     * Fight boss menu
     */
    async fightBossMenu() {
        if (!this.player) {
            this.print(this.lang.get('no_character', 'No character'));
            return;
        }
        
        const areaData = this.areasData[this.currentArea] || {};
        const possibleBosses = areaData.possible_bosses || [];
        
        if (possibleBosses.length === 0) {
            this.print(Colors.wrap(this.lang.get('no_bosses_area', `No bosses in ${areaData.name || this.currentArea}`), Colors.RED));
            return;
        }
        
        this.print(this.createSectionHeader(`${this.lang.get('bosses_in', 'BOSSES IN')} ${(areaData.name || this.currentArea).toUpperCase()}`, "="));
        
        for (let i = 0; i < possibleBosses.length; i++) {
            const bossName = possibleBosses[i];
            const bossData = this.bossesData[bossName] || {};
            let status = "";
            
            if (this.player.bossesKilled && this.player.bossesKilled[bossName]) {
                status = ` ${Colors.wrap('(' + this.lang.get('defeated', 'Recently defeated') + ')', Colors.GRAY)}`;
            }
            
            this.print(`${Colors.wrap((i + 1).toString(), Colors.YELLOW)}. ${Colors.wrap(bossData.name || bossName, Colors.BOLD)}${status}`);
        }
        
        const choice = await this.ask(`\n${this.lang.get('choose_boss_prompt', 'Choose a boss')} (1-${possibleBosses.length}) ${this.lang.get('or_cancel_prompt', 'or Enter to cancel')}: `);
        
        if (choice.isDigit()) {
            const idx = parseInt(choice) - 1;
            if (idx >= 0 && idx < possibleBosses.length) {
                const bossName = possibleBosses[idx];
                const bossData = this.bossesData[bossName];
                
                if (bossData) {
                    const boss = new Boss(bossData, this.dialoguesData);
                    this.print(`\n${Colors.wrap(this.lang.get('challenge_accepted', 'Challenge accepted!'), Colors.RED)}`);
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
            this.print(this.lang.get('no_character', 'No character'));
            return;
        }
        
        this.print(this.createSectionHeader(this.lang.get('tavern_title', 'THE TAVERN'), "="));
        this.print(`${Colors.wrap(this.lang.get('your_gold', 'Your gold:'), Colors.GOLD)} ${this.player.gold}`);
        
        this.print(`1. ${Colors.wrap(this.lang.get('buy_food', 'Buy Food'), Colors.GREEN)} (5 Gold) - Restores 20 HP`);
        this.print(`2. ${Colors.wrap(this.lang.get('buy_drink', 'Buy Drink'), Colors.BLUE)} (5 Gold) - Restores 20 MP`);
        this.print(`3. ${Colors.wrap(this.lang.get('hire_companions', 'Hire Companions'), Colors.YELLOW)}`);
        this.print(`4. ${Colors.wrap(this.lang.get('back', 'Back'), Colors.RED)}`);
        
        const choice = await this.ask(`\n${this.lang.get('choose_option', 'Choose an option:')} `);
        
        if (choice === "1") {
            if (this.player.gold >= 5) {
                this.player.gold -= 5;
                const heal = this.player.heal(20);
                this.print(`${Colors.wrap(this.lang.get('bought_food', 'You bought some food and recovered HP!'), Colors.GREEN)} (+${heal} HP)`);
            } else {
                this.print(Colors.wrap(this.lang.get('not_enough_gold', 'Not enough gold!'), Colors.RED));
            }
        } else if (choice === "2") {
            if (this.player.gold >= 5) {
                this.player.gold -= 5;
                this.player.mp = Math.min(this.player.maxMp, this.player.mp + 20);
                this.print(`${Colors.wrap(this.lang.get('bought_drink', 'You bought a drink and recovered MP!'), Colors.BLUE)} (+20 MP)`);
            } else {
                this.print(Colors.wrap(this.lang.get('not_enough_gold', 'Not enough gold!'), Colors.RED));
            }
        } else if (choice === "3") {
            await this.hireCompanionsMenu();
        }
    }

    /**
     * Hire companions menu
     */
    async hireCompanionsMenu() {
        this.print(this.createSectionHeader(this.lang.get('hire_companions', 'HIRE COMPANIONS'), "-"));
        const companions = Object.entries(this.companionsData);
        if (companions.length === 0) {
            this.print(Colors.wrap(this.lang.get('no_companions_available', 'No companions available'), Colors.GRAY));
            return;
        }
        
        for (let i = 0; i < companions.length; i++) {
            const [cid, cdata] = companions[i];
            const price = cdata.price || 0;
            this.print(`${Colors.wrap((i + 1).toString(), Colors.YELLOW)}. ${Colors.wrap(cdata.name || cid, Colors.BOLD)} - ${Colors.wrap(price + ' gold', Colors.GOLD)}`);
            this.print(`   ${Colors.wrap(cdata.description || '', Colors.GRAY)}`);
        }
        
        const choice = await this.ask(`\n${this.lang.get('hire_companion_prompt', 'Hire companion')} (1-${companions.length}) ${this.lang.get('or_leave_prompt', 'or Enter to leave')}: `);
        
        if (choice.isDigit()) {
            const idx = parseInt(choice) - 1;
            if (idx >= 0 && idx < companions.length) {
                const [cid, cdata] = companions[idx];
                const price = cdata.price || 0;
                
                if (this.player.gold >= price) {
                    if (this.player.companions.length >= 4) {
                        this.print(Colors.wrap(this.lang.get('max_companions_msg', "Maximum 4 companions allowed"), Colors.RED));
                        return;
                    }
                    
                    this.player.gold -= price;
                    this.player.companions.push({
                        id: cid,
                        name: cdata.name || cid,
                        level: 1,
                        equipment: { weapon: null, armor: null, accessory: null }
                    });
                    
                    this.print(`${Colors.wrap(this.lang.get('hired_companion_msg', 'Hired {name} for {price} gold!').replace('{name}', cdata.name || cid).replace('{price}', price), Colors.GREEN)}`);
                    this.player.updateStatsFromEquipment(this.itemsData, this.companionsData);
                } else {
                    this.print(Colors.wrap(this.lang.get('not_enough_gold', 'Not enough gold'), Colors.RED));
                }
            }
        }
    }
    
    /**
     * Visit shop
     */
    async visitShop() {
        if (!this.player) {
            this.print(this.lang.get('no_character', 'No character'));
            return;
        }
        
        const areaData = this.areasData[this.currentArea] || {};
        const areaShops = areaData.shops || [];
        
        if (areaShops.length === 0) {
            this.print(Colors.wrap(this.lang.get('no_shops_area', `No shops in ${areaData.name || this.currentArea}`), Colors.RED));
            return;
        }
        
        this.print(this.createSectionHeader(this.lang.get('shops_title', 'SHOPS'), "="));
        this.print(`${Colors.wrap(this.lang.get('your_gold', 'Your gold:'), Colors.GOLD)} ${this.player.gold}\n`);
        
        for (let i = 0; i < areaShops.length; i++) {
            const shopId = areaShops[i];
            const shopData = this.shopsData[shopId] || {};
            this.print(`${Colors.wrap((i + 1).toString(), Colors.YELLOW)}. ${Colors.wrap(shopData.name || shopId, Colors.BOLD)}`);
        }
        
        const choice = await this.ask(`\n${this.lang.get('select_shop_prompt', 'Select a shop')}: `);
        
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
        
        this.print(this.createSectionHeader(shopData.name || shopId.toUpperCase(), "-"));
        
        const items = shopData.items || [];
        if (items.length === 0) {
            this.print(Colors.wrap(this.lang.get('shop_no_items', "This shop has no items"), Colors.GRAY));
            return;
        }
        
        for (let i = 0; i < items.length; i++) {
            const itemId = items[i];
            const itemData = this.itemsData[itemId] || {};
            const price = itemData.price || 0;
            const rarity = itemData.rarity || "common";
            
            this.print(`${Colors.wrap((i + 1).toString(), Colors.YELLOW)}. ${this.formatItemName(itemData.name || itemId, rarity)} - ${Colors.wrap(price + ' gold', Colors.GOLD)}`);
            if (itemData.description) {
                this.print(`   ${Colors.wrap(itemData.description, Colors.GRAY)}`);
            }
        }
        
        const choice = await this.ask(`\n${this.lang.get('buy_item_prompt', 'Buy item')} (1-${items.length}) ${this.lang.get('or_leave_prompt', 'or Enter to leave')}: `);
        
        if (choice.isDigit()) {
            const idx = parseInt(choice) - 1;
            if (idx >= 0 && idx < items.length) {
                const itemId = items[idx];
                const itemData = this.itemsData[itemId];
                const price = itemData?.price || 0;
                
                if (this.player.gold >= price) {
                    this.player.gold -= price;
                    this.player.inventory.push(itemId);
                    this.print(`${Colors.wrap(this.lang.get('purchased_item_msg', 'Purchased {item} for {price} gold!').replace('{item}', itemData?.name || itemId).replace('{price}', price), Colors.GREEN)}`);
                } else {
                    this.print(Colors.wrap(this.lang.get('not_enough_gold', 'Not enough gold'), Colors.RED));
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
            this.print(this.lang.get('no_character', 'No character'));
            return;
        }
        
        const areaData = this.areasData[this.currentArea] || {};
        const canRest = areaData.can_rest || false;
        const restCost = areaData.rest_cost || 10;
        
        if (!canRest) {
            this.print(Colors.wrap(this.lang.get('cannot_rest_here', `You cannot rest here. It's too dangerous!`), Colors.RED));
            return;
        }
        
        this.print(this.createSectionHeader(this.lang.get('rest_title', 'REST'), "="));
        this.print(`${Colors.wrap(this.lang.get('rest_cost_label', 'Rest Cost:'), Colors.GOLD)} ${restCost} gold`);
        this.print(`HP: ${this.createHpMpBar(this.player.hp, this.player.maxHp, 20, Colors.RED)}`);
        this.print(`MP: ${this.createHpMpBar(this.player.mp, this.player.maxMp, 20, Colors.BLUE)}`);
        
        if (this.player.gold < restCost) {
            this.print(Colors.wrap(this.lang.get('not_enough_gold', 'Not enough gold!'), Colors.RED));
            return;
        }
        
        const choice = await this.ask(`${this.lang.get('rest_prompt', 'Rest for {cost} gold?').replace('{cost}', restCost)} (y/n): `);
        
        if (choice.toLowerCase() === 'y') {
            await this.loadingIndicator(this.lang.get('resting_msg', 'Resting...'));
            this.player.gold -= restCost;
            this.player.hp = this.player.maxHp;
            this.player.mp = this.player.maxMp;
            this.print(Colors.wrap(this.lang.get('rest_success_msg', 'You rest and recover full health!'), Colors.GREEN));
        }
    }
    
    /**
     * Manage companions
     */
    async manageCompanions() {
        if (!this.player) {
            this.print(this.lang.get('no_character', 'No character'));
            return;
        }
        
        this.print(this.createSectionHeader(this.lang.get('companions_title', 'COMPANIONS'), "="));
        this.print(`${Colors.wrap(this.lang.get('active_companions_label', 'Active companions:'), Colors.CYAN)} ${this.player.companions?.length || 0}/4`);
        
        if (!this.player.companions || this.player.companions.length === 0) {
            this.print(Colors.wrap(this.lang.get('no_companions_msg', "You have no companions. Visit the tavern to hire some!"), Colors.GRAY));
            return;
        }
        
        for (let i = 0; i < this.player.companions.length; i++) {
            const companion = this.player.companions[i];
            const compName = companion.name || companion;
            const compLevel = companion.level || 1;
            
            this.print(`\n${Colors.wrap((i + 1).toString(), Colors.YELLOW)}. ${Colors.wrap(compName, Colors.BOLD)} (Level ${compLevel})`);
            
            // Find companion data for bonuses
            let compData = null;
            for (const [cid, cdata] of Object.entries(this.companionsData)) {
                if (cdata.name === compName || cid === companion.id) {
                    compData = cdata;
                    break;
                }
            }
            
            if (compData) {
                const bonuses = [];
                if (compData.attack_bonus) bonuses.push(`${Colors.wrap('+' + compData.attack_bonus + ' ATK', Colors.RED)}`);
                if (compData.defense_bonus) bonuses.push(`${Colors.wrap('+' + compData.defense_bonus + ' DEF', Colors.BLUE)}`);
                if (compData.speed_bonus) bonuses.push(`${Colors.wrap('+' + compData.speed_bonus + ' SPD', Colors.GREEN)}`);
                if (bonuses.length > 0) {
                    this.print(`   Bonuses: ${bonuses.join(', ')}`);
                }
            }
        }
        
        this.print(`\nD. ${Colors.wrap(this.lang.get('dismiss_companion', 'Dismiss Companion'), Colors.RED)}`);
        this.print(`B. ${Colors.wrap(this.lang.get('back', 'Back'), Colors.GRAY)}`);
        
        const choice = await this.ask(`\n${this.lang.get('choose_action', 'Choose action:')} `);
        
        if (choice.toUpperCase() === 'D') {
            const dismissChoice = await this.ask(`${this.lang.get('dismiss_which_prompt', 'Dismiss which companion')} (1-${this.player.companions.length})? `);
            if (dismissChoice.isDigit()) {
                const idx = parseInt(dismissChoice) - 1;
                if (idx >= 0 && idx < this.player.companions.length) {
                    const dismissed = this.player.companions.splice(idx, 1)[0];
                    this.print(`${Colors.wrap(this.lang.get('dismissed_msg', 'Dismissed {name}.').replace('{name}', dismissed.name || dismissed), Colors.YELLOW)}`);
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
            this.print(this.lang.get('no_character', 'No character'));
            return;
        }
        
        this.print(this.createSectionHeader(this.lang.get('pet_shop_title', 'PET SHOP'), "="));
        this.print(`${Colors.wrap(this.lang.get('your_gold', 'Your Gold:'), Colors.GOLD)} ${this.player.gold}`);
        
        const currentPet = this.player.activePet ? (this.petsData[this.player.activePet]?.name || this.player.activePet) : this.lang.get('none', 'None');
        this.print(`${Colors.wrap(this.lang.get('current_pet_label', 'Current Pet:'), Colors.CYAN)} ${currentPet}\n`);
        
        this.print(`1. ${Colors.wrap(this.lang.get('buy_pet', 'Buy Pet'), Colors.GREEN)}`);
        this.print(`2. ${Colors.wrap(this.lang.get('manage_pets', 'Manage Pets'), Colors.YELLOW)}`);
        this.print(`3. ${Colors.wrap(this.lang.get('back', 'Back'), Colors.RED)}`);
        
        const choice = await this.ask(`${this.lang.get('select_option_prompt', 'Select an option')}: `);
        
        if (choice === "1") {
            await this.buyPetMenu();
        } else if (choice === "2") {
            await this.managePetsMenu();
        }
    }

    /**
     * Buy pet menu
     */
    async buyPetMenu() {
        this.print(this.createSectionHeader(this.lang.get('buy_pet', 'BUY PET'), "-"));
        const petEntries = Object.entries(this.petsData);
        if (petEntries.length === 0) {
            this.print(Colors.wrap(this.lang.get('no_pets_available', 'No pets available'), Colors.GRAY));
            return;
        }
        
        this.print(`\n${Colors.wrap(this.lang.get('available_pets', 'Available Pets:'), Colors.BOLD)}`);
        for (let i = 0; i < petEntries.length; i++) {
            const [petId, pet] = petEntries[i];
            const isOwned = this.player.petsOwned?.includes(petId);
            if (!isOwned) {
                this.print(`${Colors.wrap((i + 1).toString(), Colors.YELLOW)}. ${Colors.wrap(pet.name || petId, Colors.BOLD)} - ${Colors.wrap(pet.price + 'g', Colors.GOLD)}: ${Colors.wrap(pet.description || '', Colors.GRAY)}`);
            } else {
                this.print(`${Colors.wrap((i + 1).toString(), Colors.YELLOW)}. ${Colors.wrap(pet.name || petId, Colors.BOLD)} ${Colors.wrap('(' + this.lang.get('owned', 'Owned') + ')', Colors.GREEN)}`);
            }
        }
        
        const petChoice = await this.ask(`\n${this.lang.get('buy_pet_choice_prompt', 'Enter number to buy (or Enter to cancel)')}: `);
        
        if (petChoice.isDigit()) {
            const idx = parseInt(petChoice) - 1;
            if (idx >= 0 && idx < petEntries.length) {
                const [petId, pet] = petEntries[idx];
                if (this.player.petsOwned?.includes(petId)) {
                    this.print(Colors.wrap(this.lang.get('already_owned', 'Already owned!'), Colors.YELLOW));
                    return;
                }
                
                const price = pet.price || 0;
                if (this.player.gold >= price) {
                    this.player.gold -= price;
                    if (!this.player.petsOwned) this.player.petsOwned = [];
                    this.player.petsOwned.push(petId);
                    this.player.activePet = petId;
                    this.print(`${Colors.wrap(this.lang.get('purchased_pet_msg', 'You bought a {pet}!').replace('{pet}', pet.name || petId), Colors.GREEN)}`);
                } else {
                    this.print(Colors.wrap(this.lang.get('not_enough_gold', 'Not enough gold!'), Colors.RED));
                }
            }
        }
    }

    /**
     * Manage pets menu
     */
    async managePetsMenu() {
        this.print(this.createSectionHeader(this.lang.get('manage_pets', 'MANAGE PETS'), "-"));
        if (!this.player.petsOwned || this.player.petsOwned.length === 0) {
            this.print(Colors.wrap(this.lang.get('no_pets_owned', "You don't own any pets."), Colors.GRAY));
            return;
        }
        
        this.print(`\n${Colors.wrap(this.lang.get('your_pets', 'Your Pets:'), Colors.BOLD)}`);
        for (let i = 0; i < this.player.petsOwned.length; i++) {
            const petId = this.player.petsOwned[i];
            const petName = this.petsData[petId]?.name || petId;
            const status = petId === this.player.activePet ? ` ${Colors.wrap('[ACTIVE]', Colors.GREEN)}` : "";
            this.print(`${Colors.wrap((i + 1).toString(), Colors.YELLOW)}. ${Colors.wrap(petName, Colors.BOLD)}${status}`);
        }
        
        const sel = await this.ask(`\n${this.lang.get('select_pet_activate_prompt', 'Select pet to activate')} (1-${this.player.petsOwned.length}) ${this.lang.get('or_cancel_prompt', 'or Enter to cancel')}: `);
        if (sel.isDigit()) {
            const idx = parseInt(sel) - 1;
            if (idx >= 0 && idx < this.player.petsOwned.length) {
                this.player.activePet = this.player.petsOwned[idx];
                const pName = this.petsData[this.player.activePet]?.name || this.player.activePet;
                this.print(`${Colors.wrap(this.lang.get('pet_activated_msg', '{pet} is now active!').replace('{pet}', pName), Colors.GREEN)}`);
            }
        }
    }
    
    /**
     * Build home (housing)
     */
    async buildHome() {
        if (!this.player) {
            this.print(this.lang.get('no_character', 'No character'));
            return;
        }

        while (true) {
            this.clear_screen();
            this.print(this.createSectionHeader(this.lang.get('build_home_title', 'BUILD HOME'), "="));
            this.print(`${Colors.wrap(this.lang.get('comfort_points_label', 'Comfort Points:'), Colors.CYAN)} ${this.player.comfortPoints || 0}`);
            this.print(`${Colors.wrap(this.lang.get('items_owned_label', 'Items owned:'), Colors.YELLOW)} ${this.player.housingOwned.length}\n`);

            this.print(`S. ${Colors.wrap('Housing Shop', Colors.GOLD)}`);
            this.print(`V. ${Colors.wrap('View/Manage Slots', Colors.CYAN)}`);
            this.print(`B. ${Colors.wrap(this.lang.get('back', 'Back'), Colors.RED)}`);

            const choice = await this.ask(`${this.lang.get('choose_option', 'Choose an option')}: `);
            const uc = choice.toUpperCase();

            if (uc === 'B') break;
            if (uc === 'S') await this.visitHousingShop();
            if (uc === 'V') await this.manageHousingSlots();
        }
    }

    async visitHousingShop() {
        this.clear_screen();
        this.print(this.createSectionHeader('HOUSING SHOP', "="));
        const items = Object.entries(this.housingData || {});
        if (items.length === 0) {
            this.print(Colors.wrap("No housing items available in data!", Colors.RED));
            await this.ask('Press Enter...');
            return;
        }
        for (let i = 0; i < items.length; i++) {
            const [id, data] = items[i];
            this.print(`${i + 1}. ${Colors.wrap(data.name || id, Colors.YELLOW)} - ${data.price} Gold (+${data.comfort_points} Comfort)`);
        }
        const choice = await this.ask(`\nBuy item (1-${items.length}) or Enter to cancel: `);
        if (choice && !isNaN(choice)) {
            const idx = parseInt(choice) - 1;
            if (idx >= 0 && idx < items.length) {
                const [id, data] = items[idx];
                if (this.player.gold >= data.price) {
                    this.player.gold -= data.price;
                    if (!this.player.housingOwned) this.player.housingOwned = [];
                    this.player.housingOwned.push(id);
                    this.print(Colors.wrap(`Bought ${data.name}!`, Colors.GREEN));
                } else {
                    this.print(Colors.wrap('Not enough gold!', Colors.RED));
                }
                await this.ask('Press Enter to continue...');
            }
        }
    }

    async manageHousingSlots() {
        const buildingTypes = {
            house: { label: "House", slots: 3 },
            decoration: { label: "Decoration", slots: 10 },
            fencing: { label: "Fencing", slots: 1 },
            garden: { label: "Garden", slots: 3 },
            farm: { label: "Farm", slots: 2 },
            training_place: { label: "Training Place", slots: 3 }
        };

        while (true) {
            this.clear_screen();
            this.print(this.createSectionHeader('MANAGE SLOTS', "-"));
            const types = Object.keys(buildingTypes);
            for (let i = 0; i < types.length; i++) {
                this.print(`${i + 1}. ${buildingTypes[types[i]].label}`);
            }
            const choice = await this.ask(`\nSelect category (1-${types.length}) or B to back: `);
            if (choice && choice.toUpperCase() === 'B') break;
            if (choice && !isNaN(choice)) {
                const idx = parseInt(choice) - 1;
                if (idx >= 0 && idx < types.length) {
                    await this.manageSpecificSlots(types[idx], buildingTypes[types[idx]]);
                }
            }
        }
    }

    async manageSpecificSlots(bType, info) {
        while (true) {
            this.clear_screen();
            this.print(this.createSectionHeader(`${info.label.toUpperCase()} SLOTS`, "-"));
            for (let i = 1; i <= info.slots; i++) {
                const slot = `${bType}_${i}`;
                const itemId = this.player.buildingSlots?.[slot];
                const itemName = itemId ? (this.housingData[itemId]?.name || itemId) : 'Empty';
                this.print(`${i}. ${slot}: ${Colors.wrap(itemName, itemId ? Colors.GREEN : Colors.GRAY)}`);
            }
            const choice = await this.ask(`\nSelect slot (1-${info.slots}) or B to back: `);
            if (choice && choice.toUpperCase() === 'B') break;
            if (choice && !isNaN(choice)) {
                const slotIdx = parseInt(choice);
                if (slotIdx >= 1 && slotIdx <= info.slots) {
                    await this.placeItemInSlot(`${bType}_${slotIdx}`, bType);
                }
            }
        }
    }

    async placeItemInSlot(slotName, bType) {
        this.clear_screen();
        const available = (this.player.housingOwned || []).filter(id => this.housingData[id]?.type === bType);
        this.print(this.createSectionHeader(`PLACE IN ${slotName.toUpperCase()}`, "-"));
        this.print(`0. Clear Slot`);
        for (let i = 0; i < available.length; i++) {
            const data = this.housingData[available[i]];
            this.print(`${i + 1}. ${data.name} (+${data.comfort_points} Comfort)`);
        }
        const choice = await this.ask(`\nSelect item (0-${available.length}) or Enter to cancel: `);
        if (choice === '0') {
            if (!this.player.buildingSlots) this.player.buildingSlots = {};
            const oldId = this.player.buildingSlots[slotName];
            if (oldId) {
                this.player.comfortPoints = (this.player.comfortPoints || 0) - (this.housingData[oldId]?.comfort_points || 0);
                this.player.buildingSlots[slotName] = null;
            }
        } else if (choice && !isNaN(choice)) {
            const idx = parseInt(choice) - 1;
            if (idx >= 0 && idx < available.length) {
                const newId = available[idx];
                if (!this.player.buildingSlots) this.player.buildingSlots = {};
                const oldId = this.player.buildingSlots[slotName];
                if (oldId) this.player.comfortPoints = (this.player.comfortPoints || 0) - (this.housingData[oldId]?.comfort_points || 0);
                this.player.buildingSlots[slotName] = newId;
                this.player.comfortPoints = (this.player.comfortPoints || 0) + (this.housingData[newId]?.comfort_points || 0);
            }
        }
    }

    async trainingMenu() {
        if (!this.player) return;
        const hasTraining = Object.keys(this.player.buildingSlots || {}).some(s => s.startsWith('training_place') && this.player.buildingSlots[s]);
        if (!hasTraining) {
            this.print(Colors.wrap("You need a Training Place built first!", Colors.RED));
            await this.ask("Press Enter...");
            return;
        }

        while (true) {
            this.clear_screen();
            this.print(this.createSectionHeader('TRAINING GROUND', "="));
            this.print("1. Morning (+4%/+2%/-1%)\n2. Calm (+13%/+10%/+7%/+1%/-3%)\n3. Normal (+10%/-7%)\n4. Intense (+20%/+15%/+10%/-10%/-20%)\nB. Back");
            const choice = await this.ask("Choice: ");
            if (choice && choice.toUpperCase() === 'B') break;
            if (['1','2','3','4'].includes(choice)) {
                const roll = Math.floor(Math.random() * (choice === '1' ? 4 : choice === '2' ? 6 : choice === '3' ? 8 : 20)) + 1;
                this.print(`Rolled a ${roll}!`);
                this.player.attack = (this.player.attack || 10) + 1; 
                this.print("Stats improved!");
                await this.ask("Press Enter...");
            }
        }
    }

    async farmingMenu() {
        if (!this.player) return;
        const hasFarm = Object.keys(this.player.buildingSlots || {}).some(s => s.startsWith('farm') && this.player.buildingSlots[s]);
        if (!hasFarm) {
            this.print(Colors.wrap("You need a Farm built first!", Colors.RED));
            await this.ask("Press Enter...");
            return;
        }

        while (true) {
            this.clear_screen();
            this.print(this.createSectionHeader('FARMING', "="));
            this.print("P. Plant Crop\nH. Harvest\nS. Sell Crops\nB. Back");
            const choice = await this.ask("Choice: ");
            if (!choice) continue;
            const uc = choice.toUpperCase();
            if (uc === 'B') break;
            if (uc === 'P') this.print("Planted!"); 
            if (uc === 'H') this.print("Harvested!");
            if (uc === 'S') {
                this.player.gold = (this.player.gold || 0) + 100;
                this.print("Sold crops for 100 gold!");
            }
            await this.ask("Press Enter...");
        }
    }
    
    /**
     * Load a saved game
     */
    async loadGame() {
        if (this.saveLoadSystem) {
            return await this.saveLoadSystem.load_game();
        }
    }

    /**
     * Save the current game
     */
    async saveGame() {
        if (this.saveLoadSystem) {
            return await this.saveLoadSystem.save_game();
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
                    this.print(`${Colors.wrap('[Mission]', Colors.CYAN)} ${Colors.wrap(mission.name, Colors.BOLD)}: ${progress.current_count}/${progress.target_count}`);
                    
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
            
            this.print(`\n${Colors.wrap('!!! MISSION COMPLETE: ' + (mission?.name || missionId) + ' !!!', Colors.GREEN + Colors.BOLD)}`);
            this.print(Colors.wrap(this.lang.get('claim_rewards_msg', 'You can now claim your rewards from the menu.'), Colors.YELLOW));
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
        
        this.print(`\n✓ Challenge Completed: ${challenge.name}!`);
        this.print(`  Reward: ${rewardExp} EXP + ${rewardGold} Gold`);
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
            this.print(Colors.wrap(this.lang.get('no_consumables', "No consumable items!"), Colors.RED));
            return;
        }
        
        this.print(this.createSectionHeader(this.lang.get('consumables_title', 'CONSUMABLES'), "-"));
        for (let i = 0; i < consumables.length; i++) {
            const item = consumables[i];
            const itemData = this.itemsData[item];
            const rarity = itemData?.rarity || "common";
            this.print(`${Colors.wrap((i + 1).toString(), Colors.YELLOW)}. ${this.formatItemName(itemData?.name || item, rarity)} - ${Colors.wrap(itemData?.description || 'Unknown effect', Colors.GRAY)}`);
        }
        
        const choice = await this.ask(`\n${this.lang.get('choose_item_prompt', 'Choose item')} (1-${consumables.length}): `);
        
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
                const actualHeal = this.player.heal(healAmount);
                this.print(`${Colors.wrap(this.lang.get('used_item_msg', 'Used {item}').replace('{item}', itemData.name || item), Colors.GREEN)}, ${this.lang.get('healed_msg', 'healed {amount} HP!').replace('{amount}', actualHeal)}`);
            } else if (itemData.effect === "mp_restore") {
                const mpAmount = itemData.value || 0;
                const oldMp = this.player.mp;
                this.player.mp = Math.min(this.player.maxMp, this.player.mp + mpAmount);
                const restored = this.player.mp - oldMp;
                this.print(`${Colors.wrap(this.lang.get('used_item_msg', 'Used {item}').replace('{item}', itemData.name || item), Colors.BLUE)}, ${this.lang.get('restored_mp_msg', 'restored {amount} MP!').replace('{amount}', restored)}`);
            }
        }
    }
    
    // =====================================================
    // ALCHEMY/CRAFTING SYSTEM (1.1)
    // =====================================================
    
    /**
     * Visit the Alchemy workshop to craft items
     */
    async visitAlchemy() {
        if (!this.player) {
            this.print(this.lang.get('no_character', 'No character'));
            return;
        }
        
        if (!this.craftingData || !this.craftingData.recipes) {
            this.print(Colors.wrap(this.lang.get('ui_no_crafting_recipes', 'No crafting recipes available!'), Colors.YELLOW));
            return;
        }
        
        this.clear_screen();
        this.print(this.createSectionHeader(this.lang.get('alchemy_title', 'ALCHEMY WORKSHOP'), "="));
        this.print(`Welcome to the Alchemy Workshop! Here you can craft potions, elixirs, and items.`);
        this.print(`${Colors.wrap(this.lang.get('your_gold', 'Your Gold:'), Colors.GOLD)} ${this.player.gold}\n`);
        
        // Display available materials from inventory
        await this.displayCraftingMaterials();
        
        while (true) {
            this.print(`\n${Colors.wrap(this.lang.get('alchemy_categories', 'Categories:'), Colors.BOLD)}`);
            this.print(`P. ${Colors.wrap('Potions', Colors.CYAN)}`);
            this.print(`E. ${Colors.wrap('Elixirs/Enchantments', Colors.BLUE)}`);
            this.print(`U. ${Colors.wrap('Utility', Colors.GREEN)}`);
            this.print(`A. ${Colors.wrap('All Recipes', Colors.YELLOW)}`);
            this.print(`C. ${Colors.wrap('Craft Item', Colors.RED)}`);
            this.print(`M. ${Colors.wrap('View Materials', Colors.GRAY)}`);
            this.print(`B. ${Colors.wrap(this.lang.get('back', 'Back'), Colors.RED)}`);
            
            const choice = await this.ask(`${this.lang.get('choose_option', 'Choose an option')}: `);
            const uc = choice.toUpperCase();
            
            if (uc === 'B') {
                break;
            } else if (uc === 'P') {
                await this.displayRecipesByCategory('Potions');
            } else if (uc === 'E') {
                this.print(`\n${Colors.wrap('Select Sub-category:', Colors.BOLD)}`);
                this.print(`E. ${Colors.wrap('Elixirs', Colors.BLUE)}`);
                this.print(`N. ${Colors.wrap('Enchantments', Colors.PURPLE)}`);
                const subChoice = await this.ask(`Choice (E/N): `);
                if (subChoice.toUpperCase() === 'E') {
                    await this.displayRecipesByCategory('Elixirs');
                } else if (subChoice.toUpperCase() === 'N') {
                    await this.displayRecipesByCategory('Enchantments');
                }
            } else if (uc === 'U') {
                await this.displayRecipesByCategory('Utility');
            } else if (uc === 'A') {
                await this.displayAllRecipes();
            } else if (uc === 'C') {
                await this.craftItem();
            } else if (uc === 'M') {
                await this.displayCraftingMaterials();
            }
            this.clear_screen();
        }
    }
    
    /**
     * Display materials available in player's inventory for crafting
     */
    async displayCraftingMaterials() {
        if (!this.player) return;
        
        this.print(`\n${Colors.wrap(this.lang.get('your_materials', 'Your Materials:'), Colors.BOLD)}`);
        
        // Get all material categories
        const materialCategories = this.craftingData.material_categories || {};
        
        // Collect all possible materials
        const allMaterials = new Set();
        for (const materials of Object.values(materialCategories)) {
            for (const material of materials) {
                allMaterials.add(material);
            }
        }
        
        // Count materials in inventory
        const materialCounts = {};
        for (const item of this.player.inventory) {
            if (allMaterials.has(item)) {
                materialCounts[item] = (materialCounts[item] || 0) + 1;
            }
        }
        
        if (Object.keys(materialCounts).length === 0) {
            this.print(Colors.wrap(this.lang.get('no_crafting_materials', 'No crafting materials in inventory!'), Colors.YELLOW));
            this.print(Colors.wrap(this.lang.get('find_materials_hint', 'Materials can be found as drops from enemies.'), Colors.GRAY));
            return;
        }
        
        this.print(`${Colors.wrap('Material', Colors.CYAN).padEnd(25)} ${Colors.wrap('Qty', Colors.YELLOW)}`);
        this.print("-".repeat(35));
        for (const [material, count] of Object.entries(materialCounts)) {
            this.print(`${material.padEnd(25)} ${count}`);
        }
    }
    
    /**
     * Display recipes filtered by category
     */
    async displayRecipesByCategory(category) {
        if (!this.craftingData) return;
        
        const recipes = this.craftingData.recipes || {};
        const categoryRecipes = Object.entries(recipes).filter(
            ([, rdata]) => rdata.category === category
        );
        
        if (categoryRecipes.length === 0) {
            this.print(Colors.wrap(`No recipes for ${category}`, Colors.YELLOW));
            return;
        }
        
        this.print(`\n${Colors.wrap(category.toUpperCase(), Colors.BOLD)}:`);
        for (let i = 0; i < categoryRecipes.length; i++) {
            const [rid, rdata] = categoryRecipes[i];
            const name = rdata.name || rid;
            const rarity = rdata.rarity || "common";
            this.print(`${i + 1}. ${this.formatItemName(name, rarity)}`);
        }
        
        await this.ask(`\n${this.lang.get('press_enter_back', 'Press Enter to go back...')}`);
    }
    
    /**
     * Display all available recipes
     */
    async displayAllRecipes() {
        if (!this.craftingData) return;
        
        const recipes = this.craftingData.recipes || {};
        if (Object.keys(recipes).length === 0) {
            this.print(Colors.wrap(this.lang.get('no_recipes_available', 'No recipes available!'), Colors.YELLOW));
            return;
        }
        
        this.print(this.createSectionHeader(this.lang.get('all_recipes', 'ALL RECIPES'), "-"));
        
        const recipeEntries = Object.entries(recipes);
        const pageSize = 10;
        let currentPage = 0;
        
        while (true) {
            const start = currentPage * pageSize;
            const end = start + pageSize;
            const pageItems = recipeEntries.slice(start, end);
            
            for (let i = 0; i < pageItems.length; i++) {
                const [rid, rdata] = pageItems[i];
                const name = rdata.name || rid;
                const category = rdata.category || 'Unknown';
                const rarity = rdata.rarity || "common";
                this.print(`${start + i + 1}. ${this.formatItemName(name, rarity)} (${category})`);
            }
            
            const totalPages = Math.ceil(recipeEntries.length / pageSize);
            this.print(`\nPage ${currentPage + 1}/${totalPages}`);
            
            if (currentPage < totalPages - 1) {
                this.print(`N. ${Colors.wrap('Next Page', Colors.YELLOW)}`);
            }
            if (currentPage > 0) {
                this.print(`P. ${Colors.wrap('Previous Page', Colors.YELLOW)}`);
            }
            this.print(`C. ${Colors.wrap('Craft Item', Colors.RED)}`);
            this.print(`B. ${Colors.wrap(this.lang.get('back', 'Back'), Colors.RED)}`);
            
            const choice = await this.ask(`${this.lang.get('choose_option', 'Choose an option')}: `);
            const uc = choice.toUpperCase();
            
            if (uc === 'B') {
                break;
            } else if (uc === 'C') {
                await this.craftItem();
                break;
            } else if (uc === 'N' && currentPage < totalPages - 1) {
                currentPage++;
                continue;
            } else if (uc === 'P' && currentPage > 0) {
                currentPage--;
                continue;
            } else if (choice.isDigit()) {
                const idx = parseInt(choice) - 1;
                if (idx >= 0 && idx < recipeEntries.length) {
                    const [rid, rdata] = recipeEntries[idx];
                    await this.showRecipeDetails(rid, rdata);
                }
            } else {
                break;
            }
        }
    }
    
    /**
     * Show recipe details
     */
    async showRecipeDetails(recipeId, recipeData) {
        const name = recipeData.name || recipeId;
        const rarity = recipeData.rarity || "common";
        const category = recipeData.category || "Unknown";
        const description = recipeData.description || "";
        
        this.print(`\n${this.formatItemName(name, rarity)} (${category})`);
        if (description) {
            this.print(`  ${description}`);
        }
        
        // Show required materials
        const materials = recipeData.materials || {};
        this.print(`\n${Colors.wrap('Required Materials:', Colors.BOLD)}`);
        for (const [material, quantity] of Object.entries(materials)) {
            const playerHas = this.player.inventory.filter(i => i === material).length;
            const hasEnough = playerHas >= quantity;
            const status = hasEnough ? Colors.wrap('✓', Colors.GREEN) : Colors.wrap('✗', Colors.RED);
            this.print(`  ${status} ${material}: ${playerHas}/${quantity}`);
        }
        
        // Show result
        const result = recipeData.result || {};
        this.print(`\n${Colors.wrap('Result:', Colors.BOLD)}`);
        this.print(`  ${this.formatItemName(result.name || recipeId, rarity)} x${result.quantity || 1}`);
        
        await this.ask(`\n${this.lang.get('press_enter_back', 'Press Enter to go back...')}`);
    }
    
    /**
     * Craft an item
     */
    async craftItem() {
        if (!this.player || !this.craftingData) return;
        
        const recipes = this.craftingData.recipes || {};
        const recipeEntries = Object.entries(recipes);
        
        if (recipeEntries.length === 0) {
            this.print(Colors.wrap(this.lang.get('no_recipes_available', 'No recipes available!'), Colors.YELLOW));
            return;
        }
        
        this.print(this.createSectionHeader(this.lang.get('craft_item', 'CRAFT ITEM'), "-"));
        
        // Show recipes with material availability
        const craftableRecipes = [];
        
        for (let i = 0; i < recipeEntries.length; i++) {
            const [rid, rdata] = recipeEntries[i];
            const materials = rdata.materials || {};
            
            // Check if player has all materials
            let canCraft = true;
            for (const [material, quantity] of Object.entries(materials)) {
                const playerHas = this.player.inventory.filter(item => item === material).length;
                if (playerHas < quantity) {
                    canCraft = false;
                    break;
                }
            }
            
            const name = rdata.name || rid;
            const rarity = rdata.rarity || "common";
            const status = canCraft ? Colors.wrap('[CRAFTABLE]', Colors.GREEN) : Colors.wrap('[MISSING MATERIALS]', Colors.RED);
            this.print(`${i + 1}. ${this.formatItemName(name, rarity)} ${status}`);
            
            if (canCraft) {
                craftableRecipes.push([rid, rdata, i + 1]);
            }
        }
        
        if (craftableRecipes.length === 0) {
            this.print(Colors.wrap(this.lang.get('no_craftable_items', 'No craftable items - missing materials!'), Colors.YELLOW));
            return;
        }
        
        const choice = await this.ask(`\n${this.lang.get('craft_prompt', 'Choose recipe to craft')} (1-${recipeEntries.length}) ${this.lang.get('or_cancel_prompt', 'or Enter to cancel')}: `);
        
        if (!choice.isDigit()) return;
        
        const idx = parseInt(choice) - 1;
        if (idx < 0 || idx >= recipeEntries.length) return;
        
        const [rid, rdata] = recipeEntries[idx];
        const materials = rdata.materials || {};
        
        // Verify materials again
        for (const [material, quantity] of Object.entries(materials)) {
            const playerHas = this.player.inventory.filter(item => item === material).length;
            if (playerHas < quantity) {
                this.print(Colors.wrap(this.lang.get('not_enough_materials', 'Not enough materials!'), Colors.RED));
                return;
            }
        }
        
        // Consume materials
        for (const [material, quantity] of Object.entries(materials)) {
            for (let i = 0; i < quantity; i++) {
                const index = this.player.inventory.indexOf(material);
                if (index > -1) {
                    this.player.inventory.splice(index, 1);
                }
            }
        }
        
        // Add crafted item
        const result = rdata.result || {};
        const itemName = result.name || rid;
        const itemQuantity = result.quantity || 1;
        
        for (let i = 0; i < itemQuantity; i++) {
            this.player.inventory.push(itemName);
        }
        
        const name = rdata.name || rid;
        const rarity = rdata.rarity || "common";
        
        this.print(`${Colors.wrap(this.lang.get('crafted_msg', 'Crafted:'), Colors.GREEN)} ${this.formatItemName(name, rarity)} x${itemQuantity}!`);
    }
    
    // =====================================================
    // DUNGEONS SYSTEM (1.2)
    // =====================================================
    
    /**
     * Visit the dungeon menu to select and enter dungeons
     */
    async visitDungeons() {
        if (!this.player) {
            this.print(this.lang.get('no_character', 'No character'));
            return;
        }
        
        this.print(this.createSectionHeader(this.lang.get('dungeons_title', 'DUNGEONS'), "="));
        this.print(Colors.wrap(this.lang.get('dungeon_portal', 'The dungeon portal awaits...'), Colors.YELLOW));
        
        // Check if player is in a dungeon
        if (this.currentDungeon) {
            this.print(`\n${Colors.wrap(this.lang.get('currently_in_dungeon', 'You are currently in:'), Colors.YELLOW)} ${this.currentDungeon.name}`);
            this.print(`${Colors.wrap('Progress:', Colors.CYAN)} Room ${this.dungeonProgress + 1}/${this.dungeonRooms.length}`);
            
            this.print(`\nC. ${Colors.wrap(this.lang.get('continue_dungeon', 'Continue'), Colors.GREEN)}`);
            this.print(`E. ${Colors.wrap(this.lang.get('exit_dungeon', 'Exit'), Colors.RED)}`);
            
            const choice = await this.ask(`${this.lang.get('choose_option', 'Choose an option')}: `);
            
            if (choice.toUpperCase() === 'C') {
                await this.continueDungeon();
            } else if (choice.toUpperCase() === 'E') {
                await this.exitDungeon();
            }
            return;
        }
        
        // Show available dungeons
        const allDungeons = this.dungeonsData.dungeons || [];
        if (allDungeons.length === 0) {
            this.print(Colors.wrap(this.lang.get('no_dungeons', 'No dungeons available!'), Colors.YELLOW));
            return;
        }
        
        // Filter dungeons by allowed_areas
        const dungeons = allDungeons.filter(dungeon => {
            const allowedAreas = dungeon.allowed_areas || [];
            return !allowedAreas.length || allowedAreas.includes(this.currentArea);
        });
        
        if (dungeons.length === 0) {
            this.print(Colors.wrap(this.lang.get('no_dungeons_here', 'No dungeons available in this area!'), Colors.YELLOW));
            return;
        }
        
        this.print(`\n${Colors.wrap(this.lang.get('available_dungeons', 'Available Dungeons:'), Colors.BOLD)}`);
        for (let i = 0; i < dungeons.length; i++) {
            const dungeon = dungeons[i];
            const difficulty = dungeon.difficulty || [1, 3];
            const rooms = dungeon.rooms || 5;
            const minLevel = difficulty[0] * 5;
            const levelOk = this.player.level >= minLevel;
            
            const status = levelOk ? Colors.wrap('Available', Colors.GREEN) : Colors.wrap(`Level ${minLevel}+ required`, Colors.RED);
            
            this.print(`${i + 1}. ${Colors.wrap(dungeon.name, Colors.BOLD)} (Difficulty ${difficulty[0]}-${difficulty[1]}, ${rooms} rooms)`);
            this.print(`   ${dungeon.description || ''}`);
            this.print(`   Status: ${status}`);
        }
        
        const choice = await this.ask(`\n${this.lang.get('choose_dungeon_prompt', 'Choose dungeon')} (1-${dungeons.length}) ${this.lang.get('or_cancel_prompt', 'or Enter to cancel')}: `);
        
        if (!choice.isDigit()) return;
        
        const idx = parseInt(choice) - 1;
        if (idx < 0 || idx >= dungeons.length) return;
        
        const dungeon = dungeons[idx];
        const minLevel = (dungeon.difficulty || [1, 3])[0] * 5;
        
        if (this.player.level < minLevel) {
            this.print(Colors.wrap(this.lang.get('level_too_low', `You need to be at least level ${minLevel} to enter this dungeon!`), Colors.RED));
            return;
        }
        
        await this.enterDungeon(dungeon);
    }
    
    /**
     * Enter a dungeon and generate rooms
     */
    async enterDungeon(dungeon) {
        this.clear_screen();
        this.print(`\n${Colors.wrap(this.lang.get('entering_dungeon', 'Entering') + ' ' + dungeon.name + '!', Colors.MAGENTA + Colors.BOLD)}`);
        this.print(dungeon.description || '');
        
        // Set dungeon state
        this.currentDungeon = dungeon;
        this.dungeonProgress = 0;
        this.dungeonState = {
            startTime: new Date().toISOString(),
            totalRooms: dungeon.rooms,
            currentRoom: 0
        };
        
        // Generate dungeon rooms
        this.generateDungeonRooms(dungeon);
        
        // Start with first room
        await this.continueDungeon();
    }
    
    /**
     * Generate dungeon rooms based on room weights
     */
    generateDungeonRooms(dungeon) {
        const roomWeights = dungeon.room_weights || {};
        const totalRooms = dungeon.rooms || 5;
        
        this.dungeonRooms = [];
        
        // Validate room_weights
        let validWeights = {};
        if (roomWeights && Object.keys(roomWeights).length > 0) {
            const totalWeight = Object.values(roomWeights).reduce((a, b) => a + b, 0);
            if (totalWeight > 0) {
                validWeights = roomWeights;
            }
        }
        
        // Default room weights if none provided
        if (Object.keys(validWeights).length === 0) {
            validWeights = {
                'battle': 40,
                'question': 20,
                'chest': 15,
                'empty': 15,
                'trap_chest': 5,
                'multi_choice': 5
            };
        }
        
        const roomTypes = Object.keys(validWeights);
        const weights = Object.values(validWeights);
        
        for (let i = 0; i < totalRooms; i++) {
            // Last room is always boss room
            let roomType;
            if (i === totalRooms - 1) {
                roomType = 'boss';
            } else {
                roomType = roomTypes[this.weightedRandom(weights)];
            }
            
            const difficulty = (dungeon.difficulty || [1, 3])[0] + (i * 0.5);
            
            this.dungeonRooms.push({
                type: roomType,
                roomNumber: i + 1,
                difficulty: difficulty
            });
        }
    }
    
    /**
     * Weighted random selection
     */
    weightedRandom(weights) {
        const totalWeight = weights.reduce((a, b) => a + b, 0);
        let random = Math.random() * totalWeight;
        
        for (let i = 0; i < weights.length; i++) {
            random -= weights[i];
            if (random <= 0) return i;
        }
        
        return weights.length - 1;
    }
    
    /**
     * Continue through the current dungeon
     */
    async continueDungeon() {
        if (!this.currentDungeon || !this.dungeonRooms || this.dungeonRooms.length === 0) {
            this.print(Colors.wrap(this.lang.get('no_active_dungeon', 'No active dungeon!'), Colors.RED));
            return;
        }
        
        // Loop through rooms until dungeon is complete
        while (this.currentDungeon && this.dungeonProgress < this.dungeonRooms.length) {
            const room = this.dungeonRooms[this.dungeonProgress];
            
            this.print(`\n${Colors.wrap('=== Room ' + room.roomNumber + ' ===', Colors.CYAN + Colors.BOLD)}`);
            
            // Handle room based on type
            const roomType = room.type;
            if (roomType === 'question') {
                await this.handleQuestionRoom(room);
            } else if (roomType === 'battle') {
                await this.handleBattleRoom(room);
            } else if (roomType === 'chest') {
                await this.handleChestRoom(room);
            } else if (roomType === 'trap_chest') {
                await this.handleTrapChestRoom(room);
            } else if (roomType === 'multi_choice') {
                await this.handleMultiChoiceRoom(room);
            } else if (roomType === 'empty') {
                await this.handleEmptyRoom(room);
            } else if (roomType === 'boss') {
                await this.handleBossRoom(room);
            }
            
            // Check if player died
            if (!this.player || !this.player.isAlive()) {
                await this.dungeonDeath();
                return;
            }
        }
        
        // Dungeon complete
        if (this.currentDungeon && this.dungeonProgress >= this.dungeonRooms.length) {
            await this.completeDungeon();
        }
    }
    
    /**
     * Handle a question/riddle room
     */
    async handleQuestionRoom(room) {
        if (!this.player) return;
        
        this.print(Colors.wrap(this.lang.get('mystical_pedestal', 'A mystical pedestal stands before you with a glowing question...'), Colors.YELLOW));
        
        const challengeTemplates = this.dungeonsData.challenge_templates || {};
        const questionTemplate = challengeTemplates.question || {};
        
        if (!questionTemplate.types || questionTemplate.types.length === 0) {
            this.print(Colors.wrap(this.lang.get('no_questions', 'No questions available!'), Colors.GRAY));
            await this.advanceRoom();
            return;
        }
        
        const questionData = questionTemplate.types[Math.floor(Math.random() * questionTemplate.types.length)];
        
        this.print(`\n${Colors.wrap('Riddle:', Colors.CYAN)}`);
        this.print(questionData.question);
        
        const choice = await this.ask(`${this.lang.get('your_answer_prompt', 'Your answer (or type leave to skip): ')}`);
        
        if (choice.toLowerCase() === 'leave') {
            await this.advanceRoom();
            return;
        }
        
        const correctAnswer = (questionData.answer || '').toLowerCase();
        const isCorrect = choice.trim().toLowerCase() === correctAnswer;
        
        if (isCorrect) {
            this.print(Colors.wrap(this.lang.get('correct_answer', 'Correct!'), Colors.GREEN));
            
            const reward = questionData.success_reward || {};
            if (reward.gold) {
                this.player.gold += reward.gold;
                this.print(`You gained ${reward.gold} gold!`);
            }
            if (reward.experience) {
                this.player.gainExperience(reward.experience);
                this.print(`You gained ${reward.experience} experience!`);
            }
        } else {
            this.print(Colors.wrap(this.lang.get('incorrect_answer', 'Incorrect!'), Colors.RED));
            const damage = questionData.failure_damage || 15;
            const actualDamage = this.player.takeDamage(damage);
            this.print(`You took ${actualDamage} damage from the failed riddle!`);
        }
        
        await this.advanceRoom();
    }
    
    /**
     * Handle a battle room
     */
    async handleBattleRoom(room) {
        if (!this.player) {
            await this.advanceRoom();
            return;
        }
        
        this.print(Colors.wrap(this.lang.get('combat_approaching', 'Combat approaches...'), Colors.RED));
        
        const difficulty = room.difficulty || 1;
        const enemyCount = Math.max(1, Math.floor(difficulty));
        
        const areaEnemies = (this.areasData[this.currentArea] || {}).possible_enemies || [];
        
        if (areaEnemies.length === 0) {
            // Fallback enemies
            const fallbackEnemies = ['goblin', 'orc', 'skeleton'];
            areaEnemies.push(...fallbackEnemies.filter(e => this.enemiesData[e]));
        }
        
        if (areaEnemies.length === 0) {
            this.print(Colors.wrap(this.lang.get('no_enemies_found', 'No enemies found! You proceed safely.'), Colors.YELLOW));
            await this.advanceRoom();
            return;
        }
        
        const enemies = [];
        for (let i = 0; i < enemyCount; i++) {
            const enemyName = areaEnemies[Math.floor(Math.random() * areaEnemies.length)];
            const enemyData = this.enemiesData[enemyName];
            
            if (enemyData) {
                // Scale enemy stats by difficulty
                const scaledData = { ...enemyData };
                scaledData.hp = Math.floor(scaledData.hp * (0.8 + difficulty * 0.2));
                scaledData.attack = Math.floor(scaledData.attack * (0.8 + difficulty * 0.2));
                scaledData.defense = Math.floor(scaledData.defense * (0.8 + difficulty * 0.2));
                
                enemies.push(new Enemy(scaledData));
            }
        }
        
        if (enemies.length === 0) {
            this.print(Colors.wrap(this.lang.get('no_enemies_found', 'No enemies found!'), Colors.YELLOW));
            await this.advanceRoom();
            return;
        }
        
        this.print(this.lang.get('encounter_enemies_msg', `Encountered ${enemies.length} enemy(enemies)!`));
        
        // Battle each enemy
        for (const enemy of enemies) {
            if (!this.player || !this.player.isAlive()) break;
            
            this.print(`\nA wild ${enemy.name} appears!`);
            await this.battle(enemy);
        }
        
        if (this.player && this.player.isAlive()) {
            this.print(Colors.wrap(this.lang.get('battle_room_cleared', 'You cleared the battle room!'), Colors.GREEN));
            await this.advanceRoom();
        }
    }
    
    /**
     * Handle a treasure chest room
     */
    async handleChestRoom(room) {
        if (!this.player) {
            await this.advanceRoom();
            return;
        }
        
        this.print(Colors.wrap(this.lang.get('chest_found', 'You found a treasure chest in the center of the room!'), Colors.YELLOW));
        
        const difficulty = room.difficulty || 1;
        
        let chestType = 'small';
        if (difficulty >= 8) chestType = 'legendary';
        else if (difficulty >= 5) chestType = 'large';
        else if (difficulty >= 3) chestType = 'medium';
        
        const chestTemplates = this.dungeonsData.chest_templates || {};
        const chestData = chestTemplates[chestType] || chestTemplates.small || {};
        
        const goldMin = chestData.gold_range ? chestData.gold_range[0] : 50;
        const goldMax = chestData.gold_range ? chestData.gold_range[1] : 150;
        const goldReward = Math.floor(Math.random() * (goldMax - goldMin + 1)) + goldMin;
        
        const expReward = chestData.experience || 100;
        
        // Give rewards
        this.player.gold += goldReward;
        this.player.gainExperience(expReward);
        
        this.print(`${Colors.wrap('You found ' + goldReward + ' gold!', Colors.GOLD)}`);
        this.print(`${Colors.wrap('You gained ' + expReward + ' experience!', Colors.MAGENTA)}`);
        
        // Generate items
        const itemRarities = chestData.item_rarity || ['common'];
        const itemCountRange = chestData.item_count_range || [1, 2];
        const itemCount = Math.floor(Math.random() * (itemCountRange[1] - itemCountRange[0] + 1)) + itemCountRange[0];
        
        for (let i = 0; i < itemCount; i++) {
            const rarity = itemRarities[Math.floor(Math.random() * itemRarities.length)];
            const possibleItems = Object.values(this.itemsData).filter(item => item.rarity === rarity);
            
            if (possibleItems.length > 0) {
                const item = possibleItems[Math.floor(Math.random() * possibleItems.length)];
                this.player.inventory.push(item.name || item.id);
                this.print(`${Colors.wrap('Found:', Colors.GREEN)} ${this.formatItemName(item.name || item.id, rarity)}`);
            }
        }
        
        await this.advanceRoom();
    }
    
    /**
     * Handle a trapped chest room
     */
    async handleTrapChestRoom(room) {
        if (!this.player) {
            await this.advanceRoom();
            return;
        }
        
        this.print(Colors.wrap(this.lang.get('suspicious_chest', 'You found a suspicious-looking chest...'), Colors.YELLOW));
        
        const choice = await this.ask(`${this.lang.get('open_chest_prompt', 'Open the chest (O) or leave it (L)?')}: `);
        
        if (choice.toUpperCase() === 'L') {
            this.print(Colors.wrap(this.lang.get('leave_chest', 'You leave the chest alone.'), Colors.GRAY));
            await this.advanceRoom();
            return;
        }
        
        // 70% chance of trap
        if (Math.random() < 0.7) {
            this.print(Colors.wrap(this.lang.get('trap_triggered', 'A trap was triggered!'), Colors.RED));
            
            // Simple damage based on difficulty
            const damage = Math.floor(room.difficulty || 1) * 10;
            const actualDamage = this.player.takeDamage(damage);
            this.print(`You took ${actualDamage} damage from the trap!`);
            
            if (!this.player.isAlive()) {
                await this.dungeonDeath();
                return;
            }
        } else {
            // Found treasure
            const goldReward = Math.floor(Math.random() * 50) + 25;
            this.player.gold += goldReward;
            this.print(`${Colors.wrap('Lucky! You found ' + goldReward + ' gold!', Colors.GREEN)}`);
        }
        
        await this.advanceRoom();
    }
    
    /**
     * Handle a multiple choice decision room
     */
    async handleMultiChoiceRoom(room) {
        if (!this.player) {
            await this.advanceRoom();
            return;
        }
        
        this.print(Colors.wrap(this.lang.get('crossroads', 'You come to a crossroads with multiple paths...'), Colors.YELLOW));
        
        const challengeTemplates = this.dungeonsData.challenge_templates || {};
        const selectionTemplate = challengeTemplates.selection || {};
        
        if (!selectionTemplate.types || selectionTemplate.types.length === 0) {
            this.print(Colors.wrap(this.lang.get('safe_path', 'The path seems safe.'), Colors.GRAY));
            await this.advanceRoom();
            return;
        }
        
        const challenge = selectionTemplate.types[Math.floor(Math.random() * selectionTemplate.types.length)];
        
        this.print(`\n${challenge.question}`);
        
        const options = challenge.options || [];
        for (let i = 0; i < options.length; i++) {
            this.print(`${i + 1}. ${options[i].text}`);
        }
        
        const choice = await this.ask(`${this.lang.get('your_choice_prompt', 'Your choice')}: `);
        
        if (!choice.isDigit()) {
            await this.advanceRoom();
            return;
        }
        
        const idx = parseInt(choice) - 1;
        if (idx < 0 || idx >= options.length) {
            await this.advanceRoom();
            return;
        }
        
        const outcome = options[idx];
        this.print(`\n${outcome.reason || ''}`);
        
        if (outcome.correct) {
            const reward = challenge.success_reward || {};
            if (reward.gold) {
                this.player.gold += reward.gold;
                this.print(`You gained ${reward.gold} gold!`);
            }
            if (reward.experience) {
                this.player.gainExperience(reward.experience);
                this.print(`You gained ${reward.experience} experience!`);
            }
        } else {
            const damage = challenge.failure_damage || 10;
            const actualDamage = this.player.takeDamage(damage);
            this.print(`You took ${actualDamage} damage!`);
            
            if (!this.player.isAlive()) {
                await this.dungeonDeath();
                return;
            }
        }
        
        await this.advanceRoom();
    }
    
    /**
     * Handle an empty room
     */
    async handleEmptyRoom(room) {
        this.print(Colors.wrap(this.lang.get('empty_room', 'The room is empty...'), Colors.GRAY));
        
        // 30% chance for hidden treasure
        if (Math.random() < 0.3) {
            if (Math.random() < 0.5) {
                const goldFound = Math.floor(Math.random() * 40) + 10;
                this.player.gold += goldFound;
                this.print(`${Colors.wrap('You found ' + goldFound + ' gold hidden in the room!', Colors.GOLD)}`);
            } else {
                await this.randomEncounter();
            }
        } else {
            this.print(this.lang.get('nothing_interesting', 'Nothing of interest here.'));
        }
        
        await this.advanceRoom();
    }
    
    /**
     * Handle the boss room
     */
    async handleBossRoom(room) {
        const dungeon = this.currentDungeon;
        if (!dungeon) {
            await this.completeDungeon();
            return;
        }
        
        const bossId = dungeon.boss_id;
        
        if (bossId && this.bossesData[bossId]) {
            const bossData = this.bossesData[bossId];
            const boss = new Boss(bossData, this.dialoguesData);
            
            this.print(`\n${Colors.wrap(this.lang.get('boss_appears', 'A powerful boss appears!'), Colors.RED + Colors.BOLD)}`);
            this.print(`${Colors.wrap(boss.name, Colors.BOLD)} - ${boss.description || ''}`);
            
            await this.battle(boss);
            
            if (this.player && this.player.isAlive()) {
                this.print(Colors.wrap(this.lang.get('victory', 'Victory!'), Colors.GREEN + Colors.BOLD));
                this.print(`${Colors.wrap('You defeated ' + boss.name + '!', Colors.YELLOW)}`);
                
                // Boss rewards
                const expReward = (boss.experience_reward || 100) * 2;
                const goldReward = (boss.gold_reward || 50) * 2;
                
                this.player.gainExperience(expReward);
                this.player.gold += goldReward;
                
                this.print(`${Colors.wrap('Gained ' + expReward + ' experience!', Colors.MAGENTA)}`);
                this.print(`${Colors.wrap('Gained ' + goldReward + ' gold!', Colors.GOLD)}`);
            }
        } else {
            // No boss data - use completion rewards
            this.print(Colors.wrap(this.lang.get('powerful_enemy', 'A powerful guardian appears!'), Colors.RED));
            
            const completionReward = dungeon.completion_reward || {};
            const expReward = Math.floor((completionReward.experience || 500) / 2);
            const goldReward = Math.floor((completionReward.gold || 300) / 2);
            
            this.player.gainExperience(expReward);
            this.player.gold += goldReward;
            
            this.print(`${Colors.wrap('Gained ' + expReward + ' experience!', Colors.MAGENTA)}`);
            this.print(`${Colors.wrap('Gained ' + goldReward + ' gold!', Colors.GOLD)}`);
        }
        
        await this.completeDungeon();
    }
    
    /**
     * Advance to the next room
     */
    async advanceRoom() {
        this.dungeonProgress++;
        
        if (this.dungeonProgress >= this.dungeonRooms.length) {
            await this.completeDungeon();
        } else {
            this.print(this.lang.get('moving_next_room', '\nMoving to the next room...'));
            this.dungeonState.currentRoom = this.dungeonProgress;
        }
    }
    
    /**
     * Complete the current dungeon
     */
    async completeDungeon() {
        if (!this.currentDungeon) return;
        
        const dungeon = this.currentDungeon;
        
        this.print(`\n${Colors.wrap(this.lang.get('dungeon_complete', 'DUNGEON COMPLETE!'), Colors.GREEN + Colors.BOLD)}`);
        this.print(Colors.wrap(this.lang.get('cleared_dungeon', 'You cleared') + ' ' + dungeon.name + '!', Colors.YELLOW));
        
        // Give completion rewards
        const completionReward = dungeon.completion_reward || {};
        
        if (completionReward.gold) {
            this.player.gold += completionReward.gold;
            this.print(`${Colors.wrap('+' + completionReward.gold + ' gold', Colors.GOLD)}`);
        }
        
        if (completionReward.experience) {
            this.player.gainExperience(completionReward.experience);
            this.print(`${Colors.wrap('+' + completionReward.experience + ' experience', Colors.MAGENTA)}`);
        }
        
        if (completionReward.items && completionReward.items.length > 0) {
            this.print(Colors.wrap('Special items:', Colors.YELLOW));
            for (const itemName of completionReward.items) {
                this.player.inventory.push(itemName);
                const itemData = this.itemsData[itemName] || {};
                const rarity = itemData.rarity || "common";
                this.print(`  - ${this.formatItemName(itemName, rarity)}`);
            }
        }
        
        // Update challenge progress
        this.updateChallengeProgress('dungeon_complete', 1);
        
        // Clear dungeon state
        this.currentDungeon = null;
        this.dungeonProgress = 0;
        this.dungeonRooms = [];
        this.dungeonState = {};
    }
    
    /**
     * Exit the current dungeon
     */
    async exitDungeon() {
        if (!this.player) return;
        
        this.print(`\n${Colors.wrap(this.lang.get('exiting_dungeon', 'Exiting dungeon...'), Colors.YELLOW)}`);
        
        // Penalty for early exit
        if (this.dungeonProgress > 0) {
            const penaltyGold = Math.min(Math.floor(this.player.gold / 10), 100);
            if (penaltyGold > 0) {
                this.player.gold -= penaltyGold;
                this.print(`${Colors.wrap('Exit penalty: Lost ' + penaltyGold + ' gold', Colors.RED)}`);
            }
        }
        
        // Clear dungeon state
        this.currentDungeon = null;
        this.dungeonProgress = 0;
        this.dungeonRooms = [];
        this.dungeonState = {};
    }
    
    /**
     * Handle death in dungeon
     */
    async dungeonDeath() {
        if (!this.player) return;
        
        this.print(`\n${Colors.wrap(this.lang.get('dungeon_death', 'You have fallen in the dungeon!'), Colors.RED + Colors.BOLD)}`);
        
        // Death penalty
        this.player.hp = Math.floor(this.player.maxHp / 2);
        this.player.mp = Math.floor(this.player.maxMp / 2);
        
        // Lose some gold
        const goldLoss = Math.min(Math.floor(this.player.gold / 5), 200);
        this.player.gold -= goldLoss;
        
        this.print(`${Colors.wrap('Lost ' + goldLoss + ' gold in the dungeon!', Colors.YELLOW)}`);
        
        // Return to starting village
        this.currentArea = 'starting_village';
        this.print(this.lang.get('respawn_village', 'You respawn at the starting village...'));
        
        // Clear dungeon state
        this.currentDungeon = null;
        this.dungeonProgress = 0;
        this.dungeonRooms = [];
        this.dungeonState = {};
    }
}

// Export for use in browser
export default Game;