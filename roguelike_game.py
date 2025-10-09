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
WORLD_SIZE = 120  # Larger world for more exploration
TEMPERATURE_COLOR = (100, 200, 255)  # Light blue for temperature


class BiomeType(Enum):
    """Different biome types"""
    GRASSLAND = "grassland"
    FOREST = "forest"
    DESERT = "desert"
    SWAMP = "swamp"
    TUNDRA = "tundra"
    VOLCANIC = "volcanic"


class TileType(Enum):
    """Types of terrain tiles"""
    GRASS = 0
    WATER = 1
    SAND = 2
    STONE = 3
    SWAMP = 4
    SNOW = 5
    LAVA = 6


class Season(Enum):
    """Game seasons"""
    SPRING = "spring"
    SUMMER = "summer"
    AUTUMN = "autumn"
    WINTER = "winter"


class Weather(Enum):
    """Weather conditions"""
    CLEAR = "clear"
    RAIN = "rain"
    SNOW = "snow"
    STORM = "storm"


class ResourceType(Enum):
    """Types of resources"""
    # Raw materials
    WOOD = "wood"
    STONE = "stone"
    BERRIES = "berries"
    MEAT = "meat"
    MUSHROOMS = "mushrooms"
    FIBER = "fiber"
    COAL = "coal"
    IRON_ORE = "iron_ore"
    GOLD_ORE = "gold_ore"
    GEMS = "gems"
    ICE = "ice"
    CACTUS_FRUIT = "cactus_fruit"

    # Processed materials
    IRON_INGOT = "iron_ingot"
    GOLD_INGOT = "gold_ingot"
    COOKED_MEAT = "cooked_meat"
    ROPE = "rope"
    CHARCOAL = "charcoal"


class ItemType(Enum):
    """Types of items"""
    # Basic Tools
    AXE = "axe"
    PICKAXE = "pickaxe"
    SWORD = "sword"
    TORCH = "torch"
    SHOVEL = "shovel"

    # Advanced Tools
    IRON_AXE = "iron_axe"
    IRON_PICKAXE = "iron_pickaxe"
    IRON_SWORD = "iron_sword"

    # Food
    BERRIES = "berries"
    COOKED_MEAT = "cooked_meat"
    MUSHROOM_STEW = "mushroom_stew"
    TRAIL_MIX = "trail_mix"
    HEALING_POTION = "healing_potion"

    # Buildings
    CAMPFIRE = "campfire"
    WOODEN_WALL = "wooden_wall"
    CHEST = "chest"
    WORKBENCH = "workbench"
    FARM_PLOT = "farm_plot"
    FURNACE = "furnace"

    # Seeds & Plants
    BERRY_SEEDS = "berry_seeds"
    MUSHROOM_SPORES = "mushroom_spores"

    # Materials
    ROPE = "rope"
    CLOTH = "cloth"
    IRON_INGOT = "iron_ingot"
    GOLD_INGOT = "gold_ingot"


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


class MushroomPatch(WorldObject):
    """Mushroom patch in swamps"""
    def __init__(self, x: int, y: int):
        super().__init__(x, y, "mushroom_patch")
        self.resource_type = ResourceType.MUSHROOMS
        self.resource_amount = random.randint(2, 5)
        self.health = 15
        self.max_health = 15
        self.regrow_timer = 0
        self.regrow_time = 600  # 10 seconds to regrow


class CactusPlant(WorldObject):
    """Cactus plant in deserts"""
    def __init__(self, x: int, y: int):
        super().__init__(x, y, "cactus")
        self.resource_type = ResourceType.CACTUS_FRUIT
        self.resource_amount = random.randint(1, 3)
        self.health = 30
        self.max_health = 30


class IceDeposit(WorldObject):
    """Ice deposit in tundra"""
    def __init__(self, x: int, y: int):
        super().__init__(x, y, "ice_deposit")
        self.resource_type = ResourceType.ICE
        self.resource_amount = random.randint(3, 8)
        self.health = 40
        self.max_health = 40


class IronDeposit(WorldObject):
    """Rich iron ore deposit"""
    def __init__(self, x: int, y: int):
        super().__init__(x, y, "iron_deposit")
        self.resource_type = ResourceType.IRON_ORE
        self.resource_amount = random.randint(5, 12)
        self.health = 80
        self.max_health = 80


class GoldDeposit(WorldObject):
    """Rare gold ore deposit"""
    def __init__(self, x: int, y: int):
        super().__init__(x, y, "gold_deposit")
        self.resource_type = ResourceType.GOLD_ORE
        self.resource_amount = random.randint(2, 6)
        self.health = 100
        self.max_health = 100


class GemDeposit(WorldObject):
    """Precious gem deposit"""
    def __init__(self, x: int, y: int):
        super().__init__(x, y, "gem_deposit")
        self.resource_type = ResourceType.GEMS
        self.resource_amount = random.randint(1, 4)
        self.health = 120
        self.max_health = 120


class AncientRuin(WorldObject):
    """Ancient ruins with research potential"""
    def __init__(self, x: int, y: int):
        super().__init__(x, y, "ancient_ruin")
        self.health = 200
        self.max_health = 200
        self.harvestable = True
        self.research_value = random.randint(10, 25)


