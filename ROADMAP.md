# 🗺️ Tiny Swords Roguelike - Development Roadmap

## 📋 Project Overview
A survival roguelike game inspired by "Don't Starve Together", featuring environmental survival mechanics, crafting progression, and dynamic biome-based gameplay.

**Current Version:** Alpha 0.4
**Engine:** Pygame 2.6.1
**Target Platform:** Desktop (Linux/Windows/Mac)

**Latest Update:** October 9, 2025 - Phase 2 Combat & UI Enhancement Complete

---

## ✅ Phase 1: Foundation & Core Mechanics (COMPLETED)

### 🎮 Basic Game Systems
- [x] Game loop with FPS control (60 FPS)
- [x] Main menu with class selection (Warrior, Mage, Archer, Paladin)
- [x] Camera system following player
- [x] Day/night cycle (8s day, 6s night)
- [x] Tile-based world generation (120x120 tiles)
- [x] Basic player movement (WASD) with sprint (Shift)
- [x] Inventory system (8-slot hotbar + storage)
- [x] Death and respawn mechanics

### 👤 Player Systems
- [x] Health, hunger, and sanity stats
- [x] Temperature survival mechanic (0-100 scale)
- [x] Tool durability system
- [x] Class-based starting stats
- [x] Research points system
- [x] Wetness status effects

### 🌍 World Generation
- [x] 6 distinct biomes (Grassland, Forest, Desert, Swamp, Tundra, Volcanic)
- [x] Biome-based terrain tiles (Grass, Sand, Stone, Water, Lava, Snow, Swamp)
- [x] Dynamic weather system (Clear, Rain, Snow, Storm)
- [x] Seasonal progression (Spring, Summer, Autumn, Winter)
- [x] Special locations (Ancient Ruins, Cave Entrances)

### 📦 Resource System
- [x] 17 resource types (12 raw + 5 processed)
- [x] 9 harvestable object types (Trees, Rocks, Bushes, Mushrooms, Cacti, Ice, Iron, Gold, Gems)
- [x] Biome-specific resource distribution
- [x] Guaranteed starting resources around spawn
- [x] Resource gathering with tool efficiency
- [x] Resource regrowth system

### 🔨 Crafting System
- [x] 25+ recipes with tier progression
- [x] Basic tools (Axe, Pickaxe, Sword, Torch, Shovel)
- [x] Advanced tools (Iron variants requiring workbench)
- [x] Building structures (Campfire, Workbench, Furnace, Farm Plot, Chest, Walls)
- [x] Material processing (Iron/Gold ingots, Rope, Cloth)
- [x] Food recipes (Cooked Meat, Mushroom Stew, Trail Mix, Healing Potion)
- [x] Workbench and furnace requirement system

### ⚔️ Combat System
- [x] Basic melee combat (Space key)
- [x] Tool-based damage modifiers
- [x] Enemy AI with player tracking
- [x] Loot drop system
- [x] Biome-specific enemy spawning

### 🎨 Asset Integration
- [x] Tiny Swords asset pack integration
- [x] Character sprites (4 variants)
- [x] Environment sprites (Trees, Rocks, Bushes - 4 variants each)
- [x] Fantasy icon pack for resources
- [x] Sprite fallback system

---

## ✅ Phase 2: Combat & UI Enhancement (COMPLETED - Oct 9, 2025)

### 🎯 Combat Enhancement
- [x] **Enemy Health Bars** - Visual HP bars above all enemies (current/max)
- [x] **Floating Damage Numbers** - Animated damage text for player attacks (red), enemy attacks (yellow), resource gathering (green)
- [x] **Particle System** - Visual feedback with biome-appropriate colors:
  - Wood harvesting: Brown particles
  - Stone mining: Gray particles
  - Plant gathering: Green particles
  - Ore extraction: Gold sparkles
  - Combat hits: Red/orange explosions
- [x] **Class-Specific Abilities** - Unique F-key abilities with cooldowns:
  - **Warrior**: Whirlwind Attack (3-tile AOE, 30 damage, 10s CD)
  - **Mage**: Arcane Blast (8-tile range, 50 damage to nearest enemy, 12s CD)
  - **Archer**: Volley (Hit 3 nearest enemies for 25 damage each, 8s CD)
  - **Paladin**: Divine Shield (Heal 40 HP + 3s invulnerability, 15s CD)
- [x] **Ability UI Indicator** - Visual cooldown tracker with active state glow
- [x] **Class Balance** - Adjusted starting stats:
  - Warrior: 120 HP (tank)
  - Mage: 80 HP (glass cannon)
  - Archer: 90 HP, 9.0 speed (mobile)
  - Paladin: 110 HP (balanced support)

### 🎨 UI/UX Improvements
- [x] **Tooltip System** - Hover tooltips in crafting menu showing:
  - Item name and description
  - Required resources (color-coded: green=available, red=insufficient)
  - Current inventory amounts vs needed amounts
  - Smart positioning (stays on screen)
