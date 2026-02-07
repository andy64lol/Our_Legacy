"""
Our Legacy - GUI Version
A GUI wrapper for the text-based CLI Fantasy RPG Game using Py2GUI
"""

import builtins
import sys
import re
import os

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import py2gui functions
from py2gui import (
    display,
    user_type_in,
    clear,
    run as gui_run,
    set_theme,
    exit_gui
)

# Import the main game
import main

# Color code pattern for stripping
COLOR_PATTERN = re.compile(r'\x1b\[[0-9;]*m')
ANSI_PATTERN = re.compile(r'\033\[[0-9;]*m')


def strip_colors(text):
    """Remove all ANSI color codes from text"""
    if text is None:
        return ""
    text = str(text)
    text = COLOR_PATTERN.sub('', text)
    text = ANSI_PATTERN.sub('', text)
    # Also strip any Colors class references like Colors.RED, Colors.END, etc.
    text = re.sub(r'Colors\.[A-Z_]+', '', text)
    return text


# Store original functions
_original_print = print
_original_input = input


def gui_print(*args, sep=' ', end='\n', **kwargs):
    """Replacement for print() that outputs to GUI"""
    text = sep.join(str(arg) for arg in args) + end
    text = strip_colors(text)
    display(text, parse_ansi=False)


def gui_input(prompt=""):
    """Replacement for input() that uses GUI input"""
    prompt = strip_colors(prompt)
    result = user_type_in(prompt)
    # Clear the screen after user input
    clear()
    return result if result is not None else ""


def gui_ask(prompt=""):
    """Replacement for ask() function used in main.py"""
    return gui_input(prompt)


# Monkey patch built-in functions globally
builtins.print = gui_print
builtins.input = gui_input

# Patch the ask function in main module if it exists
if hasattr(main, 'ask'):
    main.ask = gui_ask

# Patch clear_screen to use py2gui's clear
if hasattr(main, 'clear_screen'):
    main.clear_screen = clear

# Also patch in the Colors class to return empty strings
class NoColors:
    """Color class that returns empty strings (no colors)"""
    def __getattr__(self, name):
        return ""

# Replace Colors class in main module
main.Colors = NoColors()


def run_gui_game():
    """Run the game in GUI mode"""
    # Clear the screen first
    clear()
    
    # Display welcome message
    display("=== Our Legacy - GUI Version ===\n")
    display("Loading game...\n")
    
    # Run the main game
    try:
        main.main()
    except SystemExit:
        pass
    except Exception as e:
        display(f"\nError occurred: {str(e)}\n")
        raise


if __name__ == "__main__":
    # Set a dark theme for better readability
    set_theme("dark")
    
    # Run the GUI
    gui_run(run_gui_game)
