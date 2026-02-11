"""
Our Legacy - Launcher GUI Version
A GUI wrapper for the launcher using Py2GUI
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
    user_write,
    clear,
    run as gui_run,
    set_theme,
    exit_gui
)

# Import the launcher
import launcher
from launcher import LauncherExit

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
    # Don't clear here - let the caller decide when to clear
    return result if result is not None else ""


# Monkey patch built-in functions globally
builtins.print = gui_print
builtins.input = gui_input

# Patch clear function in launcher module
launcher.clear = clear

# Patch the run functions to use GUI versions
def gui_run_main():
    """Run main game in GUI mode"""
    display("Starting Main Game...\n")
    try:
        subprocess.Popen([sys.executable, "main_gui.py"])
        display("Main Game launched in a new window!\n")
        display("Returning to launcher...\n")
    except Exception as e:
        display(f"Error running main game: {str(e)}\n")

def gui_run_storyland():
    """Run storyland in GUI mode"""
    display("Starting Storyland (Mod Browser)...\n")
    try:
        subprocess.Popen([sys.executable, "storyland_gui.py"])
        display("Storyland launched in a new window!\n")
        display("Returning to launcher...\n")
    except Exception as e:
        display(f"Error running storyland: {str(e)}\n")

def gui_run_storywrite():
    """Run storywrite in GUI mode"""
    display("Starting Storywrite (Mod Uploader)...\n")
    try:
        subprocess.Popen([sys.executable, "storywrite_gui.py"])
        display("Storywrite launched in a new window!\n")
        display("Returning to launcher...\n")
    except Exception as e:
        display(f"Error running storywrite: {str(e)}\n")

def gui_run_chat():
    """Run chat in GUI mode"""
    display("Starting Chat Client...\n")
    try:
        subprocess.Popen([sys.executable, "chat_gui.py"])
        display("Chat Client launched in a new window!\n")
        display("Returning to launcher...\n")
    except Exception as e:
        display(f"Error running chat: {str(e)}\n")

def gui_show_credits():
    """Show credits in GUI mode"""
    display("===============================================\n")
    display("                Our Legacy Team\n")
    display("===============================================\n")
    display("Andy64lol - Project Lead, Developer\n")
    display("\n")
    display("Btw if you're interested in joining please send me an e-mail through andy64xd@gmail.com! (Even though I'm busy normally...)\n")
    display("\n")
    display("Press Enter to return to menu...")
    # Simple input that works with monkey-patched input
    try:
        input()
    except:
        pass
    clear()

# Replace launcher functions with GUI versions
launcher.run_main = gui_run_main
launcher.run_storyland = gui_run_storyland
launcher.run_storywrite = gui_run_storywrite
launcher.run_chat = gui_run_chat
launcher.show_credits = gui_show_credits


def run_gui_launcher():
    """Run the launcher in GUI mode"""
    # Clear the screen first
    clear()
    
    # Display welcome message
    display("=== Our Legacy - Launcher GUI ===\n")
    display("Loading launcher...\n\n")
    
    # Run the main launcher menu - it has its own loop
    try:
        launcher.main_menu()
    except LauncherExit:
        # User selected exit - this is expected, close GUI properly
        exit_gui()
        return
    except SystemExit:
        # User selected exit - this is expected
        exit_gui()
        return
    except Exception as e:
        display(f"\nError occurred: {str(e)}\n")
        display("Press Enter to exit...")
        try:
            user_type_in("")
        except:
            pass
        exit_gui()
        return


if __name__ == "__main__":
    # Set a dark theme for better readability
    set_theme("dark")
    
    # Run the GUI
    gui_run(run_gui_launcher)
