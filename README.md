# Pokemon-Style Battle Game

A turn-based RPG battle game inspired by Pokemon, featuring customizable heroes fighting an Evil Wizard!

## 🎨 Custom Sprites Support!

**NEW:** You can now use your own sprite images! The game supports custom character sprites and backgrounds.

- Place PNG images in the `assets/` folder
- See `assets/QUICK_START.md` for a 5-minute setup guide
- See `assets/ASSET_GUIDE.md` for detailed instructions and free asset sources
- Game automatically uses custom sprites when available, falls back to drawn graphics if not

**Recommended free asset sources:**
- **Kenney.nl** - High quality, CC0 licensed assets
- **OpenGameArt.org** - Public domain game art
- **itch.io** - Free game asset section

## Features

### Character Creation
- **Choose your class**: Select from 4 unique hero classes
  - **Warrior**: High HP (140), balanced attack (25), rage-based abilities
  - **Mage**: Low HP (100), high attack (35), magic-focused
  - **Archer**: Medium HP (120), ranged combat (20), agility-based
  - **Paladin**: Highest HP (160), holy powers (20), tank-style
- **Name your hero**: Enter a custom name (up to 15 characters)
- **Preview sprites**: See your character before starting the battle

### Visual Character Sprites
Each character has a unique, hand-drawn sprite:
- **Warrior**: Sword and shield with steel armor
- **Mage**: Purple robes with magical staff and wizard hat
- **Archer**: Green outfit with bow and quiver of arrows
- **Paladin**: Holy armor with cross emblem and blessed sword
- **Evil Wizard**: Dark robes with glowing red eyes and dark magic staff

### Pokemon-Style Elements
- **Turn-based combat**: Player actions, then enemy turn
- **Visual battle scene**: Characters positioned like Pokemon (hero front-left, enemy back-right)
- **Health bars**: Color-coded HP bars (green/yellow/red) with current/max display
- **Info boxes**: Pokemon-style character information displays
- **Message log**: Battle messages appear in a scrolling message box
- **Limited resources**: Heal potions (3 uses) like Pokemon items

### Battle System
- **Attack**: Basic attack that builds rage for Warriors
- **Special Abilities** (Warrior-specific):
  - **Rage Strike** (Costs 3 rage): Deal 2.5x damage with a devastating blow
  - **Shield Wall**: Reduce incoming damage by 50% for the next attack
  - Other classes: Coming soon!
- **Heal**: Restore 30 HP (limited to 3 uses per battle)

### Visual Effects
- **Damage numbers**: Floating damage/heal numbers appear above characters
- **Screen shake**: Impact effects when attacks land
- **Smooth animations**: Visual feedback for all actions
- **Color-coded bars**: Health and rage bars change colors based on status
- **Hover effects**: Buttons highlight when you hover over them

### Game States
- **Character Creation**: Choose your hero before battle
- **Player Turn**: Choose your action
- **Enemy Turn**: Wizard regenerates and attacks
- **Victory**: Defeat the wizard to win!
- **Game Over**: Get defeated and see the game over screen

## How to Play

1. **Run the game**: `python battlewiz.py`
2. **Create your character**:
   - Click on a class card to select it
   - Click the name input box and type your hero's name
   - Click "START BATTLE!" when ready
3. **Battle controls** - Click buttons to perform actions:
   - **ATTACK**: Deal damage (Warriors build rage)
   - **SPECIAL**: Open special abilities menu
   - **HEAL (3)**: Use a healing potion
4. **Strategy tips**:
   - Warriors: Build rage with attacks to use Rage Strike
   - Warriors: Use Shield Wall before big enemy attacks
   - Save heals for critical moments
   - Watch the message log for combat details
   - Different classes have different HP and attack values

## Controls
- Mouse-only control
- Click buttons to perform actions
- Click special abilities in the menu
- Type to enter your character name
- Close window to exit

## Requirements
- Python 3.x
- pygame

Install pygame: `pip install pygame`

## Character Stats

### Hero Classes

#### Warrior
- Health: 140 HP
- Attack Power: 25
- Special: Rage system (max 5 stacks)
- Abilities: Rage Strike, Shield Wall

#### Mage
- Health: 100 HP
- Attack Power: 35
- Special: Magic-based (coming soon)

#### Archer
- Health: 120 HP
- Attack Power: 20
- Special: Agility-based (coming soon)

#### Paladin
- Health: 160 HP
- Attack Power: 20
- Special: Holy powers (coming soon)

### Evil Wizard
- Health: 150 HP
- Attack Power: 15
- Special: Regenerates 5 HP per turn

## Future Enhancements Ideas
- Special abilities for Mage, Archer, and Paladin
- Multiple enemy types
- Experience and leveling system
- More special abilities
- Sound effects and music
- Battle animations with sprite movement
- Status effects (poison, burn, etc.)
- Item inventory system
- Multiple battles/campaign mode
