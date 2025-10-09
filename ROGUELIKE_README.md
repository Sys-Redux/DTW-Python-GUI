# 🗡️ Tiny Swords Roguelike

A survival roguelike game inspired by "Don't Starve Together", built with Python/Pygame featuring the Tiny Swords asset pack. Survive in a procedurally generated world with dynamic biomes, seasons, weather, and challenging survival mechanics.

**Version:** Alpha 0.3
**Engine:** Pygame 2.6.1
**Status:** Active Development

---

## 🎮 Game Overview

Survive in a massive procedurally generated world filled with diverse biomes, resources, dangers, and mysteries. Gather resources, craft tools, build structures, manage your temperature and hunger, and fight off biome-specific enemies. Explore ancient ruins, delve into caves, and adapt to changing seasons and weather patterns. How many days can you survive?

---

## ✨ Key Features

### 🌍 Advanced World Generation
- **120x120 tile world** with six distinct biomes
- **Biome Types:**
  - 🌱 **Grassland** - Safe starting area with balanced resources
  - 🌲 **Forest** - Dense trees, mushrooms, bears and spiders
  - 🏜️ **Desert** - Cacti, scorpions, extreme heat
  - 🌊 **Swamp** - Mushroom patches, toxic enemies, wetlands
  - ❄️ **Tundra** - Ice deposits, freezing cold, yetis
  - 🌋 **Volcanic** - Lava, obsidian, fire elementals
- **Special Locations:**
  - Ancient ruins with research opportunities
  - Cave entrances leading to dungeons
  - Rich mineral deposits (Iron, Gold, Gems)

### 🌡️ Environmental Survival
- **Temperature System** (0-100°C): Affected by biomes, weather, and season
- **Weather Dynamics**: Clear, Rain, Snow, Storms
- **Four Seasons**: Spring, Summer, Autumn, Winter with gameplay effects
- **Wetness Mechanic**: Rain affects temperature and movement
- **Day/Night Cycle**: 8-second days, 6-second nights

### 👤 Comprehensive Survival Stats
- **Health** - Take damage from enemies, starvation, and cold
- **Hunger** - Decreases over time, eat food to survive
- **Sanity** - Drops at night and in dangerous situations
- **Temperature** - Maintain body heat in cold biomes and nights

### 📦 Rich Resource System
**17 Resource Types:**
- **Raw Materials**: Wood, Stone, Fiber, Coal, Berries, Meat
- **Biome-Specific**: Mushrooms, Cactus Fruit, Ice
- **Minerals**: Iron Ore, Gold Ore, Gems
- **Processed**: Iron/Gold Ingots, Cooked Meat, Rope, Charcoal

**11 Harvestable Object Types:**
- Trees (4 variants), Rocks (4 variants), Bushes (4 variants)
- Mushroom Patches, Cactus Plants, Ice Deposits
- Iron/Gold/Gem Deposits, Ancient Ruins, Cave Entrances

### 🔨 Advanced Crafting System (25+ Recipes)
**Basic Tools:**
- Axe, Pickaxe, Sword, Torch, Shovel

**Advanced Tools** (require Workbench):
- Iron Axe, Iron Pickaxe, Iron Sword

**Buildings:**
- Campfire, Workbench, Furnace, Farm Plot, Chest, Wooden Walls

**Food:**
- Cooked Meat, Mushroom Stew, Trail Mix, Healing Potion

**Materials:**
- Rope, Cloth, Iron/Gold Ingots

### ⚔️ Biome-Based Combat
**Enemy Types by Biome:**
- 🌱 Grassland: Goblins, Wolves
- 🌲 Forest: Bears, Spiders, Ents
- 🏜️ Desert: Scorpions, Sand Wraiths, Cobras
- 🌊 Swamp: Swamp Trolls, Bog Witches, Crocodiles
- ❄️ Tundra: Ice Wolves, Yetis, Frost Giants
- 🌋 Volcanic: Fire Elementals, Lava Golems, Wizard Bosses

**Difficulty Scaling:**
- Day 1: Basic enemies only
- Days 2-4: Medium difficulty enemies
- Day 5+: All enemy types including bosses

### 🏗️ Building & Base Construction
- Persistent structures in the world
- Workbench for advanced crafting
- Furnace for metal smelting
- Farm plots for agriculture
- Chests for storage
- Defensive walls

---

## 🎯 Controls

