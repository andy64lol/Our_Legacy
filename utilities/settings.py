"""
Settings Management for Our Legacy
Centralized configuration and settings handler
Extracted from main.py and enhanced
"""

import json
import os
from typing import Dict, List, Any, Optional

# Default settings - originally from main.py
DEFAULT_SETTINGS = {
    "mods_enabled": True,
    "disabled_mods": [],
    "overwrite_save_by_uuid": False,
    "language": "en"
}


class SettingsManager:
    """Manages game settings and configuration"""
    
    def __init__(self, settings_file: str = "data/mod_settings.json"):
        self.settings_file = settings_file
        self.settings = DEFAULT_SETTINGS.copy()
        self.load_settings()
    
    def load_settings(self):
        """Load settings from file"""
        try:
            if os.path.exists(self.settings_file):
                with open(self.settings_file, 'r', encoding='utf-8') as f:
                    loaded_settings = json.load(f)
                    # Merge with defaults to ensure all keys exist
                    self.settings.update(loaded_settings)
        except (json.JSONDecodeError, IOError, OSError) as e:
            print(f"Warning: Could not load settings: {e}")
            self.settings = DEFAULT_SETTINGS.copy()
    
    def save_settings(self):
        """Save current settings to file"""
        try:
            os.makedirs(os.path.dirname(self.settings_file), exist_ok=True)
            with open(self.settings_file, 'w', encoding='utf-8') as f:
                json.dump(self.settings, f, indent=2)
            return True
        except (IOError, OSError) as e:
            print(f"Error saving settings: {e}")
            return False
    
    def get(self, key: str, default=None):
        """Get a setting value"""
        return self.settings.get(key, default)
    
    def set(self, key: str, value: Any) -> bool:
        """Set a setting value"""
        self.settings[key] = value
        return self.save_settings()
    
    def reset_to_defaults(self):
        """Reset all settings to defaults"""
        self.settings = DEFAULT_SETTINGS.copy()
        return self.save_settings()
    
    def get_all_settings(self) -> Dict[str, Any]:
        """Get all current settings"""
        return self.settings.copy()
    
    def update_multiple(self, settings_dict: Dict[str, Any]) -> bool:
        """Update multiple settings at once"""
        self.settings.update(settings_dict)
        return self.save_settings()


class Colors:
    """ANSI color codes for terminal output"""
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'
    GOLD = '\033[93m'
    ORANGE = '\033[38;5;208m'
    PURPLE = '\033[95m'
    DARK_GRAY = '\033[90m'
    LIGHT_GRAY = '\033[37m'
    GRAY = '\033[90m'

    @staticmethod
    def _color(code: str) -> str:
        return code

    @classmethod
    def wrap(cls, text: str, color_code: str) -> str:
        return f"{cls._color(color_code)}{text}{cls._color(cls.END)}"


class ModManager:
    """Manages mod loading and data merging - Settings Only"""
    
    def __init__(self, lang=None):
        self.mods_dir = "mods"
        self.mods: Dict[str, Dict[str, Any]] = {}
        self.enabled_mods: List[str] = []
        self.settings_file = "data/mod_settings.json"
        self.settings = DEFAULT_SETTINGS.copy()
        if lang is None:
            class MockLang:
                def get(self, key, default=None, **kwargs):
                    return key
            self.lang = MockLang()
        else:
            self.lang = lang
        self.load_settings()

    def load_settings(self):
        """Load mod settings from file"""
        try:
            if os.path.exists(self.settings_file):
                with open(self.settings_file, 'r') as f:
                    loaded_settings = json.load(f)
                    # Merge with defaults
                    self.settings.update(loaded_settings)
        except (json.JSONDecodeError, IOError):
            self.settings = DEFAULT_SETTINGS.copy()

    def save_settings(self):
        """Save mod settings to file"""
        try:
            os.makedirs(os.path.dirname(self.settings_file), exist_ok=True)
            with open(self.settings_file, 'w') as f:
                json.dump(self.settings, f, indent=2)
        except IOError as e:
            print(f"Error saving mod settings: {e}")

    def get_enabled_mods(self) -> List[str]:
        """Get list of enabled mod folder names"""
        if not self.settings.get("mods_enabled", True):
            return []

        disabled = set(self.settings.get("disabled_mods", []))
        return [name for name in self.mods.keys() if name not in disabled]

    def toggle_mod(self, folder_name: str):
        """Toggle a mod's enabled state"""
        disabled = set(self.settings.get("disabled_mods", []))

        if folder_name in disabled:
            disabled.remove(folder_name)
            print(self.lang.get("mod_enabled_msg", "Mod enabled: {folder_name}").format(folder_name=folder_name))
        else:
            disabled.add(folder_name)
            print(self.lang.get("mod_disabled_msg", "Mod disabled: {folder_name}").format(folder_name=folder_name))

        self.settings["disabled_mods"] = list(disabled)
        self.save_settings()

    def toggle_mods_system(self):
        """Toggle the entire mods system on/off"""
        self.settings["mods_enabled"] = not self.settings.get(
            "mods_enabled", True)
        status = "enabled" if self.settings["mods_enabled"] else "disabled"
        print(self.lang.get("mod_system_status_msg", "Mod system {status}!").format(status=status))
        self.save_settings()
        return self.settings["mods_enabled"]


# Global settings manager instance
_settings_manager = None

def get_settings_manager() -> SettingsManager:
    """Get or create the global settings manager instance"""
    global _settings_manager
    if _settings_manager is None:
        _settings_manager = SettingsManager()
    return _settings_manager

def get_setting(key: str, default=None):
    """Convenience function to get a setting"""
    return get_settings_manager().get(key, default)

def set_setting(key: str, value: Any) -> bool:
    """Convenience function to set a setting"""
    return get_settings_manager().set(key, value)
