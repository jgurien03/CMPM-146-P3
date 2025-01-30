#!/usr/bin/env python
import logging, traceback, sys, os, inspect
logging.basicConfig(filename=__file__[:-3] +'.log', filemode='w', level=logging.DEBUG)
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.append(parentdir)

from behavior_tree_bot.behaviors import *
from behavior_tree_bot.checks import *
from behavior_tree_bot.bt_nodes import Selector, Sequence, Action, Check

from planet_wars import PlanetWars, finish_turn

def setup_behavior_tree():
    # Top-down construction of behavior tree
    root = Selector(name='High Level Ordering of Strategies')

    # Defensive strategy: Protect our planets when under attack
    defensive_plan = Sequence(name='Defensive Strategy')
    under_attack = Check(is_under_attack)
    defend = Action(defend_weakest_planet)
    defensive_plan.child_nodes = [under_attack, defend]

    # Offensive strategy: Attack when we have advantage
    offensive_plan = Sequence(name='Offensive Strategy')
    largest_fleet_check = Check(have_largest_fleet)
    growth_advantage_check = Check(have_growth_advantage)
    attack = Action(attack_weakest_enemy_planet_smart)
    offensive_plan.child_nodes = [largest_fleet_check, growth_advantage_check, attack]

    # Spread strategy: Expand to neutral planets
    aggressive_spread_plan = Sequence(name='Aggressive Spread Strategy')
    neutral_planet_check = Check(neutral_planet_available_with_ships)
    spread_action = Action(spread_to_best_neutral_planet)
    aggressive_spread_plan.child_nodes = [neutral_planet_check, spread_action]

    # Fallback aggressive strategy: Attack anyway if other strategies fail
    fallback_plan = Sequence(name='Fallback Strategy')
    enemy_planet_check = Check(enemy_planet_available_with_ships)
    aggressive_action = Action(aggressive_spread)
    fallback_plan.child_nodes = [enemy_planet_check, aggressive_action]

    # Add all strategies to the root selector
    # They will be tried in order until one succeeds
    root.child_nodes = [defensive_plan, offensive_plan, aggressive_spread_plan, fallback_plan]

    logging.info('\n' + root.tree_to_string())
    return root

def do_turn(state):
    behavior_tree.execute(planet_wars)

if __name__ == '__main__':
    logging.basicConfig(filename=__file__[:-3] + '.log', filemode='w', level=logging.DEBUG)

    behavior_tree = setup_behavior_tree()
    try:
        map_data = ''
        while True:
            current_line = input()
            if len(current_line) >= 2 and current_line.startswith("go"):
                planet_wars = PlanetWars(map_data)
                do_turn(planet_wars)
                finish_turn()
                map_data = ''
            else:
                map_data += current_line + '\n'

    except KeyboardInterrupt:
        print('ctrl-c, leaving ...')
    except Exception:
        traceback.print_exc(file=sys.stdout)
        logging.exception("Error in bot.")