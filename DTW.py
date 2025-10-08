import random

# Base character class
class Character:
    def __init__(self, name, health, attack_power):
        self.name = name
        self.health = health
        self.attack_power = attack_power
        self.max_health = health
        self.healing_potions = 3 # Each character starts with 3 healing potions

    def attack(self, opponent):
        # Calculate random damage within range
        min_dam = int(self.attack_power * 0.5)
        max_dam = int(self.attack_power * 1.5)
        damage = random.randint(min_dam, max_dam)

        opponent.health -= damage
        print(f"{self.name} attacks {opponent.name} for {damage} damage!")
        if opponent.health <= 0:
            print(f"{opponent.name} has been defeated!")

    def heal(self):
        """Use a healing potion to restore health"""
        if self.healing_potions <= 0:
            print("❌No healing potions left!")
            return False

        heal_amount = 30
        old_health = self.health
        self.health = min(self.health + heal_amount, self.max_health)
        actual_heal = self.health - old_health
        self.healing_potions -= 1

        print(f"🧪✨{self.name} drinks a healing potion!")
        print(f"{self.name} restores {actual_heal} health!")
        print(f"Current health: {self.health}/{self.max_health}")
        print(f"Potions left: {self.healing_potions}")
        return True

    def display_stats(self):
        print(f"{self.name}'s Stats - Health: {self.health}/{self.max_health}, Attack Power: {self.attack_power}")

    def use_special_ability(self, opponent):
        """Placeholder for special abilities in subclasses."""
        pass

# Warrior class
class Warrior(Character):
    def __init__(self, name):
        super().__init__(name, health=140, attack_power=25)
        self.rage_stacks = 0
        self.shield_active = False
        self.max_rage = 5

    def attack(self, opponent):
        """Warrior builds rage with each attack."""
        # Calculate random damage
        min_dam = int(self.attack_power * 0.5)
        max_dam = int(self.attack_power * 1.5)
        damage = random.randint(min_dam, max_dam)
        opponent.health -= damage
        print(f"{self.name} attacks {opponent.name} for {damage} damage!")

        # Increase rage stacks
        if self.rage_stacks < self.max_rage:
            self.rage_stacks += 1
            print(f"⚡{self.name} gains 1 rage! Current rage: {self.rage_stacks}/{self.max_rage}")
        else:
            print(f"⚡{self.name}'s rage is at maximum!")

        if opponent.health <= 0:
            print(f"{opponent.name} has been defeated!")

    def use_special_ability(self, opponent):
        """Display special ability menu for Warrior"""
        print("\n=== Warrior Special Abilities ===")
        print(f"Current Rage: ⚡{self.rage_stacks}/{self.max_rage}")
        print("1. Rage Strike - Deal massive damage (Costs 3 rage)")
        print("2. Shield Wall - Reduce incoming damage by 50% for 2 turns")
        print("3. Cancel")

        choice = input("Choose an ability: ")
        if choice == '1':
            return self.rage_strike(opponent)
        elif choice == '2':
            return self.shield_wall()
        elif choice == '3':
            print("Cancelled special ability.")
            return False
        else:
            print("Invalid choice. Try again.")
            return self.use_special_ability(opponent)

    def rage_strike(self, opponent):
        """Consume rage stacks to deal extra damage"""
        rage_cost = 3

        if self.rage_stacks < rage_cost:
            print(f"❌Not enough rage! Need {rage_cost}, have {self.rage_stacks}")
            print("Use regular attacks to build more rage.")
            return False

        # Consume rage and deal amplified damage
        self.rage_stacks -= rage_cost
        damage = int(self.attack_power * 2.5)
        opponent.health -= damage

        print(f"⚔️💥{self.name} uses RAGE STRIKE!")
        print(f"{self.name} unleashes fury dealing {damage} devastating damage to {opponent.name}!")
        print(f"Rage remaining: {self.rage_stacks}/{self.max_rage}")

        if opponent.health <= 0:
            print(f"{opponent.name} has been defeated!")
        return True

    def shield_wall(self):
        """Activate Shield Wall to reduce incoming damage"""
        if self.shield_active:
            print("🛡️Shield Wall is already active!")
            return False

        self.shield_active = True
        print(f"🛡️{self.name} uses SHIELD WALL!")
        print(f"{self.name} will take 50% less damage for the next 2 turns!")
        return True

    def take_damage(self, damage):
        """Custom damage calculation considering Shield Wall"""
        if self.shield_active and self.shield_turns > 0:
            damage = int(damage * 0.5)
            print(f"🛡️Shield Wall active! Damage reduced to {damage}!")
            self.shield_turns -= 1
            if self.shield_turns <= 0:
                self.shield_active = False
                print(f"🛡️Shield Wall has expired!")
        self.health -= damage
        return damage

    def display_stats(self):
        shield_status = " [🛡️SHIELD ACTIVE] " if self.shield_active else ""
        print(f"{self.name}'s Stats - Health: {self.health}/{self.max_health}, Attack Power: {self.attack_power}, Rage Stacks: {self.rage_stacks}, Potions: {self.healing_potions} {shield_status}")

