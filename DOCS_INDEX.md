# Our Legacy - Documentation Index

Welcome to Our Legacy! This is your complete guide to understanding, playing, and modding the game.

---

## 📚 Documentation Files

### 1. **README.md** - Start Here!
**Quick Overview of the Game**
- Game features and character classes
- Installation and quick start
- File structure overview
- Mod system introduction

👉 **For**: Players new to the game, people curious about what Our Legacy is

---

### 2. **documentation.md** - Complete Reference (937 lines)
**Comprehensive Guide to All Game Systems**
- All 11 data files explained with full parameter lists
- Complete examples for each file type
- Mod system documentation
- How mods are loaded and merged
- Best practices for development

**Sections**:
- ✅ Classes.json - Character definitions
- ✅ Items.json - Equipment and consumables
- ✅ Enemies.json - Regular encounters
- ✅ Bosses.json - Boss encounters with phases
- ✅ Areas.json - World locations
- ✅ Missions.json - Quest system
- ✅ Dialogues.json - Text content
- ✅ Dungeons.json - Procedural dungeons
- ✅ Crafting.json - Alchemy recipes
- ✅ Spells.json - Magic system
- ✅ Companions.json - Party members
- ✅ Mod system explanation with examples

👉 **For**: Modders, developers, anyone who wants to understand the complete system

---

### 3. **MOD_CREATION_GUIDE.md** - Quick Start (400+ lines)
**Fast Reference for Creating Mods**
- Step-by-step mod creation
- Copy-paste ready templates for:
  - New bosses
  - New dungeons
  - New items
  - New areas
  - New enemies
  - New classes
  - New recipes
- Parameter quick reference
- Common issues and fixes

👉 **For**: Modders who want to create content quickly

---

## 🎮 Getting Started

### Players
1. Read [README.md](README.md) for game overview
2. Run `python3 main.py`
3. Create character and explore!

### Modders - Quick Start
1. Read [MOD_CREATION_GUIDE.md](MOD_CREATION_GUIDE.md) - 5 minute overview
2. Follow "Quick Start: Create Your First Mod"
3. Copy a template for your content type
4. Test and iterate!

### Modders - Deep Dive
1. Read [MOD_CREATION_GUIDE.md](MOD_CREATION_GUIDE.md) for basics
2. Study [documentation.md](documentation.md) for complete reference
3. Review examples in each section
4. Check `mods/The Ether/` for complete mod example

### Developers
1. Review [documentation.md](documentation.md) for complete data structure
2. Check [README.md](README.md) file structure section
3. Study mod loading code in `main.py` (lines 1195-1257)
4. Review existing mods for patterns

---

## 📋 Data Files Reference

| File | Purpose | Documented In | Best For |
|------|---------|---------------|---------| 
| **classes.json** | Character classes | documentation.md | Understanding character progression |
| **items.json** | Equipment & consumables | documentation.md | Creating new gear |
| **enemies.json** | Regular encounters | documentation.md | Creating new enemies |
| **bosses.json** | Boss battles | documentation.md | Creating challenging encounters |
| **areas.json** | World locations | documentation.md | Adding new locations |
| **missions.json** | Quests | documentation.md | Creating quest content |
| **dialogues.json** | Text dialogue | documentation.md | Adding story text |
| **dungeons.json** | Procedural dungeons | documentation.md | Creating complex dungeons |
| **crafting.json** | Alchemy system | documentation.md | Adding recipes |
| **spells.json** | Magic abilities | documentation.md | Creating spells |
| **companions.json** | Party members | documentation.md | Adding companions |

---

## 🎯 Common Tasks

### I want to...

**Understand how the game works**
→ Read [README.md](README.md)

**Create my first mod**
→ Follow [MOD_CREATION_GUIDE.md](MOD_CREATION_GUIDE.md) Quick Start

**Add a new boss**
→ See boss template in [MOD_CREATION_GUIDE.md](MOD_CREATION_GUIDE.md)

