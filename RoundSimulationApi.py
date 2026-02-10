import logging

from flask import Flask, request, jsonify
from flask_cors import CORS

from typing import List, Dict

from matplotlib import pyplot as plt

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s - %(message)s'
)
logger = logging.getLogger(__name__)

from constants.GameConstants import PLAYER_COUNT, HAND_MAX_CARD_COUNT
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
CORS(app)
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


@app.route("/")
def health_check():
    return "API is up", 200


@app.route('/euchre/simulate/round', methods=['POST'])
def simulate_round():
    try:
        # serialize request
        simulation_request = to_simulation_request(request.json)
        logger.info('Received simulation request: quantity=%s', simulation_request.quantity)

        # transform to RoundSimulation
        simulation = transform_simulation_request_to_simulation(simulation_request)

        # simulate rounds
        simulation = round_simulation_service.simulate(simulation)

        # transform from RoundSimulation
        simulation_response = transform_simulation_to_response(simulation)

        logger.info('Simulation response: %s', simulation_response)

        # pretty_sim_count = f'{simulation.quantity:,}'
        # plot_dict(simulation_response.avg_points_map, 'Team', 'Average Points Won', f'Simulated {pretty_sim_count} Rounds', 4)

        return jsonify(simulation_response), 200
    except Exception as e:
        logger.error('Simulation failed: %s', e, exc_info=True)
        return jsonify(error=str(e)), 500


def to_simulation_request(json_data: Dict) -> RoundSimulationRequest:
    return RoundSimulationRequest(
        player_names=json_data.get('player_names', []),
        player_hands=json_data.get('player_hands', []),
        dealer_name=json_data.get('dealer_name', ''),
        flipped_card=json_data.get('flipped_card', ''),
        caller_name=json_data.get('caller_name', ''),
        call_suit=json_data.get('call_suit', ''),
        call_type=json_data.get('call_type', ''),
        quantity=json_data.get('quantity', '')
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
    team_names = get_team_names(simulation.players)
    team_name_1 = team_names[0]
    team_name_2 = team_names[1]

    # Build player id -> name map
    player_name_by_id = {p.id: p.name for p in simulation.players}

    rounds_count = simulation.quantity

    # Use precomputed totals from the simulation
    tp = simulation.total_points
    tw = simulation.total_wins
    tt = simulation.total_tricks_by_player

    avg_points_map = {
        team_name_1: round(tp[SuitColorEnum.BLACK] / rounds_count, 2),
        team_name_2: round(tp[SuitColorEnum.RED] / rounds_count, 2),
    }
    win_prob_map = {
        team_name_1: round(tw[SuitColorEnum.BLACK] / rounds_count, 2),
        team_name_2: round(tw[SuitColorEnum.RED] / rounds_count, 2),
    }
    avg_tricks_map = {
        player_name_by_id[pid]: round(tricks / rounds_count, 2)
        for pid, tricks in tt.items()
    }

    return RoundSimulationResponse(
        win_prob_map=win_prob_map,
        avg_points_map=avg_points_map,
        avg_tricks_map=avg_tricks_map
    )


def get_team_names(players: List[Player]) -> (str, str):
    team_1 = []
    team_2 = []
    for player in players:
        if player.team == SuitColorEnum.BLACK:
            team_1.append(player.name)
        else:
            team_2.append(player.name)
    team_name_1 = ' & '.join(team_1)
    team_name_2 = ' & '.join(team_2)
    return team_name_1, team_name_2


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

            # validate cards
            if len(players[i].hand.remaining_cards) > HAND_MAX_CARD_COUNT:
                raise Exception(f"Player: {players[i]} has too many cards")
            card_set = set()
            for card in players[i].hand.remaining_cards:
                card_set_length = len(card_set)
                card_set.add(card)
                if len(card_set) == card_set_length:
                    raise Exception(f"Duplicate card: {card} detected for player: {players[i]}")

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


def plot_dict(dict_to_plot, xlabel, ylabel, title, ylim):
    # Extract keys and values
    xvals = [k for k in dict_to_plot.keys()]
    # xvals = list(map.keys())
    yvals = [round(v, 2) for v in dict_to_plot.values()]
    # yvals = list(map.values())

    # Create a bar chart
    plt.bar(xvals, yvals)

    # Add labels and a title
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.title(title)

    # Set y-axis limits to go up to 5
    plt.ylim(0, ylim)

    # Add value annotations on top of the bars
    for i, v in enumerate(yvals):
        plt.text(i, v, str(v), ha='center', va='bottom')

    # Show the chart
    plt.show()


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8080)
