// settings.js
// Simple Settings Manager for browser
// Andy64lol

const DEFAULT_SETTINGS = {
  mods_enabled: true,
  disabled_mods: [],
  overwrite_save_by_uuid: false,
  language: "en"
};

/**
 * CSS color styles for browser console output
 * Ported from utilities/settings.py
 * Uses ANSI escape codes for compatibility with game.html's processColorCodes()
 */
export class Colors {
  // ANSI escape code versions (used by game.html for HTML rendering)
  static RED = '\x1b[31m';
  static GREEN = '\x1b[32m';
  static YELLOW = '\x1b[33m';
  static BLUE = '\x1b[34m';
  static MAGENTA = '\x1b[35m';
  static CYAN = '\x1b[36m';
  static WHITE = '\x1b[37m';
  static BOLD = '\x1b[1m';
  static UNDERLINE = '\x1b[4m';
  static END = '\x1b[0m';
  static GOLD = '\x1b[33m';  // Yellow/gold
  static ORANGE = '\x1b[33m'; // Yellow/orange
  static PURPLE = '\x1b[35m'; // Magenta
  static DARK_GRAY = '\x1b[90m';
  static LIGHT_GRAY = '\x1b[37m';
  static GRAY = '\x1b[90m';

  // CSS versions (for direct console.log styling if needed)
  static CSS_RED = 'color: #ff6b6b';
  static CSS_GREEN = 'color: #51cf66';
  static CSS_YELLOW = 'color: #fcc419';
  static CSS_BLUE = 'color: #339af0';
  static CSS_MAGENTA = 'color: #cc5de8';
  static CSS_CYAN = 'color: #22b8cf';
  static CSS_WHITE = 'color: #e0e0e0';
  static CSS_GOLD = 'color: #ffd43b';
  static CSS_DARK_GRAY = 'color: #495057';
  static CSS_ORANGE = 'color: #fd7e14';

  /**
   * Wrap text with color style for browser console
   * @param {string} text - Text to wrap
   * @param {string} color_code - ANSI color code
   * @returns {string} Formatted string with color
   */
  static _color(color_code) {
    return color_code;
  }

  /**
   * Wrap text with color style
   * @param {string} text - Text to wrap
   * @param {string} color_code - ANSI color code
   * @returns {string} Formatted string
   */
  static wrap(text, color_code) {
    if (!color_code || color_code === this.END) return text;
    return `${color_code}${text}${this.END}`;
  }
}

export class SettingsManager {
  constructor(storageKey = "game_settings") {
    this.storageKey = storageKey;
    this.settings = { ...DEFAULT_SETTINGS };
    this.loadSettings();
  }

  loadSettings() {
    try {
      if (typeof localStorage !== 'undefined') {
        const saved = localStorage.getItem(this.storageKey);
        if (saved) {
          const loadedSettings = JSON.parse(saved);
          this.settings = { ...this.settings, ...loadedSettings };
        }
      }
    } catch (e) {
      if (typeof console !== 'undefined' && console.error) {
        console.error("Could not load settings:", e);
      }
      this.settings = { ...DEFAULT_SETTINGS };
    }
  }

  saveSettings() {
    try {
      if (typeof localStorage !== 'undefined') {
        localStorage.setItem(this.storageKey, JSON.stringify(this.settings));
      }
      return true;
    } catch (e) {
      if (typeof console !== 'undefined' && console.error) {
        console.error("Error saving settings:", e);
      }
      return false;
    }
  }

  get(key, defaultValue = null) {
    return this.settings[key] ?? defaultValue;
  }

  set(key, value) {
    this.settings[key] = value;
    return this.saveSettings();
  }

  resetToDefaults() {
    this.settings = { ...DEFAULT_SETTINGS };
    return this.saveSettings();
  }

  getAllSettings() {
    return { ...this.settings };
  }

  updateMultiple(settingsObj) {
    this.settings = { ...this.settings, ...settingsObj };
    return this.saveSettings();
  }
}

export class ModManager {
  constructor(lang = null, storageKey = "game_settings") {
    this.storageKey = storageKey;
    this.settings = { ...DEFAULT_SETTINGS };
    this.lang = lang || { get: (key, defaultValue = null) => defaultValue || key };
    this.mods = {}; // Discovered mods cache
    this.modsDir = "mods";
    this.settingsFile = "data/mod_settings.json";
    this.loadSettings();
  }

  loadSettings() {
    try {
      if (typeof localStorage !== 'undefined') {
        const saved = localStorage.getItem(this.storageKey);
        if (saved) {
          const loadedSettings = JSON.parse(saved);
          this.settings = { ...this.settings, ...loadedSettings };
        }
      }
    } catch (e) {
      this.settings = { ...DEFAULT_SETTINGS };
    }
  }

