#!/usr/bin/env python3
"""
Our Legacy Mod Uploader CLI - Storywrite
Interactive Text UI Version
"""

import json
import os
import sys
import base64
import requests
from pathlib import Path

# Configuration
API_URL = "https://our-legacy.vercel.app/api/upload_test"

# Colors
class Colors:
    RESET = '\033[0m'
    BOLD = '\033[1m'
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    CYAN = '\033[36m'
    BRIGHT_WHITE = '\033[97m'


def clear():
    os.system("clear" if os.name != "nt" else "cls")


def display_banner():
    clear()
    print(f"{Colors.CYAN}{Colors.BOLD}")
    print("=" * 50)
    print("     Our Legacy Mod Uploader: Storywrite")
    print("=" * 50)
    print(f"{Colors.RESET}")


def validate_mod_directory(mod_path):
    path = Path(mod_path)
    if not path.exists():
        print(f"{Colors.RED}Error: Directory '{mod_path}' does not exist.{Colors.RESET}")
        return None, None
    if not path.is_dir():
        print(f"{Colors.RED}Error: '{mod_path}' is not a directory.{Colors.RESET}")
        return None, None

    mod_json_path = path / "mod.json"
    if not mod_json_path.exists():
        print(f"{Colors.RED}Error: Directory must contain 'mod.json'.{Colors.RESET}")
        return None, None

    try:
        with open(mod_json_path, 'r', encoding='utf-8') as f:
            mod_data = json.load(f)
        mod_name = mod_data.get('name') or mod_data.get('id') or path.name
        if not mod_name:
            print(f"{Colors.RED}Error: 'mod.json' must contain a 'name' or 'id'.{Colors.RESET}")
            return None, None
    except Exception as e:
        print(f"{Colors.RED}Error reading mod.json: {e}{Colors.RESET}")
        return None, None

    return path, mod_name


def collect_files(directory_path):
    files = {}
    for file_path in directory_path.rglob('*'):
        if file_path.is_file():
            rel_path = file_path.relative_to(directory_path)
            try:
                with open(file_path, 'rb') as f:
                    encoded = base64.b64encode(f.read()).decode('utf-8')
                    files[str(rel_path)] = encoded
            except Exception as e:
                print(f"{Colors.YELLOW}Warning: Could not read file '{rel_path}': {e}{Colors.RESET}")
    return files


def upload_mod(mod_path):
    directory_path, mod_name = validate_mod_directory(mod_path)
    if directory_path is None:
        return False

    print(f"\n{Colors.CYAN}{Colors.BOLD}Preparing to upload mod:{Colors.RESET} {Colors.BRIGHT_WHITE}{mod_name}{Colors.RESET}")
    print(f"{Colors.BLUE}Directory: {directory_path}{Colors.RESET}")

    files = collect_files(directory_path)
    if not files:
        print(f"{Colors.RED}Error: No files found in the directory.{Colors.RESET}")
        return False

    print(f"{Colors.GREEN}Found {len(files)} files.{Colors.RESET}")

    payload = {"dir_name": mod_name, "files": files}
    print(f"\n{Colors.YELLOW}Uploading to GitHub repository...{Colors.RESET}")

    try:
        response = requests.post(API_URL, json=payload)
        response.raise_for_status()
        result = response.json()
        if result.get('success'):
            print(f"\n{Colors.GREEN}{Colors.BOLD}✓ Successfully uploaded mod: {mod_name}{Colors.RESET}")
            print(f"\n{Colors.CYAN}Uploaded Files:{Colors.RESET}")
            for file in result.get('files', []):
                print(f"  • {file}")
            print(f"\n{Colors.BLUE}GitHub Directory: {result.get('directory')}{Colors.RESET}")
            return True
        else:
            print(f"\n{Colors.RED}Error: {result.get('error', 'Unknown error')}{Colors.RESET}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"\n{Colors.RED}Upload failed: {e}{Colors.RESET}")
        return False


def select_mod_directory():
    """Let user choose a mod directory interactively."""
    print(f"{Colors.CYAN}Enter the path to your mod directory:{Colors.RESET}")
    mod_path = input("> ").strip()
    return mod_path


def main_menu():
    while True:
        display_banner()
        print(f"{Colors.BLUE}1.{Colors.RESET} Upload a mod")
        print(f"{Colors.BLUE}2.{Colors.RESET} Exit")
        print("_______________________________________________")
        choice = input("Please enter (1-2): ").strip()
        if choice == "1":
            mod_path = select_mod_directory()
            success = upload_mod(mod_path)
            input("\nPress Enter to return to menu...")
        elif choice == "2":
            clear()
            sys.exit(0)
        else:
            input("Invalid choice! Press Enter to try again...")


if __name__ == "__main__":
    main_menu()