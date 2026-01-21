# Javascript Scripting API Documentation

This API allows you to interact with the game world using Javascript (powered by Node.js). 

## Getting Started

To use the API in your scripts, you should import the necessary modules from `scripting_API.js`:

```javascript
import { 
    player, enemy, battle, map, missions, system, 
    menu, tellraw, log, print
} from './scripting_API.js';
```

## Global Utilities

- `print(message)`: Outputs a message to the game console (displayed as `[Script] message`).
- `tellraw(message)`: Outputs raw text directly to the game console without the `[Script]` prefix. Use this for immersive text that appears as if the game itself is narrating.
- `log(message)`: Logs a message with a timestamp.

## Menu API (`menu`)

The Menu API allows scripts to dynamically interact with the game's UI.

- `menu.addButton(id, label, actionScript)`: Adds a custom button to the main menu. When clicked, it will execute the specified script file.
- `menu.removeButton(id)`: Removes a previously added script button.
- `menu.hide()`: Hides the main menu (clears the screen).
- `menu.show()`: Forces the main menu to reappear.

## Player Module (`player`)

### Basic Information
- `player.uuid()`: Returns the player's unique identifier.
- `player.name()`: Returns the player's current name.
- `player.class()`: Returns the player's current class.
- `player.level`: Returns the player's current level.
- `player.changeName(newName)`: Changes the player's name.
- `player.changeClass(newClass)`: Changes the player's class.

### Health & Mana
- `player.getHealth()` / `player.getMaxHealth()`: Get current or maximum HP.
- `player.setHealth(value)` / `player.addHealth(amount)`: Manage HP.
- `player.getMP()` / `player.setMP(value)`: Manage Mana.

### Experience & Economy
- `player.exp.add(amount)`: Adds experience points.
- `player.gold()`: Returns current gold.
- `player.giveGold(amount)`: Adds gold.
- `player.deleteGold(amount)`: Removes gold.

### Status Effects
- `player.hasEffect(effectId)`: Check if an effect is active (synchronized from the game's buff system).
- `player.addEffect(effectId)`: Apply a new status effect.

### Location
- `player.location()`: Returns current location object `{ id, name }`.
- `player.setLocation(locationId)`: Move the player.

### Inventory & Equipment
- `player.inventory()`: Returns an array of item IDs.
- `player.hasItem(itemId, amount)`: Check for items.
- `player.addItem(itemId, amount)`: Add items.
- `player.removeItem(itemId, amount)`: Remove items.
- `player.getEquipped()`: Returns current equipment.

## Battle Module (`battle`)

- `battle.start(enemyId)`: Initiate a battle.
- `battle.win()`: Force a victory.

## Enemy Module (`enemy`)

- `enemy.id()`: Get current enemy ID.
- `enemy.hp()`: Get current enemy HP.
- `enemy.setCurrentHP(value)`: Set enemy HP.

---

### Technical Implementation
The engine uses Node.js to run scripts. Game state is synced to `scripts/activities.json` before execution, and the API updates this file to send actions back to the Python engine.