  saveSettings() {
    try {
      localStorage.setItem(this.storageKey, JSON.stringify(this.settings));
    } catch (e) {
      console.error("Error saving mod settings:", e);
    }
  }

  /**
   * Discover all mods in the mods directory
   * In browser, this fetches from a mods manifest or API endpoint
   * @returns {Promise<Object>} Discovered mods
   */
  async discoverMods() {
    this.mods = {};
    
    // In browser environment, we try to fetch a mods manifest
    // This could be a JSON file listing available mods
    try {
      const response = await fetch(`${this.modsDir}/mods_manifest.json`);
      if (response.ok) {
        const manifest = await response.json();
        for (const [folderName, modData] of Object.entries(manifest)) {
          this.mods[folderName] = {
            ...modData,
            folder_name: folderName,
            mod_path: `${this.modsDir}/${folderName}`
          };
        }
      }
    } catch (e) {
      // If no manifest, try to discover via API or use empty list
      this.game?.print("No mods manifest found, mods discovery may be limited in browser");
    }
    
    return this.mods;
  }

  /**
   * Get list of enabled mod folder names
   * @returns {string[]} Array of enabled mod folder names
   */
  getEnabledMods() {
    if (!this.settings.mods_enabled) {
      return [];
    }

    const disabled = new Set(this.settings.disabled_mods || []);
    return Object.keys(this.mods).filter(name => !disabled.has(name));
  }

  /**
   * Load and merge data from all enabled mods for a specific data type
   * @param {string} dataType - Data type to load (e.g., "items.json", "pets.json")
   * @returns {Promise<Object>} Merged data from all enabled mods
   */
  async loadModData(dataType) {
    const mergedData = {};

    for (const modName of this.getEnabledMods()) {
      const mod = this.mods[modName];
      if (!mod) continue;

      const modPath = mod.mod_path || `${this.modsDir}/${modName}`;
      const filePath = `${modPath}/${dataType}`;

      try {
        const response = await fetch(filePath);
        if (response.ok) {
          const modData = await response.json();
          for (const [key, value] of Object.entries(modData)) {
            // Prefix with mod name if key already exists to avoid conflicts
            const newKey = key in mergedData ? `${modName}_${key}` : key;
            mergedData[newKey] = value;
          }
        }
      } catch (e) {
        this.game.print(`Failed to load ${dataType} from mod ${modName}:`, e);
      }
    }

    // Special handling for pets.json - merge with base pets
    if (dataType === "pets.json") {
      try {
        const baseResponse = await fetch('data/pets.json');
        if (baseResponse.ok) {
          const basePets = await baseResponse.json();
          return { ...basePets, ...mergedData };
        }
      } catch (e) {
        // Ignore error, return merged data only
      }
    }

    return mergedData;
  }

  /**
   * Get list of all mods with their metadata and status
   * @returns {Object[]} Array of mod metadata objects
   */
  getModList() {
    const modsList = [];
    const enabled = this.getEnabledMods();

    for (const [name, mod] of Object.entries(this.mods)) {
      modsList.push({
        folder_name: name,
        name: mod.name || name,
        description: mod.description || '',
        author: mod.author || 'Unknown',
        version: mod.version || '1.0',
        enabled: enabled.includes(name) && this.settings.mods_enabled,
        mod_path: mod.mod_path || `${this.modsDir}/${name}`
      });
    }

    return modsList;
  }

  /**
   * Toggle a mod's enabled state
   * @param {string} folderName - Folder name of the mod to toggle
   */
  toggleMod(folderName) {
    const disabled = new Set(this.settings.disabled_mods || []);
    
    if (disabled.has(folderName)) {
      disabled.delete(folderName);
      this.game?.print(this.lang.get("mod_enabled_msg", "Mod enabled: {folder_name}").replace("{folder_name}", folderName));
    } else {
      disabled.add(folderName);
      this.game?.print(this.lang.get("mod_disabled_msg", "Mod disabled: {folder_name}").replace("{folder_name}", folderName));
    }
    
    this.settings.disabled_mods = Array.from(disabled);
    this.saveSettings();
  }

  /**
   * Toggle the entire mods system on/off
   * @returns {boolean} New mods enabled state
   */
  toggleModsSystem() {
    this.settings.mods_enabled = !this.settings.mods_enabled;
    const status = this.settings.mods_enabled ? "enabled" : "disabled";
    this.game?.print(this.lang.get("mod_system_status_msg", "Mod system {status}!").replace("{status}", status));
    this.saveSettings();
    return this.settings.mods_enabled;
  }
}

export const settingsManager = new SettingsManager();