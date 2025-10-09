# Tiny Swords Roguelike

A survival roguelike game inspired by "Don't Starve Together", built using Python/Pygame and the Tiny Swords asset pack.

## Game Overview

Survive in a procedurally generated world filled with resources, dangers, and mysteries. Gather resources, craft tools, build structures, and fight off enemies that emerge at night. How many days can you survive?

## Features

### 🌍 Procedurally Generated World
- 100x100 tile world with varied terrain
- Lakes, forests, rocky areas, and resource-rich biomes
- Trees (wood), rocks (stone), and bushes (berries)

### 👤 Survival Mechanics
- **Health**: Damaged by enemies and starvation
- **Hunger**: Decreases over time, eat food to survive
- **Sanity**: Drops at night, low sanity affects gameplay
- **Death**: Game over when health reaches zero

### 🌙 Day/Night Cycle
- Dynamic time progression (8 sec day / 6 sec night)
- Screen darkens at night
- Enemies spawn during nighttime
- Campfires provide light and safety

### ⚔️ Combat System
- **Enemies spawn at night:**
  - **Goblins** (Day 1+): Basic enemies, 30 HP, 5 damage
  - **Wolves** (Day 2+): Faster, 40 HP, 8 damage
  - **Evil Wizards** (Day 5+): Boss enemies, 150 HP, 15 damage, ranged attacks
- Press **SPACE** to attack nearby enemies
- Equip a **Sword** for 2x damage
- Enemies drop meat when defeated

### 🔨 Crafting System
- **Axe** (3 wood, 2 stone): Chop trees faster
- **Pickaxe** (2 wood, 3 stone): Mine rocks faster
- **Sword** (2 wood, 4 stone): Deal more damage to enemies
- **Torch** (2 wood): Personal light source
- **Campfire** (5 wood, 3 stone): Large light radius, prevents sanity loss
- **Wooden Wall** (4 wood): Basic defensive structure

### 🏗️ Building System
- Press **B** to enter building mode
- Place campfires for light and warmth
- Build wooden walls for defense
- Buildings persist in the world

### 📦 Resource Gathering
- **Click on resources** to gather:
  - Trees → Wood (faster with axe)
  - Rocks → Stone (faster with pickaxe)
  - Bushes → Berries (no tool required)
- Resources respawn over time

## Controls

### Movement
- **W/↑** - Move Up
- **S/↓** - Move Down
- **A/←** - Move Left
- **D/→** - Move Right

### Actions
- **Left Click** - Gather resources / Interact
- **SPACE** - Attack nearest enemy
- **I** - Open/Close Inventory
- **C** - Open/Close Crafting Menu
- **B** - Enter Building Placement Mode
- **ESC** - Return to menu / Cancel

### Building Mode
- **1** - Select Campfire
- **2** - Select Wooden Wall
- **Left Click** - Place building
- **ESC** - Cancel placement

## Character Classes

Choose your survivor at game start:

1. **Warrior** - High health, strong in melee combat
2. **Mage** - Magic abilities, lower health but special powers
3. **Archer** - Balanced stats, ranged capabilities
4. **Paladin** - Support class with healing abilities

## Survival Tips

1. **Gather resources during the day** - enemies spawn at night
2. **Craft an axe and pickaxe early** - essential for efficient gathering
3. **Build campfires before nightfall** - they provide light and restore sanity
4. **Keep your hunger above 50%** - starvation damages health
5. **Craft a sword** - base attacks deal 10 damage, swords deal 20
6. **Build walls around your base** - creates safe zones
7. **Watch your sanity at night** - stay near campfires
8. **Don't venture too far** - easy to get lost in the procedural world

## Game Progression

- **Day 1**: Only goblins spawn, learn the basics
- **Day 2-4**: Wolves start appearing, more dangerous
- **Day 5+**: Evil Wizard bosses can spawn, bring rewards
- Each day the challenges increase

## HUD Elements

**Top Left Panel:**
- Health bar (red)
- Hunger bar (orange)
- Sanity bar (purple)
- Current day
- Time of day (DAY/NIGHT)

**Top Right Panel:**
- Wood count
- Stone count
- Berries count
- Meat count

**Bottom Center:**
- Control hints

## Technical Details

- **Engine**: Pygame 2.6.1
- **Resolution**: 1024x768
- **FPS**: 60
- **World Size**: 100x100 tiles (3200x3200 pixels)
- **Tile Size**: 32x32 pixels

## File Structure

```
pygame/
├── roguelike_game.py      # Main roguelike game (NEW!)
├── battlewiz.py           # Original battle game
├── DTW.py                 # Battle game logic
├── assets/                # Game assets
│   ├── warrior.png
│   ├── mage.png
│   ├── archer.png
│   ├── paladin.png
│   ├── wizard.png
│   ├── tree1.png, tree2.png
│   ├── rock1.png, rock2.png
│   ├── bush1.png, bush2.png
│   └── Tiny Swords (Free Pack)/
└── ROGUELIKE_README.md    # This file
```

## Running the Game

```bash
python roguelike_game.py
```

## Future Enhancements

Potential additions:
- Save/load game functionality
- More enemy types and bosses
- Advanced crafting (armor, potions, traps)
- Farming system
- Seasons and weather
- Multiplayer support
- Dungeon generation
- Quest system
- Achievements

## Credits

- **Game Engine**: Pygame
- **Assets**: Tiny Swords (Free Pack)
- **Inspired by**: Don't Starve Together, Terraria, Minecraft
- **Developer**: Created as an expansion of the Defeat the Wizard battle game

---

**Original Battle Game** (battlewiz.py) is still available with:
- 4 character classes with unique abilities
- 4 boss battles (Evil Wizard, Fire Dragon, Ice Titan, Shadow Assassin)
- 4 difficulty modes
- Leveling system
- Turn-based combat

Choose your adventure:
- `python roguelike_game.py` - Survival roguelike
- `python battlewiz.py` - Turn-based boss battles