# Mage class
class Mage(Character):
    def __init__(self, name):
        super().__init__(name, health=100, attack_power=35)
        self.mana = 100
        self.max_mana = 100
        self.mana_regen = 15 # Mana regenerated per turn

    def attack(self, opponent):
        """Mage attacks and regenerates mana."""
        # Calculate random damage
        min_dam = int(self.attack_power * 0.5)
        max_dam = int(self.attack_power * 1.5)
        damage = random.randint(min_dam, max_dam)
        opponent.health -= damage
        print(f"{self.name} casts a spell at {opponent.name} for {damage} damage!")

        # Regenerate mana
        if self.mana < self.max_mana:
            mana_gained = min(self.mana_regen, self.max_mana - self.mana)
            self.mana += mana_gained
            print(f"✨{self.name} regenerates {mana_gained} mana! Current mana: {self.mana}/{self.max_mana}")
        else:
            print(f"✨{self.name}'s mana is at maximum!")

        if opponent.health <= 0:
            print(f"{opponent.name} has been defeated!")

    def use_special_ability(self, opponent):
        """Display special ability menu for Mage"""
        print("\n=== Mage Special Abilities ===")
        print(f"Current Mana: ✨{self.mana}/{self.max_mana}")
        print("1. Fireball - Deal massive magical damage (Costs 40 mana)")
        print("2. Ice Shield - Absorb damage and restore health (Costs 30 mana)")
        print("3. Cancel")

        choice = input("Choose an ability: ")
        if choice == '1':
            return self.fireball(opponent)
        elif choice == '2':
            return self.ice_shield()
        elif choice == '3':
            print("Cancelled special ability.")
            return False
        else:
            print("Invalid choice. Try again.")
            return self.use_special_ability(opponent)

    def fireball(self, opponent):
        """Consume mana to cast a devastating spell"""
        mana_cost = 40

        if self.mana < mana_cost:
            print(f"❌Not enough mana! Need {mana_cost}, have {self.mana}")
            print("Use regular attacks to regenerate more mana.")
            return False

        # Consume mana and deal amplified damage
        self.mana -= mana_cost
        damage = int(self.attack_power * 2)
        opponent.health -= damage

        print(f"🔥💥{self.name} casts FIREBALL!")
        print(f"A massive ball of flame engulfs {opponent.name} for {damage} damage!")
        print(f"Mana remaining: {self.mana}/{self.max_mana}")

        if opponent.health <= 0:
            print(f"{opponent.name} has been defeated!")
        return True

    def ice_shield(self):
        """Consume mana to create a protective shield that heals"""
        mana_cost = 30

        if self.mana < mana_cost:
            print(f"❌Not enough mana! Need {mana_cost}, have {self.mana}")
            print("Use regular attacks to regenerate more mana.")
            return False

        # Consume mana and heal
        self.mana -= mana_cost
        heal_amount = 25
        self.health = min(self.health + heal_amount, self.max_health)

        print(f"🧊✨{self.name} conjures an ICE SHIELD!")
        print(f"Magical energy surrounds {self.name}, restoring {heal_amount} health!")
        print(f"Current health: {self.health}/{self.max_health}")
        print(f"Mana remaining: {self.mana}/{self.max_mana}")
        return True

    def regenerate_mana(self):
        """Regenerate mana at the end of turn"""
        if self.mana < self.max_mana:
            self.mana = min(self.mana + self.mana_regen, self.max_mana)

    def display_stats(self):
        print(f"{self.name}'s Stats - Health: {self.health}/{self.max_health}, Attack Power: {self.attack_power}, Mana: {self.mana}/{self.max_mana}, Potions: {self.healing_potions}")