**Add a new dungeon with challenges**
→ See dungeon template in [MOD_CREATION_GUIDE.md](MOD_CREATION_GUIDE.md)

**Understand all available parameters**
→ Read [documentation.md](documentation.md) parameter sections

**See a complete example**
→ Check `mods/The Ether/` for Ethereal Spire dungeon example

**Learn about the mod system**
→ See "Mod System" section in [documentation.md](documentation.md)

**Understand how mods are loaded**
→ See "How Mods Load" in [README.md](README.md) or [documentation.md](documentation.md)

**Troubleshoot my mod**
→ Check "Testing Your Mod" and "Common Issues" in [MOD_CREATION_GUIDE.md](MOD_CREATION_GUIDE.md)

---

## 🔗 Quick Links

### Documentation
- 📖 [Complete Reference](documentation.md) - 937 lines of detailed info
- ⚡ [Quick Guide](MOD_CREATION_GUIDE.md) - Fast templates and reference
- 📱 [Game Overview](README.md) - Features and structure

### Main Game
- 🎮 [Main Game](main.py) - Core game engine
- 📊 [Base Data](data/) - All game data files
- 🎯 [Example Content](mods/The%20Ether/) - Study this mod!

---

## 📊 Documentation Statistics

| Aspect | Coverage |
|--------|----------|
| Data Files | 11/11 files documented ✅ |
| Parameters | All parameters listed ✅ |
| Examples | Examples for each file type ✅ |
| Templates | 7 complete templates ✅ |
| Mod System | Fully explained ✅ |
| Best Practices | Complete guide ✅ |
| Troubleshooting | Common issues covered ✅ |

---

## 🚀 Next Steps

1. **Start with your interest level**:
   - Curious? → [README.md](README.md)
   - Want to create? → [MOD_CREATION_GUIDE.md](MOD_CREATION_GUIDE.md)
   - Need complete info? → [documentation.md](documentation.md)

2. **Choose your action**:
   - Play the game
   - Create a mod
   - Study the system
   - Contribute to community

3. **Get help**:
   - Check the relevant doc section
   - Review example mods
   - Test in-game
   - Iterate and improve

---

## 📝 File Manifest

```
Our_Legacy/
├── README.md                      ← Game overview, start here!
├── documentation.md               ← Complete reference (937 lines)
├── MOD_CREATION_GUIDE.md          ← Quick start templates
├── DOCUMENTATION_UPDATES.md       ← What was updated
├── main.py                        ← Game engine
├── data/                          ← Base game content
├── mods/                          ← Player mods
│   └── The Ether/                ← Example mod
└── ...
```

---

## 💡 Pro Tips

1. **Read in order**: README → MOD_CREATION_GUIDE → documentation.md
2. **Use templates**: Copy-paste from MOD_CREATION_GUIDE.md for quick start
3. **Study examples**: Check "The Ether" mod in mods/ folder
4. **Validate JSON**: Always check syntax before testing
5. **Test locally**: Create character to see your mod content
6. **Iterate**: Update and improve based on gameplay

---

## 🎓 Learning Path

**Beginner**: README.md → MOD_CREATION_GUIDE.md → Create first mod
**Intermediate**: MOD_CREATION_GUIDE.md → documentation.md → Create complex mod
**Advanced**: documentation.md → Study existing mods → Contribute to community

---

## 📞 Support

- **Questions about gameplay?** → See README.md
- **Need mod creation help?** → Check MOD_CREATION_GUIDE.md
- **Need parameter details?** → Search documentation.md
- **Can't find something?** → Check DOCUMENTATION_UPDATES.md

---

**Ready to dive in? Start with [README.md](README.md)!**

**Want to create? Go to [MOD_CREATION_GUIDE.md](MOD_CREATION_GUIDE.md)!**

**Need complete details? Read [documentation.md](documentation.md)!**