- [x] **Harvest Progress Bar** - Real-time visual feedback when gathering:
  - Shows remaining object health percentage
  - Color gradient (green→yellow→red) based on progress
  - Positioned above resource objects
  - Auto-clears when harvesting complete
- [x] **Visual Combat Feedback** - Hit effects for all combat interactions
- [x] **Updated Controls** - Added F-key ability system to UI hints

### 📊 Technical Improvements
- [x] Visual effects system with delta-time updates
- [x] Particle physics with gravity simulation
- [x] Alpha-based fade animations for damage numbers
- [x] Game state passing for visual effect creation
- [x] Enemy-to-player damage now creates visual feedback
- [x] Resource gathering tracked for progress display

---

## 🚧 Phase 3: World Content & Systems (NEXT UP)

### 🎯 High Priority

#### World Interaction
- [ ] Implement cave system (dungeon generation)
- [ ] Add Ancient Ruin interactions (research/lore)
- [ ] Create fishing mechanics for water tiles
- [ ] Add animal wildlife (neutral creatures)
- [ ] Implement trap placement system
- [ ] Add treasure chests in special locations
- [ ] Create world events (meteor showers, earthquakes)

#### Ranged Combat
- [ ] Implement projectile system for Archer
- [ ] Add spell projectiles for Mage
- [ ] Create weapon variety (bows, staffs, spears)
- [ ] Add ammo/mana resource management
- [ ] Implement trajectory-based aiming

#### Boss Mechanics
- [ ] Create boss enemy with attack phases
- [ ] Add special boss abilities
- [ ] Implement boss spawn conditions
- [ ] Create unique boss loot tables
- [ ] Add boss health bar UI

### 🔧 Medium Priority

#### Farming System
- [ ] Implement seed planting mechanics
- [ ] Add crop growth stages
- [ ] Create seasonal growth bonuses
- [ ] Add irrigation system
- [ ] Implement fertilizer crafting
- [ ] Add crop disease system
- [ ] Create advanced farm plots

#### Building Enhancement
- [ ] Add building upgrade system
- [ ] Implement storage chest functionality
- [ ] Create defensive structures (walls, towers, traps)
- [ ] Add building health/durability
- [ ] Implement lighting system for buildings
- [ ] Create connected wall rendering
- [ ] Add door and gate mechanics

#### Survival Mechanics
- [ ] Balance temperature effects per biome
- [ ] Add clothing/armor system for temperature
- [ ] Implement food spoilage over time
- [ ] Create poison/disease mechanics
- [ ] Add sleep/rest system
- [ ] Implement thirst mechanic
- [ ] Create weather shelter requirements

#### Enemy AI & Difficulty
- [ ] Implement difficulty scaling over days
- [ ] Add enemy patrol routes
- [ ] Create pack behavior for wolves
- [ ] Implement boss spawn conditions
- [ ] Add rare elite enemies with unique loot
- [ ] Create siege events (waves of enemies)
- [ ] Balance enemy damage and health

---

## 🎯 Phase 3: Advanced Features (PLANNED)

### 🏰 Base Building
- [ ] Create multi-tile structures
- [ ] Add electricity/power system
- [ ] Implement pipe network for water
- [ ] Add automated machines (auto-miners, auto-harvesters)
- [ ] Create NPC companion housing
- [ ] Implement base defense mechanics
- [ ] Add teleportation network between bases

### 🤝 NPC & Social Systems
- [ ] Create wandering NPC merchants
- [ ] Add quest system with objectives
- [ ] Implement NPC companion recruitment
- [ ] Create trading post buildings
- [ ] Add reputation system with factions
- [ ] Implement village building mechanics
- [ ] Create NPC dialogue system

### 🌟 Advanced Progression
- [ ] Implement skill tree system
- [ ] Add achievement system
- [ ] Create research technology tree
- [ ] Implement magic system (for Mage class)
- [ ] Add enchanting/imbuing system
- [ ] Create legendary item crafting
- [ ] Implement prestige/rebirth system

### 🎲 Content Expansion
- [ ] Add 3 more biomes (Jungle, Mountain, Crystal Caves)
- [ ] Create seasonal events (festivals, migrations)
- [ ] Add dungeon types with unique enemies
- [ ] Implement boss arenas
- [ ] Create artifact collection system
- [ ] Add mount/pet system
- [ ] Implement vehicle crafting

---

## 🐛 Phase 4: Bug Fixes & Optimization (ONGOING)

### Known Issues
- [ ] World generation hangs on large worlds (investigate performance)
- [ ] Enemy pathfinding can get stuck on water
- [ ] Resource regrowth not visible to player
- [ ] Temperature changes feel too subtle
- [ ] Crafting UI doesn't show required buildings clearly
- [ ] Night lighting could be more dramatic
- [ ] Enemy spawning can overwhelm player at night