class CaveEntrance(WorldObject):
    """Cave entrance - portal to underground"""
    def __init__(self, x: int, y: int):
        super().__init__(x, y, "cave_entrance")
        self.health = 1000  # Indestructible
        self.max_health = 1000
        self.harvestable = False  # Special interaction


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

    def update(self, dt: float, player, game_state=None):
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
                self.attack(player, game_state)
                self.attack_cooldown = 1.0 / self.attack_speed

        # Update cooldown
        if self.attack_cooldown > 0:
            self.attack_cooldown -= dt

    def attack(self, player, game_state=None):
        """Attack player"""
        player.take_damage(self.damage)
        # Add visual feedback if game state available
        if game_state:
            game_state.add_damage_number(player.x, player.y, self.damage, (255, 255, 100))
            game_state.add_particles(player.x, player.y, 6, (255, 200, 0))

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
        self.max_temperature = 100
        self.temperature = 50  # 0=freezing, 50=comfortable, 100=overheating

        # Movement
        self.speed = 8.0  # Increased from 3.0 for faster movement
        self.direction = "down"
        self.sprint_multiplier = 1.5  # Hold shift to sprint

        # Combat & Skills
        self.attack_cooldown = 0
        self.attack_speed = 1.5  # Attacks per second
        self.level = 1
        self.experience = 0
        self.skill_points = 0

        # Inventory & Equipment
        self.inventory: List[Optional[Item]] = [None] * 30  # Larger inventory
        self.equipped_tool: Optional[Item] = None
        self.equipped_armor: Optional[Item] = None
        self.hotbar: List[Optional[Item]] = [None] * 8  # More hotbar slots
        self.selected_hotbar_slot = 0

        # Expanded resources
        self.resources: Dict[ResourceType, int] = {
            ResourceType.WOOD: 0,
            ResourceType.STONE: 0,
            ResourceType.BERRIES: 0,
            ResourceType.MEAT: 0,
            ResourceType.MUSHROOMS: 0,
            ResourceType.FIBER: 0,
            ResourceType.COAL: 0,
            ResourceType.IRON_ORE: 0,
            ResourceType.GOLD_ORE: 0,
            ResourceType.GEMS: 0,
            ResourceType.ICE: 0,
            ResourceType.CACTUS_FRUIT: 0
        }

        # Status effects
        self.is_wet = False
        self.wetness_timer = 0
        self.light_radius = 0  # From torch/campfire

        # Research/Technology
        self.research_points = 0
        self.unlocked_recipes = set()

        # Base building
        self.home_base_x = x
        self.home_base_y = y

        # Animation
        self.frame = 0
        self.animation_timer = 0

        # Class abilities
        self.ability_cooldown = 0
        self.ability_duration = 0  # For abilities with duration
        self.ability_active = False

        # Class-specific stats
        if char_class == "warrior":
            self.max_health = 120
            self.health = 120
            self.ability_cooldown_time = 10  # seconds
        elif char_class == "mage":
            self.max_health = 80
            self.health = 80
            self.ability_cooldown_time = 12
        elif char_class == "archer":
            self.max_health = 90
            self.health = 90
            self.ability_cooldown_time = 8
            self.speed = 9.0  # Archers are faster
        elif char_class == "paladin":
            self.max_health = 110
            self.health = 110
            self.ability_cooldown_time = 15

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

    def update_survival(self, dt: float, is_night: bool, season: Season, weather: Weather, biome: BiomeType):
        """Update survival stats with advanced mechanics"""
        # Base hunger decay
        hunger_rate = HUNGER_DECAY_RATE
        if self.temperature < 20 or self.temperature > 80:
            hunger_rate *= 1.5  # Extreme temperatures increase hunger
        self.hunger = max(0, self.hunger - hunger_rate * dt)

        # Temperature changes based on environment
        base_temp = 50
        if season == Season.WINTER:
            base_temp = 20
        elif season == Season.SUMMER:
            base_temp = 70

        if biome == BiomeType.DESERT:
            base_temp += 20
        elif biome == BiomeType.TUNDRA:
            base_temp -= 30
        elif biome == BiomeType.VOLCANIC:
            base_temp += 35

        if is_night:
            base_temp -= 15

        if weather == Weather.RAIN or weather == Weather.SNOW:
            base_temp -= 10
            self.is_wet = True
            self.wetness_timer = 300  # Stay wet for 5 minutes

        # Gradually adjust temperature towards environment
        temp_diff = base_temp - self.temperature
        self.temperature += temp_diff * 0.1 * dt

        # Campfire warmth
        if self.light_radius > 0:
            self.temperature = min(self.max_temperature, self.temperature + 20 * dt)

        # Wetness effects
        if self.is_wet:
            self.wetness_timer -= dt
            if self.wetness_timer <= 0:
                self.is_wet = False
            self.temperature = max(0, self.temperature - 5 * dt)

        # Temperature health effects
        if self.temperature < 10:  # Freezing
            self.health -= 0.2 * dt
            self.sanity -= 0.1 * dt
        elif self.temperature > 90:  # Overheating
            self.health -= 0.15 * dt
            self.hunger -= 0.1 * dt

        # Sanity changes
        if is_night:
            sanity_loss = SANITY_DECAY_NIGHT
            if self.light_radius == 0:  # No light source
                sanity_loss *= 2
            if weather == Weather.STORM:
                sanity_loss *= 1.5
            self.sanity = max(0, self.sanity - sanity_loss * dt)
        else:
            # Recover sanity during day
            recovery_rate = 0.02
            if weather == Weather.CLEAR:
                recovery_rate *= 1.5
            self.sanity = min(self.max_sanity, self.sanity + recovery_rate * dt)

        # Health effects from other stats
        if self.hunger <= 0:
            self.health -= 0.15 * dt
        if self.sanity <= 10:
            self.health -= 0.1 * dt

        # Clamp all stats
        self.health = max(0, min(self.max_health, self.health))
        self.temperature = max(0, min(self.max_temperature, self.temperature))

    def eat_food(self, food_item: Item):
        """Consume food with varied effects"""
        if food_item.item_type == ItemType.BERRIES:
            self.hunger = min(self.max_hunger, self.hunger + 15)
            self.health = min(self.max_health, self.health + 5)
        elif food_item.item_type == ItemType.COOKED_MEAT:
            self.hunger = min(self.max_hunger, self.hunger + 40)
            self.health = min(self.max_health, self.health + 10)
        elif food_item.item_type == ItemType.MUSHROOM_STEW:
            self.hunger = min(self.max_hunger, self.hunger + 30)
            self.sanity = min(self.max_sanity, self.sanity + 20)
        elif food_item.item_type == ItemType.TRAIL_MIX:
            self.hunger = min(self.max_hunger, self.hunger + 25)
            self.temperature = min(self.max_temperature, self.temperature + 10)
        elif food_item.item_type == ItemType.HEALING_POTION:
            self.health = min(self.max_health, self.health + 50)
        elif food_item.item_type == ItemType.CACTUS_FRUIT:
            self.hunger = min(self.max_hunger, self.hunger + 20)
            self.temperature = max(0, self.temperature - 15)  # Cooling effect

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
        # Paladin shield blocks damage
        if self.ability_active and self.char_class == "paladin":
            return  # No damage taken during Divine Shield

        self.health = max(0, self.health - damage)
        self.sanity = max(0, self.sanity - 5)  # Losing health also affects sanity

    def use_ability(self, world, game_state) -> bool:
        """Use class-specific ability. Returns True if used successfully."""
        if self.ability_cooldown > 0:
            return False  # Still on cooldown

        # Activate ability based on class
        if self.char_class == "warrior":
            # Warrior: Whirlwind Attack - damage all nearby enemies
            enemies_hit = 0
            for enemy in world.enemies:
                dist = math.sqrt((enemy.x - self.x)**2 + (enemy.y - self.y)**2)
                if dist <= 3.0:  # 3 tile radius
                    damage = 30
                    enemy.health -= damage
                    game_state.add_damage_number(enemy.x, enemy.y, damage, (255, 150, 0))
                    game_state.add_particles(enemy.x, enemy.y, 10, (255, 100, 0))
                    enemies_hit += 1

            if enemies_hit > 0:
                self.ability_cooldown = self.ability_cooldown_time
                game_state.add_particles(self.x, self.y, 20, (255, 200, 0))
                return True

        elif self.char_class == "mage":
            # Mage: Arcane Blast - ranged damage in direction
            # Find nearest enemy within 8 tiles
            nearest_enemy = None
            nearest_dist = float('inf')
            for enemy in world.enemies:
                dist = math.sqrt((enemy.x - self.x)**2 + (enemy.y - self.y)**2)
                if dist <= 8.0 and dist < nearest_dist:
                    nearest_enemy = enemy
                    nearest_dist = dist

            if nearest_enemy:
                damage = 50
                nearest_enemy.health -= damage
                game_state.add_damage_number(nearest_enemy.x, nearest_enemy.y, damage, (150, 100, 255))
                # Create projectile particles
                for i in range(10):
                    t = i / 10.0
                    px = self.x + (nearest_enemy.x - self.x) * t
                    py = self.y + (nearest_enemy.y - self.y) * t
                    game_state.add_particles(px, py, 3, (200, 150, 255))

                self.ability_cooldown = self.ability_cooldown_time
                return True

        elif self.char_class == "archer":
            # Archer: Volley - shoot at 3 nearest enemies
            enemies_in_range = []
            for enemy in world.enemies:
                dist = math.sqrt((enemy.x - self.x)**2 + (enemy.y - self.y)**2)
                if dist <= 10.0:
                    enemies_in_range.append((dist, enemy))

            enemies_in_range.sort(key=lambda x: x[0])
            hit_count = min(3, len(enemies_in_range))

            for i in range(hit_count):
                enemy = enemies_in_range[i][1]
                damage = 25
                enemy.health -= damage
                game_state.add_damage_number(enemy.x, enemy.y, damage, (100, 255, 100))
                game_state.add_particles(enemy.x, enemy.y, 5, (150, 255, 150))

            if hit_count > 0:
                self.ability_cooldown = self.ability_cooldown_time
                return True

        elif self.char_class == "paladin":
            # Paladin: Divine Shield - heal and gain temporary invulnerability
            heal_amount = 40
            self.health = min(self.max_health, self.health + heal_amount)
            self.ability_duration = 3.0  # 3 seconds of protection
            self.ability_active = True

            game_state.add_damage_number(self.x, self.y, heal_amount, (255, 255, 150))
            game_state.add_particles(self.x, self.y, 15, (255, 255, 200))

            self.ability_cooldown = self.ability_cooldown_time
            return True

        return False

    def update_abilities(self, dt: float):
        """Update ability cooldowns and durations"""
        if self.ability_cooldown > 0:
            self.ability_cooldown -= dt

        if self.ability_duration > 0:
            self.ability_duration -= dt
            if self.ability_duration <= 0:
                self.ability_active = False


