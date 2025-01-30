def if_neutral_planet_available(state):
    # Check if there are any neutral planets we aren't already targeting
    return any(planet for planet in state.neutral_planets()
              if not any(fleet.destination_planet == planet.ID for fleet in state.my_fleets()))

def have_largest_fleet(state):
    # Compare total ships (planets + fleets) between us and enemy
    return sum(planet.num_ships for planet in state.my_planets()) \
           + sum(fleet.num_ships for fleet in state.my_fleets()) \
           > sum(planet.num_ships for planet in state.enemy_planets()) \
           + sum(fleet.num_ships for fleet in state.enemy_fleets())

def is_under_attack(state):
    # Check if any of our planets have incoming enemy fleets
    return any(fleet.destination_planet == planet.ID 
              for planet in state.my_planets() 
              for fleet in state.enemy_fleets())

def have_growth_advantage(state):
    # Compare total production (growth) rates between us and enemy
    my_growth = sum(planet.growth_rate for planet in state.my_planets())
    enemy_growth = sum(planet.growth_rate for planet in state.enemy_planets())
    return my_growth > enemy_growth * 0.8  # We only need 80% of enemy's growth

def neutral_planet_available_with_ships(state):
    # Check if we have enough ships to capture any neutral planets
    my_total_ships = sum(planet.num_ships for planet in state.my_planets())
    return any(planet for planet in state.neutral_planets() 
              if planet.num_ships < my_total_ships / 2 and  # Only consider if we can capture with half our ships
              not any(fleet.destination_planet == planet.ID for fleet in state.my_fleets()))

def enemy_planet_available_with_ships(state):
    # Check if we have enough ships to capture any enemy planets
    my_total_ships = sum(planet.num_ships for planet in state.my_planets())
    return any(planet for planet in state.enemy_planets()
              if planet.num_ships < my_total_ships / 2 and  # Only consider if we can capture with half our ships
              not any(fleet.destination_planet == planet.ID for fleet in state.my_fleets()))