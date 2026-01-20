#!/usr/bin/env python3
"""Test script for the scripting engine"""

import sys
sys.path.insert(0, '/home/andy64lolxd/Our_Legacy')

try:
    import quickjs
    print("QuickJS imported successfully")
except ImportError as e:
    print(f"Failed to import QuickJS: {e}")
    sys.exit(1)

# Read the scripting API
with open('/home/andy64lolxd/Our_Legacy/scripts/scripting_API.js', 'r') as f:
    api_code = f.read()

# Read the example script
with open('/home/andy64lolxd/Our_Legacy/scripts/example.js', 'r') as f:
    example_code = f.read()

# Create context and evaluate
print("\n=== Testing Scripting Engine ===\n")

context = quickjs.Context()

# Define print function for JS
def js_print(message):
    print(f"[Script] {message}")

context.globalThis['globalPrint'] = js_print

# Load the API
print("Loading scripting API...")
try:
    context.eval(api_code)
    print("API loaded successfully!\n")
except Exception as e:
    print(f"Failed to load API: {e}")
    sys.exit(1)

# Execute example script
print("Executing example script...\n")
try:
    context.eval(example_code)
    print("\nScript executed successfully!\n")
except Exception as e:
    print(f"Script execution error: {e}")
    sys.exit(1)

print("=== Test Complete ===")

