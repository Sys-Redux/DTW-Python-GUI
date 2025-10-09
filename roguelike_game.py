#!/usr/bin/env python3
"""
Tiny Swords Roguelike - A survival roguelike game inspired by Don't Starve Together
Using assets from the Tiny Swords pack
"""

import pygame
import random
import math
import os
from enum import Enum
from dataclasses import dataclass
from typing import List, Tuple, Optional, Dict

# Initialize Pygame
pygame.init()

# Constants
SCREEN_WIDTH = 1024
SCREEN_HEIGHT = 768
TILE_SIZE = 32
FPS = 60

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
DARK_OVERLAY = (0, 0, 20, 180)
UI_BG = (20, 20, 30, 200)
HEALTH_COLOR = (220, 50, 50)
HUNGER_COLOR = (255, 165, 0)
SANITY_COLOR = (138, 43, 226)

# Game constants
DAY_LENGTH = 480  # 8 seconds per day at 60 FPS
NIGHT_LENGTH = 360  # 6 seconds per night
HUNGER_DECAY_RATE = 0.02  # Per second
SANITY_DECAY_NIGHT = 0.05  # Per second at night
WORLD_SIZE = 100  # 100x100 tiles


class TileType(Enum):
    """Types of terrain tiles"""
    GRASS = 0
    WATER = 1
    SAND = 2
    STONE = 3


class ResourceType(Enum):
    """Types of resources"""
    WOOD = "wood"
    STONE = "stone"
    BERRIES = "berries"
    MEAT = "meat"


class ItemType(Enum):
    """Types of items"""
    AXE = "axe"
    PICKAXE = "pickaxe"
    SWORD = "sword"
    TORCH = "torch"
    BERRIES = "berries"
    COOKED_MEAT = "cooked_meat"
    CAMPFIRE = "campfire"
    WOODEN_WALL = "wooden_wall"


@dataclass
class Item:
    """Represents an item in inventory"""
    item_type: ItemType
    name: str
    description: str
    stackable: bool
    quantity: int = 1
    durability: Optional[int] = None
    max_durability: Optional[int] = None


@dataclass
class Recipe:
    """Crafting recipe"""
    result: ItemType
    requirements: Dict[ResourceType, int]
    tool_required: Optional[ItemType] = None


class WorldObject:
    """Base class for objects in the world"""
    def __init__(self, x: int, y: int, obj_type: str):
        self.x = x
        self.y = y
        self.obj_type = obj_type
        self.health = 100
        self.max_health = 100
        self.harvestable = True

    def take_damage(self, damage: int) -> bool:
        """Return True if object is destroyed"""
        self.health -= damage
        return self.health <= 0

    def get_screen_pos(self, camera_x: int, camera_y: int) -> Tuple[int, int]:
        """Convert world position to screen position"""
        screen_x = (self.x * TILE_SIZE) - camera_x + SCREEN_WIDTH // 2
        screen_y = (self.y * TILE_SIZE) - camera_y + SCREEN_HEIGHT // 2
        return screen_x, screen_y


class Tree(WorldObject):
    """Tree object that gives wood"""
    def __init__(self, x: int, y: int, variant: int = 1):
        super().__init__(x, y, "tree")
        self.variant = variant
        self.resource_type = ResourceType.WOOD
        self.resource_amount = random.randint(3, 6)
        self.health = 50
        self.max_health = 50


class Rock(WorldObject):
    """Rock object that gives stone"""
    def __init__(self, x: int, y: int, variant: int = 1):
        super().__init__(x, y, "rock")
        self.variant = variant
        self.resource_type = ResourceType.STONE
        self.resource_amount = random.randint(2, 4)
        self.health = 60
        self.max_health = 60


class Bush(WorldObject):
    """Bush object that gives berries"""
    def __init__(self, x: int, y: int, variant: int = 1):
        super().__init__(x, y, "bush")
        self.variant = variant
        self.resource_type = ResourceType.BERRIES
        self.resource_amount = random.randint(1, 3)
        self.health = 20
        self.max_health = 20
        self.regrow_timer = 0
        self.regrow_time = 300  # 5 seconds


class Building(WorldObject):
    """Placeable buildings"""
    def __init__(self, x: int, y: int, building_type: str):
        super().__init__(x, y, building_type)
        self.building_type = building_type

        if building_type == "campfire":
            self.health = 50
            self.max_health = 50
            self.light_radius = 5  # Tiles
            self.fuel = 100
            self.max_fuel = 100
        elif building_type == "wooden_wall":
            self.health = 100
            self.max_health = 100

    def update(self, dt: float):
        """Update building (e.g., campfire fuel)"""
        if self.building_type == "campfire" and self.fuel > 0:
            self.fuel -= dt * 2  # Burns fuel over time
            if self.fuel <= 0:
                self.fuel = 0