# Archer class
class Archer(Character):
    def __init__(self, name):
        super().__init__(name, health=120, attack_power=20)
        self.focus = 0
        self.max_focus = 5
        self.focus_regen = 1  # Focus regenerated per turn

    def attack(self, opponent):
        """Archer attacks and builds focus"""
        # Calculate random damage
        min_dam = int(self.attack_power * 0.5)
        max_dam = int(self.attack_power * 1.5)
        damage = random.randint(min_dam, max_dam)
        opponent.health -= damage
        print(f"{self.name} shoots an arrow at {opponent.name} for {damage} damage!")

        # Increase focus
        if self.focus < self.max_focus:
            focus_gained = min(self.focus_regen, self.max_focus - self.focus)
            self.focus += focus_gained
            print(f"🎯{self.name} gains {focus_gained} focus! Current focus: {self.focus}/{self.max_focus}")
        else:
            print(f"🎯{self.name}'s focus is at maximum!")

        if opponent.health <= 0:
            print(f"{opponent.name} has been defeated!")

    def use_special_ability(self, opponent):
        """Display special ability menu for Archer"""
        print("\n=== Archer Special Abilities ===")
        print(f"Current Focus: 🎯{self.focus}/{self.max_focus}")
        print("1. Multishot - Fire multiple arrows dealing heavy damage (Costs 2 focus)")
        print("2. Stun Arrow - Stun the wizard for one turn (Costs 4 focus)")
        print("3. Cancel")

        choice = input("Choose an ability: ")
        if choice == '1':
            return self.multishot(opponent)
        elif choice == '2':
            return self.stun_arrow(opponent)
        elif choice == '3':
            print("Cancelled special ability.")
            return False
        else:
            print("Invalid choice. Try again.")
            return self.use_special_ability(opponent)

    def multishot(self, opponent):
        """Fire multiple arrows for increased damage"""
        focus_cost = 2

        if self.focus < focus_cost:
            print(f"❌Not enough focus! Need {focus_cost}, have {self.focus}")
            print("Use regular attacks to build more focus.")
            return False

        # Consume focus and deal amplified damage
        self.focus -= focus_cost
        arrows = 3
        total_damage = int(self.attack_power * arrows)
        opponent.health -= total_damage

        print(f"🏹💥{self.name} uses MULTISHOT!")
        print(f"{self.name} fires {arrows} arrows rapidly!")
        print(f"The arrows strike {opponent.name} for a total of {total_damage} damage!")
        print(f"Focus remaining: {self.focus}/{self.max_focus}")

        if opponent.health <= 0:
            print(f"{opponent.name} has been defeated!")
        return True

    def stun_arrow(self, opponent):
        """Fire a stunning arrow that makes the opponent skip their next turn"""
        focus_cost = 4

        if self.focus < focus_cost:
            print(f"❌Not enough focus! Need {focus_cost}, have {self.focus}")
            print("Use regular attacks to build more focus.")
            return False

        # Consume focus and stun the opponent
        self.focus -= focus_cost
        damage = int(self.attack_power * 1.5)
        opponent.health -= damage

        # Apply stun status effect
        if hasattr(opponent, 'is_stunned'):
            opponent.is_stunned = True

        print(f"🏹✨{self.name} shoots a STUN ARROW!")
        print(f"A precise shot strikes {opponent.name}, dealing {damage} damage!")
        print(f"💫{opponent.name} is stunned and will miss their next turn!")
        print(f"Focus remaining: {self.focus}/{self.max_focus}")

        if opponent.health <= 0:
            print(f"{opponent.name} has been defeated!")
        return True

    def regenerate_focus(self):
        """Regenerate focus at the end of turn"""
        if self.focus < self.max_focus:
            self.focus = min(self.focus + self.focus_regen, self.max_focus)

    def display_stats(self):
        print(f"{self.name}'s Stats - Health: {self.health}/{self.max_health}, Attack Power: {self.attack_power}, Focus: {self.focus}/{self.max_focus}, Potions: {self.healing_potions}")

