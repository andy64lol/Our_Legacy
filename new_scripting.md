# The new scripting api based on javascript, using library quickjs

```javascript
player.uuid()
player.name()
player.class()

player.changeName(newName)
player.changeClass(newClass)

player.getHealth()
player.getMaxHealth()
player.setHealth(value)
player.setMaxHealth(value)
player.addHealth(amount)
player.addMaxHealth(amount)

player.getMP()
player.getMaxMP()
player.setMP(value)
player.setMaxMP(value)
player.addMP(amount)
player.addMaxMP(amount)

player.hasEffect(effectId)
player.addEffect(effectId)

player.location() // { id, name }
player.setLocation(locationId)
player.locationsConnectedToCurrent() // array

player.level.set(value)
player.level.add(amount)

player.exp.set(value)
player.exp.add(amount)

player.hasItem(itemId, amount = 1)
player.addItem(itemId, amount = 1)
player.removeItem(itemId, amount = 1)

player.inventory() // array
player.gold()
player.giveGold()
player.deleteGold()

player.companions() // array
player.companionSlot(slotNumber)

player.joinCompanion(companionId)
player.disbandCompanion(companionId)

player.getEquipped() // { weapon, offhand, armor, accessory }

player.equip(itemId)
player.unequip(itemId)

player.hasItemEquipped(itemId)

enemy.id()
enemy.isBoss()

enemy.hp()
enemy.setCurrentHP(value)
enemy.addCurrentHP(amount)

battle.start(enemyId)
battle.bossfightStart(bossId)

battle.flee()
battle.lose()
battle.win()

map.getAvalaibleMaterials()
map.getAvalaibleBoss()
map.getAvalaibleMonster()
map.getAvalaibleShops()
map.getAvalaibleConnections()

map.getCanRest()
map.getCanRestCosts()
map.getDifficulty()

missions.getFinished()
missions.getOngoing()
missions.getNotAccepted()

missions.accept(missionId)
missions.finish(missionId)

missions.deleteFromOngoing(missionId)
missions.deleteFromFinished(missionId)

system.latest_save()
system.saveGame()
system.deleteSaveFile()

player.lastItemConsumed()
player.lastItemObtained()```

---

Now, the scripting api should be inside scripts, the file itself will be named scripting_API.js which opens all activities that user has done which is written and updated each time by main.py in a file also inside scripts/ named activities.json where all variables needed will be stored like map.getCanRest(). 

The api works by executing every single script defined in scripts.json inside of /scripts after user hits enter key (the executing logic is handled in main.py.)