class Enemy(WorldObject):
    """Enemy creature"""
    def __init__(self, x: float, y: float, enemy_type: str):
        super().__init__(int(x), int(y), "enemy")
        self.x = float(x)  # Enemies use float positions
        self.y = float(y)
        self.enemy_type = enemy_type
        self.harvestable = False

        # Stats based on type
        if enemy_type == "goblin":
            self.max_health = 30
            self.health = 30
            self.speed = 1.5
            self.damage = 5
            self.detection_range = 8
            self.attack_range = 1.0
        elif enemy_type == "wolf":
            self.max_health = 40
            self.health = 40
            self.speed = 2.5
            self.damage = 8
            self.detection_range = 10
            self.attack_range = 1.0
        elif enemy_type == "wizard_boss":
            self.max_health = 150
            self.health = 150
            self.speed = 1.0
            self.damage = 15
            self.detection_range = 15
            self.attack_range = 5.0

        self.target = None
        self.attack_cooldown = 0
        self.attack_speed = 1.0  # Attacks per second

    def update(self, dt: float, player):
        """Update enemy AI"""
        # Calculate distance to player
        dist = math.sqrt((self.x - player.x)**2 + (self.y - player.y)**2)

        # Detect player
        if dist <= self.detection_range:
            self.target = player

            # Move towards player
            if dist > self.attack_range:
                # Move towards player
                dx = player.x - self.x
                dy = player.y - self.y
                length = math.sqrt(dx*dx + dy*dy)
                if length > 0:
                    dx /= length
                    dy /= length
                    self.x += dx * self.speed * dt
                    self.y += dy * self.speed * dt

            # Attack if in range
            elif self.attack_cooldown <= 0:
                self.attack(player)
                self.attack_cooldown = 1.0 / self.attack_speed

        # Update cooldown
        if self.attack_cooldown > 0:
            self.attack_cooldown -= dt

    def attack(self, player):
        """Attack player"""
        player.take_damage(self.damage)

    def drop_loot(self) -> Dict[ResourceType, int]:
        """Return loot when enemy dies"""
        if self.enemy_type == "goblin":
            return {ResourceType.MEAT: random.randint(1, 2)}
        elif self.enemy_type == "wolf":
            return {ResourceType.MEAT: random.randint(2, 4)}
        elif self.enemy_type == "wizard_boss":
            return {
                ResourceType.MEAT: 5,
                ResourceType.STONE: 10,
                ResourceType.WOOD: 10
            }
        return {}


class Player:
    """Player character with survival stats"""
    def __init__(self, x: float, y: float, char_class: str):
        self.x = x
        self.y = y
        self.char_class = char_class

        # Survival stats
        self.max_health = 100
        self.health = 100
        self.max_hunger = 100
        self.hunger = 100
        self.max_sanity = 100
        self.sanity = 100

        # Movement
        self.speed = 8.0  # Increased from 3.0 for faster movement
        self.direction = "down"
        self.sprint_multiplier = 1.5  # Hold shift to sprint

        # Combat
        self.attack_cooldown = 0
        self.attack_speed = 1.5  # Attacks per second

        # Inventory
        self.inventory: List[Optional[Item]] = [None] * 20
        self.equipped_tool: Optional[Item] = None
        self.hotbar: List[Optional[Item]] = [None] * 5  # Quick access slots
        self.selected_hotbar_slot = 0
        self.resources: Dict[ResourceType, int] = {
            ResourceType.WOOD: 0,
            ResourceType.STONE: 0,
            ResourceType.BERRIES: 0,
            ResourceType.MEAT: 0
        }

        # Animation
        self.frame = 0
        self.animation_timer = 0

    def move(self, dx: float, dy: float, world_objects: List[WorldObject]):
        """Move player with collision detection"""
        # Update direction
        if dx < 0:
            self.direction = "left"
        elif dx > 0:
            self.direction = "right"
        elif dy < 0:
            self.direction = "up"
        elif dy > 0:
            self.direction = "down"

        # Try to move
        new_x = self.x + dx
        new_y = self.y + dy

        # Check bounds
        if 0 <= new_x < WORLD_SIZE and 0 <= new_y < WORLD_SIZE:
            # Simple collision check with objects
            can_move = True
            player_rect = pygame.Rect(new_x - 0.3, new_y - 0.3, 0.6, 0.6)

            for obj in world_objects:
                obj_rect = pygame.Rect(obj.x - 0.4, obj.y - 0.4, 0.8, 0.8)
                if player_rect.colliderect(obj_rect):
                    can_move = False
                    break

            if can_move:
                self.x = new_x
                self.y = new_y

    def update_survival(self, dt: float, is_night: bool):
        """Update survival stats"""
        # Hunger decreases over time
        self.hunger = max(0, self.hunger - HUNGER_DECAY_RATE * dt)

        # Sanity decreases at night
        if is_night:
            self.sanity = max(0, self.sanity - SANITY_DECAY_NIGHT * dt)
        else:
            # Slowly recover sanity during day
            self.sanity = min(self.max_sanity, self.sanity + 0.01 * dt)

        # Health affected by low hunger
        if self.hunger <= 0:
            self.health -= 0.1 * dt

    def eat_food(self, food_item: Item):
        """Consume food to restore hunger"""
        if food_item.item_type == ItemType.BERRIES:
            self.hunger = min(self.max_hunger, self.hunger + 15)
        elif food_item.item_type == ItemType.COOKED_MEAT:
            self.hunger = min(self.max_hunger, self.hunger + 40)
            self.health = min(self.max_health, self.health + 10)

    def cook_food(self) -> bool:
        """Cook raw meat at a campfire to get cooked meat"""
        if self.resources[ResourceType.MEAT] > 0:
            self.resources[ResourceType.MEAT] -= 1
            # Add cooked meat item to inventory
            return True
        return False

    def equip_item(self, item: Item):
        """Equip a tool or weapon"""
        if item.item_type in [ItemType.AXE, ItemType.PICKAXE, ItemType.SWORD, ItemType.TORCH]:
            self.equipped_tool = item

    def add_to_hotbar(self, item: Item, slot: int):
        """Add item to hotbar slot"""
        if 0 <= slot < 5:
            self.hotbar[slot] = item

    def use_hotbar_item(self, slot: int):
        """Use item from hotbar"""
        if 0 <= slot < 5 and self.hotbar[slot]:
            item = self.hotbar[slot]
            if item.item_type in [ItemType.BERRIES, ItemType.COOKED_MEAT]:
                self.eat_food(item)
                self.hotbar[slot] = None
            elif item.item_type in [ItemType.AXE, ItemType.PICKAXE, ItemType.SWORD, ItemType.TORCH]:
                self.equip_item(item)

    def add_resource(self, resource_type: ResourceType, amount: int):
        """Add resources to inventory"""
        self.resources[resource_type] += amount

    def has_resources(self, requirements: Dict[ResourceType, int]) -> bool:
        """Check if player has required resources"""
        for resource, amount in requirements.items():
            if self.resources[resource] < amount:
                return False
        return True

    def consume_resources(self, requirements: Dict[ResourceType, int]):
        """Remove resources from inventory"""
        for resource, amount in requirements.items():
            self.resources[resource] -= amount

    def attack_enemy(self, enemy: Enemy) -> int:
        """Attack an enemy, return damage dealt"""
        base_damage = 10

        # Bonus damage with sword
        if self.equipped_tool and self.equipped_tool.item_type == ItemType.SWORD:
            base_damage = 20
            # Damage tool
            if self.equipped_tool.durability:
                self.equipped_tool.durability -= 1

        enemy.health -= base_damage
        return base_damage

    def take_damage(self, damage: int):
        """Take damage from enemy"""
        self.health = max(0, self.health - damage)
        self.sanity = max(0, self.sanity - 5)  # Losing health also affects sanity


