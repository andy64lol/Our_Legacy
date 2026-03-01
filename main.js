/**
 * Our Legacy - Browser-Based Fantasy RPG Game
 * Ported from main.py for browser use
 * Andy64lol
 */
import { Character } from './utilities_js/character.js';
import { BattleSystem } from './utilities_js/battle.js';
import { SpellCastingSystem } from './spellcasting.js';
import { SaveLoadSystem } from './utilities_js/save_load.js';
import { LanguageManager } from './utilities_js/language.js';
import { SettingsManager, Colors, ModManager } from './utilities_js/settings.js';
import { Enemy, Boss } from './utilities_js/entities.js';
import { Dice } from './utilities_js/dice.js';
import MarketAPI from './utilities_js/market.js';

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
}
