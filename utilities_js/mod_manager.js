/**
 * Mod Manager for Our Legacy (Browser Version)
 * Centralized mod handler
 * Ported from utilities/mod_manager.py
 */

import { Colors } from './settings.js';

// Default settings - must be defined before use
const DEFAULT_SETTINGS = {
  mods_enabled: true,
  disabled_mods: []
};

/**
 * Mock language class for browser
 */
class MockLangModManager {
  get(key, defaultValue = null, params = {}) {
    return key;
  }
}

/**
 * Mod Manager class
 */
export class ModManager {
  /**
   * @param {Object} lang - Language manager
   * @param {Object} game - Optional game instance for output
   */
  constructor(lang = null, game = null) {
    this.modsDir = "mods";
    this.mods = {};
    this.enabledMods = [];
    this.settingsFile = "data/mod_settings.json";
    this.settings = { ...DEFAULT_SETTINGS };
    this.game = game;
    
    if (lang === null) {
      this.lang = new MockLangModManager();
    } else {
      this.lang = lang;
    }
    
    this.loadSettings();
    this.discoverMods();
  }

  /**
   * Output a message to game UI or console
   * @param {string} message - Message to output
   */
  print(message) {
    if (this.game && typeof this.game.print === 'function') {
      this.game.print(message);
    }
  }

  /**
   * Load mod settings from localStorage (browser)
   */
  loadSettings() {
    try {
      const savedSettings = localStorage.getItem('mod_settings');
      if (savedSettings) {
        const loadedSettings = JSON.parse(savedSettings);
        this.settings = { ...this.settings, ...loadedSettings };
      }
    } catch (e) {
      this.settings = { ...DEFAULT_SETTINGS };
    }
  }

  /**
   * Save mod settings to localStorage
   */
  saveSettings() {
    try {
      localStorage.setItem('mod_settings', JSON.stringify(this.settings));
    } catch (e) {
      this.print(`Error saving mod settings: ${e}`);
    }
  }

  /**
   * Discover all mods in the mods directory
   */
  discoverMods() {
    this.mods = {};
    // In browser, mods would need to be loaded differently
    // This is a placeholder for browser functionality
    this.print("Mod discovery not fully implemented in browser version");
  }

  /**
   * Get list of enabled mod folder names
   * @returns {Array} List of enabled mods
   */
  getEnabledMods() {
    if (!this.settings.get("mods_enabled", true)) {
      return [];
    }

    const disabled = new Set(this.settings.get("disabled_mods", []));
    return Object.keys(this.mods).filter(name => !disabled.has(name));
  }

  /**
   * Load and merge data from all enabled mods
   * @param {string} dataType - Data type to load
   * @returns {Object} Merged data
   */
  loadModData(dataType) {
    // Browser version would load mod data differently
    // This is a placeholder
    return {};
  }

  /**
   * Get list of all mods
   * @returns {Array} List of mods with metadata
   */
  getModList() {
    const modsList = [];
    const enabled = this.getEnabledMods();

    for (const [name, mod] of Object.entries(this.mods)) {
      modsList.push({
        folder_name: name,
        name: mod.get('name', name),
        description: mod.get('description', ''),
        author: mod.get('author', 'Unknown'),
        version: mod.get('version', '1.0'),
        enabled: enabled.includes(name) && this.settings.get("mods_enabled", true),
        mod_path: mod.get('mod_path', '')
      });
    }

    return modsList;
  }

  /**
   * Toggle a mod's enabled state
   * @param {string} folderName - Mod folder name
   */
  toggleMod(folderName) {
    const disabled = new Set(this.settings.get("disabled_mods", []));

    if (disabled.has(folderName)) {
      disabled.delete(folderName);
      this.print(`Mod enabled: ${folderName}`);
    } else {
      disabled.add(folderName);
      this.print(`Mod disabled: ${folderName}`);
    }

    this.settings["disabled_mods"] = Array.from(disabled);
    this.saveSettings();
  }

  /**
   * Toggle the entire mods system on/off
   * @returns {boolean} New status
   */
  toggleModsSystem() {
    this.settings["mods_enabled"] = !this.settings.get("mods_enabled", true);
    const status = this.settings["mods_enabled"] ? "enabled" : "disabled";
    this.print(`Mod system ${status}!`);
    this.saveSettings();
    return this.settings["mods_enabled"];
  }
}

export { DEFAULT_SETTINGS };

export default ModManager;
