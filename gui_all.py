#!/usr/bin/env python3
"""
Our Legacy - GUI All Version
A comprehensive GUI wrapper for the full project using Py2GUI.
This version integrates the launcher and all modules into a single GUI experience.
"""

import builtins
import sys
import re
import os

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import py2gui functions
from py2gui import (display, user_type_in, clear, run as gui_run, set_theme,
                    exit_gui)

# Import the main components
import launcher
from launcher import LauncherExit
import main
import storyland
import storywrite
import chat

# Color code patterns for stripping
COLOR_PATTERN = re.compile(r'\x1b\[[0-9;]*m')
ANSI_PATTERN = re.compile(r'\033\[[0-9;]*m')


def strip_colors(text):
    """Remove all ANSI color codes from text"""
    if text is None:
        return ""
    text = str(text)
    text = COLOR_PATTERN.sub('', text)
    text = ANSI_PATTERN.sub('', text)
    # Also strip any Colors class references
    text = re.sub(r'Colors\.[A-Z_]+', '', text)
    return text


def gui_print(*args, sep=' ', end='\n', **_kwargs):
    """Replacement for print() that outputs to GUI"""
    text = sep.join(str(arg) for arg in args) + end
    text = strip_colors(text)
    display(text, parse_ansi=False)


def gui_input(prompt=""):
    """Replacement for input() that uses GUI input"""
    prompt = strip_colors(prompt)
    result = user_type_in(prompt)
    return result if result is not None else ""


# Monkey patch built-in functions globally
builtins.print = gui_print
builtins.input = gui_input


# Shared NoColors class
class NoColors:
    """Color class that returns empty strings (no colors)"""

    def __getattr__(self, _name):
        return ""


# Apply patches to all modules
modules_to_patch = [main, storyland, storywrite, chat, launcher]
for mod in modules_to_patch:
    if hasattr(mod, 'clear_screen'):
        setattr(mod, 'clear_screen', clear)
    if hasattr(mod, 'clear'):
        setattr(mod, 'clear', clear)
    setattr(mod, 'Colors', NoColors())

# Specific patches for modules
if hasattr(main, 'ask'):
    setattr(main, 'ask', gui_input)


# Launcher specific GUI functions
def gui_run_main():
    clear()
    display("=== Starting Main Game ===\n")
    try:
        main.main()
    except (SystemExit, KeyboardInterrupt):
        pass
    except Exception as e:
        display(f"\nError in Main Game: {str(e)}\n")
    display("\nReturning to launcher...")
    clear()


def gui_run_storyland():
    clear()
    display("=== Starting Storyland (Mod Browser) ===\n")
    try:
        storyland.main()
    except (SystemExit, KeyboardInterrupt):
        pass
    except Exception as e:
        display(f"\nError in Storyland: {str(e)}\n")
    display("\nReturning to launcher...")
    clear()


def gui_run_storywrite():
    clear()
    display("=== Starting Storywrite (Mod Uploader) ===\n")
    try:
        storywrite.main_menu()
    except (SystemExit, KeyboardInterrupt):
        pass
    except Exception as e:
        display(f"\nError in Storywrite: {str(e)}\n")
    display("\nReturning to launcher...")
    clear()


def gui_run_chat():
    clear()
    display("=== Starting Chat Client ===\n")
    try:
        chat_client = chat.EnhancedChatClient()
        chat_client.run()
    except (SystemExit, KeyboardInterrupt):
        pass
    except Exception as e:
        display(f"\nError in Chat: {str(e)}\n")
    display("\nReturning to launcher...")
    clear()


def gui_show_credits():
    clear()
    display("===============================================\n")
    display("                Our Legacy Team\n")
    display("===============================================\n")
    display("Andy64lol - Project Lead, Developer\n")
    display("\nBtw if you're interested in joining please contact us!\n")
    display("\nReturning to launcher...")
    clear()


# Override launcher functions to stay within the same process/GUI
launcher.run_main = gui_run_main
launcher.run_storyland = gui_run_storyland
launcher.run_storywrite = gui_run_storywrite
launcher.run_chat = gui_run_chat
launcher.show_credits = gui_show_credits


def run_full_gui():
    """Run the complete integrated GUI"""
    clear()
    display("=== Our Legacy===\n")
    display("Welcome to the unified interface for all components.\n\n")

    try:
        launcher.main_menu()
    except (LauncherExit, SystemExit):
        display("\nExiting application...")
        exit_gui()
    except Exception as e:
        display(f"\nFatal error: {str(e)}\n")
        display("Press Enter to exit...")
        input()
        exit_gui()


if __name__ == "__main__":
    set_theme("dark")
    gui_run(run_full_gui)