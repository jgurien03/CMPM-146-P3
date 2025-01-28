import sys
sys.path.insert(0, '../')
from planet_wars import issue_order

def attack_weakest_enemy_planet(state):
    strongest_planet = max(state.my_planets(), key=lambda p: p.num_ships, default=None)
    weakest_planet = min(state.enemy_planets(), key=lambda p: p.num_ships, default=None)
    
    if not strongest_planet or not weakest_planet:
        return False
        
    required_ships = weakest_planet.num_ships + state.distance(strongest_planet.ID, weakest_planet.ID) * weakest_planet.growth_rate + 1
    if strongest_planet.num_ships > required_ships:
        return issue_order(state, strongest_planet.ID, weakest_planet.ID, required_ships)
    return False

def spread_to_weakest_neutral_planet(state):
    strongest_planet = max(state.my_planets(), key=lambda p: p.num_ships, default=None)
    weakest_planet = min(state.neutral_planets(), key=lambda p: p.num_ships, default=None)
    
    if not strongest_planet or not weakest_planet:
        return False
    
    required_ships = weakest_planet.num_ships + 1
    if strongest_planet.num_ships > required_ships * 1.5:
        return issue_order(state, strongest_planet.ID, weakest_planet.ID, required_ships)
    return False

def attack_high_growth_planet(state):
    target_planets = [p for p in state.not_my_planets() if p.growth_rate >= 3]
    if not target_planets:
        return False
        
    target_planet = min(target_planets, key=lambda p: p.num_ships)
    my_planets = sorted(state.my_planets(), key=lambda p: p.num_ships, reverse=True)
    
    required_ships = target_planet.num_ships + \
                    state.distance(my_planets[0].ID, target_planet.ID) * target_planet.growth_rate + 1
                    
    total_available = sum(p.num_ships - max(10, p.growth_rate * 3) for p in my_planets if p.num_ships > 10)
    
    if total_available > required_ships:
        return issue_order(state, my_planets[0].ID, target_planet.ID, required_ships)
    return False

def defend_against_threats(state):
    for fleet in state.enemy_fleets():
        if fleet.destination_planet in [p.ID for p in state.my_planets()]:
            target_planet = next(p for p in state.my_planets() if p.ID == fleet.destination_planet)
            
            if target_planet.num_ships < fleet.num_ships:
                reinforcement = fleet.num_ships - target_planet.num_ships + 1
                
                for source in sorted(state.my_planets(), key=lambda p: state.distance(p.ID, target_planet.ID)):
                    if source.ID != target_planet.ID and source.num_ships > reinforcement:
                        return issue_order(state, source.ID, target_planet.ID, reinforcement)
    return False

def steal_neutral_after_enemy(state):
    for fleet in state.enemy_fleets():
        if fleet.destination_planet in [p.ID for p in state.neutral_planets()]:
            target = next(p for p in state.neutral_planets() if p.ID == fleet.destination_planet)
            my_closest = min(state.my_planets(), key=lambda p: state.distance(p.ID, target.ID))
            
            ships_needed = fleet.num_ships + 1
            if my_closest.num_ships > ships_needed * 1.2:
                return issue_order(state, my_closest.ID, target.ID, ships_needed)
    return False