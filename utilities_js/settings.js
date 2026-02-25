// settings.js
// Simple Settings Manager for browser
// Andy64lol

const DEFAULT_SETTINGS = {
  overwrite_save_by_uuid: false,
  language: "en",
  someFlag: true
};

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

// Optional singleton instance
export const settingsManager = new SettingsManager();