# Paladin class
class Paladin(Character):
    def __init__(self, name):
        super().__init__(name, health=160, attack_power=20)
        self.holy_power = 0
        self.max_holy_power = 5
        self.holy_regen = 1  # Holy power regenerated per turn
        self.is_invulnerable = False  # For Divine Shield ability

    def attack(self, opponent):
        """Paladin attacks and builds holy power"""
        # Calculate random damage
        min_dam = int(self.attack_power * 0.5)
        max_dam = int(self.attack_power * 1.5)
        damage = random.randint(min_dam, max_dam)

        opponent.health -= damage
        print(f"{self.name} strikes {opponent.name} with holy might for {damage} damage!")

        # Increase holy power
        if self.holy_power < self.max_holy_power:
            holy_power_gained = min(self.holy_regen, self.max_holy_power - self.holy_power)
            self.holy_power += holy_power_gained
            print(f"📿{self.name} gains {holy_power_gained} holy power! Current holy power: {self.holy_power}")
        else:
            print(f"📿{self.name}'s holy power is at maximum!")

        if opponent.health <= 0:
            print(f"{opponent.name} has been defeated!")

    def use_special_ability(self, opponent):
        """Display special ability menu for Paladin"""
        print("\n=== Paladin Special Abilities ===")
        print(f"Current Holy Power: 📿{self.holy_power}/{self.max_holy_power}")
        print("1. Divine Shield - Become invulnerable for 1 turn (Costs 2 holy power)")
        print("2. Lay on Hands - Restore a large amount of health (Costs 4 holy power)")
        print("3. Cancel")

        choice = input("Choose an ability: ")
        if choice == '1':
            return self.divine_shield()
        elif choice == '2':
            return self.lay_on_hands()
        elif choice == '3':
            print("Cancelled special ability.")
            return False
        else:
            print("Invalid choice. Try again.")
            return self.use_special_ability(opponent)

    def divine_shield(self):
        """Become invulnerable for one turn"""
        holy_power_cost = 2

        if self.holy_power < holy_power_cost:
            print(f"❌Not enough holy power! Need {holy_power_cost}, have {self.holy_power}")
            print("Use regular attacks to build more holy power.")
            return False

        # Consume holy power and activate shield
        self.holy_power -= holy_power_cost
        self.is_invulnerable = True

        print(f"🛡️✨{self.name} uses DIVINE SHIELD!")
        print(f"A holy barrier surrounds {self.name}!")
        print(f"{self.name} will be invulnerable and will take NO damage for the next turn!")
        print(f"Holy power remaining: {self.holy_power}/{self.max_holy_power}")
        return True

    def lay_on_hands(self):
        """Restore a large amount of health"""
        holy_power_cost = 4

        if self.holy_power < holy_power_cost:
            print(f"❌Not enough holy power! Need {holy_power_cost}, have {self.holy_power}")
            print("Use regular attacks to build more holy power.")
            return False

        # Consume holy power and heal
        self.holy_power -= holy_power_cost
        heal_amount = 50
        old_health = self.health
        self.health = min(self.health + heal_amount, self.max_health)
        actual_heal = self.health - old_health

        print(f"🙏✨{self.name} uses LAY ON HANDS!")
        print(f"A warm light envelops {self.name}, restoring {actual_heal} health!")
        print(f"Current health: {self.health}/{self.max_health}")
        print(f"Holy power remaining: {self.holy_power}/{self.max_holy_power}")
        return True

    def regenerate_holy_power(self):
        """Regenerate holy power at the end of turn"""
        if self.holy_power < self.max_holy_power:
            self.holy_power = min(self.holy_power + self.holy_regen, self.max_holy_power)

    def take_damage(self, damage):
        """Custom damage calculation considering Divine Shield"""
        if hasattr(self, 'is_invulnerable') and self.is_invulnerable:
            print(f"🛡️Divine Shield active! {self.name} takes NO damage!")
            self.is_invulnerable = False  # Shield lasts for one attack
            return 0
        self.health -= damage
        return damage

    def display_stats(self):
        invuln_status = " [🛡️DIVINE SHIELD ACTIVE] " if hasattr(self, 'is_invulnerable') and self.is_invulnerable else ""
        print(f"{self.name}'s Stats - Health: {self.health}/{self.max_health}, Attack Power: {self.attack_power}, Holy Power: {self.holy_power}/{self.max_holy_power}, Potions: {self.healing_potions} {invuln_status}")

