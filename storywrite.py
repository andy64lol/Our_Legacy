#!/usr/bin/env python3
"""
Our Legacy Mod Uploader CLI - Storywrite

Uploads mods to the GitHub repository via the upload_test API.
Features: Colored output, file validation, error handling.
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


def validate_mod_directory(mod_path):
    """Validate that the mod directory contains required files."""
    path = Path(mod_path)
    
    if not path.exists():
        print(f"{Colors.RED}Error: Directory '{mod_path}' does not exist.{Colors.RESET}")
        return None, None
    
    if not path.is_dir():
        print(f"{Colors.RED}Error: '{mod_path}' is not a directory.{Colors.RESET}")
        return None, None
    
    # Check for mod.json
    mod_json_path = path / "mod.json"
    if not mod_json_path.exists():
        print(f"{Colors.RED}Error: Directory must contain 'mod.json' file.{Colors.RESET}")
        return None, None
    
    # Read mod.json to get the mod name
    try:
        with open(mod_json_path, 'r', encoding='utf-8') as f:
            mod_data = json.load(f)
        
        mod_name = mod_data.get('name') or mod_data.get('id') or path.name
        
        if not mod_name:
            print(f"{Colors.RED}Error: mod.json must contain a 'name' or 'id' field.{Colors.RESET}")
            return None, None
            
    except json.JSONDecodeError as e:
        print(f"{Colors.RED}Error: Invalid JSON in mod.json: {e}{Colors.RESET}")
        return None, None
    except Exception as e:
        print(f"{Colors.RED}Error reading mod.json: {e}{Colors.RESET}")
        return None, None
    
    return path, mod_name


def collect_files(directory_path):
    """Collect all files from the mod directory."""
    files = {}
    
    for file_path in directory_path.rglob('*'):
        if file_path.is_file():
            # Get the relative path from the mod directory
            rel_path = file_path.relative_to(directory_path)
            
            # Read file content and encode
            try:
                with open(file_path, 'rb') as f:
                    content = f.read()
                    # Encode to base64
                    encoded = base64.b64encode(content).decode('utf-8')
                    files[str(rel_path)] = encoded
            except Exception as e:
                print(f"{Colors.YELLOW}Warning: Could not read file '{rel_path}': {e}{Colors.RESET}")
                continue
    
    return files


def upload_mod(mod_path):
    """Upload a mod to the GitHub repository via the API."""
    directory_path, mod_name = validate_mod_directory(mod_path)
    
    if directory_path is None:
        return False
    
    print(f"\n{Colors.CYAN}{Colors.BOLD}Preparing to upload mod: {Colors.RESET}{Colors.BRIGHT_WHITE}{mod_name}{Colors.RESET}")
    print(f"{Colors.BLUE}Directory: {directory_path}{Colors.RESET}")
    
    # Collect files
    print(f"\n{Colors.YELLOW}Collecting files...{Colors.RESET}")
    files = collect_files(directory_path)
    
    if not files:
        print(f"{Colors.RED}Error: No files found in the directory.{Colors.RESET}")
        return False
    
    print(f"{Colors.GREEN}Found {len(files)} files.{Colors.RESET}")
    
    # Prepare the payload
    payload = {
        "dir_name": mod_name,
        "files": files
    }
    
    print(f"\n{Colors.YELLOW}Uploading to GitHub repository...{Colors.RESET}")
    
    response = None
    status_code = 500
    try:
        response = requests.post(API_URL, json=payload)
        status_code = response.status_code
        response.raise_for_status()
        
        result = response.json()
        
        if result.get('success'):
            print(f"\n{Colors.GREEN}{Colors.BOLD}✓ Successfully uploaded mod: {mod_name}{Colors.RESET}")
            print(f"\n{Colors.BRIGHT_CYAN}Uploaded Files:{Colors.RESET}")
            for file in result.get('files', []):
                print(f"  {Colors.GREEN}  • {file}{Colors.RESET}")
            print(f"\n{Colors.BLUE}GitHub Directory: {result.get('directory')}{Colors.RESET}")
            return True
        else:
            print(f"\n{Colors.RED}Error: {result.get('error', 'Unknown error')}{Colors.RESET}")
            return False
            
    except requests.exceptions.HTTPError:
        error_msg = "Unknown error"
        try:
            if response is not None:
                error_data = response.json()
                error_msg = error_data.get('error', str(status_code))
            else:
                error_msg = str(status_code)
        except (ValueError, AttributeError):
            error_msg = str(status_code)
        
        print(f"\n{Colors.RED}Upload failed: {error_msg}{Colors.RESET}")
        
        # Provide helpful error messages
        if status_code == 409:
            print(f"{Colors.YELLOW}This mod directory already exists in the repository.{Colors.RESET}")
        elif status_code == 400:
            print(f"{Colors.YELLOW}Check that your mod.json is valid and all files are correct.{Colors.RESET}")
        elif status_code == 401 or status_code == 403:
            print(f"{Colors.YELLOW}Authentication failed. Check your GITHUB_REST_API token.{Colors.RESET}")
        
        return False
        
    except requests.exceptions.RequestException as e:
        print(f"\n{Colors.RED}Network error: {e}{Colors.RESET}")
        print(f"{Colors.YELLOW}Please check your internet connection and try again.{Colors.RESET}")
        return False


def display_banner():
    """Display the CLI banner."""
    print(f"{Colors.CYAN}{Colors.BOLD}")
    print("=" * 50)
    print("     Our Legacy Mod Uploader: Storywrite")
    print("=" * 50)
    print(f"{Colors.RESET}")


def print_help():
    """Print help information."""
    print(f"\n{Colors.BRIGHT_CYAN}{Colors.BOLD}Usage:{Colors.RESET}")
    print(f"  {Colors.YELLOW}python3 storywrite.py <mod_directory>{Colors.RESET}")
    print()
    print(f"{Colors.BRIGHT_CYAN}{Colors.BOLD}Arguments:{Colors.RESET}")
    print(f"  {Colors.WHITE}<mod_directory>{Colors.RESET}  Path to the mod directory containing mod.json")
    print()
    print(f"{Colors.BRIGHT_CYAN}{Colors.BOLD}Environment Variables (Optional):{Colors.RESET}")
    print(f"  {Colors.WHITE}GITHUB_REST_API{Colors.RESET}      GitHub REST API token (for authentication)")
    print(f"  {Colors.WHITE}GITHUB_USERNAME{Colors.RESET}      GitHub username (defaults to 'andy64lol')")
    print(f"  {Colors.WHITE}GITHUB_REPOSITORY{Colors.RESET}    GitHub repository name (defaults to 'Our_Legacy_Mods')")
    print()
    print(f"{Colors.BRIGHT_CYAN}{Colors.BOLD}Example:{Colors.RESET}")
    print(f"  {Colors.GREEN}python3 storywrite.py ./mods/my_awesome_mod{Colors.RESET}")
    print()
    print(f"{Colors.YELLOW}Note: The mod directory must contain a valid 'mod.json' file.{Colors.RESET}")


def main():
    """Main CLI function."""
    display_banner()
    
    # Check for --help or -h flag
    if len(sys.argv) > 1 and sys.argv[1] in ['--help', '-h']:
        print_help()
        sys.exit(0)
    
    # Check for mod directory argument
    if len(sys.argv) < 2:
        print(f"{Colors.RED}Error: No mod directory specified.{Colors.RESET}\n")
        print(f"{Colors.YELLOW}Use --help for usage information.{Colors.RESET}")
        sys.exit(1)
    
    mod_path = sys.argv[1]
    
    # Upload the mod
    success = upload_mod(mod_path)
    
    if success:
        print(f"\n{Colors.GREEN}{Colors.BOLD}✓ Upload complete!{Colors.RESET}")
        print(f"{Colors.CYAN}Your mod is now available in the repository.{Colors.RESET}")
        sys.exit(0)
    else:
        print(f"\n{Colors.RED}{Colors.BOLD}✗ Upload failed.{Colors.RESET}")
        sys.exit(1)


if __name__ == "__main__":
    main()

