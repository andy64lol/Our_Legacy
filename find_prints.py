#!/usr/bin/env python3
"""
Script to find all print statements that don't contain language_manager.get() or self.lang.get() in their line.
This helps identify hardcoded strings that should be using the translation system.
Searches only in main.py.
"""

import os
import re
import sys
from pathlib import Path


def find_prints_without_language_manager():
    """
    Find all print statements that don't contain language_manager.get() or self.lang.get() in the same line.
    Searches only in main.py.
    
    Returns:
        List of tuples (filepath, line_number, line_content)
    """
    results = []
    
    # Pattern to match print statements (including f-strings, multiline)
    # This captures print( and everything until the closing parenthesis
    print_pattern = re.compile(r'print\s*\([^)]*\)', re.MULTILINE)
    
    # Pattern to check if line contains language_manager.get() or self.lang.get()
    lang_manager_pattern = re.compile(r'(language_manager\.get\(|self\.lang\.get\()')
    
    # Only search in main.py (in parent directory relative to this script)
    filepath = 'main.py'
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            lines = content.split('\n')
            
            for line_num, line in enumerate(lines, start=1):
                # Check if line contains a print statement
                if print_pattern.search(line):
                    # Check if line does NOT contain language_manager.get() or self.lang.get()
                    if not lang_manager_pattern.search(line):
                        results.append((filepath, line_num, line.strip()))
    
    except Exception as e:
        print(f"Error reading {filepath}: {e}", file=sys.stderr)
    
    return results


def main():
    """Main function to run the script."""
    print("Searching for print statements without language_manager.get() or self.lang.get() in: main.py")
    print("=" * 80)
    
    results = find_prints_without_language_manager()
    
    if not results:
        print("\n✓ No print statements without language_manager.get() or self.lang.get() found!")
        print("All print statements are properly using the translation system.")
        return 0
    
    # Group results by file
    current_file = None
    count = 0
    
    for filepath, line_num, line_content in results:
        # Show file header when file changes
        if filepath != current_file:
            if current_file is not None:
                print()  # Empty line between files
            current_file = filepath
            print(f"\n📄 {filepath}")
            print("-" * 80)
        
        # Print the line info
        print(f"  Line {line_num:4d}: {line_content[:100]}")
        if len(line_content) > 100:
            print(f"           ... {line_content[100:150]}...")
        count += 1
    
    print("\n" + "=" * 80)
    print(f"Total print statements without language_manager.get() or self.lang.get(): {count}")
    print(f"Files affected: {len(set(r[0] for r in results))}")
    
    return 1


if __name__ == "__main__":
    sys.exit(main())