class World:
    """Game world with procedural generation"""
    def __init__(self, seed: Optional[int] = None):
        self.seed = seed if seed else random.randint(0, 999999)
        random.seed(self.seed)

        self.tiles = [[TileType.GRASS for _ in range(WORLD_SIZE)] for _ in range(WORLD_SIZE)]
        self.objects: List[WorldObject] = []
        self.enemies: List[Enemy] = []
        self.buildings: List[Building] = []

        self.generate_world()

    def generate_world(self):
        """Generate procedural world"""
        # Generate water bodies
        for _ in range(5):
            lake_x = random.randint(10, WORLD_SIZE - 10)
            lake_y = random.randint(10, WORLD_SIZE - 10)
            lake_size = random.randint(5, 10)

            for dx in range(-lake_size, lake_size):
                for dy in range(-lake_size, lake_size):
                    if dx*dx + dy*dy < lake_size*lake_size:
                        x, y = lake_x + dx, lake_y + dy
                        if 0 <= x < WORLD_SIZE and 0 <= y < WORLD_SIZE:
                            self.tiles[y][x] = TileType.WATER

        # Generate forests
        for _ in range(150):
            tree_x = random.randint(2, WORLD_SIZE - 3)
            tree_y = random.randint(2, WORLD_SIZE - 3)

            if self.tiles[tree_y][tree_x] == TileType.GRASS:
                variant = random.randint(1, 2)
                self.objects.append(Tree(tree_x, tree_y, variant))

        # Generate rocks
        for _ in range(80):
            rock_x = random.randint(2, WORLD_SIZE - 3)
            rock_y = random.randint(2, WORLD_SIZE - 3)

            if self.tiles[rock_y][rock_x] == TileType.GRASS:
                variant = random.randint(1, 2)
                self.objects.append(Rock(rock_x, rock_y, variant))

        # Generate bushes
        for _ in range(100):
            bush_x = random.randint(2, WORLD_SIZE - 3)
            bush_y = random.randint(2, WORLD_SIZE - 3)

            if self.tiles[bush_y][bush_x] == TileType.GRASS:
                variant = random.randint(1, 2)
                self.objects.append(Bush(bush_x, bush_y, variant))

    def get_tile(self, x: int, y: int) -> TileType:
        """Get tile at position"""
        if 0 <= x < WORLD_SIZE and 0 <= y < WORLD_SIZE:
            return self.tiles[y][x]
        return TileType.WATER

    def get_objects_in_range(self, x: float, y: float, radius: float) -> List[WorldObject]:
        """Get objects within range of position"""
        nearby = []
        for obj in self.objects:
            dist = math.sqrt((obj.x - x)**2 + (obj.y - y)**2)
            if dist <= radius:
                nearby.append(obj)
        return nearby

    def spawn_enemy(self, x: float, y: float, enemy_type: str):
        """Spawn an enemy at position"""
        enemy = Enemy(x, y, enemy_type)
        self.enemies.append(enemy)

    def place_building(self, x: int, y: int, building_type: str) -> bool:
        """Place a building at tile position"""
        # Check if space is clear
        for building in self.buildings:
            if building.x == x and building.y == y:
                return False
        for obj in self.objects:
            if obj.x == x and obj.y == y:
                return False

        building = Building(x, y, building_type)
        self.buildings.append(building)
        return True

    def update_enemies(self, dt: float, player):
        """Update all enemies"""
        for enemy in self.enemies[:]:
            enemy.update(dt, player)
            if enemy.health <= 0:
                self.enemies.remove(enemy)
                # Drop loot
                for resource, amount in enemy.drop_loot().items():
                    player.add_resource(resource, amount)

    def update_buildings(self, dt: float):
        """Update all buildings"""
        for building in self.buildings:
            building.update(dt)


class CraftingSystem:
    """Manages crafting recipes"""
    def __init__(self):
        self.recipes: List[Recipe] = [
            Recipe(ItemType.AXE, {ResourceType.WOOD: 3, ResourceType.STONE: 2}),
            Recipe(ItemType.PICKAXE, {ResourceType.WOOD: 2, ResourceType.STONE: 3}),
            Recipe(ItemType.SWORD, {ResourceType.WOOD: 2, ResourceType.STONE: 4}),
            Recipe(ItemType.TORCH, {ResourceType.WOOD: 2}),
            Recipe(ItemType.CAMPFIRE, {ResourceType.WOOD: 5, ResourceType.STONE: 3}),
            Recipe(ItemType.WOODEN_WALL, {ResourceType.WOOD: 4}),
        ]

    def can_craft(self, player: Player, recipe: Recipe) -> bool:
        """Check if player can craft item"""
        return player.has_resources(recipe.requirements)

    def craft_item(self, player: Player, recipe: Recipe) -> Optional[Item]:
        """Craft an item"""
        if not self.can_craft(player, recipe):
            return None

        player.consume_resources(recipe.requirements)

        # Create item
        if recipe.result == ItemType.AXE:
            return Item(ItemType.AXE, "Axe", "Chop trees for wood", False, 1, 100, 100)
        elif recipe.result == ItemType.PICKAXE:
            return Item(ItemType.PICKAXE, "Pickaxe", "Mine rocks for stone", False, 1, 100, 100)
        elif recipe.result == ItemType.SWORD:
            return Item(ItemType.SWORD, "Sword", "Defend yourself", False, 1, 150, 150)
        elif recipe.result == ItemType.TORCH:
            return Item(ItemType.TORCH, "Torch", "Light source", False, 1, 60, 60)
        elif recipe.result == ItemType.CAMPFIRE:
            return Item(ItemType.CAMPFIRE, "Campfire", "Provides light and warmth", False, 1)
        elif recipe.result == ItemType.WOODEN_WALL:
            return Item(ItemType.WOODEN_WALL, "Wooden Wall", "Basic defense", False, 1)

        return None


