#!/usr/bin/env python3
"""
Our Legacy Mod Downloader CLI

Downloads mods from the GitHub repository and installs them locally.
Features: Pagination, colored output, screen clearing, navigation.
"""

import json
import os
import sys
import requests
import zipfile
import io
from pathlib import Path


# Configuration
GITHUB_API_URL = "https://api.github.com"
REPO_OWNER = "andy64lol"
REPO_NAME = "Our_Legacy_Mods"
MODS_BRANCH = "main"
LOCAL_MODS_DIR = Path(__file__).parent / "mods"
MODS_PER_PAGE = 10


# Colors
class Colors:
    RESET = '\033[0m'
    BOLD = '\033[1m'
    
    # Colors
    BLACK = '\033[30m'
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    MAGENTA = '\033[35m'
    CYAN = '\033[36m'
    WHITE = '\033[37m'
    
    # Bright colors
    BRIGHT_BLACK = '\033[90m'
    BRIGHT_RED = '\033[91m'
    BRIGHT_GREEN = '\033[92m'
    BRIGHT_YELLOW = '\033[93m'
    BRIGHT_BLUE = '\033[94m'
    BRIGHT_MAGENTA = '\033[95m'
    BRIGHT_CYAN = '\033[96m'
    BRIGHT_WHITE = '\033[97m'
    
    # Background colors
    BG_RED = '\033[41m'
    BG_GREEN = '\033[42m'
    BG_YELLOW = '\033[43m'
    BG_BLUE = '\033[44m'


def clear_screen():
    """Clear the terminal screen."""
    os.system('cls' if os.name == 'nt' else 'clear')


def get_available_mods():
    """Fetch list of available mods from GitHub repository."""
    url = f"{GITHUB_API_URL}/repos/{REPO_OWNER}/{REPO_NAME}/contents/mods?ref={MODS_BRANCH}"
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        contents = response.json()
        
        mods = []
        for item in contents:
            if item['type'] == 'dir' or item['type'] == 'file':
                if item['name'] != '.gitkeep':  # Skip gitkeep files
                    mods.append(item['name'])
        
        return sorted(mods)
    except requests.exceptions.RequestException as e:
        print(f"{Colors.RED}Error fetching mods: {e}{Colors.RESET}")
        return []


def get_mod_details(mod_name):
    """Get details of a specific mod."""
    url = f"{GITHUB_API_URL}/repos/{REPO_OWNER}/{REPO_NAME}/contents/mods/{mod_name}?ref={MODS_BRANCH}"
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"{Colors.RED}Error fetching mod details: {e}{Colors.RESET}")
        return None


def download_and_install_mod(mod_name):
    """Download a mod and install it to the local mods directory."""
    # First, try to get the mod as a zip from GitHub
    zip_url = f"https://github.com/{REPO_OWNER}/{REPO_NAME}/archive/refs/heads/{MODS_BRANCH}.zip"
    
    try:
        # Download the entire repository as zip
        response = requests.get(zip_url)
        response.raise_for_status()
        
        # Extract the zip in memory
        with zipfile.ZipFile(io.BytesIO(response.content)) as zf:
            # The zip will have a folder like "Our_Legacy_Mods-main/mods/{mod_name}/"
            prefix = f"Our_Legacy_Mods-{MODS_BRANCH}/mods/{mod_name}/"
            
            # Find all files for this mod
            mod_files = [f for f in zf.namelist() if f.startswith(prefix) and not f.endswith('/')]
            
            if not mod_files:
                print(f"{Colors.RED}No files found for mod: {mod_name}{Colors.RESET}")
                return False
            
            # Create the local mod directory
            local_mod_dir = LOCAL_MODS_DIR / mod_name
            local_mod_dir.mkdir(parents=True, exist_ok=True)
            
            # Extract each file
            for file_path in mod_files:
                # Remove the prefix to get the relative path
                relative_path = file_path[len(prefix):]
                
                # Skip if it's just a directory reference
                if not relative_path:
                    continue
                
                # Create the full local path
                local_path = local_mod_dir / relative_path
                
                # Create parent directories if needed
                local_path.parent.mkdir(parents=True, exist_ok=True)
                
                # Extract the file
                with zf.open(file_path) as source, open(local_path, 'wb') as target:
                    target.write(source.read())
            
            print(f"{Colors.GREEN}✓ Successfully installed mod: {mod_name}{Colors.RESET}")
            return True
            
    except requests.exceptions.RequestException as e:
        print(f"{Colors.RED}Error downloading mod: {e}{Colors.RESET}")
        return False
    except zipfile.BadZipFile:
        print(f"{Colors.RED}Error: Invalid zip file received from GitHub{Colors.RESET}")
        return False
    except Exception as e:
        print(f"{Colors.RED}Error installing mod: {e}{Colors.RESET}")
        return False


