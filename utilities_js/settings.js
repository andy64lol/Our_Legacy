// settings.js
// Simple Settings Manager for browser
// Andy64lol

const DEFAULT_SETTINGS = {
  mods_enabled: true,
  disabled_mods: [],
  overwrite_save_by_uuid: false,
  language: "en"
};

export class Colors {
  static RED = 'color: #ff0000';
  static GREEN = 'color: #00ff00';
  static YELLOW = 'color: #ffff00';
  static BLUE = 'color: #0000ff';
  static MAGENTA = 'color: #ff00ff';
  static CYAN = 'color: #00ffff';
  static WHITE = 'color: #ffffff';
  static BOLD = 'font-weight: bold';
  static END = '';

  static wrap(text, color_style) {
    // For browser console, we usually use %c
    return [`%c${text}`, color_style];
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
      const saved = localStorage.getItem(this.storageKey);
      if (saved) {
        const loadedSettings = JSON.parse(saved);
        this.settings = { ...this.settings, ...loadedSettings };
      }
    } catch (e) {
      console.warn("Could not load settings:", e);
      this.settings = { ...DEFAULT_SETTINGS };
    }
  }

  saveSettings() {
    try {
      localStorage.setItem(this.storageKey, JSON.stringify(this.settings));
      return true;
    } catch (e) {
      console.error("Error saving settings:", e);
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
    this.lang = lang || { get: (key) => key };
    this.loadSettings();
  }

  loadSettings() {
    try {
      const saved = localStorage.getItem(this.storageKey);
      if (saved) {
        const loadedSettings = JSON.parse(saved);
        this.settings = { ...this.settings, ...loadedSettings };
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

  toggleMod(folderName) {
    const disabled = new Set(this.settings.disabled_mods || []);
    if (disabled.has(folderName)) {
      disabled.delete(folderName);
      console.log(this.lang.get("mod_enabled_msg") || `Mod enabled: ${folderName}`);
    } else {
      disabled.add(folderName);
      console.log(this.lang.get("mod_disabled_msg") || `Mod disabled: ${folderName}`);
    }
    this.settings.disabled_mods = Array.from(disabled);
    this.saveSettings();
  }

  toggleModsSystem() {
    this.settings.mods_enabled = !this.settings.mods_enabled;
    const status = this.settings.mods_enabled ? "enabled" : "disabled";
    console.log(this.lang.get("mod_system_status_msg") || `Mod system ${status}!`);
    this.saveSettings();
    return this.settings.mods_enabled;
  }
}

export const settingsManager = new SettingsManager();
