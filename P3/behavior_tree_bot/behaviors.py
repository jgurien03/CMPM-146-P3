import sys
sys.path.insert(0, '../')
from planet_wars import issue_order

def attack_weakest_enemy_planet_smart(state):
    # Get all my planets that aren't currently being attacked
    my_planets = [planet for planet in state.my_planets() 
                  if not any(fleet.destination_planet == planet.ID for fleet in state.enemy_fleets())]
    
    if not my_planets:
        return False
        
    # Find our strongest planet to attack from
    strongest_planet = max(my_planets, key=lambda p: p.num_ships)

    # Get enemy planets that we aren't already attacking
    enemy_planets = [planet for planet in state.enemy_planets() 
                    if not any(fleet.destination_planet == planet.ID for fleet in state.my_fleets())]
    
    if not enemy_planets:
        return False
        
    # Score enemy planets based on ships, growth rate, and distance
    def planet_score(planet):
        distance = state.distance(strongest_planet.ID, planet.ID)
        growth_factor = planet.growth_rate * distance  # Consider growth during travel time
        return (planet.num_ships + growth_factor) / (planet.growth_rate + 1)
    
    # Choose the enemy planet with the lowest score (easiest to capture)
    target_planet = min(enemy_planets, key=planet_score)
    
    # Calculate ships needed considering growth during travel
    required_ships = target_planet.num_ships + \
                    state.distance(strongest_planet.ID, target_planet.ID) * target_planet.growth_rate + 1
    
    # Only attack if we have enough ships
    if strongest_planet.num_ships > required_ships:
        return issue_order(state, strongest_planet.ID, target_planet.ID, required_ships)
    return False

def spread_to_best_neutral_planet(state):
    # Get my planets that aren't under attack
    my_planets = [planet for planet in state.my_planets() 
                  if not any(fleet.destination_planet == planet.ID for fleet in state.enemy_fleets())]
    
    if not my_planets:
        return False
        
    # Get neutral planets we aren't already targeting
    neutral_planets = [planet for planet in state.neutral_planets() 
                      if not any(fleet.destination_planet == planet.ID for fleet in state.my_fleets())]
    
    if not neutral_planets:
        return False

    def evaluate_planet_value(neutral_planet, my_planet):
        distance = state.distance(my_planet.ID, neutral_planet.ID)
        ships_needed = neutral_planet.num_ships + 1
        if ships_needed >= my_planet.num_ships:
            return -1
        
        # Calculate value based on growth rate, distance, and required ships
        return (neutral_planet.growth_rate * 100) / (ships_needed * distance + 1)

    # Find the best value planet and source combination
    best_value = -1
    target_planet = None
    source_planet = None

    for my_planet in my_planets:
        for neutral_planet in neutral_planets:
            value = evaluate_planet_value(neutral_planet, my_planet)
            if value > best_value:
                best_value = value
                target_planet = neutral_planet
                source_planet = my_planet

    # Attack if we found a valuable target
    if best_value > 0:
        return issue_order(state, source_planet.ID, target_planet.ID, target_planet.num_ships + 1)
    return False

def defend_weakest_planet(state):
    # Only defend if we have multiple planets
    my_planets = state.my_planets()
    if not my_planets or len(my_planets) < 2:
        return False
        
    def planet_under_attack_value(planet):
        # Calculate how many enemy ships are incoming
        incoming_fleets = [fleet for fleet in state.enemy_fleets() 
                          if fleet.destination_planet == planet.ID]
        if not incoming_fleets:
            return 0
            
        # Return deficit of ships (negative means we can defend ourselves)
        total_attacking_ships = sum(fleet.num_ships for fleet in incoming_fleets)
        return total_attacking_ships - planet.num_ships
    
    # Find the planet most in need of defense
    weakest_planet = max(my_planets, key=planet_under_attack_value)
    threat_value = planet_under_attack_value(weakest_planet)
    
    # If no real threat, don't defend
    if threat_value <= 0:
        return False

    # Find planets that can send reinforcements
    other_planets = [planet for planet in my_planets 
                    if planet.ID != weakest_planet.ID and 
                    not any(fleet.destination_planet == planet.ID for fleet in state.enemy_fleets())]
    
    if not other_planets:
        return False
        
    # Send reinforcements from our strongest available planet
    reinforcement_planet = max(other_planets, key=lambda p: p.num_ships)
    ships_to_send = min(reinforcement_planet.num_ships - 1, threat_value + 1)
    
    if ships_to_send > 0:
        return issue_order(state, reinforcement_planet.ID, weakest_planet.ID, ships_to_send)
    return False

def aggressive_spread(state):
    # Get all my planets
    my_planets = [planet for planet in state.my_planets()]
    if not my_planets:
        return False

    # Get all planets we aren't already attacking
    target_planets = [planet for planet in state.not_my_planets() 
                     if not any(fleet.destination_planet == planet.ID for fleet in state.my_fleets())]
    
    if not target_planets:
        return False

    # Try to spread from our strongest planets to weakest targets
    for my_planet in sorted(my_planets, key=lambda p: p.num_ships, reverse=True):
        for target_planet in sorted(target_planets, key=lambda p: p.num_ships):
            required_ships = target_planet.num_ships + 1
            if target_planet.owner != 0:  # If it's an enemy planet
                # Account for growth during travel
                required_ships += state.distance(my_planet.ID, target_planet.ID) * target_planet.growth_rate
            
            # Attack if we have enough ships plus a 10% buffer
            if my_planet.num_ships > required_ships * 1.1:
                return issue_order(state, my_planet.ID, target_planet.ID, required_ships)
                
    return False