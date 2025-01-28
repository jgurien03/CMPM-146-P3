def if_neutral_planet_available(state):
    return any(state.neutral_planets())

def have_largest_fleet(state):
    return sum(planet.num_ships for planet in state.my_planets()) \
             + sum(fleet.num_ships for fleet in state.my_fleets()) \
           > sum(planet.num_ships for planet in state.enemy_planets()) \
             + sum(fleet.num_ships for fleet in state.enemy_fleets())

def have_nearby_threats(state):
    enemy_fleets = state.enemy_fleets()
    for fleet in enemy_fleets:
        if fleet.turns_remaining <= 3:
            return True
    return False

def can_steal_neutral(state):
    for fleet in state.enemy_fleets():
        if fleet.destination_planet in [p.ID for p in state.neutral_planets()]:
            neutral_planet = next(p for p in state.neutral_planets() if p.ID == fleet.destination_planet)
            return True if neutral_planet.num_ships < fleet.num_ships + 2 else False
    return False

def have_excess_ships(state):
    for planet in state.my_planets():
        if planet.num_ships > planet.growth_rate * 5:
            return True
    return False

def under_attack(state):
    return any(fleet.destination_planet in [p.ID for p in state.my_planets()] 
              for fleet in state.enemy_fleets())

def have_high_growth_targets(state):
    return any(p.growth_rate >= 3 for p in state.neutral_planets())