### Movement
- **W/A/S/D** or **Arrow Keys** - Move character
- **Shift** - Sprint (costs hunger)

### Actions
- **E** - Interact/Harvest nearby resources
- **Space** - Attack nearest enemy
- **Left Click** - Harvest resource at mouse position (alternative)
- **I** - Toggle Inventory
- **Tab** - Open Inventory
- **C** - Open Crafting Menu
- **B** - Enter Building Placement Mode
- **Q** - Drop equipped item
- **ESC** - Return to menu / Cancel action

### Hotbar (Quick Use)
- **1-8** - Select and use hotbar slots

### Building Mode
- **1** - Place Campfire
- **ESC** - Cancel placement
- **Left Click** - Confirm placement

---

## 🎭 Character Classes

### ⚔️ Warrior
- **Health:** 120 HP
- **Strength:** High melee damage
- **Best for:** Close combat, tanking enemies

### 🔮 Mage
- **Health:** 80 HP
- **Intelligence:** Magic potential (future abilities)
- **Best for:** Range combat, special powers

### 🏹 Archer
- **Health:** 100 HP
- **Agility:** Fast movement, ranged attacks
- **Best for:** Kiting, ranged combat

### 🛡️ Paladin
- **Health:** 110 HP
- **Resilience:** Balanced stats, support abilities
- **Best for:** Versatile gameplay, healing

---

## 💡 Survival Guide

### Getting Started (Day 1)
1. **Gather basic resources** - Look for trees, rocks, and bushes nearby
2. **Craft tools immediately:**
   - Axe (3 wood, 2 stone) for faster tree chopping
   - Pickaxe (2 wood, 3 stone) for faster mining
3. **Build a campfire** (5 wood, 3 stone) before nightfall
4. **Stay near your campfire** at night to maintain sanity and light

### Early Game (Days 2-5)
1. **Explore biomes** - Each has unique resources
2. **Craft a workbench** (12 wood, 4 stone) for advanced items
3. **Build a furnace** (15 stone, 5 coal) for metal processing
4. **Gather iron ore** and smelt into ingots
5. **Upgrade to iron tools** for better efficiency
6. **Build farm plots** for sustainable food

### Mid Game (Days 5-10)
1. **Explore special locations** - Ruins for research, caves for minerals
2. **Manage temperature** - Carry torches in cold biomes
3. **Craft healing potions** for emergencies
4. **Build defensive walls** around your base
5. **Stockpile resources** in chests
6. **Adapt to seasons** - Winter requires extra preparation

### Advanced Tips
- **Tool Efficiency:**
  - Axe = 4x faster tree harvesting
  - Pickaxe = 4x faster rock/ore mining
  - No tool = 1x speed for everything

- **Temperature Management:**
  - Cold biomes (Tundra, Mountains) require fires and warm clothing
  - Hot biomes (Desert, Volcanic) drain temperature faster
  - Night temperatures drop everywhere

- **Weather Effects:**
  - Rain makes you wet (decreases temperature faster)
  - Snow accumulates in cold biomes
  - Storms increase danger levels

- **Biome Strategy:**
  - Start in Grassland for safety
  - Forest has abundant wood
  - Desert has rare cactus fruit
  - Swamp has mushrooms for advanced recipes
  - Tundra has ice (preserves food longer)
  - Volcanic has obsidian (future upgrades)

---

## 📊 HUD Elements

### Top Left - Survival Stats
- ❤️ **Health Bar** (Red)
- 🍖 **Hunger Bar** (Orange)
- 🧠 **Sanity Bar** (Purple)
- 🌡️ **Temperature Bar** (Blue)

### Top Right - Resources
- 🪵 Wood
- 🪨 Stone
- 🫐 Berries
- 🥩 Meat
- *+ 13 more resources*

### Top Center - Time & Season
- ⏰ Current Day
- ☀️/🌙 Day/Night indicator
- 🌸 Current Season
- 🌤️ Current Weather

### Bottom Center
- 🎯 Control hints
- 💡 Interaction prompts

### Bottom Left - Hotbar
- 8 quick-access item slots
- Visual item icons
- Quantity indicators

---

## 🎯 Game Progression

### Phase 1: Survival Basics (Days 1-3)
- Master resource gathering
- Craft essential tools
- Establish base camp with campfire
- Learn combat basics

