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


MAX_SIMULATION_QUANTITY = 1_000_000

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

        # validate request fields
        validate_simulation_request(simulation_request)

        # transform to RoundSimulation
        simulation = transform_simulation_request_to_simulation(simulation_request)

        # validate cross-field business rules
        validate_simulation(simulation)

        # simulate rounds
        simulation = round_simulation_service.simulate(simulation)

        # transform from RoundSimulation
        simulation_response = transform_simulation_to_response(simulation)

        logger.info('Simulation response: %s', simulation_response)

        return jsonify(simulation_response), 200
    except ValueError as e:
        logger.warning('Validation error: %s', e)
        return jsonify(error=str(e)), 400
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


def validate_simulation_request(simulation_request: RoundSimulationRequest):
    if simulation_request.quantity is not None and simulation_request.quantity <= 0:
        raise ValueError(f"quantity must be a positive integer, got {simulation_request.quantity}")
    if simulation_request.quantity is not None and simulation_request.quantity > MAX_SIMULATION_QUANTITY:
        raise ValueError(f"quantity must not exceed {MAX_SIMULATION_QUANTITY}, got {simulation_request.quantity}")


def validate_simulation(simulation: RoundSimulation):
    # Check for duplicate cards across all player hands
    all_cards = []
    for player in simulation.players:
        for card in player.hand.remaining_cards:
            if card in all_cards:
                raise ValueError(f"Duplicate card '{card}' found across player hands")
            all_cards.append(card)

    # Check that flipped card is not in any player's hand.
    # For P1 calls the dealer has already picked up the flipped card,
    # so it legitimately appears in a player's hand.
    is_p2_call = (simulation.call is not None
                  and simulation.call.type in (CallTypeEnum.REGULAR_P2, CallTypeEnum.LONER_P2))
    if (simulation.flipped_card is not None
            and simulation.flipped_card in all_cards
            and is_p2_call):
        raise ValueError(f"Flipped card '{simulation.flipped_card}' is already in a player's hand")

    # For P1 calls, the call suit must match the flipped card's suit
    if (simulation.call is not None
            and simulation.flipped_card is not None
            and simulation.call.type in (CallTypeEnum.REGULAR_P1, CallTypeEnum.LONER_P1)
            and simulation.call.suit != simulation.flipped_card.suit):
        raise ValueError(
            f"For phase 1 calls, the call suit must match the flipped card's suit "
            f"('{simulation.flipped_card.suit.name.name.lower()}'), "
            f"got '{simulation.call.suit.name.name.lower()}'"
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
            raise ValueError(f'Number of player names must be {PLAYER_COUNT}')
        if len(simulation_request.player_hands) != len(players):
            raise ValueError(f'Number of player hands must be {PLAYER_COUNT}')

        # update players and cards
        for i in range(len(simulation_request.player_names)):
            players[i].name = simulation_request.player_names[i]
            players[i].hand.remaining_cards = get_cards_by_names(simulation_request.player_hands[i])

            # validate cards
            if len(players[i].hand.remaining_cards) > HAND_MAX_CARD_COUNT:
                raise ValueError(f"Player: {players[i]} has too many cards")
            card_set = set()
            for card in players[i].hand.remaining_cards:
                card_set_length = len(card_set)
                card_set.add(card)
                if len(card_set) == card_set_length:
                    raise ValueError(f"Duplicate card: {card} detected for player: {players[i]}")

    return players


def get_call_from_sim(simulation_request: RoundSimulationRequest, player_name_map: Dict[str, Player]) -> Call:
    suit = get_suit_by_name(simulation_request.call_suit)
    call_type_str = simulation_request.call_type
    if not call_type_str:
        call_type = CallTypeEnum.REGULAR_P1
    else:
        call_type = CallTypeEnum.create(call_type_str)
    if suit is None:
        return None
    return Call(
        suit=suit,
        type=call_type,
        player_id=get_id_or_default(simulation_request.caller_name, player_name_map, 0)
    )


def get_id_or_default(player_name: str, player_name_map: Dict[str, Player], default_value: int) -> int:
    if not player_name:
        return default_value
    if player_name not in player_name_map:
        valid_names = ', '.join(sorted(player_name_map.keys()))
        raise ValueError(f"'{player_name}' does not match any player. Valid names: {valid_names}")
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
