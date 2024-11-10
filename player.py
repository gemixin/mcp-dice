import random
from collections import Counter


class Player():
    """The parent class for Attacker and Defender that has all the generic
    player methods that don't apply specifically to attack or defence. Never
    called directly.
    """

    # A list of the 8 sides of the die
    RESULTS = ['crit', 'wild', 'hit', 'hit', 'block', 'blank', 'blank', 'skull']

    def __init__(self, num_dice, num_rerolls=0, can_reroll_skulls=False,
                 dr_strange_reroll=(False, 0), is_hexed=False, counts_blanks=False,
                 counts_skulls=False):
        """Initialise the player.

        Args:
            num_dice (int): The number of dice being rolled initially.
            num_rerolls (int, optional): The number of standard rerolls available.
                Defaults to 0.
            can_reroll_skulls (bool, optional): Whether skulls can be rerolled during
                standard rerolls. Defaults to False.
            dr_strange_reroll (tuple, optional): Whether the player can reroll all dice
                including skulls (bool) and if so, what damage threshold (int) to base
                the decision on. Defaults to (False, 0).
            is_hexed (bool, optional): Whether the hex condition is applied.
                Defaults to False.
            counts_blanks (bool, optional): Whether blanks are counted as successes.
                Defaults to False.
            counts_skulls (bool, optional): Whether skulls are counted as successes.
                Defaults to False.
        """
        # Set the 2 numeric values
        self.num_dice = num_dice
        self.num_rerolls = num_rerolls

        # Set the value for Dr Strange reroll threshold from the passed tuple
        self.dr_strange_reroll_threshold = dr_strange_reroll[1]

        # Set all boolean values inside a dictionary for easy access later (subclass
        # will add specifics to this when initiated)
        self.status = {
            'dr_strange_reroll': dr_strange_reroll[0],
            'can_reroll_skulls': can_reroll_skulls,
            'is_hexed': is_hexed,
            'counts_blanks': counts_blanks,
            'counts_skulls': counts_skulls
        }

        # Create a list of results which are classed as successes (subclass will add
        # specifics to this when initiated)
        # Crits and wild are always successes
        self.success_results = ['crit', 'wild']

        # Create a list of results which are classed as rerollable fails (subclass will
        # add specifics to this when initiated)
        self.rerollable_fails = []

        # Add skulls to successes or rerollable failures (if applicable)
        if self.status['counts_skulls']:
            self.success_results.append('skull')
        else:
            if self.status['can_reroll_skulls']:
                self.rerollable_fails.append('skull')

        # Add blanks to successes or rerollable failures
        if self.status['counts_blanks']:
            self.success_results.append('blank')
        else:
            self.rerollable_fails.append('blank')

    def initial_roll(self):
        """Choose a random result for each die being rolled and add it to a list called
        dice pool.
        """
        self.dice_pool = [random.choice(self.RESULTS) for _ in range(self.num_dice)]

    def explode_crits(self):
        """For each crit result in the dice pool, add a new random result to the pool.
        This simulates the exploding of crits where each crit lets the player roll a
        new die.
        """
        num_crits = self.dice_pool.count('crit')
        for _ in range(num_crits):
            self.dice_pool.append(random.choice(self.RESULTS))

    def _change_die(self, old_value, new_value):
        """Replace the first instance of a result in the dice pool with another.

        Args:
            old_value (str): The die rersult being replaced.
            new_value (str): The new die result.
        """
        for index, result in enumerate(self.dice_pool):
            if result == old_value:
                self.dice_pool[index] = new_value
                break

    def get_text(self):
        """Give an overview of the player as a formatted string.

        Returns:
           str: The player overview text.
        """
        # Create initial string with dice info
        reroll_text = 'rerolls'
        if self.num_rerolls == 1:
            reroll_text = 'reroll'
        text = (f': {self.num_dice} dice with {self.num_rerolls} {reroll_text}')
        # If at least one status is true, append the status text
        if True in self.status.values():
            text += self._get_status_text()
        return text

    def _get_status_text(self):
        """Get any active optional boolean params to append to the player overview text.

        Returns:
            str: The active statuses in square brackets.
        """
        status_text = ' ['
        for key, val in self.status.items():
            if val:
                status_text += key
                # Add extra threshold text for dr_strange_reroll param
                if key == 'dr_strange_reroll' and self.dr_strange_reroll_threshold >= 0:
                    status_text += f' ({self.dr_strange_reroll_threshold})'
                status_text += ', '

        # Remove underscores and trailing comma
        return status_text.replace('_', ' ').rstrip(', ') + ']'

    def get_successes(self):
        """Get the number of successful results in the dice pool for the player.

        Returns:
            int: The number of successful results.
        """
        # Count the dice results
        count = Counter(self.dice_pool)
        return sum([count[result] for result in self.success_results])

    def reroll(self, failures):
        """Update the dice pool with new random results for the number of rerolls,
        making sure to only reroll failures passed by the child class.

        Args:
            failures (list[str]): The results which are considered failures.
        """
        # Sort failures by preferred reroll order (skulls > blanks > blocks/hits)
        failures = sorted(failures, key=self.rerollable_fails.index)
        # Create a reroll pool by selecting failure results equal to number of rerolls
        reroll_pool = failures[:self.num_rerolls]
        # Randomise the results in the reroll pool to create a new list of results
        updated_reroll_pool = [random.choice(self.RESULTS) for result in reroll_pool]
        # Remove old results from the dice pool
        for result in reroll_pool:
            self.dice_pool.remove(result)
        # Append replacement results to end of dice pool
        self.dice_pool.extend(updated_reroll_pool)

    def decide_dr_strange_reroll(self, current_damage, player_type):
        """Check the criteria for a Dr Strange reroll and execute the complete reroll
        function if the criteria is met. This is based on the damage threshold, if
        provided, or the percentage of expected successes if not.

        Args:
            current_damage (int): The current damage being inflicted/taken.
            player_type (str): Whether the player is an 'attacker' or 'defender'.
        """
        # Only proceed if all dice aren't already successes
        if self.get_successes() < len(self.dice_pool):
            # Check if a damage threshold was provided, and if so use that to decide
            if self.dr_strange_reroll_threshold > -1:
                # Attacker-specific
                if player_type == 'attacker':
                    # If current damage being dealt is below the allowed value, reroll
                    if current_damage < self.dr_strange_reroll_threshold:
                        self._complete_reroll()
                # Defender-specific
                elif player_type == 'defender':
                    # If current damage being taken is above the allowed value, reroll
                    if current_damage > self.dr_strange_reroll_threshold:
                        self._complete_reroll()
            # Otherwise, use the percentage of expected successes
            else:
                if self.get_successes() / len(self.dice_pool) < self.success_rate:
                    self._complete_reroll()

    def _complete_reroll(self):
        """Update the dice pool with new random results for all dice.
        """
        # Create a list of random results equal to the length of the current dice pool
        updated_dice_pool = [random.choice(self.RESULTS) for i in
                             range(len(self.dice_pool))]
        # Swap the old results for the new ones in the dice pool
        self.dice_pool = updated_dice_pool
