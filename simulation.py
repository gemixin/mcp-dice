class Simulation():
    """A class for the simulation of attacks by an attacker on a defender.
    """

    def __init__(self, attacker, defender):
        """Initialise the simulation.

        Args:
            attacker (Attacker): The Attacker object.
            defender (Defender): The Defender object.
        """
        self.attacker = attacker
        self.defender = defender

        # Logging is false by default and only enabled via generate_single
        self.logging = False
        # Create an empty log to append to if and when logging is enabled
        self.log = ''

    def generate_single(self):
        """Generate a single attack resolution and a log of text.

        Returns:
            str: A log of text.
        """
        # Enable logging
        self.logging = True
        # Resolve the attack and return the output and log
        return self._resolve_attack(), self.log

    def generate_results(self, num_sims):
        """Generate a list of tuples with damage outputs and whether the combo was
        achieved for attacks, simulated a number of times.

        Args:
            num_sims (int): The number of times to simulate the attack.

        Returns:
            list[tuple]: A list of tuples with each damage output (int) and
                whether the combo was achieved (bool).
        """
        return [self._resolve_attack() for _ in range(num_sims)]

    def _resolve_attack(self):
        """Resolve the attack by calling methods on the attacker and defender objects.

        Returns:
            tuple, str: A tuple of damage dealt to the defender by the attacker (int)
                and whether the combo was achieved (bool).
        """
        # ------Roll attacker's initial dice pool------
        self.attacker.initial_roll()
        # ------Roll defender's initial dice pool------
        self.defender.initial_roll()

        if self.logging:
            self._print_status('initial roll')

        # ------Resolve crits for attacker------
        if not self.attacker.status['is_hexed']:
            self.attacker.explode_crits()
        # ------Resolve crits for defender------
        if not self.defender.status['is_hexed']:
            self.defender.explode_crits()

        if self.logging:
            self._print_status('crits exploded')
            self.log += 'Current Damage Output (inc future cover application): '
            self.log += f'{self._calculate_current_damage()}\n'

        # ------Attacker modifies own dice------
        # Resolve any all-or-nothing rerolls
        if self.attacker.status['dr_strange_reroll']:
            self.attacker.decide_dr_strange_reroll(self._calculate_current_damage())
        # Resolve any standard rerolls
        if self.attacker.num_rerolls > 0:
            self.attacker.reroll()

        # ------Defender modifies own dice------
        # Resolve any all-or-nothing rerolls
        if self.defender.status['dr_strange_reroll']:
            self.defender.decide_dr_strange_reroll(self._calculate_current_damage())
        # Resolve any standard rerolls
        if self.defender.num_rerolls > 0:
            self.defender.reroll()

        if self.logging:
            self._print_status('rerolls')

        # Apply cover
        if self.defender.status['has_cover']:
            self.defender.apply_cover()
            if self.logging:
                self._print_status('cover applied')

        # ------Attacker modifies defender's dice------
        # Apply pierce if attacker rolled a wild
        if (self.attacker.status['pierce_on_wild'] and
                'wild' in self.attacker.dice_pool):
            self.defender.apply_pierce()
            if self.logging:
                self._print_status('pierce applied')

        # ------Defender modifies attacker's dice------
        # Nothing here yet

        if self.logging:
            self.log += f'Final Damage Output: {self._calculate_damage()}'

        # ------Calculate results------
        # Default result to return if no combo was provided
        combo_result = False
        # If a special combo was provided, get the bool
        if len(self.attacker.combo) > 0:
            combo_result = self.attacker.check_combo()
            if self.logging:
                self.log += f'\nCombo Achieved: {combo_result}'

        # Return damage and combo bool as a tuple
        return (self._calculate_damage(), combo_result)

    def _print_status(self, phase):
        """Add the relevant message to the log.

        Args:
            phase (str): The phase of the attack which is being logged.
        """
        # Don't log the pierce and cover phases for the attacker (dice are not modified)
        if phase != 'pierce applied' and phase != 'cover applied':
            self.log += f'Attacker dice pool after {phase}: {self.attacker.dice_pool}\n'
        self.log += f'Defender dice pool after {phase}: {self.defender.dice_pool}\n'

    def _calculate_current_damage(self):
        """Calculate the current damage being dealt by the attacker to the defender
        based on the current successes of the dice in their pools and potential
        for future application of cover.

        Returns:
            int: The current damage being dealt by the attacker to the defender.
        """
        # Calculate current damage output
        current_damage = self._calculate_damage()
        # If the defender has cover and has applicable results in dice pool,
        # decrease current damage output
        cover_applied = False
        if self.defender.status['has_cover'] and any(i in self.defender.dice_pool
                                                     for i in ['hit', 'blank']):
            current_damage -= 1
            cover_applied = True
        # If the attacker has pierce on wild and has a wild, and defender has successes
        # in dice pool or defender will apply cover thereby creating a success,
        # increase current damage output
        if (self.attacker.status['pierce_on_wild'] and 'wild' in
                self.attacker.dice_pool and (self.defender.get_successes() > 0
                                             or cover_applied)):
            current_damage += 1
        # Return the current damage dealt (minimum of 0)
        if current_damage < 0:
            return 0
        else:
            return current_damage

    def _calculate_damage(self):
        """Calculate the damage dealt by the attacker to the defender based on the
        successes of the dice in their pools.

        Returns:
            int: The damage dealt by the attacker to the defender.
        """
        # Get successes
        attack_damage = self.attacker.get_successes()
        defence_damage = self.defender.get_successes()

        # If the defender has successes more than or equal to the attacker,
        # no damage is dealt
        if attack_damage <= defence_damage:
            self.damage_dealt = 0
        # Otherwise, the damage dealt is the attacker's successes minus the
        # defender's successes
        else:
            self.damage_dealt = attack_damage - defence_damage

        # Return the damage dealt
        return self.damage_dealt
