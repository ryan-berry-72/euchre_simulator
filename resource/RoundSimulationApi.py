from flask import Flask, request, jsonify
from typing import List, Dict

from constants.GameConstants import PLAYER_COUNT
from dtos.BasicDto import Player, Call, CallTypeEnum, SuitColorEnum
from dtos.SimulationDto import RoundSimulationRequest, RoundSimulation, RoundSimulationResponse
from services.CallService import CallService
from services.DealingService import DealingService
from services.PlayService import PlayService
from services.PlayerService import PlayerService
from services.RoundService import RoundService
from services.ShuffleService import ShuffleService
from services.TrickService import TrickService
from services.simulation.RoundSimulationService import RoundSimulationService
from utils.BasicsUtil import create_player_name_map
from utils.CardUtil import get_card_by_name, get_cards_by_names, get_suit_by_name

app = Flask(__name__)
player_service = PlayerService()
round_simulation_service = RoundSimulationService(
    dealing_service=DealingService(),
    shuffle_service=ShuffleService(),
    call_service=CallService(),
    player_service=player_service,
    round_service=RoundService(
        trick_service=TrickService(
            play_service=PlayService()
        ),
        dealing_service=DealingService(),
        call_service=CallService(),
        shuffle_service=ShuffleService(),
    )
)


@app.route('/euchre/simulate/round', methods=['POST'])
def simulate_round():
    try:
        # serialize request
        simulation_request = to_simulation_request(request.json)
        print(simulation_request)

        # transform to RoundSimulation
        simulation = transform_simulation_request_to_simulation(simulation_request)

        # simulate rounds
        simulation = round_simulation_service.simulate(simulation)

        # transform from RoundSimulation
        simulation_response = transform_simulation_to_response(simulation)

        print(simulation_response)

        return jsonify(simulation_response), 200
    except Exception as e:
        print(e)
        return jsonify(e), 400


def to_simulation_request(json_data: Dict) -> RoundSimulationRequest:
    return RoundSimulationRequest(
        player_names=json_data['player_names'],
        player_hands=json_data['player_hands'],
        dealer_name=json_data['dealer_name'],
        flipped_card=json_data['flipped_card'],
        caller_name=json_data['caller_name'],
        call_suit=json_data['call_suit'],
        call_type=json_data['call_type'],
        quantity=json_data['quantity']
    )


def transform_simulation_request_to_simulation(simulation_request: RoundSimulationRequest) -> RoundSimulation:
    players = get_players_from_sim(simulation_request)
    player_name_map = create_player_name_map(players)

    return RoundSimulation(
        players=players,
        call=get_call_from_sim(simulation_request, player_name_map),
        rounds=[],
        flipped_card=get_card_by_name(simulation_request.flipped_card),
        dealer_id=get_id_or_default(simulation_request.dealer_name, player_name_map, 0),
        quantity=simulation_request.quantity
    )


def transform_simulation_to_response(simulation: RoundSimulation) -> RoundSimulationResponse:
    rounds = simulation.rounds
    team_name_1 = simulation.players[0].name + ' & ' + simulation.players[2].name
    team_name_2 = simulation.players[1].name + ' & ' + simulation.players[3].name

    total_points_map = {team_name_1: 0, team_name_2: 0}
    total_wins_map = {team_name_1: 0, team_name_2: 0}
    total_tricks_map = {player.name: 0 for player in simulation.players}

    for rd in rounds:
        total_points_map[team_name_1] += rd.points_won_map[SuitColorEnum.BLACK]
        total_points_map[team_name_2] += rd.points_won_map[SuitColorEnum.RED]
        total_wins_map[team_name_1] += 0 if rd.points_won_map[SuitColorEnum.BLACK] == 0 else 1
        total_wins_map[team_name_2] += 0 if rd.points_won_map[SuitColorEnum.RED] == 0 else 1
        for tricks in rd.tricks:
            total_tricks_map[tricks.winning_play.player.name] += 1

    rounds_count = len(rounds)

    avg_points_map = {team_name_1: 0, team_name_2: 0}
    win_prob_map = {team_name_1: 0, team_name_2: 0}
    avg_tricks_map = {player.name: 0 for player in simulation.players}

    for key in avg_points_map.keys():
        avg_points_map[key] = round(total_points_map[key] / rounds_count, 2)
        win_prob_map[key] = round(total_wins_map[key] / rounds_count, 2)

    for key in avg_tricks_map.keys():
        avg_tricks_map[key] = round(total_tricks_map[key] / rounds_count, 2)

    return RoundSimulationResponse(
        win_prob_map=win_prob_map,
        avg_points_map=avg_points_map,
        avg_tricks_map=avg_tricks_map
    )


def get_players_from_sim(simulation_request: RoundSimulationRequest) -> List[Player]:
    players = player_service.create_players(PLAYER_COUNT)
    if simulation_request.player_names is not None:
        # validation
        if len(simulation_request.player_names) != len(players):
            raise Exception('Number of player names must be', PLAYER_COUNT)
        if len(simulation_request.player_hands) != len(players):
            raise Exception('Number of player hands must be', PLAYER_COUNT)

        # update players and cards
        for i in range(len(simulation_request.player_names)):
            players[i].name = simulation_request.player_names[i]
            players[i].hand.remaining_cards = get_cards_by_names(simulation_request.player_hands[i])

    return players


def get_call_from_sim(simulation_request: RoundSimulationRequest, player_name_map: Dict[str, Player]) -> Call:
    return Call(
        suit=get_suit_by_name(simulation_request.call_suit),
        type=CallTypeEnum.create(simulation_request.call_type),
        player_id=get_id_or_default(simulation_request.caller_name, player_name_map, 0)
    )


def get_id_or_default(player_name: str, player_name_map: Dict[str, Player], default_value: int) -> int:
    if player_name is None or player_name not in player_name_map:
        return default_value
    return player_name_map[player_name].id


if __name__ == '__main__':
    app.run(debug=True)
