#!/usr/bin/env python3
"""
Our Legacy Launcher - Fancy Text UI
"""

import os
import sys
import subprocess

# ANSI colors
BLUE = "\033[34m"
RESET = "\033[0m"

def clear():
    os.system("clear" if os.name != "nt" else "cls")

def run_main():
    script_path = os.path.join(os.path.dirname(__file__), "main.py")
    subprocess.run([sys.executable, script_path])

def run_storyland():
    script_path = os.path.join(os.path.dirname(__file__), "storyland.py")
    subprocess.run([sys.executable, script_path])

def run_storywrite():
    mod_path = input("Enter path to your mod directory: ").strip()
    if not os.path.exists(mod_path):
        print(f"Mod path '{mod_path}' does not exist!")
        input("Press Enter to return to menu...")
        return
    script_path = os.path.join(os.path.dirname(__file__), "storywrite.py")
    subprocess.run([sys.executable, script_path, mod_path])

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
        print(f"{BLUE}4.{RESET} Exit")
        print(f"{BLUE}5.{RESET} Credits")
        print("_______________________________________________")
        choice = input("Please enter (1-5): ").strip()

        if choice == "1":
            run_main()
        elif choice == "2":
            run_storyland()
        elif choice == "3":
            run_storywrite()
        elif choice == "4":
            clear()
            sys.exit(0)
        elif choice == "5":
            clear()
            show_credits()
        else:
            input("Invalid choice! Press Enter to try again...")

if __name__ == "__main__":
    clear()
    main_menu()
    clear()