### Performance Optimization
- [ ] Optimize rendering (cull off-screen objects)
- [ ] Implement chunk-based world loading
- [ ] Add object pooling for enemies/projectiles
- [ ] Optimize collision detection
- [ ] Reduce memory usage for large worlds
- [ ] Profile and optimize hotspots

### Code Quality
- [ ] Add unit tests for core systems
- [ ] Implement save/load system
- [ ] Add configuration file for game balance
- [ ] Refactor large classes (GameState, World)
- [ ] Add debug console for testing
- [ ] Create mod support framework
- [ ] Improve error handling and logging

---

## 📊 Current Game Statistics

### Content Count
- **Biomes:** 6 types
- **Resources:** 17 types (12 raw + 5 processed)
- **Items:** 35+ types
- **Recipes:** 25+
- **Enemies:** 15+ types (biome-specific)
- **Buildings:** 6 types
- **World Objects:** 11 types

### Technical Specs
- **World Size:** 120x120 tiles
- **Tile Size:** 32 pixels
- **Screen Resolution:** 1024x768
- **Target FPS:** 60
- **Asset Count:** 24+ sprites loaded

---

## 🎯 Milestone Goals

### Short Term (1-2 weeks)
1. Complete combat enhancement with class abilities
2. Add sound effects and basic music
3. Implement cave dungeon system
4. Polish UI with tooltips and feedback
5. Balance survival mechanics and difficulty

### Medium Term (1 month)
1. Full farming system implementation
2. NPC merchant and quest system
3. Advanced base building features
4. Achievement and progression tracking
5. Save/load functionality

### Long Term (2-3 months)
1. Multiplayer co-op support (local/network)
2. Mod support and custom content
3. Complete skill and magic systems
4. Content expansion (new biomes, enemies, items)
5. Steam release preparation

---

## 🔄 Version History

### v0.4 (October 9, 2025) - CURRENT
**Major Update: Combat & UI Enhancement**
- ✨ **Class Abilities System** - F-key special abilities for all 4 classes with unique mechanics
- 🎯 **Visual Combat Feedback** - Floating damage numbers, particle effects, and hit animations
- 💚 **Enemy Health Bars** - Real-time HP display above all enemies
- 📊 **Harvest Progress Indicator** - Visual progress bar showing resource gathering status
- 💡 **Tooltip System** - Hover tooltips in crafting menu with detailed item info
- 🎨 **Particle System** - Dynamic particle effects for combat and resource gathering
- ⚖️ **Class Balancing** - Adjusted starting HP and speed for each class
- 🎮 **UI Polish** - Ability cooldown indicator, updated controls, visual improvements

**Technical Changes:**
- Added visual effects system (damage numbers, particles)
- Implemented ability cooldown/duration tracking
- Enhanced Player class with use_ability() method
- Updated Enemy.attack() to create visual feedback
- Added game state parameter to update_enemies()
- Created get_item_description() for tooltip content
- Added harvesting_target tracking for progress display

### v0.3
- Added asset integration (Tiny Swords + Fantasy Icons)
- Implemented keyboard harvesting (E key)
- Fixed sprite display issues
- Enhanced resource generation with guaranteed starting resources
- Improved crafting system with 25+ recipes

### v0.2
- Added biome system (6 types)
- Implemented seasons and weather
- Created temperature survival mechanic
- Added advanced crafting with tier progression
- Implemented special locations (ruins, caves)

### v0.1
- Basic game loop and player movement
- Simple inventory and crafting
- Day/night cycle
- Basic enemy spawning
- Resource gathering with trees, rocks, bushes

---

## 🤝 Contributing Guidelines

### Development Priorities
1. **User Experience:** Features that improve gameplay feel
2. **Content:** New biomes, items, enemies
3. **Polish:** Visual/audio feedback, UI improvements
4. **Balance:** Difficulty tuning, resource economy
5. **Optimization:** Performance improvements

### Code Standards
- Follow existing code structure and naming conventions
- Comment complex game logic
- Test new features before committing
- Update this roadmap when completing features
- Document new systems in separate markdown files

---

## 📝 Notes

### Design Philosophy
- **Engaging Progression:** Always give player something to work toward
- **Environmental Challenge:** Weather, temperature, and biomes matter
- **Meaningful Choices:** Tools, resources, and timing decisions impact success
- **Exploration Reward:** Hidden locations and rare resources encourage exploration
- **Fair Difficulty:** Challenging but learnable, scales with player progress

### Inspiration Sources
- Don't Starve Together (survival mechanics, art style)
- Terraria (crafting progression, biome diversity)
- Minecraft (resource gathering, building freedom)
- Stardew Valley (farming mechanics, progression)

### Future Vision
Create a deeply engaging survival experience where every game session feels unique due to procedural generation, with enough depth in crafting and building to support long-term gameplay, while maintaining the simple charm of pixel art aesthetics.

---

**Last Updated:** October 9, 2025
**Maintainer:** Sys-Redux
**License:** Project-specific (define as needed)
