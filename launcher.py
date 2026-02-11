#!/usr/bin/env python3
"""
Our Legacy Launcher - Fancy Text UI
Runs all scripts directly from the same directory.
"""

import os
import sys
import subprocess

# Custom exception for clean exit (used by GUI wrapper)
class LauncherExit(Exception):
    """Exception raised when user wants to exit the launcher"""
    pass

# ANSI colors
BLUE = "\033[34m"
RESET = "\033[0m"

def clear():
    os.system("clear" if os.name != "nt" else "cls")

def run_main():
    subprocess.run([sys.executable, "main.py"])

def run_storyland():
    subprocess.run([sys.executable, "storyland.py"])

def run_storywrite():
    # Just execute storywrite.py directly
    subprocess.run(["python3", "storywrite.py"])

def run_chat():
    # Execute chat.py directly
    subprocess.run([sys.executable, "chat.py"])

def show_credits():
    print(BLUE + "===============================================")
    print("                Our Legacy Team")
    print("===============================================" + RESET)
    print("Andy64lol - Project Lead, Developer")
    print()
    print()
    print("Btw if you're interested in joining please send me an e-mail through andy64xd@gmail.com! (Even though I'm busy normally...)")
    print()
    print()
    input("Press Enter to return to menu...")
    clear()

def main_menu():
    while True:
        clear()
        print(BLUE + "===============================================")
        print("             Our Legacy Launcher")
        print("===============================================" + RESET)
        print(f"{BLUE}1.{RESET} Main game")
        print(f"{BLUE}2.{RESET} Browse mods")
        print(f"{BLUE}3.{RESET} Upload mod")
        print(f"{BLUE}4.{RESET} Chat")
        print(f"{BLUE}5.{RESET} Credits")
        print(f"{BLUE}6.{RESET} Exit")
        print("_______________________________________________")
        choice = input("Please enter (1-6): ").strip()

        if choice == "1":
            run_main()
        elif choice == "2":
            run_storyland()
        elif choice == "3":
            run_storywrite()
        elif choice == "4":
            run_chat()
        elif choice == "5":
            clear()
            show_credits()
        elif choice == "6":
            clear()
            raise LauncherExit()
        else:
            input("Invalid choice! Press Enter to try again...")

if __name__ == "__main__":
    clear()
    try:
        main_menu()
    except LauncherExit:
        pass
    clear()