### Phase 2: Tool Advancement (Days 4-7)
- Build workbench and furnace
- Smelt iron ore into ingots
- Craft iron tools
- Explore nearby biomes

### Phase 3: Base Building (Days 8-15)
- Construct permanent base
- Add farm plots for food
- Build storage chests
- Create defensive walls

### Phase 4: Exploration (Days 15+)
- Visit all biome types
- Explore ancient ruins
- Delve into cave systems
- Fight biome-specific bosses

---

## 🏆 Achievements (Coming Soon)

- **First Night** - Survive your first night
- **Tool Master** - Craft all tool types
- **Base Builder** - Place 10+ buildings
- **Explorer** - Visit all 6 biomes
- **Treasure Hunter** - Find ancient ruins
- **Survivor** - Reach day 30
- **Legend** - Defeat all boss types

---

## 🔧 Technical Details

### System Requirements
- **OS:** Windows 10+, Linux, macOS
- **Python:** 3.8+
- **Pygame:** 2.6.1+
- **RAM:** 4GB minimum
- **Storage:** 200MB

### Game Specs
- **Resolution:** 1024x768
- **FPS Target:** 60
- **World Size:** 120x120 tiles (14,400 tiles)
- **Tile Size:** 32x32 pixels
- **Total World:** 3,840 x 3,840 pixels

### Asset Count
- 24+ sprites loaded
- 4 character variants
- 12 resource object types
- 8+ UI elements

---

## 📁 Project Structure

```
pygame/
├── roguelike_game.py           # Main game file (2000+ lines)
├── ROADMAP.md                  # Development roadmap
├── ROGUELIKE_README.md         # This file
├── assets/
│   ├── Tiny Swords (Free Pack)/
│   │   ├── Decorations/
│   │   │   ├── Trees/ (Tree1-4.png)
│   │   │   ├── Rocks/ (Rock1-4.png)
│   │   │   └── Bushes/ (Bushe1-4.png)
│   │   ├── Units/ (Character sprites)
│   │   └── Terrain/ (Tile textures)
│   ├── Free - Raven Fantasy Icons/
│   │   └── 32x32/ (2000+ icon sprites)
│   ├── warrior.png, mage.png, archer.png, paladin.png
│   └── wizard.png
└── __pycache__/
```

---

## 🚀 Running the Game

### Installation
```bash
# Install dependencies
pip install pygame

# Run the game
python roguelike_game.py
```

### First Launch
1. Start game - Main menu appears
2. Select character class (1-4)
3. World generates automatically
4. Spawn in center of Grassland biome
5. Start gathering resources immediately!

---

## 🐛 Known Issues

See [ROADMAP.md](ROADMAP.md) for complete list. Current issues:
- World generation can be slow on first launch
- Enemy pathfinding occasionally gets stuck on water
- Temperature changes could be more dramatic
- Some enemy types are placeholders (no unique sprites)

---

## 🗺️ Future Development

See [ROADMAP.md](ROADMAP.md) for the complete development plan. Upcoming features:

### Short Term
- Sound effects and music
- Class-specific abilities
- Cave dungeon system
- Advanced UI tooltips

### Medium Term
- Full farming system
- NPC merchants and quests
- Save/load functionality
- Achievement system

### Long Term
- Multiplayer co-op
- Mod support
- Magic system
- Steam release

---

## 🙏 Credits

### Development
- **Lead Developer:** Sys-Redux
- **Engine:** Pygame 2.6.1
- **Language:** Python 3.12

### Assets
- **Tiny Swords Pack** - Pixelnauts (itch.io)
- **Raven Fantasy Icons** - Clockwork Raven Studios

### Inspiration
- **Don't Starve Together** - Klei Entertainment
- **Terraria** - Re-Logic
- **Minecraft** - Mojang Studios
- **Stardew Valley** - ConcernedApe

---

## 📜 License

*To be determined - currently a learning/portfolio project*

---

## 🔗 Related Projects

**Original Battle Game** (`battlewiz.py`) - Turn-based boss battles:
- 4 character classes with unique abilities
- 4 epic boss battles
- 4 difficulty modes
- Leveling and progression system

Choose your adventure:
- `python roguelike_game.py` - **Survival roguelike (Current)**
- `python battlewiz.py` - Turn-based boss battles (Legacy)

---

**Last Updated:** October 9, 2025
**Version:** Alpha 0.3
**Repository:** github.com/Sys-Redux/DTW-Python-GUI
