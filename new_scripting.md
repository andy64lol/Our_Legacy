# Javascript Scripting API Documentation

This API allows you to interact with the game world using Javascript (powered by QuickJS). 

## Getting Started

To use the API in your scripts, you should import the necessary modules from `scripting_API.js`:

```javascript
import { 
    player, enemy, battle, map, missions, system, 
    events, getActivities, clearActivities, getActivityCount, 
    log, print, activities, loadActivities, saveActivities 
} from './scripting_API.js';
```

## Global Utilities

- `print(message)`: Outputs a message to the game console (displayed as `[Script] message`).
- `tellraw(message)`: Outputs raw text directly to the game console without the `[Script]` prefix. Use this for immersive text that appears as if the game itself is narrating.
- `log(message)`: Logs a message with a timestamp.
- `getActivityCount()`: Returns the number of API actions performed in the current execution.
- `getActivities()`: Returns an array of all logged activities.
- `clearActivities()`: Resets the activity log.

## Player Module (`player`)

### Basic Information
- `player.uuid()`: Returns the player's unique identifier.
- `player.name()`: Returns the player's current name.
- `player.class()`: Returns the player's current class.
- `player.level`: Returns the player's current level (Direct property).
- `player.changeName(newName)`: Changes the player's name.
- `player.changeClass(newClass)`: Changes the player's class.

### Health & Mana
- `player.getHealth()` / `player.getMaxHealth()`: Get current or maximum HP.
- `player.setHealth(value)` / `player.setMaxHealth(value)`: Set HP values directly.
- `player.addHealth(amount)` / `player.addMaxHealth(amount)`: Increase/Decrease HP values.
- `player.getMP()` / `player.getMaxMP()`: Get current or maximum Mana.
- `player.setMP(value)` / `player.setMaxMP(value)`: Set Mana values directly.
- `player.addMP(amount)` / `player.addMaxMP(amount)`: Increase/Decrease Mana values.

### Experience & Leveling
- `player.exp.set(value)`: Sets the player's experience.
- `player.exp.add(amount)`: Adds experience points.

### Status Effects
- `player.hasEffect(effectId)`: Check if an effect is active.
- `player.addEffect(effectId)`: Apply a new status effect (e.g., 'poison', 'regeneration').

### Location
- `player.location()`: Returns current location object `{ id, name }`.
- `player.setLocation(locationId)`: Move the player to a new location.
- `player.locationsConnectedToCurrent()`: Returns an array of accessible neighboring locations.

### Inventory & Economy
- `player.inventory()`: Returns an array of items in the player's possession.
- `player.hasItem(itemId, amount = 1)`: Check for specific items.
- `player.addItem(itemId, amount = 1)`: Add items to inventory.
- `player.removeItem(itemId, amount = 1)`: Remove items from inventory.
- `player.gold()`: Get current gold amount.
- `player.giveGold()`: Add gold to the player.
- `player.deleteGold()`: Remove gold from the player.
- `player.lastItemConsumed()`: Get the ID of the last item used.
- `player.lastItemObtained()`: Get the ID of the last item picked up.

### Equipment
- `player.getEquipped()`: Returns current equipment `{ weapon, offhand, armor, accessory }`.
- `player.equip(itemId)`: Equip an item.
- `player.unequip(itemId)`: Unequip an item.
- `player.hasItemEquipped(itemId)`: Check if an item is currently being worn.

### Companions
- `player.companions()`: List all current companions.
- `player.companionSlot(slotNumber)`: Get details of a companion in a specific slot.
- `player.joinCompanion(companionId)`: Recruit a companion.
- `player.disbandCompanion(companionId)`: Remove a companion.

## Battle Module (`battle`)

- `battle.start(enemyId)`: Initiate a regular battle.
- `battle.bossfightStart(bossId)`: Initiate a boss encounter.
- `battle.win()`: Force a victory.
- `battle.lose()`: Force a defeat.
- `battle.flee()`: Attempt to escape the battle.

## Enemy Module (`enemy`)

- `enemy.id()`: Get the current enemy's ID.
- `enemy.isBoss()`: Check if the current enemy is a boss.
- `enemy.hp()`: Get current enemy HP.
- `enemy.setCurrentHP(value)`: Set enemy HP directly.
- `enemy.addCurrentHP(amount)`: Modify enemy HP.

## Map Module (`map`)

- `map.getDifficulty()`: Get the difficulty level of the current area.
- `map.getCanRest()`: Check if resting is allowed here.
- `map.getCanRestCosts()`: Get the cost to rest.
- `map.getAvalaibleMaterials()`: List harvestable materials in the area.
- `map.getAvalaibleMonster()` / `map.getAvalaibleBoss()`: List potential encounters.
- `map.getAvalaibleShops()`: List accessible shops.
- `map.getAvalaibleConnections()`: List neighboring map nodes.

## Missions Module (`missions`)

- `missions.getNotAccepted()`: List available missions.
- `missions.getOngoing()`: List active missions.
- `missions.getFinished()`: List completed missions.
- `missions.accept(missionId)`: Accept a new mission.
- `missions.finish(missionId)`: Complete a mission.
- `missions.deleteFromOngoing(missionId)` / `missions.deleteFromFinished(missionId)`: Remove mission records.

## Events System (`events`)

- `events.on(eventName, callback)`: Listen for a specific event.
- `events.emit(eventName, data)`: Trigger a custom event with data.

## System Module (`system`)

- `system.saveGame()`: Save current progress.
- `system.latest_save()`: Get timestamp or info of the last save.
- `system.deleteSaveFile()`: Wipe save data.

---

### Technical Implementation
The system executes scripts listed in `scripts/scripts.json` inside the `scripts/` directory whenever the user interacts with the game. Data is synchronized via `scripts/activities.json`.
