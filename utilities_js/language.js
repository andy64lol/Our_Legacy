/**
 * LanguageManager class for managing language loading and translation
 * Ported from utilities/language.py
 */
class LanguageManager {
    /**
     * @param {Function} getSettingFunc - Function to get settings
     * @param {Function} setSettingFunc - Function to set settings
     */
    constructor(getSettingFunc, setSettingFunc) {
        this.config = {};
        this.translations = {};
        this.getSetting = getSettingFunc;
        this.setSetting = setSettingFunc;
        this.currentLanguage = getSettingFunc ? getSettingFunc("language", "en") : "en";
        this.init();
    }

    /**
     * Initialize language manager
     */
    async init() {
        await this.load_config();
        await this.load_translations();
    }

    /**
     * Load language configuration
     */
    async load_config() {
        try {
            const response = await fetch('data/languages/config.json');
            this.config = await response.json();
            if (this.getSetting) {
                this.currentLanguage = this.getSetting("language", this.config.default_language || "en");
            }
        } catch (e) {
            this.config = {
                "default_language": "en",
                "available_languages": {
                    "en": "English",
                    "es": "Español",
                    "zh_simp": "简体中文"
                },
                "fallback_language": "en",
                "overwrite_save_files": true
            };
        }
    }

    async changeLanguage(langCode) {
        return await this.change_language(langCode);
    }

    /**
     * Change current language and save to settings
     * @param {string} langCode - Language code to change to
     * @returns {boolean} True if language was changed successfully
     */
    async change_language(langCode) {
        if (this.config.available_languages && this.config.available_languages[langCode]) {
            this.currentLanguage = langCode;
            if (this.setSetting) {
                this.setSetting("language", langCode);
            }
            await this.load_translations();
            return true;
        }
        return false;
    }

    /**
     * Load translation strings for current language
     */
    async load_translations() {
        try {
            const response = await fetch(`data/languages/${this.currentLanguage}.json`);
            this.translations = await response.json();
        } catch (e) {
            if (this.currentLanguage !== 'en') {
                try {
                    const response = await fetch('data/languages/en.json');
                    this.translations = await response.json();
                } catch (e2) {
                    this.translations = {};
                }
            }
        }
    }

    /**
     * Get translated string with robust formatting and escape handling
     * @param {string} key - Translation key
     * @param {string} defaultValue - Default value if key not found
     * @param {Object} params - Parameters for string formatting
     * @returns {string} Translated and formatted string
     */
    get(key, defaultValue = null, params = {}) {
        let text = this.translations[key] || (defaultValue !== null ? defaultValue : key);

        // Handle literal escape sequences found in JSON files
        text = text.replace(/\\n/g, "\n").replace(/\\033/g, "\u001b").replace(/\\x1b/g, "\u001b").replace(/\\r/g, "\r");

        if (params && Object.keys(params).length > 0) {
            for (const [k, v] of Object.entries(params)) {
                text = text.replace(new RegExp(`\\{${k}\\}`, 'g'), String(v));
            }
        }

        return text;
    }

    /**
     * Check if save files should be overwritten
     * @returns {boolean} True if save files should be overwritten
     */
    should_overwrite_saves() {
        return this.config.overwrite_save_files !== false;
    }
}

export { LanguageManager };
export default LanguageManager;
