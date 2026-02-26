class LanguageManager {
    constructor(getSettingFunc, setSettingFunc) {
        this.config = {};
        this.translations = {};
        this.getSetting = getSettingFunc;
        this.setSetting = setSettingFunc;
        this.currentLanguage = getSettingFunc ? getSettingFunc("language", "en") : "en";
        this.loadConfig();
        this.loadTranslations();
    }

    async loadConfig() {
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
        if (this.config.available_languages && this.config.available_languages[langCode]) {
            this.currentLanguage = langCode;
            if (this.setSetting) {
                this.setSetting("language", langCode);
            }
            await this.loadTranslations();
            return true;
        }
        return false;
    }

    async loadTranslations() {
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

    get(key, defaultValue = null, params = {}) {
        let text = this.translations[key] || (defaultValue !== null ? defaultValue : key);

        // Handle escapes if necessary (JS strings already handle most)
        // text = text.replace(/\\n/g, "\n"); 

        if (params && Object.keys(params).length > 0) {
            for (const [k, v] of Object.entries(params)) {
                text = text.replace(new RegExp(`\\{${k}\\}`, 'g'), String(v));
            }
        }

        return text;
    }

    shouldOverwriteSaves() {
        return this.config.overwrite_save_files !== false;
    }
}

export default LanguageManager;
