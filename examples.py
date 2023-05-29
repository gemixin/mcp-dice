from statistics import mean, median
from collections import Counter
import plotly.express as px

from simulation import Simulation
from attacker import Attacker
from defender import Defender

# Create the Attacker object
attacker = Attacker(num_dice=6,
                    num_rerolls=1,
                    can_reroll_skulls=False,
                    dr_strange_reroll=(False, 0),
                    is_hexed=False,
                    counts_blanks=False,
                    counts_skulls=False,
                    pierce_on_wild=False,
                    combo=(['hit', 'crit', 'wild'], True))

# Create the Defender object
defender = Defender(num_dice=3,
                    num_rerolls=0,
                    can_reroll_skulls=False,
                    dr_strange_reroll=(False, 0),
                    is_hexed=False,
                    counts_blanks=False,
                    counts_skulls=False,
                    has_cover=True)

# Create the simulation
sim = Simulation(attacker, defender)
print('-----ATTACKER AND DEFENDER INFO-----')
summary_text = f'{sim.attacker.get_text()}\n{sim.defender.get_text()}'
print(summary_text)

# Simulation of multiple attacks
print('\n-----10,000 ATTACKS-----')
# Generate the results as a list of tuples
results = sim.generate_results(10000)
# Split the list of tuples in to two separate lists
damage, combo_hits = zip(*results)
# Calculate and print the average damage dealt
print(f'Mean damage: {mean(damage)}')
print(f'Median damage: {median(damage)}')
print(f'Range of damage: {min(damage)} to {max(damage)}')
# If a combo was provided, calculate and print the success rate
if len(attacker.combo) > 0:
    percentage = (sum(combo_hits) / len(combo_hits)) * 100
    print('Combo success rate: {0:.4g}%'.format(percentage))
# Generate a graph of damage dealt
count = Counter(list(damage))
x_values = count.keys()
y_values = count.values()
fig = px.bar(x=x_values, y=y_values, title=summary_text,
             labels={'x': 'Damage Dealt', 'y': 'Frequency'})
fig.show()

# Text log from single attack
dmg, log = sim.generate_single()
print('\n-----SINGLE ATTACK-----')
print(f'Output of single attack: {dmg}')
print(f'Log of single attack:\n{log}')
