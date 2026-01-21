/**
 * Test script for dynamic button management API
 * This demonstrates how scripts can add custom menu buttons to the game
 */

// Add a button that runs an inline script
system.addButton("Test Inline Button", "inline", "print('Inline button clicked!'); tellraw('Hello from inline script!');");

// Add a button that runs a file-based script (uncomment to test with actual file)
// system.addButton("Test File Button", "file", "test_button_action.js");

// List all current buttons
var buttons = system.listButtons();
print("\nCurrent buttons:");
for (var key in buttons) {
    print("  - " + key + " (type: " + buttons[key].type + ")");
}

// Check if a button exists
if (system.hasButton("Test Inline Button")) {
    print("Button 'Test Inline Button' exists!");
}

// Demonstrate defineButtonScript - update an existing button's script
system.defineButtonScript("Test Inline Button", "print('Updated inline button!'); player.addGold(50); print('Gained 50 gold!');");

print("\nButton script updated. New script will give gold when clicked.");

print("\n=== Dynamic Button Test Complete ===");
print("Use 'Others' menu in the game to see and test your buttons.");
print("You can delete buttons from the Others menu (option D).");

