from player import Player


class Defender(Player):
    """Subclass of Player specifically for the defender.

    Args:
        Player (Player): The parent Player object.
    """

    def __init__(self, num_dice, num_rerolls=0, can_reroll_skulls=False,
                 dr_strange_reroll=(False, 0), is_hexed=False, counts_blanks=False,
                 counts_skulls=False, has_cover=False):
        """Take parent params plus defender-specific has_cover param.

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
            has_cover (bool, optional):Whether cover should be applied.
                Defaults to False.
        """
        # Call parent constructor
        super().__init__(num_dice, num_rerolls, can_reroll_skulls,
                         dr_strange_reroll, is_hexed, counts_blanks, counts_skulls)

        # Add the defender-specific param to the parent's status dictionary
        self.status['has_cover'] = has_cover

        # Add defender-specific block to the parent's success results list
        self.success_results.append('block')
        # Add defender-specific hit to the parent's rerollable fail results list
        self.rerollable_fails.append('hit')

        # Defender-specific success rate for dice
        self.success_rate = 0.375

    # ------------------------------
    # Overrides parent methods
    # ------------------------------

    def get_text(self):
        """Call parent function with defender-specific text at start of string.

        Returns:
            str: Defender-specific text.
        """
        return 'Defender' + super().get_text()

    def decide_dr_strange_reroll(self, current_damage):
        """Calls parent function with defender flag.

        Args:
            current_damage (int): The current damage being taken.
        """
        super().decide_dr_strange_reroll(current_damage, 'defender')

    def reroll(self):
        """Call parent function with a list of failure results that can be rerolled.
        """
        # Get all rerollable failure results from the dice pool
        failures = [result for result in self.dice_pool
                    if result in self.rerollable_fails]
        super().reroll(failures)

    # ------------------------------
    # Exclusive methods for defender
    # ------------------------------

    def apply_pierce(self):
        """Apply pierce by changing a result to a blank. First choice = crit, second
        choice = wild, third choice = block.
        """
        if 'crit' in self.dice_pool:
            self._change_die('crit', 'blank')
        elif 'wild' in self.dice_pool:
            self._change_die('wild', 'blank')
        elif 'block' in self.dice_pool:
            self._change_die('block', 'blank')

    def apply_cover(self):
        """Apply cover by changing a result to a block. First choice = hit, second
        choice = blank.
        """
        if 'hit' in self.dice_pool:
            self._change_die('hit', 'block')
        elif 'blank' in self.dice_pool:
            self._change_die('blank', 'block')
