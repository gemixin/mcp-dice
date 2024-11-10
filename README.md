# Marvel Crisis Protocol Attack Simulator

## Introduction

This Python project simulates attacks in the tabletop game Marvel Crisis Protocol by Atomic Mass Games.

An attack consists of an Attacker and a Defender rolling dice, applying effects, and generating damage.

The simulation allows the user to find the average amount of damage dealt by simulating an attack many thousands of times.

I have included various paramaters to allow for simulating common conditions and special abilities, but this certainly doesn't cover all possibilities within the game.

## Parameters

- The number of dice being rolled initially.
- The number of standard rerolls available.
- Whether skulls can be rerolled during standard rerolls.
- Whether the player can reroll all dice including skulls (Dr Strange 'all or nothing' style reroll) and if so, what damage threshold to base the decision on (Attacker: reroll if current damage being dealt is below the provided value. Defender: reroll if current damage being taken is above the provided value.).
- Whether the hex condition is applied.
- Whether blanks are counted as successes.
- Whether skulls are counted as successes.

### Attacker-only:

- Whether pierce is applied if a wild result is rolled.
- A combo that is being looked for (e.g. ['hit', 'crit', 'wild']) and whether we want to reroll an achieved combo to seek more successes if rerolling. 

### Defender-only:

- Whether cover should be applied.

## Usage

The source code can be used to run simulations using the examples.py file.

![Command line screenshot](/screenshots/cmd.jpg)

![Plotly plot screenshot](/screenshots/plot.jpg)
