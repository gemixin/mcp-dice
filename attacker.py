from collections import Counter

from player import Player


class Attacker(Player):
    """Subclass of Player specifically for the attacker.

    Args:
        Player (Player): The parent Player object.
    """

    def __init__(self, num_dice, num_rerolls=0, can_reroll_skulls=False,
                 dr_strange_reroll=(False, 0), is_hexed=False, counts_blanks=False,
                 counts_skulls=False, pierce_on_wild=False, combo=([], True)):
        """Take parent params plus attacker-specific pierce_on_wild and combo params.

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
            pierce_on_wild (bool, optional): Whether pierce is applied if a wild result
                is rolled. Defaults to False.
            combo (tuple, optional): A combo that is being looked for (list) and
                whether we want to reroll achieved combos to seek more successes (bool).
                Defaults to ([], True).
        """
        # Call parent constructor
        super().__init__(num_dice, num_rerolls, can_reroll_skulls,
                         dr_strange_reroll, is_hexed, counts_blanks, counts_skulls)

        # Add the attacker-specific params to the parent's status dictionary
        self.status['pierce_on_wild'] = pierce_on_wild

        # Attacker-specific combo params
        self.combo = combo[0]
        self.rerolls_combos = combo[1]

        # Add attacker-specific hit to the parent's success results list
        self.success_results.append('hit')
        # Add attacker-specific block to the parent's rerollable fail results list
        self.rerollable_fails.append('block')

        # Attacker-specific success rate for dice
        self.success_rate = 0.5

    # ------------------------------
    # Overrides parent methods
    # ------------------------------

    def get_text(self):
        """Call parent function with attacker-specific text at start of string.

        Returns:
            str: Attacker-specific text.
        """
        text = 'Attacker' + super().get_text()
        # If a combo was provided
        if len(self.combo) > 0:
            text += f'\nLooking for combo {self.combo}'
        return text

    def decide_dr_strange_reroll(self, current_damage):
        """Call parent function with attacker flag if combo situation allows.

        Args:
            current_damage (int): The current damage being inflicted.
        """
        # If a combo is provided and we should not reroll combos, and a combo is being
        # achieved
        if len(self.combo) > 0 and not self.rerolls_combos and self.check_combo():
            # Don't proceed with reroll check
            pass
        else:
            super().decide_dr_strange_reroll(current_damage, 'attacker')

    def reroll(self):
        """Call parent function with a list of failure results that can be rerolled.
        """
        # Get all rerollable failure results from the dice pool
        failures = [result for result in self.dice_pool
                    if result in self.rerollable_fails]

        # If a combo is provided and we should not reroll combos if a combo is being
        # achieved
        if len(self.combo) > 0 and not self.rerolls_combos and self.check_combo():
            # Remove any combo successes from list of rerollable failures
            failures = list((Counter(failures) - Counter(self.combo)).elements())

        super().reroll(failures)

    # ------------------------------
    # Exclusive methods for attacker
    # ------------------------------

    def check_combo(self):
        """Check the dice pool to see if the required combo has been achieved and
        return True if it has, and False if not.

        Returns:
            bool: Whether the combo has been achieved.
        """
        return not (Counter(self.combo) - Counter(self.dice_pool))