# EvilWizard class
class EvilWizard(Character):
    def __init__(self, name):
        super().__init__(name, health=150, attack_power=15)
        self.is_stunned = False
        self.turn_counter = 0 # Track turns for special ability

    def regenerate(self):
        # Check if stunned first
        if self.is_stunned:
            print(f"💫{self.name} is stunned and cannot regenerate.")
            return

        self.health = min(self.health + 5, self.max_health)
        print(f"{self.name} regenerates 5 health! Current health: {self.health}")

    def attack(self, opponent):
        # Check if stunned
        if self.is_stunned:
            print(f"💫{self.name} is stunned and cannot attack this turn!")
            self.is_stunned = False  # Stun wears off after missing one turn
            print(f"{self.name} recovers from the stun!")
            return

        # Increment turn counter
        self.turn_counter += 1
        # Check if it's time to use special ability (every 4 turns)
        if self.turn_counter % 4 == 0:
            self.dark_bolt(opponent)
        else:
            # Regular attack
            min_dam = int(self.attack_power * 0.5)
            max_dam = int(self.attack_power * 1.5)
            damage = random.randint(min_dam, max_dam)
            opponent.health -= damage
            print(f"{self.name} attacks {opponent.name} for {damage} damage!")
            if opponent.health <= 0:
                print(f"{opponent.name} has been defeated!")

    def dark_bolt(self, opponent):
        """Special Ability - powerful dark magic attack used every 4 turns"""
        special_damage = 35
        spec_dam_max = 60
        damage = random.randint(special_damage, spec_dam_max)
        opponent.health -= damage
        print(f"🌑💥{self.name} unleashes DARK BOLT!")
        print(f"A surge of dark energy hits {opponent.name} for {damage} damage!")
        print(f"👹The dark magic courses through {opponent.name}")

        if opponent.health <= 0:
            print(f"{opponent.name} has been defeated!")

def create_character():
    print("Choose your character class:")
    print("1. Warrior")
    print("2. Mage")
    print("3. Archer")
    print("4. Paladin")

    class_choice = input("Enter the number of your choice: ")
    name = input("Enter your character's name: ")

    if class_choice == '1':
        return Warrior(name)
    elif class_choice == '2':
        return Mage(name)
    elif class_choice == '3':
        return Archer(name)
    elif class_choice == '4':
        return Paladin(name)
    else:
        print("Invalid choice. Defaulting to Warrior.")
        return Warrior(name)

def battle(player, wizard):
    while wizard.health > 0 and player.health > 0:
        print("\n--- ⚔️⚔️⚔️ Your Turn ⚔️⚔️⚔️ ---")
        print("1. Attack")
        print("2. Use Special Ability")
        print("3. Heal")
        print("4. View Stats")

        choice = input("Choose an action: ")

        if choice == '1':
            player.attack(wizard)
        elif choice == '2':
            # Call the character's special ability method
            ability_used = player.use_special_ability(wizard)
            if not ability_used:
                continue  # Let player choose again if ability wasn't used
        elif choice == '3':
            # Use healing potion
            heal_used = player.heal()
            if not heal_used:
                continue  # Let player choose again if no potions left
        elif choice == '4':
            player.display_stats()
            wizard.display_stats()
            continue  # Viewing stats doesn't consume a turn
        else:
            print("Invalid choice. Try again.")
            continue

        # Wizard's turn
        if wizard.health > 0:
            print("\n--- 🧙🧙🧙 Wizard's Turn 🧙🧙🧙 ---")
            wizard.regenerate()

            # Check if player has damage reduction abilities
            if isinstance(player, Warrior) and player.shield_active:
                actual_damage = player.take_damage(wizard.attack_power)
                print(f"{wizard.name} attacks {player.name} for {actual_damage} damage!")
            elif isinstance(player, Paladin) and hasattr(player, 'is_invulnerable') and player.is_invulnerable:
                actual_damage = player.take_damage(wizard.attack_power)
                print(f"{wizard.name} attacks {player.name} but {player.name} takes NO damage due to Divine Shield!")
            else:
                wizard.attack(player)

        if player.health <= 0:
            print(f"\n💀{player.name} has been defeated!")
            break

    if wizard.health <= 0:
        print(f"\n🎉The wizard {wizard.name} has been defeated by {player.name}!")

def main():
    print("=" * 50)
    print("🧙 Defeat the Evil Wizard! 🧙‍")
    print("=" * 50)
    player = create_character()
    wizard = EvilWizard("Malakar the Malevolent")
    print(f"\n{player.name} faces {wizard.name}!")
    battle(player, wizard)

if __name__ == "__main__":
    main()