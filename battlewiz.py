import pygame
import os
from DTW import Warrior, Mage, Archer, Paladin, EvilWizard, FireDragon, IceTitan, ShadowAssassin

class VisualBattleGame:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((800, 600))
        pygame.display.set_caption("Battle the Bosses!")
        self.clock = pygame.time.Clock()

        # Game logic - will be set after character creation
        self.player = None
        self.wizard = None  # Will be set after boss selection
        self.selected_boss_type = None
        self.selected_difficulty = 1.0

        # Load sprite assets (if available)
        self.load_assets()

        # Game state
        self.game_state = "character_creation"  # "character_creation", "boss_selection", "difficulty_selection", "player_turn", "enemy_turn", "game_over", "victory", "special_menu"
        self.messages = []
        self.message_timer = 0
        self.waiting_for_next_turn = False

        # Character creation state
        self.selected_class = None
        self.player_name = ""
        self.name_active = False

        # Special ability menu state
        self.special_menu_active = False
        self.special_buttons = {}

        # Main menu state
        self.main_menu_active = False
        self.main_menu_buttons = {}

        # Animation state
        self.damage_numbers = []  # List of (x, y, text, timer) tuples
        self.shake_offset = [0, 0]
        self.shake_timer = 0
        self.particles = []  # Battle particles for visual effects

        # Fonts
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)
        self.message_font = pygame.font.Font(None, 28)
        self.title_font = pygame.font.Font(None, 72)

        # Pokemon-style positions
        # Hero: Front-left (lower left corner) - moved down and right to be clearly visible
        self.hero_pos = (200, 450)
        # Wizard: Center position, just above action buttons for visibility
        self.wizard_pos = (450, 420)

        # Buttons - arranged in 2x2 grid at the bottom of the screen
        self.buttons = {
            'attack': pygame.Rect(270, 540, 120, 50),
            'special': pygame.Rect(400, 540, 120, 50),
            'heal': pygame.Rect(270, 480, 120, 50),
            'menu': pygame.Rect(400, 480, 120, 50),
        }

        # Character creation buttons - positioned in a 2x2 grid
        self.class_buttons = {
            'warrior': pygame.Rect(75, 180, 140, 200),
            'mage': pygame.Rect(235, 180, 140, 200),
            'archer': pygame.Rect(395, 180, 140, 200),
            'paladin': pygame.Rect(555, 180, 140, 200),
        }
        self.start_button = pygame.Rect(300, 510, 200, 50)

    def load_assets(self):
        """Load sprite images if available, otherwise use drawn sprites"""
        self.sprites = {
            'warrior': None,
            'mage': None,
            'archer': None,
            'paladin': None,
            'wizard': None,
            'background': None
        }

        # Decorations
        self.decorations = {
            'tree1': None,
            'tree2': None,
            'rock1': None,
            'rock2': None,
            'bush1': None,
            'bush2': None
        }

        # Animation tracking
        self.sprite_frames = {}  # Store individual frames
        self.current_frame = 0
        self.frame_counter = 0
        self.frame_speed = 8  # Frames to wait before changing sprite frame

        # Try to load sprites from assets folder
        asset_dir = 'assets'
        if os.path.exists(asset_dir):
            sprite_files = {
                'warrior': 'warrior.png',
                'mage': 'mage.png',
                'archer': 'archer.png',
                'paladin': 'paladin.png',
                'wizard': 'wizard.png',
                'background': 'battle_bg.png'
            }

            for key, filename in sprite_files.items():
                filepath = os.path.join(asset_dir, filename)
                if os.path.exists(filepath):
                    try:
                        img = pygame.image.load(filepath).convert_alpha()

                        # Check if it's a sprite sheet (for characters)
                        if key != 'background':
                            # Extract frames from sprite sheet
                            frames = self.extract_sprite_frames(img, key)
                            if frames:
                                self.sprite_frames[key] = frames
                                self.sprites[key] = frames[0]  # Use first frame as default
                                print(f"✓ Loaded {filename} ({len(frames)} frames)")
                            else:
                                self.sprites[key] = img
                                print(f"✓ Loaded {filename}")
                        else:
                            self.sprites[key] = img
                            print(f"✓ Loaded {filename}")
                    except Exception as e:
                        print(f"✗ Failed to load {filename}: {e}")
                        self.sprites[key] = None

            # Load decorations
            decoration_files = {
                'tree1': 'tree1.png',
                'tree2': 'tree2.png',
                'rock1': 'rock1.png',
                'rock2': 'rock2.png',
                'bush1': 'bush1.png',
                'bush2': 'bush2.png',
                'tower': 'tower.png',
                'house1': 'house1.png',
                'house2': 'house2.png',
                'house3': 'house3.png'
            }

            for key, filename in decoration_files.items():
                filepath = os.path.join(asset_dir, filename)
                if os.path.exists(filepath):
                    try:
                        img = pygame.image.load(filepath).convert_alpha()
                        self.decorations[key] = img
                        print(f"✓ Loaded decoration {filename}")
                    except Exception as e:
                        print(f"✗ Failed to load decoration {filename}: {e}")

        # Print instructions if no assets found
        if all(sprite is None for sprite in self.sprites.values()):
            print("\n" + "="*60)
            print("💡 NO CUSTOM SPRITES FOUND - Using drawn sprites")
            print("="*60)
            print("To use custom sprites, create an 'assets' folder and add:")
            print("  - warrior.png (recommended: 100x100px)")
            print("  - mage.png (recommended: 100x100px)")
            print("  - archer.png (recommended: 100x100px)")
            print("  - paladin.png (recommended: 100x100px)")
            print("  - wizard.png (recommended: 100x100px)")
            print("  - battle_bg.png (optional: 800x600px)")
            print("\n🎨 Free asset sources:")
            print("  • opengameart.org")
            print("  • kenney.nl")
            print("  • itch.io (free section)")
            print("  • craftpix.net (free section)")
            print("="*60 + "\n")

    def extract_sprite_frames(self, sprite_sheet, char_type):
        """Extract individual frames from a sprite sheet"""
        try:
            width, height = sprite_sheet.get_size()

            # Tiny Swords sprites are 192x192 per frame
            frame_size = 192

            # Calculate number of frames
            num_frames = width // frame_size

            if num_frames == 0:
                return None

            frames = []
            for i in range(num_frames):
                # Extract frame
                frame = sprite_sheet.subsurface((i * frame_size, 0, frame_size, frame_size))
                frames.append(frame)

            return frames
        except:
            return None

    def draw_warrior_sprite(self, x, y, size):
        """Draw a warrior with sword and shield"""
        # Shadow
        pygame.draw.ellipse(self.screen, (0, 0, 0, 100),
                           (x - size//2, y + size - 10, size, 20))

        # Body (armor) - steel blue
        pygame.draw.rect(self.screen, (70, 130, 180),
                        (x - size//3, y - size//2, size//1.5, size//1.5),
                        border_radius=5)

        # Head
        pygame.draw.circle(self.screen, (255, 220, 177), (x, y - size//2), size//4)

        # Helmet
        pygame.draw.arc(self.screen, (169, 169, 169),
                       (x - size//4, y - size//2 - size//4, size//2, size//2),
                       0, 3.14, 3)

        # Shield (left side)
        shield_x = x - size//2.5
        pygame.draw.rect(self.screen, (192, 192, 192),
                        (shield_x, y - size//3, size//4, size//2.5),
                        border_radius=3)
        pygame.draw.rect(self.screen, (255, 215, 0),
                        (shield_x, y - size//3, size//4, size//2.5), 2,
                        border_radius=3)

        # Sword (right side)
        sword_x = x + size//3
        pygame.draw.rect(self.screen, (192, 192, 192),
                        (sword_x, y - size//2, size//8, size//1.5))
        # Sword hilt
        pygame.draw.rect(self.screen, (139, 69, 19),
                        (sword_x - size//16, y - size//4, size//4, size//8))

    def draw_mage_sprite(self, x, y, size):
        """Draw a mage with staff and robes"""
        # Shadow
        pygame.draw.ellipse(self.screen, (0, 0, 0, 100),
                           (x - size//2, y + size - 10, size, 20))

        # Robes (flowing)
        pygame.draw.polygon(self.screen, (138, 43, 226),
                           [(x, y - size//2),
                            (x - size//2, y + size//4),
                            (x + size//2, y + size//4)])

        # Inner robe
        pygame.draw.polygon(self.screen, (75, 0, 130),
                           [(x, y - size//3),
                            (x - size//3, y + size//4),
                            (x + size//3, y + size//4)])

        # Head
        pygame.draw.circle(self.screen, (255, 220, 177), (x, y - size//2), size//4)

        # Wizard hat
        pygame.draw.polygon(self.screen, (75, 0, 130),
                           [(x, y - size),
                            (x - size//3, y - size//2),
                            (x + size//3, y - size//2)])
        pygame.draw.circle(self.screen, (255, 215, 0), (x, y - size + 5), 4)

        # Staff
        staff_x = x + size//3
        pygame.draw.rect(self.screen, (139, 69, 19),
                        (staff_x, y - size, size//12, size))
        # Orb on staff
        pygame.draw.circle(self.screen, (0, 191, 255), (staff_x, y - size + 10), size//6)
        pygame.draw.circle(self.screen, (173, 216, 230), (staff_x, y - size + 10), size//8)

    def draw_archer_sprite(self, x, y, size):
        """Draw an archer with bow"""
        # Shadow
        pygame.draw.ellipse(self.screen, (0, 0, 0, 100),
                           (x - size//2, y + size - 10, size, 20))

        # Body (leather armor) - brown/green
        pygame.draw.rect(self.screen, (34, 139, 34),
                        (x - size//3, y - size//2, size//1.5, size//1.5),
                        border_radius=5)

        # Head
        pygame.draw.circle(self.screen, (255, 220, 177), (x, y - size//2), size//4)

        # Hood
        pygame.draw.arc(self.screen, (34, 100, 34),
                       (x - size//3, y - size//2 - size//5, size//1.5, size//2),
                       0, 3.14, 3)

        # Bow (curved on left side)
        bow_x = x - size//2.5
        pygame.draw.arc(self.screen, (139, 69, 19),
                       (bow_x - size//4, y - size//2, size//2, size),
                       -1.57, 1.57, 3)

        # Quiver on back (right side)
        quiver_x = x + size//3
        pygame.draw.rect(self.screen, (101, 67, 33),
                        (quiver_x, y - size//3, size//6, size//2.5),
                        border_radius=2)
        # Arrows
        for i in range(3):
            arrow_y = y - size//3 + i * size//8
            pygame.draw.line(self.screen, (139, 69, 19),
                           (quiver_x + size//12, arrow_y),
                           (quiver_x + size//12, arrow_y - size//6), 2)

    def draw_paladin_sprite(self, x, y, size):
        """Draw a paladin with holy armor"""
        # Shadow
        pygame.draw.ellipse(self.screen, (0, 0, 0, 100),
                           (x - size//2, y + size - 10, size, 20))

        # Body (holy armor) - silver with gold trim
        pygame.draw.rect(self.screen, (192, 192, 192),
                        (x - size//3, y - size//2, size//1.5, size//1.5),
                        border_radius=5)
        pygame.draw.rect(self.screen, (255, 215, 0),
                        (x - size//3, y - size//2, size//1.5, size//1.5), 2,
                        border_radius=5)

        # Head
        pygame.draw.circle(self.screen, (255, 220, 177), (x, y - size//2), size//4)

        # Helmet with cross
        pygame.draw.rect(self.screen, (192, 192, 192),
                        (x - size//4, y - size//2 - size//6, size//2, size//3),
                        border_radius=3)
        # Holy cross on helmet
        pygame.draw.line(self.screen, (255, 215, 0),
                        (x, y - size//2 - size//8),
                        (x, y - size//2 + size//16), 3)
        pygame.draw.line(self.screen, (255, 215, 0),
                        (x - size//12, y - size//2 - size//12),
                        (x + size//12, y - size//2 - size//12), 3)

        # Large shield (left)
        shield_x = x - size//2.5
        pygame.draw.rect(self.screen, (220, 220, 220),
                        (shield_x, y - size//2.5, size//3, size//1.8),
                        border_radius=3)
        # Cross on shield
        pygame.draw.line(self.screen, (255, 0, 0),
                        (shield_x + size//6, y - size//3),
                        (shield_x + size//6, y + size//8), 2)
        pygame.draw.line(self.screen, (255, 0, 0),
                        (shield_x + size//12, y - size//8),
                        (shield_x + size//4, y - size//8), 2)

        # Sword (right)
        sword_x = x + size//3
        pygame.draw.rect(self.screen, (220, 220, 220),
                        (sword_x, y - size//2, size//8, size//1.5))
        pygame.draw.rect(self.screen, (255, 215, 0),
                        (sword_x - size//16, y - size//4, size//4, size//8))

    def draw_wizard_sprite(self, x, y, size):
        """Draw the evil wizard"""
        # Shadow
        pygame.draw.ellipse(self.screen, (0, 0, 0, 100),
                           (x - size//2, y + size - 10, size, 20))

        # Dark robes
        pygame.draw.polygon(self.screen, (75, 0, 130),
                           [(x, y - size//2),
                            (x - size//2, y + size//4),
                            (x + size//2, y + size//4)])

        # Inner robe (darker)
        pygame.draw.polygon(self.screen, (50, 0, 80),
                           [(x, y - size//3),
                            (x - size//3, y + size//4),
                            (x + size//3, y + size//4)])

        # Head (pale/greenish for evil look)
        pygame.draw.circle(self.screen, (200, 220, 200), (x, y - size//2), size//4)

        # Evil wizard hat (pointed, darker)
        pygame.draw.polygon(self.screen, (50, 0, 80),
                           [(x, y - size * 1.1),
                            (x - size//2.5, y - size//2),
                            (x + size//2.5, y - size//2)])
        # Hat band
        pygame.draw.rect(self.screen, (138, 43, 226),
                        (x - size//2.5, y - size//2, size//1.2, size//12))

        # Evil staff with dark orb
        staff_x = x + size//3
        pygame.draw.rect(self.screen, (60, 40, 20),
                        (staff_x, y - size, size//12, size))
        # Dark energy orb
        pygame.draw.circle(self.screen, (138, 43, 226), (staff_x, y - size + 10), size//6)
        pygame.draw.circle(self.screen, (75, 0, 130), (staff_x, y - size + 10), size//8)

        # Glowing eyes (evil)
        pygame.draw.circle(self.screen, (255, 0, 0), (x - size//8, y - size//2), 3)
        pygame.draw.circle(self.screen, (255, 0, 0), (x + size//8, y - size//2), 3)

    def draw_decorations(self):
        """Draw battlefield decorations (trees, rocks, bushes, buildings)"""
        # Define decoration positions (x, y, type, scale)
        # Place decorations around the edges, not blocking the battle area
        decoration_layout = [
            # Left side background trees (keep on left)
            (80, 280, 'tree1', 0.45),
            (120, 295, 'tree2', 0.42),

            # Line of buildings in background (higher up, near horizon)
            (280, 230, 'house2', 0.40),
            (380, 225, 'house1', 0.43),
            (480, 235, 'house3', 0.41),
            (580, 222, 'tower', 0.50),
            (680, 228, 'house1', 0.42),
            (730, 233, 'house2', 0.39),

            # Left foreground bushes and rocks
            (40, 500, 'bush1', 0.6),
            (90, 520, 'rock1', 0.5),
            (130, 515, 'bush2', 0.55),

            # Right foreground bushes and rocks
            (670, 505, 'rock2', 0.5),
            (720, 520, 'bush1', 0.55),
            (760, 510, 'bush2', 0.6),

            # Some mid-ground decorations
            (150, 440, 'rock1', 0.4),
            (630, 450, 'rock2', 0.38),
        ]

        for x, y, deco_type, scale in decoration_layout:
            if self.decorations.get(deco_type):
                deco = self.decorations[deco_type]
                # Calculate scaled size
                width, height = deco.get_size()
                new_width = int(width * scale)
                new_height = int(height * scale)
                scaled_deco = pygame.transform.scale(deco, (new_width, new_height))
                # Draw decoration centered at position
                rect = scaled_deco.get_rect(center=(x, y))
                self.screen.blit(scaled_deco, rect)

    def draw_character_sprite(self, character, x, y, size):
        """Draw the appropriate sprite based on character type (image or drawn)"""
        # Determine which sprite to use
        sprite_key = None
        if isinstance(character, Warrior):
            sprite_key = 'warrior'
        elif isinstance(character, Mage):
            sprite_key = 'mage'
        elif isinstance(character, Archer):
            sprite_key = 'archer'
        elif isinstance(character, Paladin):
            sprite_key = 'paladin'
        elif isinstance(character, EvilWizard):
            sprite_key = 'wizard'

        # Try to draw image sprite first
        if sprite_key and self.sprites.get(sprite_key):
            # Use animated sprite if available
            if sprite_key in self.sprite_frames and self.sprite_frames[sprite_key]:
                frames = self.sprite_frames[sprite_key]
                # Calculate current frame based on animation counter
                frame_index = (self.current_frame // self.frame_speed) % len(frames)
                img = frames[frame_index]
            else:
                img = self.sprites[sprite_key]

            # Scale image to desired size (maintain aspect ratio)
            scaled_img = pygame.transform.scale(img, (size, size))
            # Center the image at the position
            img_rect = scaled_img.get_rect(center=(x, y))
            self.screen.blit(scaled_img, img_rect)
        else:
            # Fall back to drawn sprites
            if isinstance(character, Warrior):
                self.draw_warrior_sprite(x, y, size)
            elif isinstance(character, Mage):
                self.draw_mage_sprite(x, y, size)
            elif isinstance(character, Archer):
                self.draw_archer_sprite(x, y, size)
            elif isinstance(character, Paladin):
                self.draw_paladin_sprite(x, y, size)
            elif isinstance(character, EvilWizard):
                self.draw_wizard_sprite(x, y, size)

    def draw_character_placeholder(self, x, y, size, color, name):
        """Draw a simple character placeholder (rectangle/circle) - DEPRECATED"""
        # This is now replaced by draw_character_sprite
        pass

    def draw_health_bar(self, character, x, y, show_label=True):
        """Draw health bar with label"""
        if show_label:
            label = self.small_font.render("HP", True, (255, 255, 255))
            self.screen.blit(label, (x, y - 2))  # Label now inside box

        # Background bar - made smaller, positioned after HP label
        pygame.draw.rect(self.screen, (100, 100, 100), (x + 28, y, 152, 18))

        # Health bar (color changes based on health percentage)
        health_percent = character.health / character.max_health
        if health_percent > 0.5:
            color = (0, 255, 0)  # Green
        elif health_percent > 0.25:
            color = (255, 255, 0)  # Yellow
        else:
            color = (255, 0, 0)  # Red

        health_width = health_percent * 152
        pygame.draw.rect(self.screen, color, (x + 28, y, health_width, 18))

        # Health text - smaller
        health_text = f"{int(character.health)}/{character.max_health}"
        text_surf = self.small_font.render(health_text, True, (255, 255, 255))
        text_rect = text_surf.get_rect(center=(x + 104, y + 9))
        self.screen.blit(text_surf, text_rect)

    def draw_rage_bar(self, warrior, x, y):
        """Draw rage bar for warrior"""
        label = self.small_font.render("RAGE", True, (255, 165, 0))
        self.screen.blit(label, (x, y - 2))  # Label now inside box

        # Background - made smaller, positioned after RAGE label
        pygame.draw.rect(self.screen, (100, 50, 0), (x + 50, y, 130, 12))

        # Rage bar
        rage_width = (warrior.rage_stacks / warrior.max_rage) * 130
        pygame.draw.rect(self.screen, (255, 165, 0), (x + 50, y, rage_width, 12))

        # Rage stacks text - smaller
        rage_text = f"{warrior.rage_stacks}/{warrior.max_rage}"
        text_surf = self.small_font.render(rage_text, True, (255, 255, 255))
        self.screen.blit(text_surf, (x + 185, y - 2))

    def draw_mana_bar(self, mage, x, y):
        """Draw mana bar for mage"""
        label = self.small_font.render("MANA", True, (100, 149, 237))
        self.screen.blit(label, (x, y - 2))

        # Background
        pygame.draw.rect(self.screen, (20, 50, 100), (x + 50, y, 130, 12))

        # Mana bar
        mana_width = (mage.mana / mage.max_mana) * 130
        pygame.draw.rect(self.screen, (100, 149, 237), (x + 50, y, mana_width, 12))

        # Mana text
        mana_text = f"{mage.mana}/{mage.max_mana}"
        text_surf = self.small_font.render(mana_text, True, (255, 255, 255))
        self.screen.blit(text_surf, (x + 185, y - 2))

    def draw_focus_bar(self, archer, x, y):
        """Draw focus bar for archer"""
        label = self.small_font.render("FOCUS", True, (50, 205, 50))
        self.screen.blit(label, (x, y - 2))

        # Background
        pygame.draw.rect(self.screen, (20, 80, 20), (x + 50, y, 130, 12))

        # Focus bar
        focus_width = (archer.focus / archer.max_focus) * 130
        pygame.draw.rect(self.screen, (50, 205, 50), (x + 50, y, focus_width, 12))

        # Focus text
        focus_text = f"{archer.focus}/{archer.max_focus}"
        text_surf = self.small_font.render(focus_text, True, (255, 255, 255))
        self.screen.blit(text_surf, (x + 185, y - 2))

    def draw_holy_power_bar(self, paladin, x, y):
        """Draw holy power bar for paladin"""
        label = self.small_font.render("HOLY", True, (255, 215, 0))
        self.screen.blit(label, (x, y - 2))

        # Background
        pygame.draw.rect(self.screen, (100, 80, 0), (x + 50, y, 130, 12))

        # Holy power bar
        holy_width = (paladin.holy_power / paladin.max_holy_power) * 130
        pygame.draw.rect(self.screen, (255, 215, 0), (x + 50, y, holy_width, 12))

        # Holy power text
        holy_text = f"{paladin.holy_power}/{paladin.max_holy_power}"
        text_surf = self.small_font.render(holy_text, True, (255, 255, 255))
        self.screen.blit(text_surf, (x + 185, y - 2))

    def draw_info_box(self, character, x, y, is_player=True):
        """Draw Pokemon-style info box"""
        # Box background - made smaller with enhanced styling
        # Adjust height based on character class
        box_height = 80 if is_player and not isinstance(character, EvilWizard) else 65
        box_rect = pygame.Rect(x, y, 240, box_height)

        # Add subtle gradient to box
        for i in range(box_height):
            alpha = int(200 - (i / box_height) * 30)
            color = (40 + i // 4, 40 + i // 4, 60 + i // 3)
            pygame.draw.line(self.screen, color,
                           (x + 10, y + i), (x + 230, y + i))

        # Box border with glow effect
        pygame.draw.rect(self.screen, (40, 40, 60), box_rect, border_radius=10)
        pygame.draw.rect(self.screen, (150, 150, 200), box_rect, width=3, border_radius=10)
        pygame.draw.rect(self.screen, (100, 100, 150), box_rect, width=1, border_radius=10)

        # Character name - smaller font
        name_text = character.name
        # Add shield indicator for Warrior with active shield
        if is_player and isinstance(character, Warrior) and character.shield_active:
            name_text += f" 🛡️x{character.shield_turns}"
        # Add invulnerability indicator for Paladin
        if is_player and isinstance(character, Paladin) and hasattr(character, 'is_invulnerable') and character.is_invulnerable:
            name_text += " 🛡️"
        # Add stun indicator for wizard
        if isinstance(character, EvilWizard) and hasattr(character, 'is_stunned') and character.is_stunned:
            name_text += " 💫"
        name_surf = self.small_font.render(name_text, True, (255, 255, 255))
        self.screen.blit(name_surf, (x + 10, y + 5))

        # Health bar - smaller
        self.draw_health_bar(character, x + 10, y + 30, show_label=True)

        # Resource bar based on class
        if is_player:
            if isinstance(character, Warrior):
                self.draw_rage_bar(character, x + 10, y + 55)
            elif isinstance(character, Mage):
                self.draw_mana_bar(character, x + 10, y + 55)
            elif isinstance(character, Archer):
                self.draw_focus_bar(character, x + 10, y + 55)
            elif isinstance(character, Paladin):
                self.draw_holy_power_bar(character, x + 10, y + 55)

    def draw_button(self, text, rect, color, hover=False):
        """Draw button with hover effect"""
        button_color = tuple(min(c + 30, 255) for c in color) if hover else color

        # Button shadow (more pronounced)
        shadow_rect = rect.copy()
        shadow_rect.y += 4
        shadow_rect.x += 2
        pygame.draw.rect(self.screen, (0, 0, 0, 100), shadow_rect, border_radius=5)

        # Button with gradient effect
        for i in range(rect.height):
            brightness = int(i / rect.height * 40) - 20
            grad_color = tuple(max(0, min(255, c + brightness)) for c in button_color)
            pygame.draw.line(self.screen, grad_color,
                           (rect.x, rect.y + i),
                           (rect.x + rect.width, rect.y + i))

        # Button outline
        pygame.draw.rect(self.screen, button_color, rect, border_radius=5)
        pygame.draw.rect(self.screen, (255, 255, 255), rect, width=2, border_radius=5)

        # Highlight effect on hover
        if hover:
            highlight_rect = rect.copy()
            highlight_rect.inflate_ip(-4, -4)
            pygame.draw.rect(self.screen, (255, 255, 255, 50), highlight_rect, width=1, border_radius=3)

        # Text with shadow
        text_surf = self.font.render(text, True, (0, 0, 0))
        text_rect = text_surf.get_rect(center=(rect.centerx + 2, rect.centery + 2))
        self.screen.blit(text_surf, text_rect)

        text_surf = self.font.render(text, True, (255, 255, 255))
        text_rect = text_surf.get_rect(center=rect.center)
        self.screen.blit(text_surf, text_rect)

    def add_message(self, message):
        """Add a message to the battle log"""
        self.messages.append(message)
        if len(self.messages) > 3:  # Keep only last 3 messages
            self.messages.pop(0)

    def draw_message_box(self):
        """Draw Pokemon-style message box at the bottom"""
        # Message box background with enhanced styling
        msg_box = pygame.Rect(560, 400, 220, 180)

        # Gradient background
        for i in range(180):
            brightness = int(240 - (i / 180) * 20)
            pygame.draw.line(self.screen, (brightness, brightness, brightness),
                           (560, 400 + i), (780, 400 + i))

        # Border with glow
        pygame.draw.rect(self.screen, (240, 240, 240), msg_box, border_radius=10)
        pygame.draw.rect(self.screen, (150, 150, 200), msg_box, width=3, border_radius=10)
        pygame.draw.rect(self.screen, (100, 100, 150), msg_box, width=1, border_radius=10)

        # Draw messages with enhanced text
        y_offset = 410
        for message in self.messages:
            # Word wrap for long messages
            words = message.split(' ')
            lines = []
            current_line = ""

            for word in words:
                test_line = current_line + word + " "
                if self.small_font.size(test_line)[0] <= 200:
                    current_line = test_line
                else:
                    if current_line:
                        lines.append(current_line)
                    current_line = word + " "
            if current_line:
                lines.append(current_line)

            for line in lines:
                # Text shadow for better readability
                shadow_surf = self.small_font.render(line, True, (100, 100, 100))
                self.screen.blit(shadow_surf, (571, y_offset + 1))

                text_surf = self.small_font.render(line, True, (0, 0, 0))
                self.screen.blit(text_surf, (570, y_offset))
                y_offset += 25

    def add_damage_number(self, x, y, damage, is_heal=False):
        """Add floating damage/heal number"""
        color = (0, 255, 0) if is_heal else (255, 50, 50)
        text = f"+{damage}" if is_heal else f"-{damage}"
        self.damage_numbers.append([x, y, text, 60, color])  # 60 frames = 1 second

    def draw_damage_numbers(self):
        """Draw and update floating damage numbers"""
        for dmg in self.damage_numbers[:]:
            x, y, text, timer, color = dmg
            if timer > 0:
                # Draw damage number with outline for better visibility
                alpha = min(255, timer * 4)

                # Outline/shadow
                for dx, dy in [(-2, 0), (2, 0), (0, -2), (0, 2)]:
                    surf = self.font.render(text, True, (0, 0, 0))
                    self.screen.blit(surf, (x + dx, y + dy))

                # Main text
                surf = self.font.render(text, True, color)
                self.screen.blit(surf, (x, y))

                # Update position and timer
                dmg[1] -= 1  # Move up
                dmg[3] -= 1  # Decrease timer
            else:
                self.damage_numbers.remove(dmg)

    def shake_screen(self, intensity=10):
        """Trigger screen shake effect"""
        self.shake_timer = 10
        import random
        self.shake_offset = [random.randint(-intensity, intensity),
                           random.randint(-intensity, intensity)]

    def apply_shake(self):
        """Apply and update shake effect"""
        if self.shake_timer > 0:
            self.shake_timer -= 1
            if self.shake_timer == 0:
                self.shake_offset = [0, 0]
        return self.shake_offset

    def add_particles(self, x, y, count, color, particle_type='impact'):
        """Add visual particles for effects"""
        import random
        for _ in range(count):
            if particle_type == 'impact':
                # Impact particles spread outward
                angle = random.uniform(0, 6.28)
                speed = random.uniform(2, 6)
                vx = speed * pygame.math.Vector2(1, 0).rotate_rad(angle).x
                vy = speed * pygame.math.Vector2(1, 0).rotate_rad(angle).y
                size = random.randint(3, 7)
                life = random.randint(20, 40)
            elif particle_type == 'sparkle':
                # Sparkles for healing/magic
                vx = random.uniform(-2, 2)
                vy = random.uniform(-4, -1)
                size = random.randint(2, 5)
                life = random.randint(30, 50)

            self.particles.append({
                'x': x, 'y': y, 'vx': vx, 'vy': vy,
                'size': size, 'color': color, 'life': life, 'max_life': life
            })

    def draw_particles(self):
        """Draw and update all particles"""
        for particle in self.particles[:]:
            if particle['life'] > 0:
                # Calculate alpha based on remaining life
                alpha = int((particle['life'] / particle['max_life']) * 255)

                # Draw particle with fade out
                surf = pygame.Surface((particle['size'] * 2, particle['size'] * 2), pygame.SRCALPHA)
                color_with_alpha = (*particle['color'], alpha)
                pygame.draw.circle(surf, color_with_alpha,
                                 (particle['size'], particle['size']), particle['size'])
                self.screen.blit(surf, (int(particle['x']), int(particle['y'])))

                # Update particle
                particle['x'] += particle['vx']
                particle['y'] += particle['vy']
                particle['vy'] += 0.2  # Gravity
                particle['life'] -= 1
            else:
                self.particles.remove(particle)

    def draw_special_menu(self, mouse_pos):
        """Draw special ability selection menu"""
        # Semi-transparent overlay
        overlay = pygame.Surface((800, 600))
        overlay.set_alpha(128)
        overlay.fill((0, 0, 0))
        self.screen.blit(overlay, (0, 0))

        # Menu background - made taller to fit all content properly
        menu_rect = pygame.Rect(200, 120, 400, 360)
        pygame.draw.rect(self.screen, (40, 40, 60), menu_rect, border_radius=15)
        pygame.draw.rect(self.screen, (100, 100, 150), menu_rect, width=4, border_radius=15)

        # Title
        title = self.font.render("Special Abilities", True, (255, 255, 255))
        title_rect = title.get_rect(center=(400, 160))
        self.screen.blit(title, title_rect)

        # Show different abilities based on class
        if isinstance(self.player, Warrior):
            # Rage info
            rage_text = f"Rage: {self.player.rage_stacks}/{self.player.max_rage}"
            rage_surf = self.small_font.render(rage_text, True, (255, 165, 0))
            self.screen.blit(rage_surf, (220, 200))

            # Ability buttons
            self.special_buttons = {
                'rage_strike': pygame.Rect(220, 230, 360, 65),
                'shield_wall': pygame.Rect(220, 305, 360, 65),
                'cancel': pygame.Rect(220, 395, 360, 50),
            }

            # Rage Strike button
            can_use_rage = self.player.rage_stacks >= 3
            self._draw_ability_button('rage_strike', "Rage Strike (3 Rage)", "Deal 2.5x damage",
                                     (180, 70, 70) if can_use_rage else (80, 80, 80),
                                     mouse_pos, can_use_rage)

            # Shield Wall button
            self._draw_ability_button('shield_wall', "Shield Wall", "Reduce damage 50% for 2 turns",
                                     (70, 130, 180) if not self.player.shield_active else (80, 80, 80),
                                     mouse_pos, not self.player.shield_active)

        elif isinstance(self.player, Mage):
            # Mana info
            mana_text = f"Mana: {self.player.mana}/{self.player.max_mana}"
            mana_surf = self.small_font.render(mana_text, True, (100, 149, 237))
            self.screen.blit(mana_surf, (220, 200))

            # Ability buttons
            self.special_buttons = {
                'fireball': pygame.Rect(220, 230, 360, 65),
                'ice_shield': pygame.Rect(220, 305, 360, 65),
                'cancel': pygame.Rect(220, 395, 360, 50),
            }

            # Fireball button
            can_use_fireball = self.player.mana >= 40
            self._draw_ability_button('fireball', "Fireball (40 Mana)", "Deal 2x magical damage",
                                     (255, 69, 0) if can_use_fireball else (80, 80, 80),
                                     mouse_pos, can_use_fireball)

            # Ice Shield button
            can_use_ice = self.player.mana >= 30
            self._draw_ability_button('ice_shield', "Ice Shield (30 Mana)", "Heal 25 HP",
                                     (135, 206, 250) if can_use_ice else (80, 80, 80),
                                     mouse_pos, can_use_ice)

        elif isinstance(self.player, Archer):
            # Focus info
            focus_text = f"Focus: {self.player.focus}/{self.player.max_focus}"
            focus_surf = self.small_font.render(focus_text, True, (50, 205, 50))
            self.screen.blit(focus_surf, (220, 200))

            # Ability buttons
            self.special_buttons = {
                'multishot': pygame.Rect(220, 230, 360, 65),
                'stun_arrow': pygame.Rect(220, 305, 360, 65),
                'cancel': pygame.Rect(220, 395, 360, 50),
            }

            # Multishot button
            can_use_multishot = self.player.focus >= 2
            self._draw_ability_button('multishot', "Multishot (2 Focus)", "Fire 3 arrows",
                                     (34, 139, 34) if can_use_multishot else (80, 80, 80),
                                     mouse_pos, can_use_multishot)

            # Stun Arrow button
            can_use_stun = self.player.focus >= 4
            self._draw_ability_button('stun_arrow', "Stun Arrow (4 Focus)", "Stun wizard for 1 turn",
                                     (50, 205, 50) if can_use_stun else (80, 80, 80),
                                     mouse_pos, can_use_stun)

        elif isinstance(self.player, Paladin):
            # Holy power info
            holy_text = f"Holy Power: {self.player.holy_power}/{self.player.max_holy_power}"
            holy_surf = self.small_font.render(holy_text, True, (255, 215, 0))
            self.screen.blit(holy_surf, (220, 200))

            # Ability buttons
            self.special_buttons = {
                'divine_shield': pygame.Rect(220, 230, 360, 65),
                'lay_on_hands': pygame.Rect(220, 305, 360, 65),
                'cancel': pygame.Rect(220, 395, 360, 50),
            }

            # Divine Shield button
            can_use_divine = self.player.holy_power >= 2
            self._draw_ability_button('divine_shield', "Divine Shield (2 Holy)", "Invulnerable for 1 turn",
                                     (255, 215, 0) if can_use_divine else (80, 80, 80),
                                     mouse_pos, can_use_divine)

            # Lay on Hands button
            can_use_lay = self.player.holy_power >= 4
            self._draw_ability_button('lay_on_hands', "Lay on Hands (4 Holy)", "Restore 50 HP",
                                     (255, 255, 150) if can_use_lay else (80, 80, 80),
                                     mouse_pos, can_use_lay)

        # Cancel button (always present)
        hover = self.special_buttons['cancel'].collidepoint(mouse_pos)
        self.draw_button("Cancel", self.special_buttons['cancel'], (100, 100, 100), hover)

    def _draw_ability_button(self, button_key, title, description, color, mouse_pos, enabled):
        """Helper function to draw an ability button"""
        button_rect = self.special_buttons[button_key]
        hover = button_rect.collidepoint(mouse_pos)
        button_color = tuple(min(c + 30, 255) for c in color) if (hover and enabled) else color

        # Button shadow
        shadow_rect = button_rect.copy()
        shadow_rect.y += 3
        pygame.draw.rect(self.screen, (0, 0, 0), shadow_rect, border_radius=5)

        # Button
        pygame.draw.rect(self.screen, button_color, button_rect, border_radius=5)
        pygame.draw.rect(self.screen, (255, 255, 255), button_rect, width=2, border_radius=5)

        # Button text - two lines inside button
        title_text = self.font.render(title, True, (255, 255, 255))
        title_rect = title_text.get_rect(center=(button_rect.centerx, button_rect.centery - 12))
        self.screen.blit(title_text, title_rect)

        desc_text = self.small_font.render(description, True, (200, 200, 200))
        desc_rect = desc_text.get_rect(center=(button_rect.centerx, button_rect.centery + 15))
        self.screen.blit(desc_text, desc_rect)

    def draw_main_menu(self, mouse_pos):
        """Draw the main menu overlay"""
        # Semi-transparent overlay
        overlay = pygame.Surface((800, 600))
        overlay.set_alpha(128)
        overlay.fill((0, 0, 0))
        self.screen.blit(overlay, (0, 0))

        # Menu background
        menu_rect = pygame.Rect(250, 200, 300, 200)
        pygame.draw.rect(self.screen, (40, 40, 60), menu_rect, border_radius=15)
        pygame.draw.rect(self.screen, (100, 100, 150), menu_rect, width=4, border_radius=15)

        # Title
        title = self.font.render("Menu", True, (255, 255, 255))
        title_rect = title.get_rect(center=(400, 240))
        self.screen.blit(title, title_rect)

        # Menu buttons
        self.main_menu_buttons = {
            'restart': pygame.Rect(275, 280, 250, 50),
            'cancel': pygame.Rect(275, 340, 250, 50),
        }

        # Restart button
        hover = self.main_menu_buttons['restart'].collidepoint(mouse_pos)
        self.draw_button("Restart Battle", self.main_menu_buttons['restart'], (180, 70, 70), hover)

        # Cancel button
        hover = self.main_menu_buttons['cancel'].collidepoint(mouse_pos)
        self.draw_button("Back to Battle", self.main_menu_buttons['cancel'], (70, 130, 180), hover)

    def draw_game_over_screen(self):
        """Draw game over screen"""
        overlay = pygame.Surface((800, 600))
        overlay.set_alpha(200)
        overlay.fill((0, 0, 0))
        self.screen.blit(overlay, (0, 0))

        # Game Over text
        game_over_text = self.font.render("GAME OVER", True, (255, 0, 0))
        game_over_rect = game_over_text.get_rect(center=(400, 250))
        self.screen.blit(game_over_text, game_over_rect)

        defeat_text = self.small_font.render("You were defeated by the Evil Wizard!", True, (255, 255, 255))
        defeat_rect = defeat_text.get_rect(center=(400, 300))
        self.screen.blit(defeat_text, defeat_rect)

        restart_text = self.small_font.render("Close window to exit", True, (150, 150, 150))
        restart_rect = restart_text.get_rect(center=(400, 350))
        self.screen.blit(restart_text, restart_rect)

    def draw_victory_screen(self):
        """Draw enhanced victory screen with XP and level info"""
        overlay = pygame.Surface((800, 600))
        overlay.set_alpha(200)
        overlay.fill((0, 0, 0))
        self.screen.blit(overlay, (0, 0))

        # Victory text with glow effect
        victory_text = self.title_font.render("VICTORY!", True, (255, 215, 0))
        victory_rect = victory_text.get_rect(center=(400, 100))
        self.screen.blit(victory_text, victory_rect)

        # Boss defeated
        boss_text = self.font.render(f"You defeated {self.wizard.name}!", True, (255, 255, 255))
        boss_rect = boss_text.get_rect(center=(400, 170))
        self.screen.blit(boss_text, boss_rect)

        # XP gained
        if hasattr(self.wizard, 'get_exp_reward'):
            exp_gained = self.wizard.get_exp_reward()
            exp_text = self.font.render(f"✨ Experience Gained: {exp_gained} XP", True, (100, 255, 100))
            exp_rect = exp_text.get_rect(center=(400, 230))
            self.screen.blit(exp_text, exp_rect)

        # Player stats
        y_offset = 280
        stats = [
            f"Level: {self.player.level}",
            f"Total XP: {self.player.experience}",
            f"Next Level: {self.player.exp_to_next_level - self.player.experience} XP needed",
            f"Victories: {self.player.victories}",
        ]

        for stat in stats:
            stat_surf = self.small_font.render(stat, True, (200, 200, 255))
            stat_rect = stat_surf.get_rect(center=(400, y_offset))
            self.screen.blit(stat_surf, stat_rect)
            y_offset += 30

        # Continue option
        continue_text = self.font.render("Press SPACE to continue", True, (255, 215, 0))
        continue_rect = continue_text.get_rect(center=(400, 500))
        self.screen.blit(continue_text, continue_rect)

        close_text = self.small_font.render("or close window to exit", True, (150, 150, 150))
        close_rect = close_text.get_rect(center=(400, 540))
        self.screen.blit(close_text, close_rect)

    def draw_battle_scene(self, mouse_pos):
        """Draw the complete battle scene"""
        # Apply screen shake
        shake_x, shake_y = self.apply_shake()

        # Draw background (image or gradient)
        if self.sprites.get('background'):
            # Create a simple grass field background for battle
            # Sky - nice blue gradient (only 1/4 of screen = 150px)
            for i in range(150):
                # Sky gradient from light blue to deeper blue
                r = int(135 - (i / 150) * 20)
                g = int(206 - (i / 150) * 30)
                b = int(235 - (i / 150) * 20)
                pygame.draw.line(self.screen, (r, g, b), (0, i), (800, i))

            # Grass field - flat green ground (3/4 of screen)
            for i in range(150, 600):
                # Grass gradient - darker as it goes down for depth
                depth_factor = (i - 150) / 450
                r = int(85 + depth_factor * 15)
                g = int(160 - depth_factor * 30)
                b = int(73 + depth_factor * 10)
                pygame.draw.line(self.screen, (r, g, b), (0, i), (800, i))

            # Add grass texture pattern using a separate random generator
            # so we don't affect game logic random numbers
            import random
            grass_random = random.Random(42)  # Use separate Random instance
            for _ in range(200):
                x = grass_random.randint(0, 800)
                y = grass_random.randint(150, 600)
                size = grass_random.randint(2, 4)
                darkness = grass_random.randint(-10, 10)
                grass_color = (85 + darkness, 160 + darkness, 73 + darkness)
                pygame.draw.circle(self.screen, grass_color, (x, y), size)

            # Horizon line
            pygame.draw.line(self.screen, (100, 140, 80), (0, 150), (800, 150), 2)

        else:
            # Enhanced background - sky gradient (dawn/dusk battle scene)
            for i in range(300):
                # Sky gradient from purple to orange
                r = int(120 + (i / 300) * 100)
                g = int(60 + (i / 300) * 80)
                b = int(150 - (i / 300) * 80)
                pygame.draw.line(self.screen, (r, g, b), (0, i), (800, i))

            # Ground gradient (darker)
            for i in range(300, 600):
                darkness = int((i - 300) / 300 * 40)
                pygame.draw.line(self.screen, (40 + darkness, 50 + darkness, 30 + darkness),
                               (0, i), (800, i))

        # Add atmospheric elements based on background type
        if self.sprites.get('background'):
            # For grass field - add some clouds
            cloud_color = (255, 255, 255, 120)
            for cloud_x in [120, 400, 680]:
                for offset in range(3):
                    x = cloud_x + offset * 25 - 25
                    y = 60 + offset * 8
                    pygame.draw.ellipse(self.screen, cloud_color,
                                      (x, y, 70, 35))
        else:
            # For gradient background - add clouds and mountains
            # Add some atmospheric clouds
            cloud_color = (180, 160, 200, 100)
            for cloud_x in [100, 400, 650]:
                for offset in range(3):
                    x = cloud_x + offset * 30 - 30
                    y = 80 + offset * 10
                    pygame.draw.ellipse(self.screen, cloud_color,
                                      (x, y, 80, 40))

            # Draw distant mountains/hills for depth
            mountain_points = [
                (0, 350), (150, 280), (250, 320), (400, 260),
                (550, 300), (700, 270), (800, 320), (800, 350), (0, 350)
            ]
            pygame.draw.polygon(self.screen, (60, 50, 80), mountain_points)

            # Battle platform/arena floor with perspective
            # Front platform (darker, closer)
            platform_front = [
                (0, 480), (800, 480), (750, 520), (50, 520)
            ]
            pygame.draw.polygon(self.screen, (80, 70, 60), platform_front)
            pygame.draw.polygon(self.screen, (100, 90, 70), platform_front, 3)

            # Back platform (lighter, further away)
            platform_back = [
                (100, 400), (700, 400), (750, 480), (50, 480)
            ]
            pygame.draw.polygon(self.screen, (100, 90, 70), platform_back)

            # Platform lines for depth
            for i in range(5):
                y = 400 + i * 20
                left_x = 100 + i * 10
                right_x = 700 - i * 10
                pygame.draw.line(self.screen, (70, 60, 50),
                               (left_x, y), (right_x, y), 2)

        # Draw battlefield decorations
        self.draw_decorations()

        # Add character glow effects for player
        if isinstance(self.player, Warrior) and self.player.rage_stacks >= 3:
            # Rage glow for warrior with high rage
            for radius in range(60, 40, -5):
                alpha = int(50 - (60 - radius) * 2)
                glow_surf = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
                pygame.draw.circle(glow_surf, (255, 100, 0, alpha), (radius, radius), radius)
                self.screen.blit(glow_surf, (self.hero_pos[0] + shake_x - radius,
                                            self.hero_pos[1] + shake_y - radius))

        # Evil wizard dark aura
        for radius in range(50, 30, -5):
            alpha = int(40 - (50 - radius) * 2)
            glow_surf = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
            pygame.draw.circle(glow_surf, (138, 43, 226, alpha), (radius, radius), radius)
            self.screen.blit(glow_surf, (self.wizard_pos[0] + shake_x - radius,
                                        self.wizard_pos[1] + shake_y - radius))

        # Draw characters with shake offset using new sprites
        # Hero (front-left, bigger)
        self.draw_character_sprite(
            self.player,
            self.hero_pos[0] + shake_x, self.hero_pos[1] + shake_y,
            100
        )

        # Wizard (back-center, smaller to show depth)
        self.draw_character_sprite(
            self.wizard,
            self.wizard_pos[0] + shake_x, self.wizard_pos[1] + shake_y,
            80
        )

        # Draw info boxes
        # Player info box (bottom left) - positioned at the very bottom of screen
        self.draw_info_box(self.player, 10, 520, is_player=True)

        # Wizard info box (positioned in the upper area)
        self.draw_info_box(self.wizard, 530, 310, is_player=False)

        # Draw particles (before UI elements so they don't overlap)
        self.draw_particles()

        # Draw message box
        self.draw_message_box()

        # Draw damage numbers
        self.draw_damage_numbers()

        # Draw buttons or special menu based on game state
        if self.main_menu_active:
            self.draw_main_menu(mouse_pos)
        elif self.special_menu_active:
            self.draw_special_menu(mouse_pos)
        elif self.game_state == "player_turn":
            for action, rect in self.buttons.items():
                hover = rect.collidepoint(mouse_pos)
                button_text = action.upper()
                if action == 'heal':
                    button_text = f"HEAL ({self.player.healing_potions})"
                self.draw_button(button_text, rect, (70, 130, 180), hover)
        elif self.game_state == "game_over":
            self.draw_game_over_screen()
        elif self.game_state == "victory":
            self.draw_victory_screen()

    def player_attack(self):
        """Handle player attack action"""
        # Use the attack method from character class which includes random damage
        old_wizard_health = self.wizard.health
        self.player.attack(self.wizard)
        damage = old_wizard_health - self.wizard.health

        self.add_message(f"Hero attacks for {damage} damage!")
        self.add_damage_number(self.wizard_pos[0], self.wizard_pos[1] - 50, damage)
        self.add_particles(self.wizard_pos[0], self.wizard_pos[1] - 20, 15, (255, 100, 100), 'impact')
        self.shake_screen(8)

        if self.wizard.health <= 0:
            # Award XP for defeating the boss
            exp_reward = self.wizard.get_exp_reward()
            self.player.gain_experience(exp_reward)
            self.player.victories += 1

            self.game_state = "victory"
            self.add_message("Victory! Wizard defeated!")
        else:
            self.game_state = "enemy_turn"
            self.message_timer = 60  # Wait 1 second before enemy turn

    def player_heal(self):
        """Handle player heal action using healing potions"""
        if self.player.healing_potions > 0:
            heal_amount = self.player.heal()
            if heal_amount > 0:
                self.add_message(f"Hero heals {heal_amount} HP! ({self.player.healing_potions} potions left)")
                self.add_damage_number(self.hero_pos[0], self.hero_pos[1] - 50, heal_amount, is_heal=True)
                self.add_particles(self.hero_pos[0], self.hero_pos[1] - 20, 20, (100, 255, 100), 'sparkle')
            else:
                self.add_message("Already at full health!")

            self.game_state = "enemy_turn"
            self.message_timer = 60
        else:
            self.add_message("No potions left!")

    def open_menu(self):
        """Open the main menu"""
        self.main_menu_active = True

    def restart_battle(self):
        """Restart the battle with the same character"""
        # Reset player health
        self.player.health = self.player.max_health
        self.player.healing_potions = 3

        # Reset warrior-specific stats
        if isinstance(self.player, Warrior):
            self.player.rage_stacks = 0
            self.player.shield_active = False
            self.player.shield_turns = 0

        # Reset mage-specific stats
        elif isinstance(self.player, Mage):
            self.player.mana = self.player.max_mana

        # Reset archer-specific stats
        elif isinstance(self.player, Archer):
            self.player.focus = 0

        # Reset paladin-specific stats
        elif isinstance(self.player, Paladin):
            self.player.holy_power = 0
            self.player.is_invulnerable = False

        # Reset wizard
        self.wizard.health = self.wizard.max_health
        self.wizard.is_stunned = False
        self.wizard.turn_counter = 0

        # Reset game state
        self.messages = []
        self.damage_numbers = []
        self.game_state = "player_turn"

        self.add_message("Battle restarted!")
        self.add_message("Choose your action!")

    def use_rage_strike(self):
        """Use Rage Strike ability"""
        if self.player.rage_stacks >= 3:
            success = self.player.rage_strike(self.wizard)
            if success:
                damage = int(self.player.attack_power * 2.5)

                self.add_message(f"RAGE STRIKE! {damage} damage!")
                self.add_damage_number(self.wizard_pos[0], self.wizard_pos[1] - 50, damage)
                self.add_particles(self.wizard_pos[0], self.wizard_pos[1] - 20, 25, (255, 50, 0), 'impact')
                self.shake_screen(15)

                if self.wizard.health <= 0:
                    # Award XP for defeating the boss
                    exp_reward = self.wizard.get_exp_reward()
                    self.player.gain_experience(exp_reward)
                    self.player.victories += 1

                    self.game_state = "victory"
                    self.add_message("Victory! Wizard defeated!")
                else:
                    self.game_state = "enemy_turn"
                    self.message_timer = 60

    def use_shield_wall(self):
        """Use Shield Wall ability"""
        if not self.player.shield_active:
            self.player.shield_active = True
            self.player.shield_turns = 2  # Shield lasts for 2 turns
            self.add_message("Shield Wall activated!")
            self.add_particles(self.hero_pos[0], self.hero_pos[1] - 20, 15, (192, 192, 192), 'sparkle')

            self.game_state = "enemy_turn"
            self.message_timer = 60
        else:
            self.add_message("Shield already active!")

    def use_fireball(self):
        """Use Mage Fireball ability"""
        if self.player.mana >= 40:
            success = self.player.fireball(self.wizard)
            if success:
                damage = int(self.player.attack_power * 2)

                self.add_message(f"FIREBALL! {damage} damage!")
                self.add_damage_number(self.wizard_pos[0], self.wizard_pos[1] - 50, damage)
                self.add_particles(self.wizard_pos[0], self.wizard_pos[1] - 20, 30, (255, 69, 0), 'impact')
                self.shake_screen(12)

                if self.wizard.health <= 0:
                    # Award XP for defeating the boss
                    exp_reward = self.wizard.get_exp_reward()
                    self.player.gain_experience(exp_reward)
                    self.player.victories += 1

                    self.game_state = "victory"
                    self.add_message("Victory! Wizard defeated!")
                else:
                    self.game_state = "enemy_turn"
                    self.message_timer = 60

    def use_ice_shield(self):
        """Use Mage Ice Shield ability"""
        if self.player.mana >= 30:
            old_health = self.player.health
            success = self.player.ice_shield()
            if success:
                heal_amount = self.player.health - old_health
                self.add_message(f"Ice Shield! Healed {heal_amount} HP!")
                self.add_damage_number(self.hero_pos[0], self.hero_pos[1] - 50, heal_amount, is_heal=True)
                self.add_particles(self.hero_pos[0], self.hero_pos[1] - 20, 20, (135, 206, 250), 'sparkle')

                self.game_state = "enemy_turn"
                self.message_timer = 60

    def use_multishot(self):
        """Use Archer Multishot ability"""
        if self.player.focus >= 2:
            success = self.player.multishot(self.wizard)
            if success:
                total_damage = int(self.player.attack_power * 3)

                self.add_message(f"MULTISHOT! {total_damage} damage (3 arrows)!")
                self.add_damage_number(self.wizard_pos[0], self.wizard_pos[1] - 50, total_damage)
                self.add_particles(self.wizard_pos[0], self.wizard_pos[1] - 20, 25, (34, 139, 34), 'impact')
                self.shake_screen(10)

                if self.wizard.health <= 0:
                    # Award XP for defeating the boss
                    exp_reward = self.wizard.get_exp_reward()
                    self.player.gain_experience(exp_reward)
                    self.player.victories += 1

                    self.game_state = "victory"
                    self.add_message("Victory! Wizard defeated!")
                else:
                    self.game_state = "enemy_turn"
                    self.message_timer = 60

    def use_stun_arrow(self):
        """Use Archer Stun Arrow ability"""
        if self.player.focus >= 4:
            success = self.player.stun_arrow(self.wizard)
            if success:
                damage = int(self.player.attack_power * 1.5)
                self.wizard.is_stunned = True

                self.add_message(f"Stun Arrow! {damage} damage! Wizard stunned!")
                self.add_damage_number(self.wizard_pos[0], self.wizard_pos[1] - 50, damage)
                self.add_particles(self.wizard_pos[0], self.wizard_pos[1] - 20, 20, (50, 205, 50), 'impact')
                self.shake_screen(8)

                if self.wizard.health <= 0:
                    # Award XP for defeating the boss
                    exp_reward = self.wizard.get_exp_reward()
                    self.player.gain_experience(exp_reward)
                    self.player.victories += 1

                    self.game_state = "victory"
                    self.add_message("Victory! Wizard defeated!")
                else:
                    self.game_state = "enemy_turn"
                    self.message_timer = 60

    def use_divine_shield(self):
        """Use Paladin Divine Shield ability"""
        if self.player.holy_power >= 2:
            self.player.holy_power -= 2
            self.player.divine_shield()
            self.add_message("Divine Shield! Invulnerable for 1 turn!")
            self.add_particles(self.hero_pos[0], self.hero_pos[1] - 20, 25, (255, 215, 0), 'sparkle')

            self.game_state = "enemy_turn"
            self.message_timer = 60

    def use_lay_on_hands(self):
        """Use Paladin Lay on Hands ability"""
        if self.player.holy_power >= 4:
            old_health = self.player.health
            success = self.player.lay_on_hands()
            if success:
                heal_amount = self.player.health - old_health
                self.add_message(f"Lay on Hands! Healed {heal_amount} HP!")
                self.add_damage_number(self.hero_pos[0], self.hero_pos[1] - 50, heal_amount, is_heal=True)
                self.add_particles(self.hero_pos[0], self.hero_pos[1] - 20, 30, (255, 255, 150), 'sparkle')

                self.game_state = "enemy_turn"
                self.message_timer = 60

    def enemy_turn(self):
        """Handle enemy turn"""
        # Check if wizard is stunned
        if self.wizard.is_stunned:
            self.wizard.is_stunned = False
            self.add_message("Wizard is stunned and can't attack!")
            self.game_state = "player_turn"

            # Regenerate resources for player
            if isinstance(self.player, Mage):
                self.player.regenerate_mana()
            elif isinstance(self.player, Archer):
                self.player.regenerate_focus()
            elif isinstance(self.player, Paladin):
                self.player.regenerate_holy_power()

            # Clear invulnerability
            if isinstance(self.player, Paladin) and self.player.is_invulnerable:
                self.player.is_invulnerable = False
                self.add_message("Divine Shield fades!")

            return

        # Regenerate wizard
        old_health = self.wizard.health
        self.wizard.regenerate()
        regen = self.wizard.health - old_health
        if regen > 0:
            self.add_message(f"Wizard regenerates {regen} HP!")
            self.add_damage_number(self.wizard_pos[0], self.wizard_pos[1] - 50, regen, is_heal=True)
            self.add_particles(self.wizard_pos[0], self.wizard_pos[1] - 20, 10, (138, 43, 226), 'sparkle')

        # Check for dark bolt (every 4 turns)
        self.wizard.turn_counter += 1
        use_dark_bolt = (self.wizard.turn_counter % 4 == 0)

        # Attack
        if use_dark_bolt:
            # Use dark bolt special attack
            import random
            damage = random.randint(35, 60)

            # Check if player is invulnerable (Paladin Divine Shield)
            if isinstance(self.player, Paladin) and self.player.is_invulnerable:
                self.add_message("DARK BOLT! Divine Shield blocks all damage!")
                self.add_particles(self.hero_pos[0], self.hero_pos[1] - 20, 30, (255, 215, 0), 'sparkle')
                damage = 0
            else:
                self.player.health -= damage
                self.add_message(f"DARK BOLT! {damage} damage!")
                self.add_damage_number(self.hero_pos[0], self.hero_pos[1] - 50, damage)
                self.add_particles(self.hero_pos[0], self.hero_pos[1] - 20, 25, (75, 0, 130), 'impact')
                self.shake_screen(15)
        else:
            # Normal attack - use randomized damage
            import random
            min_dam = int(self.wizard.attack_power * 0.5)
            max_dam = int(self.wizard.attack_power * 1.5)
            damage = random.randint(min_dam, max_dam)

            # Check if player is invulnerable (Paladin Divine Shield)
            if isinstance(self.player, Paladin) and self.player.is_invulnerable:
                self.add_message("Divine Shield blocks all damage!")
                self.add_particles(self.hero_pos[0], self.hero_pos[1] - 20, 20, (255, 215, 0), 'sparkle')
                damage = 0
            # Check if player is a Warrior with shield
            elif isinstance(self.player, Warrior) and hasattr(self.player, 'shield_active') and self.player.shield_active:
                turns_before = self.player.shield_turns
                damage = self.player.take_damage(damage)
                if turns_before > 0 and self.player.shield_turns <= 0:
                    self.add_message(f"Shield blocks! {damage} damage taken")
                    self.add_message("Shield Wall expired!")
                else:
                    self.add_message(f"Shield blocks! {damage} damage taken")
            else:
                self.player.health -= damage
                self.add_message(f"Wizard attacks for {damage} damage!")

            if damage > 0:
                self.add_damage_number(self.hero_pos[0], self.hero_pos[1] - 50, damage)
                self.add_particles(self.hero_pos[0], self.hero_pos[1] - 20, 12, (138, 43, 226), 'impact')
                self.shake_screen(8)

        # Clear invulnerability at end of turn
        if isinstance(self.player, Paladin) and self.player.is_invulnerable:
            self.player.is_invulnerable = False
            if damage == 0:  # Only show fade message if we blocked damage
                self.add_message("Divine Shield fades!")

        # Regenerate player resources
        if isinstance(self.player, Mage):
            old_mana = self.player.mana
            self.player.regenerate_mana()
            if self.player.mana > old_mana:
                self.add_message(f"Mana regenerated! ({self.player.mana}/{self.player.max_mana})")
        elif isinstance(self.player, Archer):
            old_focus = self.player.focus
            self.player.regenerate_focus()
            if self.player.focus > old_focus:
                self.add_message(f"Focus increased! ({self.player.focus}/{self.player.max_focus})")
        elif isinstance(self.player, Paladin):
            old_holy = self.player.holy_power
            self.player.regenerate_holy_power()
            if self.player.holy_power > old_holy:
                self.add_message(f"Holy Power gained! ({self.player.holy_power}/{self.player.max_holy_power})")

        if self.player.health <= 0:
            self.game_state = "game_over"
            self.add_message("Defeated...")
        else:
            self.game_state = "player_turn"

    def update(self):
        """Update game state"""
        # Update animation frame counter
        self.frame_counter += 1
        if self.frame_counter >= self.frame_speed:
            self.current_frame += 1
            self.frame_counter = 0

        if self.message_timer > 0:
            self.message_timer -= 1
            if self.message_timer == 0 and self.game_state == "enemy_turn":
                self.enemy_turn()

    def draw_character_creation(self, mouse_pos):
        """Draw the character creation screen"""
        # Background
        self.screen.fill((20, 20, 40))

        # Title
        title = self.title_font.render("Create Your Hero", True, (255, 215, 0))
        title_rect = title.get_rect(center=(400, 60))
        self.screen.blit(title, title_rect)

        # Instructions
        instruction = self.small_font.render("Choose your class:", True, (255, 255, 255))
        self.screen.blit(instruction, (50, 130))

        # Class selection cards - arranged in a single row
        classes = [
            ('warrior', 'Warrior', Warrior, 75, (70, 130, 180)),
            ('mage', 'Mage', Mage, 235, (138, 43, 226)),
            ('archer', 'Archer', Archer, 395, (34, 139, 34)),
            ('paladin', 'Paladin', Paladin, 555, (192, 192, 192))
        ]

        for class_id, class_name, class_type, x_pos, color in classes:
            # Use pre-defined button positions
            button_rect = self.class_buttons[class_id]

            # Draw card with black background
            is_selected = self.selected_class == class_id
            is_hover = button_rect.collidepoint(mouse_pos)

            # Black background for all cards
            pygame.draw.rect(self.screen, (0, 0, 0), button_rect, border_radius=10)

            # Border color changes based on selection/hover
            border_color = color  # Use class color for border
            if is_selected:
                border_color = (255, 215, 0)  # Gold for selected
            elif is_hover:
                border_color = tuple(min(c + 50, 255) for c in color)  # Brighter on hover

            pygame.draw.rect(self.screen, border_color, button_rect, 3, border_radius=10)

            # Draw mini sprite preview - positioned to show full body
            temp_char = class_type("Preview")
            sprite_y = button_rect.top + 90  # Position sprite lower to show full body
            self.draw_character_sprite(temp_char, button_rect.centerx, sprite_y, 45)

            # Class name
            name_surf = self.small_font.render(class_name, True, (255, 255, 255))
            name_rect = name_surf.get_rect(center=(button_rect.centerx, button_rect.bottom - 50))
            self.screen.blit(name_surf, name_rect)

            # Stats preview (small)
            stats = [
                f"HP: {temp_char.max_health}",
                f"ATK: {temp_char.attack_power}"
            ]
            y_offset = button_rect.bottom - 32
            for stat in stats:
                stat_surf = self.small_font.render(stat, True, (200, 200, 200))
                stat_rect = stat_surf.get_rect(center=(button_rect.centerx, y_offset))
                self.screen.blit(stat_surf, stat_rect)
                y_offset += 16

        # Name input section
        name_label = self.font.render("Enter your name:", True, (255, 255, 255))
        self.screen.blit(name_label, (50, 400))

        # Name input box
        input_box = pygame.Rect(50, 440, 700, 40)
        box_color = (100, 100, 150) if self.name_active else (70, 70, 100)
        pygame.draw.rect(self.screen, box_color, input_box, border_radius=5)
        pygame.draw.rect(self.screen, (255, 255, 255), input_box, 2, border_radius=5)

        # Display current name
        name_display = self.player_name if self.player_name else "Hero"
        name_surf = self.font.render(name_display, True, (255, 255, 255))
        self.screen.blit(name_surf, (60, 448))

        # Cursor blink when active
        if self.name_active and pygame.time.get_ticks() % 1000 < 500:
            cursor_x = 60 + self.font.size(self.player_name)[0]
            pygame.draw.line(self.screen, (255, 255, 255),
                           (cursor_x + 5, 445), (cursor_x + 5, 470), 2)

        # Start button
        self.start_button = pygame.Rect(300, 510, 200, 50)
        can_start = self.selected_class is not None
        button_color = (0, 200, 0) if can_start else (80, 80, 80)
        hover = self.start_button.collidepoint(mouse_pos) and can_start
        if hover:
            button_color = tuple(min(c + 30, 255) for c in button_color)

        pygame.draw.rect(self.screen, button_color, self.start_button, border_radius=10)
        pygame.draw.rect(self.screen, (255, 255, 255), self.start_button, 2, border_radius=10)

        start_text = self.font.render("START BATTLE!", True, (255, 255, 255))
        start_rect = start_text.get_rect(center=self.start_button.center)
        self.screen.blit(start_text, start_rect)

        if not can_start:
            hint = self.small_font.render("Select a class to continue", True, (200, 100, 100))
            hint_rect = hint.get_rect(center=(400, 575))
            self.screen.blit(hint, hint_rect)

    def start_battle(self):
        """Initialize the battle after character creation"""
        name = self.player_name if self.player_name else "Hero"

        if self.selected_class == 'warrior':
            self.player = Warrior(name)
        elif self.selected_class == 'mage':
            self.player = Mage(name)
        elif self.selected_class == 'archer':
            self.player = Archer(name)
        elif self.selected_class == 'paladin':
            self.player = Paladin(name)

        self.game_state = "boss_selection"  # Go to boss selection instead of battle
        self.add_message("Choose your opponent!")

    def draw_boss_selection(self, mouse_pos):
        """Draw boss selection screen"""
        self.screen.fill((20, 20, 40))

        # Title
        title = self.title_font.render("Choose Your Opponent", True, (255, 69, 0))
        title_rect = title.get_rect(center=(400, 40))
        self.screen.blit(title, title_rect)

        # Boss cards - 2x2 grid
        bosses = [
            ('wizard', 'Evil Wizard\nMalakar', 150, 180, (138, 43, 226), "Dark magic user"),
            ('dragon', 'Fire Dragon\nInfernius', 550, 180, (255, 69, 0), "Burning breath attacks"),
            ('titan', 'Ice Titan\nFrostbane', 150, 380, (0, 191, 255), "Defensive ice fortress"),
            ('assassin', 'Shadow Assassin\nNyx', 550, 380, (64, 64, 64), "Fast critical strikes")
        ]

        for boss_id, boss_name, x, y, color, desc in bosses:
            rect = pygame.Rect(x, y, 200, 160)

            is_hover = rect.collidepoint(mouse_pos)

            # Draw card
            pygame.draw.rect(self.screen, (0, 0, 0), rect, border_radius=10)
            border_color = tuple(min(c + 50, 255) for c in color) if is_hover else color
            pygame.draw.rect(self.screen, border_color, rect, 3, border_radius=10)

            # Boss name
            lines = boss_name.split('\n')
            y_offset = y + 20
            for line in lines:
                name_surf = self.small_font.render(line, True, (255, 255, 255))
                name_rect = name_surf.get_rect(center=(x + 100, y_offset))
                self.screen.blit(name_surf, name_rect)
                y_offset += 25

            # Description
            desc_surf = self.small_font.render(desc, True, (200, 200, 200))
            desc_rect = desc_surf.get_rect(center=(x + 100, y + 110))
            self.screen.blit(desc_surf, desc_rect)

            # Store rect for click detection
            if not hasattr(self, 'boss_buttons'):
                self.boss_buttons = {}
            self.boss_buttons[boss_id] = rect

        # Instructions
        inst = self.font.render("Click to select your opponent", True, (255, 255, 255))
        self.screen.blit(inst, (180, 560))

    def draw_difficulty_selection(self, mouse_pos):
        """Draw difficulty selection screen"""
        self.screen.fill((20, 20, 40))

        # Title
        title = self.title_font.render("Choose Difficulty", True, (255, 215, 0))
        title_rect = title.get_rect(center=(400, 60))
        self.screen.blit(title, title_rect)

        # Difficulty cards
        difficulties = [
            ('easy', 'Easy', 0.8, 100, 200, (100, 255, 100), "80% stats"),
            ('normal', 'Normal', 1.0, 250, 200, (100, 100, 255), "100% stats"),
            ('hard', 'Hard', 1.3, 400, 200, (255, 140, 0), "130% stats"),
            ('nightmare', 'Nightmare', 1.7, 550, 200, (255, 50, 50), "170% stats")
        ]

        for diff_id, diff_name, multiplier, x, y, color, desc in difficulties:
            rect = pygame.Rect(x, 200, 140, 200)

            is_hover = rect.collidepoint(mouse_pos)

            # Draw card
            pygame.draw.rect(self.screen, (0, 0, 0), rect, border_radius=10)
            border_color = tuple(min(c + 50, 255) for c in color) if is_hover else color
            pygame.draw.rect(self.screen, border_color, rect, 3, border_radius=10)

            # Difficulty name
            name_surf = self.font.render(diff_name, True, (255, 255, 255))
            name_rect = name_surf.get_rect(center=(x + 70, y + 240))
            self.screen.blit(name_surf, name_rect)

            # Stats
            stat_surf = self.small_font.render(desc, True, (200, 200, 200))
            stat_rect = stat_surf.get_rect(center=(x + 70, y + 270))
            self.screen.blit(stat_surf, stat_rect)

            # Reward multiplier
            reward = f"XP x{multiplier}"
            reward_surf = self.small_font.render(reward, True, (255, 215, 0))
            reward_rect = reward_surf.get_rect(center=(x + 70, y + 300))
            self.screen.blit(reward_surf, reward_rect)

            # Store rect
            if not hasattr(self, 'difficulty_buttons'):
                self.difficulty_buttons = {}
            self.difficulty_buttons[diff_id] = (rect, multiplier)

        # Instructions
        inst = self.font.render("Click to select difficulty", True, (255, 255, 255))
        self.screen.blit(inst, (220, 480))

    def run(self):
        running = True

        while running:
            mouse_pos = pygame.mouse.get_pos()

            # Update game state
            if self.game_state not in ["character_creation", "boss_selection", "difficulty_selection"]:
                self.update()

            # Draw based on game state
            if self.game_state == "character_creation":
                self.draw_character_creation(mouse_pos)
            elif self.game_state == "boss_selection":
                self.draw_boss_selection(mouse_pos)
            elif self.game_state == "difficulty_selection":
                self.draw_difficulty_selection(mouse_pos)
            else:
                self.draw_battle_scene(mouse_pos)

            # Event handling
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

                # Character creation events
                if self.game_state == "character_creation":
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        # Check class selection
                        for class_id, button_rect in self.class_buttons.items():
                            if button_rect.collidepoint(event.pos):
                                self.selected_class = class_id

                        # Check name input box
                        input_box = pygame.Rect(50, 440, 700, 40)
                        if input_box.collidepoint(event.pos):
                            self.name_active = True
                        else:
                            self.name_active = False

                        # Check start button
                        if self.start_button.collidepoint(event.pos) and self.selected_class:
                            self.start_battle()

                    elif event.type == pygame.KEYDOWN and self.name_active:
                        if event.key == pygame.K_RETURN:
                            self.name_active = False
                        elif event.key == pygame.K_BACKSPACE:
                            self.player_name = self.player_name[:-1]
                        elif len(self.player_name) < 15:  # Max name length
                            if event.unicode.isprintable():
                                self.player_name += event.unicode

                # Boss selection events
                elif self.game_state == "boss_selection" and event.type == pygame.MOUSEBUTTONDOWN:
                    if hasattr(self, 'boss_buttons'):
                        for boss_id, button_rect in self.boss_buttons.items():
                            if button_rect.collidepoint(event.pos):
                                self.selected_boss_type = boss_id
                                self.game_state = "difficulty_selection"

                # Difficulty selection events
                elif self.game_state == "difficulty_selection" and event.type == pygame.MOUSEBUTTONDOWN:
                    if hasattr(self, 'difficulty_buttons'):
                        for diff_id, (button_rect, multiplier) in self.difficulty_buttons.items():
                            if button_rect.collidepoint(event.pos):
                                self.selected_difficulty = multiplier
                                # Create the boss based on selection
                                if self.selected_boss_type == 'wizard':
                                    self.wizard = EvilWizard("Malakar the Malevolent", self.selected_difficulty)
                                elif self.selected_boss_type == 'dragon':
                                    self.wizard = FireDragon("Infernius the Scorcher", self.selected_difficulty)
                                elif self.selected_boss_type == 'titan':
                                    self.wizard = IceTitan("Frostbane the Frozen", self.selected_difficulty)
                                elif self.selected_boss_type == 'assassin':
                                    self.wizard = ShadowAssassin("Nyx the Silent", self.selected_difficulty)
                                # Start the battle
                                self.game_state = "player_turn"
                                self.add_message("Battle started!")
                                self.add_message("Choose your action!")

                # Battle events
                elif event.type == pygame.MOUSEBUTTONDOWN and self.game_state == "player_turn":
                    # Handle main menu
                    if self.main_menu_active:
                        if self.main_menu_buttons.get('restart') and \
                           self.main_menu_buttons['restart'].collidepoint(event.pos):
                            # Restart the battle
                            self.restart_battle()
                            self.main_menu_active = False

                        elif self.main_menu_buttons.get('cancel') and \
                             self.main_menu_buttons['cancel'].collidepoint(event.pos):
                            # Close menu and return to battle
                            self.main_menu_active = False

                    # Handle special menu
                    elif self.special_menu_active:
                        # Warrior abilities
                        if isinstance(self.player, Warrior):
                            if self.special_buttons.get('rage_strike') and \
                               self.special_buttons['rage_strike'].collidepoint(event.pos):
                                if self.player.rage_stacks >= 3:
                                    self.use_rage_strike()
                                    self.special_menu_active = False

                            elif self.special_buttons.get('shield_wall') and \
                                 self.special_buttons['shield_wall'].collidepoint(event.pos):
                                if not self.player.shield_active:
                                    self.use_shield_wall()
                                    self.special_menu_active = False

                        # Mage abilities
                        elif isinstance(self.player, Mage):
                            if self.special_buttons.get('fireball') and \
                               self.special_buttons['fireball'].collidepoint(event.pos):
                                if self.player.mana >= 40:
                                    self.use_fireball()
                                    self.special_menu_active = False

                            elif self.special_buttons.get('ice_shield') and \
                                 self.special_buttons['ice_shield'].collidepoint(event.pos):
                                if self.player.mana >= 30:
                                    self.use_ice_shield()
                                    self.special_menu_active = False

                        # Archer abilities
                        elif isinstance(self.player, Archer):
                            if self.special_buttons.get('multishot') and \
                               self.special_buttons['multishot'].collidepoint(event.pos):
                                if self.player.focus >= 2:
                                    self.use_multishot()
                                    self.special_menu_active = False

                            elif self.special_buttons.get('stun_arrow') and \
                                 self.special_buttons['stun_arrow'].collidepoint(event.pos):
                                if self.player.focus >= 4:
                                    self.use_stun_arrow()
                                    self.special_menu_active = False

                        # Paladin abilities
                        elif isinstance(self.player, Paladin):
                            if self.special_buttons.get('divine_shield') and \
                               self.special_buttons['divine_shield'].collidepoint(event.pos):
                                if self.player.holy_power >= 2:
                                    self.use_divine_shield()
                                    self.special_menu_active = False

                            elif self.special_buttons.get('lay_on_hands') and \
                                 self.special_buttons['lay_on_hands'].collidepoint(event.pos):
                                if self.player.holy_power >= 4:
                                    self.use_lay_on_hands()
                                    self.special_menu_active = False

                        # Cancel button for all classes
                        if self.special_buttons.get('cancel') and \
                             self.special_buttons['cancel'].collidepoint(event.pos):
                            self.special_menu_active = False
                            self.add_message("Cancelled.")

                    # Handle main buttons
                    elif self.buttons['attack'].collidepoint(event.pos):
                        self.player_attack()

                    elif self.buttons['special'].collidepoint(event.pos):
                        self.special_menu_active = True

                    elif self.buttons['heal'].collidepoint(event.pos):
                        self.player_heal()

                    elif self.buttons['menu'].collidepoint(event.pos):
                        self.open_menu()

            pygame.display.flip()
            self.clock.tick(60)

        pygame.quit()

if __name__ == "__main__":
    game = VisualBattleGame()
    game.run()