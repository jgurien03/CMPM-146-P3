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

def do_turn(state):
   behavior_tree.execute(state)

def setup_behavior_tree():
   root = Selector(name='High Level Strategy')

   defensive_plan = Sequence(name='Defensive Strategy')
   under_attack_check = Check(under_attack)
   defend = Action(defend_against_threats)
   defensive_plan.child_nodes = [under_attack_check, defend]

   stealing_plan = Sequence(name='Neutral Stealing Strategy')
   can_steal_check = Check(can_steal_neutral)
   steal = Action(steal_neutral_after_enemy)
   stealing_plan.child_nodes = [can_steal_check, steal]

   growth_plan = Sequence(name='High Growth Strategy')
   high_growth_check = Check(have_high_growth_targets)
   attack_growth = Action(attack_high_growth_planet)
   growth_plan.child_nodes = [high_growth_check, attack_growth]

   offensive_plan = Sequence(name='Offensive Strategy')
   largest_fleet_check = Check(have_largest_fleet)
   attack = Action(attack_weakest_enemy_planet)
   offensive_plan.child_nodes = [largest_fleet_check, attack]

   spread_sequence = Sequence(name='Spread Strategy')
   neutral_planet_check = Check(if_neutral_planet_available)
   spread_action = Action(spread_to_weakest_neutral_planet)
   spread_sequence.child_nodes = [neutral_planet_check, spread_action]

   root.child_nodes = [defensive_plan, stealing_plan, growth_plan, 
                      offensive_plan, spread_sequence, attack.copy()]

   logging.info('\n' + root.tree_to_string())
   return root

# Global reference to the behavior tree
behavior_tree = setup_behavior_tree()

if __name__ == '__main__':
   logging.basicConfig(filename=__file__[:-3] + '.log', filemode='w', level=logging.DEBUG)

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