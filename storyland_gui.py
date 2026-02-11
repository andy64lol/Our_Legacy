#!/usr/bin/env python3
"""
Our Legacy - Storyland GUI Version
A GUI wrapper for the mod downloader using Py2GUI
"""

import builtins
import sys
import re
import os
import subprocess

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

# Import the storyland module
import storyland

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
    return result if result is not None else ""


# Monkey patch built-in functions globally
builtins.print = gui_print
builtins.input = gui_input

# Patch clear_screen to use py2gui's clear
storyland.clear_screen = clear

# Replace Colors class in storyland module
class NoColors:
    """Color class that returns empty strings (no colors)"""
    def __getattr__(self, name):
        return ""

storyland.Colors = NoColors()


def run_gui_storyland():
    """Run the mod downloader in GUI mode"""
    # Clear the screen first
    clear()
    
    # Display welcome message
    display("=== Our Legacy - Storyland GUI Version ===\n")
    display("Loading mod browser...\n\n")
    
    # Run the mod downloader
    try:
        storyland.main()
    except SystemExit:
        pass
    except Exception as e:
        print(f"\nError occurred: {str(e)}\n")
        raise


if __name__ == "__main__":
    # Set a dark theme for better readability
    set_theme("dark")
    
    # Run the GUI
    gui_run(run_gui_storyland)