class GameState:
    """Main game state"""
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Tiny Swords Roguelike")

        self.clock = pygame.time.Clock()
        self.running = True

        # Game state
        self.state = "menu"  # menu, playing, inventory, crafting, building_placement
        self.world = None
        self.player = None
        self.camera_x = 0
        self.camera_y = 0

        # Building placement
        self.building_to_place: Optional[ItemType] = None
        self.placement_valid = False

        # Time
        self.time = 0  # 0 = dawn, goes to DAY_LENGTH + NIGHT_LENGTH
        self.day_count = 1
        self.last_spawn_time = 0  # Track enemy spawns

        # UI
        self.font = pygame.font.Font(None, 24)
        self.title_font = pygame.font.Font(None, 48)
        self.small_font = pygame.font.Font(None, 18)

        # Crafting
        self.crafting_system = CraftingSystem()

        # Load assets
        self.load_assets()

    def load_assets(self):
        """Load game assets"""
        self.assets = {}
        asset_path = "./assets"

        try:
            # Load character sprites - extract single frame from spritesheet
            for char in ["warrior", "mage", "archer", "paladin"]:
                path = os.path.join(asset_path, f"{char}.png")
                if os.path.exists(path):
                    spritesheet = pygame.image.load(path).convert_alpha()
                    # Extract first frame (assuming 192x192 frames in a row)
                    frame_width = spritesheet.get_height()  # Usually square frames
                    frame = pygame.Surface((frame_width, frame_width), pygame.SRCALPHA)
                    frame.blit(spritesheet, (0, 0), (0, 0, frame_width, frame_width))
                    # Scale down to reasonable size
                    self.assets[char] = pygame.transform.scale(frame, (48, 48))

            # Load environment objects
            for obj in ["tree1", "tree2", "rock1", "rock2", "bush1", "bush2"]:
                path = os.path.join(asset_path, f"{obj}.png")
                if os.path.exists(path):
                    sprite = pygame.image.load(path).convert_alpha()
                    # Scale to reasonable size
                    self.assets[obj] = pygame.transform.scale(sprite, (32, 32))

            # Load wizard sprite
            path = os.path.join(asset_path, "wizard.png")
            if os.path.exists(path):
                spritesheet = pygame.image.load(path).convert_alpha()
                frame_width = spritesheet.get_height()
                frame = pygame.Surface((frame_width, frame_width), pygame.SRCALPHA)
                frame.blit(spritesheet, (0, 0), (0, 0, frame_width, frame_width))
                self.assets["wizard"] = pygame.transform.scale(frame, (48, 48))

        except Exception as e:
            print(f"Error loading assets: {e}")

    def start_game(self, char_class: str):
        """Start a new game"""
        self.world = World()

        # Find a good spawn location (away from water)
        spawn_x, spawn_y = WORLD_SIZE // 2, WORLD_SIZE // 2
        while self.world.get_tile(int(spawn_x), int(spawn_y)) == TileType.WATER:
            spawn_x = random.randint(10, WORLD_SIZE - 10)
            spawn_y = random.randint(10, WORLD_SIZE - 10)

        self.player = Player(spawn_x, spawn_y, char_class)
        self.camera_x = int(spawn_x * TILE_SIZE)
        self.camera_y = int(spawn_y * TILE_SIZE)

        self.state = "playing"
        self.time = 0
        self.day_count = 1

    def handle_events(self):
        """Handle input events"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            elif event.type == pygame.KEYDOWN:
                if self.state == "menu":
                    if event.key == pygame.K_1:
                        self.start_game("warrior")
                    elif event.key == pygame.K_2:
                        self.start_game("mage")
                    elif event.key == pygame.K_3:
                        self.start_game("archer")
                    elif event.key == pygame.K_4:
                        self.start_game("paladin")

                elif self.state == "playing":
                    if event.key == pygame.K_i:
                        self.state = "inventory"
                    elif event.key == pygame.K_c:
                        self.state = "crafting"
                    elif event.key == pygame.K_b:
                        self.state = "building_placement"
                        self.building_to_place = ItemType.CAMPFIRE  # Default
                    elif event.key == pygame.K_ESCAPE:
                        self.state = "menu"
                    elif event.key == pygame.K_SPACE:  # Attack nearby enemies
                        self.handle_attack()
                    elif event.key == pygame.K_e:  # Interact/cook at campfire
                        self.handle_interact()
                    elif event.key == pygame.K_q:  # Drop item
                        self.handle_drop_item()
                    # Hotbar keys
                    elif event.key == pygame.K_1:
                        self.player.selected_hotbar_slot = 0
                        self.player.use_hotbar_item(0)
                    elif event.key == pygame.K_2:
                        self.player.selected_hotbar_slot = 1
                        self.player.use_hotbar_item(1)
                    elif event.key == pygame.K_3:
                        self.player.selected_hotbar_slot = 2
                        self.player.use_hotbar_item(2)
                    elif event.key == pygame.K_4:
                        self.player.selected_hotbar_slot = 3
                        self.player.use_hotbar_item(3)
                    elif event.key == pygame.K_5:
                        self.player.selected_hotbar_slot = 4
                        self.player.use_hotbar_item(4)

                elif self.state == "building_placement":
                    if event.key == pygame.K_ESCAPE:
                        self.state = "playing"
                        self.building_to_place = None
                    elif event.key == pygame.K_1:
                        self.building_to_place = ItemType.CAMPFIRE
                    elif event.key == pygame.K_2:
                        self.building_to_place = ItemType.WOODEN_WALL

                elif self.state in ["inventory", "crafting"]:
                    if event.key == pygame.K_ESCAPE or event.key == pygame.K_i or event.key == pygame.K_c:
                        self.state = "playing"

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if self.state == "playing" and event.button == 1:  # Left click
                    self.handle_gather_action()
                elif self.state == "building_placement" and event.button == 1:  # Place building
                    self.handle_place_building()

    def handle_gather_action(self):
        """Handle gathering resources"""
        if not self.player:
            return

        # Get mouse position
        mouse_x, mouse_y = pygame.mouse.get_pos()

        # Convert to world position
        world_x = (mouse_x - SCREEN_WIDTH // 2 + self.camera_x) / TILE_SIZE
        world_y = (mouse_y - SCREEN_HEIGHT // 2 + self.camera_y) / TILE_SIZE

        # Check distance
        dist = math.sqrt((world_x - self.player.x)**2 + (world_y - self.player.y)**2)
        if dist > 2:  # Too far
            return

        # Find object at position
        for obj in self.world.objects:
            if abs(obj.x - world_x) < 0.5 and abs(obj.y - world_y) < 0.5:
                if obj.harvestable:
                    self.gather_resource(obj)
                    break

    def gather_resource(self, obj: WorldObject):
        """Gather resource from object"""
        # Check if player has right tool
        if isinstance(obj, Tree):
            if self.player.equipped_tool and self.player.equipped_tool.item_type == ItemType.AXE:
                damage = 20
            else:
                damage = 5
        elif isinstance(obj, Rock):
            if self.player.equipped_tool and self.player.equipped_tool.item_type == ItemType.PICKAXE:
                damage = 20
            else:
                damage = 5
        elif isinstance(obj, Bush):
            damage = 20  # Bushes don't need tools
        else:
            return

        # Damage object
        destroyed = obj.take_damage(damage)

        if destroyed:
            # Give resources
            if hasattr(obj, 'resource_type'):
                self.player.add_resource(obj.resource_type, obj.resource_amount)

            # Remove object
            self.world.objects.remove(obj)

    def handle_attack(self):
        """Attack nearest enemy"""
        if not self.player or not self.world:
            return

        # Find nearest enemy within range
        nearest_enemy = None
        nearest_dist = float('inf')
        attack_range = 2.0

        for enemy in self.world.enemies:
            dist = math.sqrt((enemy.x - self.player.x)**2 + (enemy.y - self.player.y)**2)
            if dist < attack_range and dist < nearest_dist:
                nearest_enemy = enemy
                nearest_dist = dist

        if nearest_enemy:
            damage = self.player.attack_enemy(nearest_enemy)

    def handle_interact(self):
        """Interact with nearby objects (cook at campfire, etc)"""
        if not self.player or not self.world:
            return

        # Find nearest campfire
        nearest_fire = None
        nearest_dist = float('inf')
        interact_range = 2.0

        for building in self.world.buildings:
            if building.building_type == "campfire":
                dist = math.sqrt((building.x - self.player.x)**2 + (building.y - self.player.y)**2)
                if dist < interact_range and dist < nearest_dist:
                    nearest_fire = building
                    nearest_dist = dist

        if nearest_fire and nearest_fire.fuel > 0:
            # Cook meat
            if self.player.cook_food():
                # Successfully cooked meat
                pass

    def handle_drop_item(self):
        """Drop currently equipped item"""
        if self.player.equipped_tool:
            # Add to hotbar or drop
            for i in range(5):
                if self.player.hotbar[i] is None:
                    self.player.hotbar[i] = self.player.equipped_tool
                    self.player.equipped_tool = None
                    break

    def handle_place_building(self):
        """Place a building at mouse position"""
        if not self.player or not self.world or not self.building_to_place:
            return

        # Get mouse position
        mouse_x, mouse_y = pygame.mouse.get_pos()

        # Convert to tile position
        tile_x = int((mouse_x - SCREEN_WIDTH // 2 + self.camera_x) / TILE_SIZE)
        tile_y = int((mouse_y - SCREEN_HEIGHT // 2 + self.camera_y) / TILE_SIZE)

        # Check distance
        dist = math.sqrt((tile_x - self.player.x)**2 + (tile_y - self.player.y)**2)
        if dist > 5:  # Too far
            return

        # Try to place building
        building_name = self.building_to_place.value
        if self.world.place_building(tile_x, tile_y, building_name):
            self.state = "playing"
            self.building_to_place = None

    def update(self, dt: float):
        """Update game state"""
        if self.state not in ["playing", "building_placement"]:
            return

        if not self.player or not self.world:
            return

        # Handle movement
        keys = pygame.key.get_pressed()
        dx = dy = 0

        # Check for sprint
        speed = self.player.speed
        if keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]:
            speed *= self.player.sprint_multiplier
            # Sprinting increases hunger drain
            self.player.hunger = max(0, self.player.hunger - 0.05 * dt)

        if keys[pygame.K_w] or keys[pygame.K_UP]:
            dy = -speed * dt
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            dy = speed * dt
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            dx = -speed * dt
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            dx = speed * dt

        if dx != 0 or dy != 0:
            self.player.move(dx, dy, self.world.objects)

        # Update camera to follow player
        self.camera_x = int(self.player.x * TILE_SIZE)
        self.camera_y = int(self.player.y * TILE_SIZE)

        # Update time
        self.time += 1
        if self.time >= DAY_LENGTH + NIGHT_LENGTH:
            self.time = 0
            self.day_count += 1

        # Update survival stats
        is_night = self.time >= DAY_LENGTH
        self.player.update_survival(dt, is_night)

        # Update enemies
        self.world.update_enemies(dt, self.player)

        # Update buildings
        self.world.update_buildings(dt)

        # Spawn enemies at night
        if is_night and self.time - self.last_spawn_time > 180:  # Every 3 seconds
            self.spawn_enemy_near_player()
            self.last_spawn_time = self.time

        # Check death
        if self.player.health <= 0:
            self.state = "menu"

    def spawn_enemy_near_player(self):
        """Spawn an enemy near the player but not too close"""
        if not self.player or not self.world:
            return

        # Spawn 10-20 tiles away from player
        angle = random.random() * 2 * math.pi
        distance = random.uniform(10, 20)

        spawn_x = self.player.x + math.cos(angle) * distance
        spawn_y = self.player.y + math.sin(angle) * distance

        # Keep within bounds
        spawn_x = max(5, min(WORLD_SIZE - 5, spawn_x))
        spawn_y = max(5, min(WORLD_SIZE - 5, spawn_y))

        # Choose enemy type based on day
        if self.day_count == 1:
            enemy_type = "goblin"
        elif self.day_count < 5:
            enemy_type = random.choice(["goblin", "wolf"])
        else:
            enemy_type = random.choice(["goblin", "wolf", "wizard_boss"])

        self.world.spawn_enemy(spawn_x, spawn_y, enemy_type)

    def draw(self):
        """Render game"""
        self.screen.fill(BLACK)

        if self.state == "menu":
            self.draw_menu()
        elif self.state == "playing":
            self.draw_game()
        elif self.state == "building_placement":
            self.draw_game()  # Draw game in background
            self.draw_building_placement()
        elif self.state == "inventory":
            self.draw_inventory()
        elif self.state == "crafting":
            self.draw_crafting()

        pygame.display.flip()

    def draw_menu(self):
        """Draw main menu"""
        title = self.title_font.render("TINY SWORDS ROGUELIKE", True, WHITE)
        self.screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 150))

        subtitle = self.font.render("Choose Your Character", True, WHITE)
        self.screen.blit(subtitle, (SCREEN_WIDTH // 2 - subtitle.get_width() // 2, 250))

        classes = [
            ("1. Warrior - High health, strong melee", 320),
            ("2. Mage - Magic abilities, low health", 360),
            ("3. Archer - Ranged attacks, balanced", 400),
            ("4. Paladin - Support abilities, healing", 440)
        ]

        for text, y in classes:
            surf = self.font.render(text, True, WHITE)
            self.screen.blit(surf, (SCREEN_WIDTH // 2 - surf.get_width() // 2, y))

    def draw_game(self):
        """Draw main game view"""
        if not self.world or not self.player:
            return

        # Draw tiles
        start_x = max(0, int((self.camera_x - SCREEN_WIDTH // 2) / TILE_SIZE))
        end_x = min(WORLD_SIZE, int((self.camera_x + SCREEN_WIDTH // 2) / TILE_SIZE) + 1)
        start_y = max(0, int((self.camera_y - SCREEN_HEIGHT // 2) / TILE_SIZE))
        end_y = min(WORLD_SIZE, int((self.camera_y + SCREEN_HEIGHT // 2) / TILE_SIZE) + 1)

        for y in range(start_y, end_y):
            for x in range(start_x, end_x):
                tile = self.world.get_tile(x, y)
                screen_x = (x * TILE_SIZE) - self.camera_x + SCREEN_WIDTH // 2
                screen_y = (y * TILE_SIZE) - self.camera_y + SCREEN_HEIGHT // 2

                if tile == TileType.GRASS:
                    color = (34, 139, 34)
                elif tile == TileType.WATER:
                    color = (30, 144, 255)
                else:
                    color = (128, 128, 128)

                pygame.draw.rect(self.screen, color, (screen_x, screen_y, TILE_SIZE, TILE_SIZE))

        # Draw objects
        for obj in self.world.objects:
            screen_x, screen_y = obj.get_screen_pos(self.camera_x, self.camera_y)

            if -TILE_SIZE < screen_x < SCREEN_WIDTH and -TILE_SIZE < screen_y < SCREEN_HEIGHT:
                # Try to use sprite, otherwise use colored rect
                sprite_key = None
                if isinstance(obj, Tree):
                    sprite_key = f"tree{obj.variant}"
                elif isinstance(obj, Rock):
                    sprite_key = f"rock{obj.variant}"
                elif isinstance(obj, Bush):
                    sprite_key = f"bush{obj.variant}"

                if sprite_key and sprite_key in self.assets:
                    sprite = self.assets[sprite_key]
                    self.screen.blit(sprite, (screen_x - sprite.get_width() // 2, screen_y - sprite.get_height() // 2))
                else:
                    # Fallback to colored rectangles
                    if isinstance(obj, Tree):
                        pygame.draw.circle(self.screen, (34, 100, 34), (screen_x, screen_y), 12)
                    elif isinstance(obj, Rock):
                        pygame.draw.circle(self.screen, (128, 128, 128), (screen_x, screen_y), 10)
                    elif isinstance(obj, Bush):
                        pygame.draw.circle(self.screen, (50, 150, 50), (screen_x, screen_y), 8)

        # Draw buildings
        for building in self.world.buildings:
            screen_x, screen_y = building.get_screen_pos(self.camera_x, self.camera_y)

            if -TILE_SIZE < screen_x < SCREEN_WIDTH and -TILE_SIZE < screen_y < SCREEN_HEIGHT:
                if building.building_type == "campfire":
                    pygame.draw.circle(self.screen, (255, 100, 0), (screen_x, screen_y), 10)
                    # Draw light radius if night
                    if self.time >= DAY_LENGTH and building.fuel > 0:
                        pygame.draw.circle(self.screen, (255, 200, 100, 50), (screen_x, screen_y), int(building.light_radius * TILE_SIZE))
                elif building.building_type == "wooden_wall":
                    pygame.draw.rect(self.screen, (139, 69, 19), (screen_x - 12, screen_y - 12, 24, 24))

        # Draw enemies
        for enemy in self.world.enemies:
            screen_x, screen_y = enemy.get_screen_pos(self.camera_x, self.camera_y)

            if -TILE_SIZE < screen_x < SCREEN_WIDTH and -TILE_SIZE < screen_y < SCREEN_HEIGHT:
                if enemy.enemy_type == "goblin":
                    pygame.draw.circle(self.screen, (0, 150, 0), (screen_x, screen_y), 10)
                elif enemy.enemy_type == "wolf":
                    pygame.draw.circle(self.screen, (100, 100, 100), (screen_x, screen_y), 12)
                elif enemy.enemy_type == "wizard_boss":
                    # Try to use wizard sprite
                    if "wizard" in self.assets:
                        sprite = self.assets["wizard"]
                        self.screen.blit(sprite, (screen_x - sprite.get_width() // 2, screen_y - sprite.get_height() // 2))
                    else:
                        pygame.draw.circle(self.screen, (128, 0, 128), (screen_x, screen_y), 16)

                # Draw health bar above enemy
                health_width = 30
                health_fill = int((enemy.health / enemy.max_health) * health_width)
                pygame.draw.rect(self.screen, (50, 50, 50), (screen_x - health_width // 2, screen_y - 25, health_width, 4))
                pygame.draw.rect(self.screen, (255, 0, 0), (screen_x - health_width // 2, screen_y - 25, health_fill, 4))

        # Draw player
        player_screen_x = SCREEN_WIDTH // 2
        player_screen_y = SCREEN_HEIGHT // 2

        if self.player.char_class in self.assets:
            sprite = self.assets[self.player.char_class]
            self.screen.blit(sprite, (player_screen_x - sprite.get_width() // 2, player_screen_y - sprite.get_height() // 2))
        else:
            pygame.draw.circle(self.screen, (255, 255, 0), (player_screen_x, player_screen_y), 16)

        # Apply night overlay
        if self.time >= DAY_LENGTH:
            night_alpha = min(180, int((self.time - DAY_LENGTH) / NIGHT_LENGTH * 180))
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            overlay.fill((0, 0, 20))
            overlay.set_alpha(night_alpha)
            self.screen.blit(overlay, (0, 0))

        # Draw HUD
        self.draw_hud()

    def draw_hud(self):
        """Draw HUD elements"""
        if not self.player:
            return

        # Background panel
        pygame.draw.rect(self.screen, UI_BG, (10, 10, 300, 120))

        # Health bar
        self.draw_bar(20, 20, 280, 20, self.player.health, self.player.max_health, HEALTH_COLOR, "Health")

        # Hunger bar
        self.draw_bar(20, 50, 280, 20, self.player.hunger, self.player.max_hunger, HUNGER_COLOR, "Hunger")

        # Sanity bar
        self.draw_bar(20, 80, 280, 20, self.player.sanity, self.player.max_sanity, SANITY_COLOR, "Sanity")

        # Day counter
        day_text = self.font.render(f"Day {self.day_count}", True, WHITE)
        self.screen.blit(day_text, (20, 105))

        # Time of day
        if self.time < DAY_LENGTH:
            time_text = "DAY"
            time_color = (255, 255, 100)
        else:
            time_text = "NIGHT"
            time_color = (100, 100, 255)
        time_surf = self.font.render(time_text, True, time_color)
        self.screen.blit(time_surf, (250, 105))

        # Resources panel
        pygame.draw.rect(self.screen, UI_BG, (SCREEN_WIDTH - 210, 10, 200, 120))

        y_offset = 20
        for resource, amount in self.player.resources.items():
            text = self.small_font.render(f"{resource.value.title()}: {amount}", True, WHITE)
            self.screen.blit(text, (SCREEN_WIDTH - 200, y_offset))
            y_offset += 25

        # Enemy count
        enemy_count = len(self.world.enemies) if self.world else 0
        enemy_text = self.small_font.render(f"Enemies: {enemy_count}", True, (255, 100, 100))
        self.screen.blit(enemy_text, (SCREEN_WIDTH - 200, y_offset))

        # Hotbar at bottom center
        hotbar_width = 5 * 52 + 10
        hotbar_x = SCREEN_WIDTH // 2 - hotbar_width // 2
        hotbar_y = SCREEN_HEIGHT - 140

        pygame.draw.rect(self.screen, UI_BG, (hotbar_x - 5, hotbar_y - 5, hotbar_width, 62))

        for i in range(5):
            slot_x = hotbar_x + i * 52
            slot_color = (100, 100, 255) if i == self.player.selected_hotbar_slot else (80, 80, 80)
            pygame.draw.rect(self.screen, slot_color, (slot_x, hotbar_y, 48, 48))
            pygame.draw.rect(self.screen, WHITE, (slot_x, hotbar_y, 48, 48), 2)

            # Draw number
            num_text = self.small_font.render(str(i + 1), True, WHITE)
            self.screen.blit(num_text, (slot_x + 2, hotbar_y + 2))

            # Draw item if present
            if self.player.hotbar[i]:
                item = self.player.hotbar[i]
                item_name = item.item_type.value[:3].upper()
                item_text = self.small_font.render(item_name, True, WHITE)
                self.screen.blit(item_text, (slot_x + 12, hotbar_y + 18))

        # Equipped tool display
        if self.player.equipped_tool:
            tool_text = self.font.render(f"Equipped: {self.player.equipped_tool.name}", True, WHITE)
            self.screen.blit(tool_text, (SCREEN_WIDTH // 2 - tool_text.get_width() // 2, hotbar_y - 30))

            # Durability bar if applicable
            if self.player.equipped_tool.durability is not None:
                dur_x = SCREEN_WIDTH // 2 - 50
                dur_y = hotbar_y - 10
                dur_width = 100
                dur_fill = int((self.player.equipped_tool.durability / self.player.equipped_tool.max_durability) * dur_width)
                pygame.draw.rect(self.screen, (50, 50, 50), (dur_x, dur_y, dur_width, 4))
                pygame.draw.rect(self.screen, (100, 255, 100), (dur_x, dur_y, dur_fill, 4))

        # Controls hint
        hint_bg = pygame.Surface((750, 90))
        hint_bg.fill((20, 20, 30))
        hint_bg.set_alpha(200)
        self.screen.blit(hint_bg, (SCREEN_WIDTH // 2 - 375, SCREEN_HEIGHT - 60))

        hints = [
            "WASD: Move | Shift: Sprint | Click: Gather | Space: Attack",
            "1-5: Hotbar | E: Interact/Cook | Q: Drop | I: Inv | C: Craft | B: Build"
        ]
        for i, hint in enumerate(hints):
            text = self.small_font.render(hint, True, WHITE)
            self.screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, SCREEN_HEIGHT - 50 + i * 20))

    def draw_bar(self, x: int, y: int, width: int, height: int, current: float, maximum: float, color: Tuple[int, int, int], label: str):
        """Draw a status bar"""
        # Background
        pygame.draw.rect(self.screen, (50, 50, 50), (x, y, width, height))

        # Fill
        fill_width = int((current / maximum) * width)
        pygame.draw.rect(self.screen, color, (x, y, fill_width, height))

        # Border
        pygame.draw.rect(self.screen, WHITE, (x, y, width, height), 2)

        # Label
        text = self.small_font.render(f"{label}: {int(current)}/{int(maximum)}", True, WHITE)
        self.screen.blit(text, (x + 5, y + 2))

    def draw_inventory(self):
        """Draw inventory screen"""
        self.draw_game()  # Draw game in background

        # Overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.fill((0, 0, 0))
        overlay.set_alpha(180)
        self.screen.blit(overlay, (0, 0))

        # Inventory panel
        panel_width = 600
        panel_height = 500
        panel_x = SCREEN_WIDTH // 2 - panel_width // 2
        panel_y = SCREEN_HEIGHT // 2 - panel_height // 2

        pygame.draw.rect(self.screen, (30, 30, 40), (panel_x, panel_y, panel_width, panel_height))
        pygame.draw.rect(self.screen, WHITE, (panel_x, panel_y, panel_width, panel_height), 3)

        # Title
        title = self.title_font.render("INVENTORY", True, WHITE)
        self.screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, panel_y + 20))

        # Close hint
        hint = self.small_font.render("Press ESC or I to close", True, WHITE)
        self.screen.blit(hint, (SCREEN_WIDTH // 2 - hint.get_width() // 2, panel_y + panel_height - 30))

    def draw_crafting(self):
        """Draw crafting screen"""
        self.draw_game()  # Draw game in background

        # Overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.fill((0, 0, 0))
        overlay.set_alpha(180)
        self.screen.blit(overlay, (0, 0))

        # Crafting panel
        panel_width = 700
        panel_height = 550
        panel_x = SCREEN_WIDTH // 2 - panel_width // 2
        panel_y = SCREEN_HEIGHT // 2 - panel_height // 2

        pygame.draw.rect(self.screen, (30, 30, 40), (panel_x, panel_y, panel_width, panel_height))
        pygame.draw.rect(self.screen, WHITE, (panel_x, panel_y, panel_width, panel_height), 3)

        # Title
        title = self.title_font.render("CRAFTING", True, WHITE)
        self.screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, panel_y + 20))

        # List recipes
        y_offset = panel_y + 100
        for i, recipe in enumerate(self.crafting_system.recipes):
            can_craft = self.crafting_system.can_craft(self.player, recipe)
            color = (100, 255, 100) if can_craft else (150, 150, 150)

            # Recipe name
            name = recipe.result.value.replace("_", " ").title()
            text = self.font.render(f"{i+1}. {name}", True, color)
            self.screen.blit(text, (panel_x + 50, y_offset))

            # Requirements
            req_text = " | ".join([f"{res.value}: {amt}" for res, amt in recipe.requirements.items()])
            req_surf = self.small_font.render(f"   Requires: {req_text}", True, color)
            self.screen.blit(req_surf, (panel_x + 50, y_offset + 25))

            y_offset += 60

        # Close hint
        hint = self.small_font.render("Press ESC or C to close | Press 1-4 to craft", True, WHITE)
        self.screen.blit(hint, (SCREEN_WIDTH // 2 - hint.get_width() // 2, panel_y + panel_height - 30))

    def draw_building_placement(self):
        """Draw building placement overlay"""
        # Semi-transparent overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.fill((0, 0, 0))
        overlay.set_alpha(100)
        self.screen.blit(overlay, (0, 0))

        # Get mouse tile position
        mouse_x, mouse_y = pygame.mouse.get_pos()
        tile_x = int((mouse_x - SCREEN_WIDTH // 2 + self.camera_x) / TILE_SIZE)
        tile_y = int((mouse_y - SCREEN_HEIGHT // 2 + self.camera_y) / TILE_SIZE)

        # Calculate screen position of tile
        screen_x = (tile_x * TILE_SIZE) - self.camera_x + SCREEN_WIDTH // 2
        screen_y = (tile_y * TILE_SIZE) - self.camera_y + SCREEN_HEIGHT // 2

        # Check if placement is valid
        dist = math.sqrt((tile_x - self.player.x)**2 + (tile_y - self.player.y)**2)
        valid = dist <= 5

        # Draw placement indicator
        color = (100, 255, 100, 128) if valid else (255, 100, 100, 128)
        pygame.draw.rect(self.screen, color, (screen_x, screen_y, TILE_SIZE, TILE_SIZE))

        # Instructions
        hint_text = f"Placing: {self.building_to_place.value.replace('_', ' ').title()}"
        hint = self.font.render(hint_text, True, WHITE)
        self.screen.blit(hint, (SCREEN_WIDTH // 2 - hint.get_width() // 2, 20))

        sub_hint = self.small_font.render("Click to place | ESC to cancel | 1: Campfire | 2: Wall", True, WHITE)
        self.screen.blit(sub_hint, (SCREEN_WIDTH // 2 - sub_hint.get_width() // 2, 50))

    def run(self):
        """Main game loop"""
        while self.running:
            dt = self.clock.tick(FPS) / 1000.0  # Delta time in seconds

            self.handle_events()
            self.update(dt)
            self.draw()

        pygame.quit()


if __name__ == "__main__":
    game = GameState()
    game.run()