def display_banner():
    """Display the CLI banner."""
    clear_screen()
    print(f"{Colors.CYAN}{Colors.BOLD}")
    print("=" * 50)
    print("     Our Legacy Mod Downloader: Storyland")
    print("=" * 50)
    print(f"{Colors.RESET}")


def display_mod_list(mods, current_page, total_pages):
    """Display a page of mods with pagination info."""
    print(f"\n{Colors.BRIGHT_BLUE}Available Mods (Page {current_page}/{total_pages}){Colors.RESET}")
    print("-" * 50)
    
    start_idx = (current_page - 1) * MODS_PER_PAGE
    end_idx = min(start_idx + MODS_PER_PAGE, len(mods))
    
    for i in range(start_idx, end_idx):
        mod_num = i + 1
        mod_name = mods[i]
        
        # Alternate colors for mod numbers
        if mod_num % 2 == 0:
            num_color = Colors.YELLOW
        else:
            num_color = Colors.BRIGHT_YELLOW
        
        print(f"{num_color}{mod_num:2}.{Colors.RESET} {Colors.WHITE}{mod_name}{Colors.RESET}")
    
    print("-" * 50)


def main():
    """Main CLI function."""
    display_banner()
    
    # Get list of available mods
    print(f"\n{Colors.YELLOW}Fetching available mods...{Colors.RESET}")
    mods = get_available_mods()
    
    if not mods:
        print(f"\n{Colors.RED}No mods found or error connecting to GitHub.{Colors.RESET}")
        sys.exit(1)
    
    total_mods = len(mods)
    total_pages = (total_mods + MODS_PER_PAGE - 1) // MODS_PER_PAGE
    current_page = 1
    
    # Main loop
    while True:
        display_banner()
        display_mod_list(mods, current_page, total_pages)
        
        print(f"\n{Colors.MAGENTA}{Colors.BOLD}Enter your choice:{Colors.RESET} ", end="")
        
        try:
            choice = input().strip().lower()
        except (EOFError, OSError):
            # Handle Ctrl+D or other input errors
            print(f"\n{Colors.RED}Input error. Use 'q' to quit.{Colors.RESET}")
            continue
        
        # Clear screen after each action
        clear_screen()
        
        # Handle navigation commands
        if choice in ['q', 'quit']:
            print(f"\n{Colors.CYAN}Thank you for using Our Legacy Mod Downloader Storyland!{Colors.RESET}")
            print(f"{Colors.CYAN}Goodbye!{Colors.RESET}\n")
            sys.exit(0)
        
        elif choice == 'n' or choice == 'next':
            if current_page < total_pages:
                current_page += 1
                print(f"\n{Colors.GREEN}Going to next page...{Colors.RESET}")
            else:
                print(f"\n{Colors.YELLOW}Already on the last page.{Colors.RESET}")
            continue
        
        elif choice == 'p' or choice == 'prev' or choice == 'previous':
            if current_page > 1:
                current_page -= 1
                print(f"\n{Colors.GREEN}Going to previous page...{Colors.RESET}")
            else:
                print(f"\n{Colors.YELLOW}Already on the first page.{Colors.RESET}")
            continue
        
        # Handle mod selection
        try:
            choice_idx = int(choice) - 1
            
            # Calculate which page this mod would be on
            if choice_idx < 0 or choice_idx >= total_mods:
                print(f"\n{Colors.RED}Invalid selection. Please enter a number between 1 and {total_mods}{Colors.RESET}")
                input(f"\n{Colors.BLUE}Press Enter to continue...{Colors.RESET}")
                continue
            
            selected_mod = mods[choice_idx]
            
            # Navigate to the correct page if needed
            required_page = (choice_idx // MODS_PER_PAGE) + 1
            if required_page != current_page:
                current_page = required_page
            
            print(f"\n{Colors.YELLOW}Downloading and installing: {Colors.BRIGHT_WHITE}{selected_mod}{Colors.RESET}...")
            
            if download_and_install_mod(selected_mod):
                print(f"\n{Colors.GREEN}✓ Mod '{selected_mod}' has been successfully installed!{Colors.RESET}")
                print(f"{Colors.BLUE}  Location: {LOCAL_MODS_DIR / selected_mod}{Colors.RESET}")
            else:
                print(f"\n{Colors.RED}✗ Failed to install mod '{selected_mod}'{Colors.RESET}")
            
            input(f"\n{Colors.BLUE}Press Enter to continue...{Colors.RESET}")
            
        except ValueError:
            print(f"\n{Colors.RED}Invalid input. Please enter a number, 'n', 'p', or 'q'.{Colors.RESET}")
            input(f"\n{Colors.BLUE}Press Enter to continue...{Colors.RESET}")


if __name__ == "__main__":
    main()