class World:
    """Advanced game world with biomes, seasons, and weather"""
    def __init__(self, seed: Optional[int] = None):
        self.seed = seed if seed else random.randint(0, 999999)
        random.seed(self.seed)

        # Terrain and biomes
        self.tiles = [[TileType.GRASS for _ in range(WORLD_SIZE)] for _ in range(WORLD_SIZE)]
        self.biomes = [[BiomeType.GRASSLAND for _ in range(WORLD_SIZE)] for _ in range(WORLD_SIZE)]

        # World objects
        self.objects: List[WorldObject] = []
        self.enemies: List[Enemy] = []
        self.buildings: List[Building] = []

        # Dynamic systems
        self.current_season = Season.SPRING
        self.current_weather = Weather.CLEAR
        self.weather_timer = 0
        self.season_timer = 0

        # Special locations
        self.ruins_locations = []
        self.cave_entrances = []
        self.mineral_deposits = []

        self.generate_world()

    def generate_world(self):
        """Generate diverse biomes and interesting locations"""
        # Generate biome regions
        self.generate_biomes()

        # Generate terrain based on biomes
        self.generate_terrain()

        # Place resources based on biomes
        self.generate_resources()

        # Create special locations
        self.generate_special_locations()

    def generate_biomes(self):
        """Create biome regions using noise-like generation"""
        # Create biome seeds
        biome_centers = [
            (WORLD_SIZE // 4, WORLD_SIZE // 4, BiomeType.FOREST),
            (3 * WORLD_SIZE // 4, WORLD_SIZE // 4, BiomeType.DESERT),
            (WORLD_SIZE // 4, 3 * WORLD_SIZE // 4, BiomeType.SWAMP),
            (3 * WORLD_SIZE // 4, 3 * WORLD_SIZE // 4, BiomeType.TUNDRA),
            (WORLD_SIZE // 2, WORLD_SIZE // 2, BiomeType.VOLCANIC),
        ]

        for y in range(WORLD_SIZE):
            for x in range(WORLD_SIZE):
                # Find closest biome center
                min_dist = float('inf')
                closest_biome = BiomeType.GRASSLAND

                for cx, cy, biome in biome_centers:
                    dist = math.sqrt((x - cx) ** 2 + (y - cy) ** 2)
                    # Add some randomness
                    dist += random.uniform(-10, 10)

                    if dist < min_dist:
                        min_dist = dist
                        closest_biome = biome

                self.biomes[y][x] = closest_biome

    def generate_terrain(self):
        """Generate terrain tiles based on biomes"""
        for y in range(WORLD_SIZE):
            for x in range(WORLD_SIZE):
                biome = self.biomes[y][x]

                if biome == BiomeType.DESERT:
                    self.tiles[y][x] = TileType.SAND
                elif biome == BiomeType.SWAMP:
                    if random.random() < 0.3:
                        self.tiles[y][x] = TileType.WATER
                    else:
                        self.tiles[y][x] = TileType.SWAMP
                elif biome == BiomeType.TUNDRA:
                    self.tiles[y][x] = TileType.SNOW
                elif biome == BiomeType.VOLCANIC:
                    if random.random() < 0.1:
                        self.tiles[y][x] = TileType.LAVA
                    else:
                        self.tiles[y][x] = TileType.STONE
                else:  # Forest and Grassland
                    self.tiles[y][x] = TileType.GRASS

        # Add some water bodies
        for _ in range(8):
            lake_x = random.randint(10, WORLD_SIZE - 10)
            lake_y = random.randint(10, WORLD_SIZE - 10)
            lake_size = random.randint(3, 8)

            for dx in range(-lake_size, lake_size):
                for dy in range(-lake_size, lake_size):
                    if dx*dx + dy*dy < lake_size*lake_size:
                        wx, wy = lake_x + dx, lake_y + dy
                        if 0 <= wx < WORLD_SIZE and 0 <= wy < WORLD_SIZE:
                            self.tiles[wy][wx] = TileType.WATER

    def generate_resources(self):
        """Place resources appropriate to each biome - optimized for performance"""
        objects_count = 0

        # Sample every 2nd tile for better performance
        for y in range(0, WORLD_SIZE, 2):
            for x in range(0, WORLD_SIZE, 2):
                if self.tiles[y][x] in [TileType.WATER, TileType.LAVA]:
                    continue

                biome = self.biomes[y][x]

                # Trees
                if biome == BiomeType.FOREST and random.random() < 0.3:
                    self.objects.append(Tree(x, y, random.randint(1, 2)))
                    objects_count += 1
                elif biome == BiomeType.GRASSLAND and random.random() < 0.08:
                    self.objects.append(Tree(x, y, random.randint(1, 2)))
                    objects_count += 1

                # Rocks and mineral deposits
                elif biome == BiomeType.VOLCANIC and random.random() < 0.15:
                    self.objects.append(Rock(x, y, variant=3))  # Obsidian
                    objects_count += 1
                elif biome == BiomeType.TUNDRA and random.random() < 0.12:
                    self.objects.append(IceDeposit(x, y))
                    objects_count += 1
                elif random.random() < 0.04:
                    self.objects.append(Rock(x, y, random.randint(1, 2)))
                    objects_count += 1

                # Bushes and plants
                elif biome == BiomeType.GRASSLAND and random.random() < 0.06:
                    self.objects.append(Bush(x, y, random.randint(1, 2)))
                    objects_count += 1
                elif biome == BiomeType.SWAMP and random.random() < 0.1:
                    self.objects.append(MushroomPatch(x, y))
                    objects_count += 1
                elif biome == BiomeType.DESERT and random.random() < 0.05:
                    self.objects.append(CactusPlant(x, y))
                    objects_count += 1

        # Add mineral deposits scattered around
        for _ in range(30):  # Iron deposits
            x = random.randint(5, WORLD_SIZE - 5)
            y = random.randint(5, WORLD_SIZE - 5)
            if self.tiles[y][x] not in [TileType.WATER, TileType.LAVA]:
                self.objects.append(IronDeposit(x, y))
                objects_count += 1

        for _ in range(12):  # Gold deposits
            x = random.randint(5, WORLD_SIZE - 5)
            y = random.randint(5, WORLD_SIZE - 5)
            if self.tiles[y][x] not in [TileType.WATER, TileType.LAVA]:
                self.objects.append(GoldDeposit(x, y))
                objects_count += 1

        for _ in range(8):  # Gem deposits
            x = random.randint(5, WORLD_SIZE - 5)
            y = random.randint(5, WORLD_SIZE - 5)
            if self.tiles[y][x] not in [TileType.WATER, TileType.LAVA]:
                self.objects.append(GemDeposit(x, y))
                objects_count += 1

        # Add guaranteed starting resources around spawn point
        spawn_center = WORLD_SIZE // 2
        for angle in range(0, 360, 30):  # Every 30 degrees for more resources
            distance = random.uniform(2, 6)
            x = int(spawn_center + math.cos(math.radians(angle)) * distance)
            y = int(spawn_center + math.sin(math.radians(angle)) * distance)

            if 5 < x < WORLD_SIZE - 5 and 5 < y < WORLD_SIZE - 5:
                if self.tiles[y][x] not in [TileType.WATER, TileType.LAVA]:
                    # Add variety of starting resources
                    if angle % 90 == 0:  # Trees
                        self.objects.append(Tree(x, y, 1))
                        objects_count += 1
                    elif angle % 60 == 0:  # Rocks
                        self.objects.append(Rock(x, y, 1))
                        objects_count += 1
                    else:  # Bushes
                        self.objects.append(Bush(x, y, 1))
                        objects_count += 1

    def generate_special_locations(self):
        """Create ruins, caves, and other points of interest"""
        # Ancient ruins
        for _ in range(5):
            ruin_x = random.randint(20, WORLD_SIZE - 20)
            ruin_y = random.randint(20, WORLD_SIZE - 20)
            self.ruins_locations.append((ruin_x, ruin_y))
            # Place some structures
            for dx in range(-2, 3):
                for dy in range(-2, 3):
                    if random.random() < 0.3:
                        self.objects.append(AncientRuin(ruin_x + dx, ruin_y + dy))

        # Cave entrances
        for _ in range(8):
            cave_x = random.randint(10, WORLD_SIZE - 10)
            cave_y = random.randint(10, WORLD_SIZE - 10)
            if self.biomes[cave_y][cave_x] in [BiomeType.FOREST, BiomeType.VOLCANIC]:
                self.cave_entrances.append((cave_x, cave_y))
                self.objects.append(CaveEntrance(cave_x, cave_y))

        # Rich mineral deposits
        for _ in range(12):
            deposit_x = random.randint(5, WORLD_SIZE - 5)
            deposit_y = random.randint(5, WORLD_SIZE - 5)
            biome = self.biomes[deposit_y][deposit_x]

            if biome == BiomeType.VOLCANIC:
                self.objects.append(GoldDeposit(deposit_x, deposit_y))
            elif biome == BiomeType.TUNDRA:
                self.objects.append(IronDeposit(deposit_x, deposit_y))
            elif biome == BiomeType.DESERT:
                self.objects.append(GemDeposit(deposit_x, deposit_y))

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

    def update_enemies(self, dt: float, player, game_state=None):
        """Update all enemies"""
        for enemy in self.enemies[:]:
            enemy.update(dt, player, game_state)
            if enemy.health <= 0:
                self.enemies.remove(enemy)
                # Drop loot
                for resource, amount in enemy.drop_loot().items():
                    player.add_resource(resource, amount)

    def update_buildings(self, dt: float):
        """Update all buildings"""
        for building in self.buildings:
            building.update(dt)

    def update_world_systems(self, dt: float):
        """Update weather, seasons, and world events"""
        # Update weather
        self.weather_timer += dt
        if self.weather_timer >= 300:  # Change weather every 5 minutes
            self.weather_timer = 0
            self.change_weather()

        # Update seasons
        self.season_timer += dt
        if self.season_timer >= 2400:  # Season change every 40 minutes
            self.season_timer = 0
            self.change_season()

        # Update resource regrowth
        for obj in self.objects:
            if hasattr(obj, 'regrow_timer') and obj.resource_amount <= 0:
                obj.regrow_timer += dt
                if obj.regrow_timer >= obj.regrow_time:
                    obj.regrow_timer = 0
                    if isinstance(obj, Bush):
                        obj.resource_amount = random.randint(1, 3)
                    elif isinstance(obj, MushroomPatch):
                        obj.resource_amount = random.randint(2, 5)
                    obj.health = obj.max_health

    def change_weather(self):
        """Randomly change weather with seasonal influences"""
        if self.current_season == Season.WINTER:
            self.current_weather = random.choice([Weather.CLEAR, Weather.SNOW, Weather.STORM])
        elif self.current_season == Season.SUMMER:
            self.current_weather = random.choice([Weather.CLEAR, Weather.CLEAR, Weather.STORM])
        else:
            self.current_weather = random.choice([Weather.CLEAR, Weather.RAIN, Weather.STORM])

    def change_season(self):
        """Progress to next season"""
        seasons = [Season.SPRING, Season.SUMMER, Season.AUTUMN, Season.WINTER]
        current_index = seasons.index(self.current_season)
        self.current_season = seasons[(current_index + 1) % 4]

    def get_biome_at(self, x: int, y: int) -> BiomeType:
        """Get biome type at position"""
        if 0 <= x < WORLD_SIZE and 0 <= y < WORLD_SIZE:
            return self.biomes[y][x]
        return BiomeType.GRASSLAND


class CraftingSystem:
    """Advanced crafting system with tier progression"""
    def __init__(self):
        self.recipes: List[Recipe] = [
            # Basic Tools
            Recipe(ItemType.AXE, {ResourceType.WOOD: 3, ResourceType.STONE: 2}),
            Recipe(ItemType.PICKAXE, {ResourceType.WOOD: 2, ResourceType.STONE: 3}),
            Recipe(ItemType.SWORD, {ResourceType.WOOD: 2, ResourceType.STONE: 4}),
            Recipe(ItemType.SHOVEL, {ResourceType.WOOD: 2, ResourceType.STONE: 1}),
            Recipe(ItemType.TORCH, {ResourceType.WOOD: 2, ResourceType.FIBER: 1}),

            # Advanced Tools (require workbench)
            Recipe(ItemType.IRON_AXE, {ResourceType.IRON_INGOT: 2, ResourceType.WOOD: 1}, ItemType.WORKBENCH),
            Recipe(ItemType.IRON_PICKAXE, {ResourceType.IRON_INGOT: 2, ResourceType.WOOD: 1}, ItemType.WORKBENCH),
            Recipe(ItemType.IRON_SWORD, {ResourceType.IRON_INGOT: 3, ResourceType.WOOD: 1}, ItemType.WORKBENCH),

            # Buildings
            Recipe(ItemType.CAMPFIRE, {ResourceType.WOOD: 5, ResourceType.STONE: 3}),
            Recipe(ItemType.WOODEN_WALL, {ResourceType.WOOD: 4}),
            Recipe(ItemType.CHEST, {ResourceType.WOOD: 8}),
            Recipe(ItemType.WORKBENCH, {ResourceType.WOOD: 12, ResourceType.STONE: 4}),
            Recipe(ItemType.FURNACE, {ResourceType.STONE: 15, ResourceType.COAL: 5}),
            Recipe(ItemType.FARM_PLOT, {ResourceType.WOOD: 6, ResourceType.FIBER: 4}),

            # Materials
            Recipe(ItemType.ROPE, {ResourceType.FIBER: 5}),
            Recipe(ItemType.CLOTH, {ResourceType.FIBER: 8}),
            Recipe(ItemType.IRON_INGOT, {ResourceType.IRON_ORE: 2, ResourceType.COAL: 1}, ItemType.FURNACE),
            Recipe(ItemType.GOLD_INGOT, {ResourceType.GOLD_ORE: 1, ResourceType.COAL: 2}, ItemType.FURNACE),

            # Food
            Recipe(ItemType.COOKED_MEAT, {ResourceType.MEAT: 1}, ItemType.CAMPFIRE),
            Recipe(ItemType.MUSHROOM_STEW, {ResourceType.MUSHROOMS: 3, ResourceType.BERRIES: 2}, ItemType.CAMPFIRE),
            Recipe(ItemType.TRAIL_MIX, {ResourceType.BERRIES: 4, ResourceType.CACTUS_FRUIT: 2}),
            Recipe(ItemType.HEALING_POTION, {ResourceType.MUSHROOMS: 2, ResourceType.BERRIES: 3, ResourceType.GEMS: 1}),

            # Seeds
            Recipe(ItemType.BERRY_SEEDS, {ResourceType.BERRIES: 5}),
            Recipe(ItemType.MUSHROOM_SPORES, {ResourceType.MUSHROOMS: 3}),
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

        # Visual effects
        self.damage_numbers = []  # List of {x, y, damage, lifetime, color}
        self.particles = []  # List of {x, y, vx, vy, lifetime, color, size}
        self.harvesting_target = None  # Track current harvesting target for progress bar

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

            # Load environment objects from assets folder root
            for obj in ["tree1", "tree2", "rock1", "rock2", "bush1", "bush2"]:
                path = os.path.join(asset_path, f"{obj}.png")
                if os.path.exists(path):
                    sprite = pygame.image.load(path).convert_alpha()
                    # Scale to reasonable size
                    self.assets[obj] = pygame.transform.scale(sprite, (32, 32))

            # Load Tiny Swords assets
            tiny_swords_path = os.path.join(asset_path, "Tiny Swords (Free Pack)", "Decorations")

            # Load trees from Tiny Swords
            tree_path = os.path.join(tiny_swords_path, "Trees")
            for i in range(1, 5):  # Tree1.png to Tree4.png
                path = os.path.join(tree_path, f"Tree{i}.png")
                if os.path.exists(path):
                    sprite = pygame.image.load(path).convert_alpha()
                    self.assets[f"tree{i}"] = pygame.transform.scale(sprite, (48, 48))

            # Load rocks from Tiny Swords
            rock_path = os.path.join(tiny_swords_path, "Rocks")
            for i in range(1, 5):  # Rock1.png to Rock4.png
                path = os.path.join(rock_path, f"Rock{i}.png")
                if os.path.exists(path):
                    sprite = pygame.image.load(path).convert_alpha()
                    self.assets[f"rock{i}"] = pygame.transform.scale(sprite, (32, 32))

            # Load bushes from Tiny Swords (note the typo in filenames)
            bush_path = os.path.join(tiny_swords_path, "Bushes")
            for i in range(1, 5):  # Bushe1.png to Bushe4.png
                path = os.path.join(bush_path, f"Bushe{i}.png")
                if os.path.exists(path):
                    sprite = pygame.image.load(path).convert_alpha()
                    self.assets[f"bush{i}"] = pygame.transform.scale(sprite, (32, 32))

            # Load fantasy icons for minerals and special items
            fantasy_icon_path = os.path.join(asset_path, "Free - Raven Fantasy Icons",
                                           "Free - Raven Fantasy Icons", "Separated Files", "32x32")

            # Map specific fantasy icons to game resources (educated guesses for resource icons)
            icon_mappings = {
                "mushroom": "fb150.png",   # Try different ranges for resources
                "cactus": "fb200.png",     # Plants/nature
                "ice": "fb300.png",        # Ice/crystals
                "iron_ore": "fb400.png",   # Metals/ores
                "gold_ore": "fb450.png",   # Gold/precious metals
                "gems": "fb500.png",       # Gems/crystals
                "ruin": "fb600.png",       # Buildings/structures
                "cave": "fb700.png"        # Dark/cave entries
            }

            for asset_name, filename in icon_mappings.items():
                path = os.path.join(fantasy_icon_path, filename)
                if os.path.exists(path):
                    sprite = pygame.image.load(path).convert_alpha()
                    self.assets[asset_name] = pygame.transform.scale(sprite, (32, 32))



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
                    elif event.key == pygame.K_f:  # Use class ability
                        if self.player and self.world:
                            if self.player.use_ability(self.world, self):
                                print(f"{self.player.char_class.title()} ability activated!")
                            else:
                                print(f"Ability on cooldown: {self.player.ability_cooldown:.1f}s")
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
        # Set as current harvesting target for progress display
        self.harvesting_target = obj

        # Check if player has right tool and determine damage
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
        elif isinstance(obj, (Bush, MushroomPatch, CactusPlant)):
            damage = 15  # Plants don't need tools but take some effort
        elif isinstance(obj, (IceDeposit, IronDeposit, GoldDeposit, GemDeposit)):
            if self.player.equipped_tool and self.player.equipped_tool.item_type == ItemType.PICKAXE:
                damage = 25
            else:
                damage = 8  # Slower without proper tools
        else:
            self.harvesting_target = None
            return

        # Damage object
        destroyed = obj.take_damage(damage)

        # Add visual feedback for gathering
        if isinstance(obj, Tree):
            self.add_particles(obj.x, obj.y, 5, (139, 69, 19))  # Wood particles
        elif isinstance(obj, Rock):
            self.add_particles(obj.x, obj.y, 5, (150, 150, 150))  # Stone particles
        elif isinstance(obj, (Bush, MushroomPatch, CactusPlant)):
            self.add_particles(obj.x, obj.y, 4, (50, 200, 50))  # Plant particles
        else:
            self.add_particles(obj.x, obj.y, 6, (255, 215, 0))  # Gold sparkles for minerals

        if destroyed:
            # Give resources
            if hasattr(obj, 'resource_type'):
                amount = obj.resource_amount
                self.player.add_resource(obj.resource_type, amount)
                # Visual feedback
                print(f"Gathered {amount} {obj.resource_type.value}!")
                # Show resource gain as floating text
                self.add_damage_number(obj.x, obj.y, amount, (100, 255, 100))

            # Remove object
            self.world.objects.remove(obj)
            self.harvesting_target = None

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
            # Add damage number visual
            self.add_damage_number(nearest_enemy.x, nearest_enemy.y, damage, (255, 100, 100))
            # Add hit particles
            self.add_particles(nearest_enemy.x, nearest_enemy.y, 8, (255, 50, 50))

    def handle_interact(self):
        """Interact with nearby objects (harvest resources, cook at campfire, etc)"""
        if not self.player or not self.world:
            return

        interact_range = 2.0

        # First, try to find nearest harvestable object
        nearest_object = None
        nearest_dist = float('inf')

        for obj in self.world.objects:
            if obj.harvestable:
                dist = math.sqrt((obj.x - self.player.x)**2 + (obj.y - self.player.y)**2)
                if dist < interact_range and dist < nearest_dist:
                    nearest_object = obj
                    nearest_dist = dist

        # If we found a harvestable object, harvest it
        if nearest_object:
            self.gather_resource(nearest_object)
            return

        # If no harvestable objects, try campfire interaction
        nearest_fire = None
        nearest_dist = float('inf')

        for building in self.world.buildings:
            if building.building_type == "campfire":
                dist = math.sqrt((building.x - self.player.x)**2 + (building.y - self.player.y)**2)
                if dist < interact_range and dist < nearest_dist:
                    nearest_fire = building
                    nearest_dist = dist

        if nearest_fire and nearest_fire.fuel > 0:
            # Cook meat
            if self.player.cook_food():
                # Successfully cooked food
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

        # Update world systems (weather, seasons, regrowth)
        self.world.update_world_systems(dt)

        # Get environmental context
        is_night = self.time >= DAY_LENGTH
        player_biome = self.world.get_biome_at(int(self.player.x), int(self.player.y))

        # Update player light radius based on torch/campfire proximity
        self.update_player_lighting()

        # Update survival stats with advanced mechanics
        self.player.update_survival(dt, is_night, self.world.current_season,
                                  self.world.current_weather, player_biome)

        # Update player abilities
        self.player.update_abilities(dt)

        # Update enemies
        self.world.update_enemies(dt, self.player, self)

        # Update buildings
        self.world.update_buildings(dt)

        # More dynamic enemy spawning based on biome and danger
        if is_night and self.time - self.last_spawn_time > 180:  # Every 3 seconds
            self.spawn_enemy_near_player(player_biome)
            self.last_spawn_time = self.time

        # Random events and discoveries
        if random.random() < 0.001:  # 0.1% chance per frame
            self.trigger_random_event()

        # Update visual effects
        self.update_visual_effects(dt)

        # Check death
        if self.player.health <= 0:
            self.state = "menu"

    def update_player_lighting(self):
        """Update player's light radius from nearby sources"""
        self.player.light_radius = 0

        # Check for torch
        if (self.player.equipped_tool and
            self.player.equipped_tool.item_type == ItemType.TORCH):
            self.player.light_radius = 3

        # Check for nearby campfires
        for building in self.world.buildings:
            if (building.building_type == "campfire" and building.fuel > 0):
                dist = math.sqrt((building.x - self.player.x)**2 +
                               (building.y - self.player.y)**2)
                if dist <= 5:
                    self.player.light_radius = max(self.player.light_radius, 5)

    def trigger_random_event(self):
        """Trigger random world events for excitement"""
        events = [
            "meteor_shower",
            "resource_discovery",
            "wandering_merchant",
            "ancient_artifact",
            "rare_enemy"
        ]

        event = random.choice(events)

        if event == "meteor_shower":
            # Spawn rare materials around player
            for _ in range(5):
                angle = random.random() * 2 * math.pi
                distance = random.uniform(5, 15)
                x = int(self.player.x + math.cos(angle) * distance)
                y = int(self.player.y + math.sin(angle) * distance)
                if 0 <= x < WORLD_SIZE and 0 <= y < WORLD_SIZE:
                    self.world.objects.append(GemDeposit(x, y))

        elif event == "resource_discovery":
            # Player gains research points
            self.player.research_points += random.randint(5, 15)

        elif event == "rare_enemy":
            # Spawn a powerful enemy with good loot
            self.world.spawn_enemy(self.player.x + random.uniform(-8, 8),
                                 self.player.y + random.uniform(-8, 8),
                                 "wizard_boss")

    def spawn_enemy_near_player(self, biome_type=BiomeType.GRASSLAND):
        """Spawn a biome-appropriate enemy near the player"""
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

        # Choose enemy based on biome and progression
        biome_enemies = {
            BiomeType.GRASSLAND: ["goblin", "wolf"],
            BiomeType.FOREST: ["goblin", "wolf", "bear", "spider"],
            BiomeType.DESERT: ["scorpion", "sand_wraith", "cobra"],
            BiomeType.SWAMP: ["swamp_troll", "bog_witch", "crocodile"],
            BiomeType.TUNDRA: ["ice_wolf", "yeti", "frost_giant"],
            BiomeType.VOLCANIC: ["fire_elemental", "lava_golem", "wizard_boss"]
        }

        enemy_types = biome_enemies.get(biome_type, ["goblin", "wolf"])

        # Filter by day progression
        if self.day_count == 1:
            # Only weakest enemies on day 1
            enemy_type = "goblin"
        elif self.day_count < 5:
            # Basic enemies first few days
            basic_enemies = [e for e in enemy_types if e in ["goblin", "wolf", "scorpion"]]
            enemy_type = random.choice(basic_enemies if basic_enemies else enemy_types[:2])
        else:
            # All biome enemies after day 5
            enemy_type = random.choice(enemy_types)

        self.world.spawn_enemy(spawn_x, spawn_y, enemy_type)

    def add_damage_number(self, x: float, y: float, damage: int, color: Tuple[int, int, int] = (255, 50, 50)):
        """Add a floating damage number at the specified world position"""
        self.damage_numbers.append({
            'x': x,
            'y': y,
            'damage': damage,
            'lifetime': 1.0,  # Seconds
            'color': color,
            'offset_y': 0  # Will rise upward
        })

    def add_particles(self, x: float, y: float, count: int, color: Tuple[int, int, int] = (255, 255, 255)):
        """Add particle effect at world position"""
        for _ in range(count):
            angle = random.random() * 2 * math.pi
            speed = random.uniform(20, 60)
            self.particles.append({
                'x': x,
                'y': y,
                'vx': math.cos(angle) * speed,
                'vy': math.sin(angle) * speed,
                'lifetime': random.uniform(0.3, 0.8),
                'color': color,
                'size': random.randint(2, 5)
            })

    def update_visual_effects(self, dt: float):
        """Update damage numbers and particles"""
        # Update damage numbers
        for dmg in self.damage_numbers[:]:
            dmg['lifetime'] -= dt
            dmg['offset_y'] -= 30 * dt  # Rise upward
            if dmg['lifetime'] <= 0:
                self.damage_numbers.remove(dmg)

        # Update particles
        for particle in self.particles[:]:
            particle['x'] += particle['vx'] * dt
            particle['y'] += particle['vy'] * dt
            particle['vy'] += 100 * dt  # Gravity
            particle['lifetime'] -= dt
            if particle['lifetime'] <= 0:
                self.particles.remove(particle)

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
                elif isinstance(obj, MushroomPatch):
                    sprite_key = "mushroom"
                elif isinstance(obj, CactusPlant):
                    sprite_key = "cactus"
                elif isinstance(obj, IceDeposit):
                    sprite_key = "ice"
                elif isinstance(obj, IronDeposit):
                    sprite_key = "iron_ore"
                elif isinstance(obj, GoldDeposit):
                    sprite_key = "gold_ore"
                elif isinstance(obj, GemDeposit):
                    sprite_key = "gems"
                elif isinstance(obj, AncientRuin):
                    sprite_key = "ruin"
                elif isinstance(obj, CaveEntrance):
                    sprite_key = "cave"

                if sprite_key and sprite_key in self.assets:
                    sprite = self.assets[sprite_key]
                    self.screen.blit(sprite, (screen_x - sprite.get_width() // 2, screen_y - sprite.get_height() // 2))
                else:
                    # Fallback to colored rectangles/circles
                    if isinstance(obj, Tree):
                        pygame.draw.circle(self.screen, (34, 100, 34), (screen_x, screen_y), 12)
                    elif isinstance(obj, Rock):
                        pygame.draw.circle(self.screen, (128, 128, 128), (screen_x, screen_y), 10)
                    elif isinstance(obj, Bush):
                        pygame.draw.circle(self.screen, (50, 150, 50), (screen_x, screen_y), 8)
                    elif isinstance(obj, MushroomPatch):
                        pygame.draw.circle(self.screen, (138, 43, 226), (screen_x, screen_y), 8)
                    elif isinstance(obj, CactusPlant):
                        pygame.draw.circle(self.screen, (0, 100, 0), (screen_x, screen_y), 10)
                    elif isinstance(obj, IceDeposit):
                        pygame.draw.circle(self.screen, (173, 216, 230), (screen_x, screen_y), 10)
                    elif isinstance(obj, IronDeposit):
                        pygame.draw.circle(self.screen, (169, 169, 169), (screen_x, screen_y), 10)
                    elif isinstance(obj, GoldDeposit):
                        pygame.draw.circle(self.screen, (255, 215, 0), (screen_x, screen_y), 10)
                    elif isinstance(obj, GemDeposit):
                        pygame.draw.circle(self.screen, (255, 20, 147), (screen_x, screen_y), 8)
                    elif isinstance(obj, AncientRuin):
                        pygame.draw.rect(self.screen, (139, 69, 19), (screen_x-8, screen_y-8, 16, 16))
                    elif isinstance(obj, CaveEntrance):
                        pygame.draw.circle(self.screen, (0, 0, 0), (screen_x, screen_y), 12)

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

        # Draw particles
        for particle in self.particles:
            # Convert world position to screen position
            screen_x = int((particle['x'] * TILE_SIZE) - self.camera_x + SCREEN_WIDTH // 2)
            screen_y = int((particle['y'] * TILE_SIZE) - self.camera_y + SCREEN_HEIGHT // 2)

            if -50 < screen_x < SCREEN_WIDTH + 50 and -50 < screen_y < SCREEN_HEIGHT + 50:
                # Fade alpha based on lifetime
                alpha = int(255 * (particle['lifetime'] / 0.8))
                color = (*particle['color'], alpha)
                size = particle['size']

                # Draw particle as a circle
                particle_surf = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
                pygame.draw.circle(particle_surf, color, (size, size), size)
                self.screen.blit(particle_surf, (screen_x - size, screen_y - size))

        # Draw damage numbers
        for dmg in self.damage_numbers:
            # Convert world position to screen position
            screen_x = int((dmg['x'] * TILE_SIZE) - self.camera_x + SCREEN_WIDTH // 2)
            screen_y = int((dmg['y'] * TILE_SIZE) - self.camera_y + SCREEN_HEIGHT // 2 + dmg['offset_y'])

            if -100 < screen_x < SCREEN_WIDTH + 100 and -100 < screen_y < SCREEN_HEIGHT + 100:
                # Fade alpha based on lifetime
                alpha = int(255 * dmg['lifetime'])

                # Create text with outline for visibility
                text = str(dmg['damage'])
                # Draw outline (black)
                for ox, oy in [(-1, -1), (-1, 1), (1, -1), (1, 1)]:
                    outline_surf = self.font.render(text, True, (0, 0, 0))
                    outline_surf.set_alpha(alpha)
                    self.screen.blit(outline_surf, (screen_x + ox, screen_y + oy))

                # Draw main text
                text_surf = self.font.render(text, True, dmg['color'])
                text_surf.set_alpha(alpha)
                text_rect = text_surf.get_rect(center=(screen_x, screen_y))
                self.screen.blit(text_surf, text_rect)

        # Draw harvest progress bar if actively harvesting
        if self.harvesting_target and self.harvesting_target in self.world.objects:
            obj = self.harvesting_target
            screen_x, screen_y = obj.get_screen_pos(self.camera_x, self.camera_y)

            if -TILE_SIZE < screen_x < SCREEN_WIDTH and -TILE_SIZE < screen_y < SCREEN_HEIGHT:
                # Progress bar above object
                bar_width = 40
                bar_height = 6
                bar_x = screen_x - bar_width // 2
                bar_y = screen_y - 35

                # Calculate progress (remaining health)
                progress = obj.health / obj.max_health
                fill_width = int(bar_width * progress)

                # Draw background
                pygame.draw.rect(self.screen, (50, 50, 50), (bar_x, bar_y, bar_width, bar_height))

                # Draw progress fill (green to red gradient based on health)
                if progress > 0.6:
                    color = (100, 255, 100)
                elif progress > 0.3:
                    color = (255, 255, 100)
                else:
                    color = (255, 150, 100)

                pygame.draw.rect(self.screen, color, (bar_x, bar_y, fill_width, bar_height))
                pygame.draw.rect(self.screen, WHITE, (bar_x, bar_y, bar_width, bar_height), 1)

                # Show percentage
                percent_text = self.small_font.render(f"{int(progress * 100)}%", True, WHITE)
                self.screen.blit(percent_text, (bar_x + bar_width // 2 - percent_text.get_width() // 2, bar_y - 15))

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

        # Ability cooldown indicator (top right corner near resources)
        ability_x = SCREEN_WIDTH - 210
        ability_y = 145
        ability_size = 60

        # Draw ability background
        if self.player.ability_active:
            # Golden glow when active
            pygame.draw.rect(self.screen, (255, 215, 0), (ability_x, ability_y, ability_size, ability_size), 3)
        else:
            pygame.draw.rect(self.screen, UI_BG, (ability_x, ability_y, ability_size, ability_size))

        # Draw class icon letter
        class_initial = self.player.char_class[0].upper()
        class_text = self.title_font.render(class_initial, True, WHITE)
        self.screen.blit(class_text, (ability_x + ability_size // 2 - class_text.get_width() // 2,
                                      ability_y + ability_size // 2 - class_text.get_height() // 2))

        # Draw cooldown overlay
        if self.player.ability_cooldown > 0:
            cooldown_percent = self.player.ability_cooldown / self.player.ability_cooldown_time
            overlay_height = int(ability_size * cooldown_percent)

            overlay = pygame.Surface((ability_size, overlay_height))
            overlay.fill((0, 0, 0))
            overlay.set_alpha(180)
            self.screen.blit(overlay, (ability_x, ability_y))

            # Cooldown text
            cd_text = self.small_font.render(f"{self.player.ability_cooldown:.1f}s", True, (255, 100, 100))
            self.screen.blit(cd_text, (ability_x + ability_size // 2 - cd_text.get_width() // 2,
                                       ability_y + ability_size // 2 - cd_text.get_height() // 2))

        # Ability name below
        ability_name_text = self.small_font.render(f"[F] Ability", True, WHITE)
        self.screen.blit(ability_name_text, (ability_x, ability_y + ability_size + 5))

        # Active indicator
        if self.player.ability_active:
            active_text = self.small_font.render(f"ACTIVE {self.player.ability_duration:.1f}s", True, (255, 215, 0))
            self.screen.blit(active_text, (ability_x, ability_y + ability_size + 25))

        # Controls hint
        hint_bg = pygame.Surface((750, 90))
        hint_bg.fill((20, 20, 30))
        hint_bg.set_alpha(200)
        self.screen.blit(hint_bg, (SCREEN_WIDTH // 2 - 375, SCREEN_HEIGHT - 60))

        hints = [
            "WASD: Move | Shift: Sprint | Click: Gather | Space: Attack",
            "1-5: Hotbar | E: Interact | F: Ability | Q: Drop | I: Inv | C: Craft | B: Build"
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

        # Draw tooltips for items if mouse hovering
        self.draw_item_tooltips()

    def draw_item_tooltips(self):
        """Draw tooltip for item under mouse cursor"""
        mouse_x, mouse_y = pygame.mouse.get_pos()

        # Check if in crafting menu
        if self.state == "crafting":
            panel_width = 700
            panel_height = 550
            panel_x = SCREEN_WIDTH // 2 - panel_width // 2
            panel_y = SCREEN_HEIGHT // 2 - panel_height // 2

            y_offset = panel_y + 100
            for i, recipe in enumerate(self.crafting_system.recipes):
                recipe_rect = pygame.Rect(panel_x + 50, y_offset, 600, 50)

                if recipe_rect.collidepoint(mouse_x, mouse_y):
                    # Draw tooltip for this recipe
                    tooltip_width = 300
                    tooltip_height = 150
                    tooltip_x = mouse_x + 15
                    tooltip_y = mouse_y + 15

                    # Keep tooltip on screen
                    if tooltip_x + tooltip_width > SCREEN_WIDTH:
                        tooltip_x = mouse_x - tooltip_width - 15
                    if tooltip_y + tooltip_height > SCREEN_HEIGHT:
                        tooltip_y = mouse_y - tooltip_height - 15

                    # Draw tooltip background
                    pygame.draw.rect(self.screen, (40, 40, 50),
                                   (tooltip_x, tooltip_y, tooltip_width, tooltip_height))
                    pygame.draw.rect(self.screen, (200, 200, 200),
                                   (tooltip_x, tooltip_y, tooltip_width, tooltip_height), 2)

                    # Item name
                    name = recipe.result.value.replace("_", " ").title()
                    name_text = self.font.render(name, True, (255, 215, 0))
                    self.screen.blit(name_text, (tooltip_x + 10, tooltip_y + 10))

                    # Requirements
                    req_y = tooltip_y + 40
                    req_title = self.small_font.render("Requirements:", True, WHITE)
                    self.screen.blit(req_title, (tooltip_x + 10, req_y))
                    req_y += 25

                    for resource, amount in recipe.requirements.items():
                        has_amount = self.player.resources.get(resource, 0)
                        color = (100, 255, 100) if has_amount >= amount else (255, 100, 100)
                        req_text = self.small_font.render(
                            f"  {resource.value}: {has_amount}/{amount}", True, color)
                        self.screen.blit(req_text, (tooltip_x + 10, req_y))
                        req_y += 20

                    # Description based on item type
                    desc_y = req_y + 10
                    description = self.get_item_description(recipe.result)
                    if description:
                        desc_text = self.small_font.render(description, True, (200, 200, 200))
                        self.screen.blit(desc_text, (tooltip_x + 10, desc_y))

                    break

                y_offset += 60

    def get_item_description(self, item_type: ItemType) -> str:
        """Get description for an item type"""
        descriptions = {
            ItemType.AXE: "Chop trees faster (4x speed)",
            ItemType.PICKAXE: "Mine rocks and ores faster",
            ItemType.SWORD: "Deal 2x damage to enemies",
            ItemType.TORCH: "Provides light in darkness",
            ItemType.CAMPFIRE: "Cook food, stay warm, repel enemies",
            ItemType.WOODEN_WALL: "Basic defensive structure",
            ItemType.WORKBENCH: "Unlock advanced crafting",
            ItemType.FURNACE: "Smelt ores into ingots",
            ItemType.IRON_INGOT: "Refined iron for tools",
            ItemType.STEEL_INGOT: "Advanced metal for weapons",
            ItemType.COOKED_MEAT: "Restores 30 hunger",
            ItemType.BERRY_PIE: "Restores 20 hunger, 10 sanity",
        }
        return descriptions.get(item_type, "")

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
