from dtos.BasicDto import *


def create_player_id_map(players):
    player_id_map = {}
    for player in players:
        player_id_map[player.id] = player
    return player_id_map


def create_player_name_map(players):
    player_name_map = {}
    for player in players:
        player_name_map[player.name] = player
    return player_name_map


# finds the teammate of the given player
def get_teammate(players, player):
    for p in players:
        if p != player and p.team == player.team:
            return p
    return None


# determines the player to the left of the last player
def get_next_player(player_id_map, last_player_id):
    next_player_id = last_player_id + 1
    if next_player_id > 4:
        return get_next_player(player_id_map, 0)

    if next_player_id in player_id_map:
        return player_id_map[next_player_id]

    return get_next_player(player_id_map, next_player_id)


# determines the opposite team of the given team
def get_opposing_team(team):
    if team == SuitColorEnum.BLACK:
        return SuitColorEnum.RED
    elif team == SuitColorEnum.RED:
        return SuitColorEnum.BLACK
    else:
        return None


# creates a new dict with the given map and adds the increase amount to the new dict's values
def create_increased_hierarchy(hierarchy_map, increase_amount):
    increased_hierarchy = {}.update(hierarchy_map)
    for key, value in increased_hierarchy.items():
        increased_hierarchy[key] = value + increase_amount
    return increased_hierarchy
