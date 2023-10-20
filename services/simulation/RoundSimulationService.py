from typing import List

from injector import inject

from constants.GameConstants import *
from dtos.BasicDto import Round, SuitColorEnum, Player, Card, Call, CallTypeEnum
from dtos.SimulationDto import RoundSimulation
from services.CallService import CallService
from services.DealingService import DealingService
from services.PlayService import PlayService
from services.PlayerService import PlayerService
from services.RoundService import RoundService
from services.ShuffleService import ShuffleService
from services.TrickService import TrickService
from utils.BasicsUtil import create_player_id_map
import random
import matplotlib.pyplot as plt


class RoundSimulationService:
    @inject
    def __init__(self, dealing_service: DealingService, shuffle_service: ShuffleService, call_service: CallService,
                 player_service: PlayerService, round_service: RoundService):
        self.dealing_service = dealing_service
        self.shuffle_service = shuffle_service
        self.call_service = call_service
        self.player_service = player_service
        self.round_service = round_service

    def simulate(self, round_simulation: RoundSimulation) -> RoundSimulation:
        if round_simulation.players is None:
            round_simulation.players = self.player_service.create_players(PLAYER_COUNT)
        player_ids = [player.id for player in round_simulation.players]

        if round_simulation.call is None:
            # TODO: implement random call using call service
            pass
        random_caller = True if round_simulation.call.player_id == 0 else False

        if round_simulation.flipped_card is None:
            # get random card from remaining cards
            round_simulation.flipped_card = random.choice(self.get_remaining_cards(round_simulation.players))

        random_dealer = True if round_simulation.dealer_id == 0 else False

        # retain player starting cards in a map
        player_cards_map = {}
        for player in round_simulation.players:
            player_cards_map[player.id] = list(player.hand.remaining_cards)

        for round_id in range(1, round_simulation.quantity+1):
            print('Playing round ' + f'{round_id:,}' + '...')

            # get random dealer
            if random_dealer:
                round_simulation.dealer_id = random.choice(player_ids)

            # shuffle and deal remaining cards
            remaining_cards = self.get_remaining_cards(round_simulation.players)
            self.shuffle_service.shuffle_cards(remaining_cards)
            self.dealing_service.deal_cards(round_simulation.players, remaining_cards)

            # get random player to call
            if random_caller:
                round_simulation.call.player_id = random.choice(player_ids)

            euchre_round = Round(
                players=list(round_simulation.players),
                player_id_map=create_player_id_map(round_simulation.players),
                tricks=[],
                tricks_won_map={SuitColorEnum.BLACK: 0, SuitColorEnum.RED: 0},
                points_won_map={SuitColorEnum.BLACK: 0, SuitColorEnum.RED: 0},
                flipped_card=round_simulation.flipped_card,
                call=round_simulation.call,
                id=round_id,
                dealer_id=round_simulation.dealer_id,
            )

            self.round_service.play_round(euchre_round)
            round_simulation.rounds.append(euchre_round)
            print('-'.join([str(v) for v in euchre_round.points_won_map.values()]))

            for player in round_simulation.players:
                player.hand.remaining_cards = list(player_cards_map[player.id])
                player.hand.starting_cards.clear()

        return round_simulation

    @staticmethod
    def get_remaining_cards(players: List[Player]) -> List[Card]:
        cards_in_use = []
        for player in players:
            for card in player.hand.remaining_cards:
                cards_in_use.append(card)
        return list(set(euchre_deck) - set(cards_in_use))


# round_simulation_service = RoundSimulationService(
#     dealing_service=DealingService(),
#     shuffle_service=ShuffleService(),
#     call_service=CallService(),
#     player_service=PlayerService(),
#     round_service=RoundService(
#         trick_service=TrickService(
#             play_service=PlayService()
#         ),
#         dealing_service=DealingService(),
#         call_service=CallService(),
#         shuffle_service=ShuffleService(),
#     )
# )
#
# sim_count = 30000
# call_type = CallTypeEnum.REGULAR_P2
# calling_suit = spades
# players = PlayerService().create_players(PLAYER_COUNT)
# calling_player = players[0]
# # calling_player.hand.remaining_cards = [
# #     euchre_deck_map[jack_of_spades],
# #     euchre_deck_map[ace_of_diamonds],
# #     euchre_deck_map[ace_of_hearts],
# #     euchre_deck_map[ace_of_clubs],
# #     euchre_deck_map[nine_of_hearts],
# # ]
# calling_player.hand.remaining_cards = [
#     euchre_deck_map[ace_of_diamonds],
#     euchre_deck_map[king_of_spades],
#     euchre_deck_map[queen_of_spades],
#     euchre_deck_map[ten_of_spades],
#     euchre_deck_map[nine_of_spades],
# ]
# if len(set(calling_player.hand.remaining_cards)) < 5:
#     raise Exception('Invalid hand')
#
# simulation = round_simulation_service.simulate(
#     RoundSimulation(
#         players=players,
#         call=Call(
#             suit=calling_suit,
#             type=call_type,
#             player_id=calling_player.id
#         ),
#         rounds=[],
#         flipped_card=None,
#         quantity=sim_count
#     )
# )
#
#
# rounds = simulation.rounds
#
#
# total_points_map = {SuitColorEnum.BLACK: 0, SuitColorEnum.RED: 0}
# total_wins_map = {SuitColorEnum.BLACK: 0, SuitColorEnum.RED: 0}
# total_tricks_map = {
#     simulation.players[0].id: 0,
#     simulation.players[1].id: 0,
#     simulation.players[2].id: 0,
#     simulation.players[3].id: 0
# }
# for rd in rounds:
#     total_points_map[SuitColorEnum.BLACK] += rd.points_won_map[SuitColorEnum.BLACK]
#     total_points_map[SuitColorEnum.RED] += rd.points_won_map[SuitColorEnum.RED]
#     total_wins_map[SuitColorEnum.BLACK] += 0 if rd.points_won_map[SuitColorEnum.BLACK] == 0 else 1
#     total_wins_map[SuitColorEnum.RED] += 0 if rd.points_won_map[SuitColorEnum.RED] == 0 else 1
#     for tricks in rd.tricks:
#         total_tricks_map[tricks.winning_play.player.id] += 1
#
#
# rounds_count = len(rounds)
#
# avg_points_map = {SuitColorEnum.BLACK: 0, SuitColorEnum.RED: 0}
# win_prob_map = {SuitColorEnum.BLACK: 0, SuitColorEnum.RED: 0}
# avg_tricks_map = {
#     simulation.players[0].id: 0,
#     simulation.players[1].id: 0,
#     simulation.players[2].id: 0,
#     simulation.players[3].id: 0
# }
#
# for key in avg_points_map.keys():
#     avg_points_map[key] = total_points_map[key] / rounds_count
#     win_prob_map[key] = total_wins_map[key] / rounds_count
#
# for key in avg_tricks_map.keys():
#     avg_tricks_map[key] = total_tricks_map[key] / rounds_count
#
# print(f'\navg points: {avg_points_map}\nwin prob: {win_prob_map}\navg tricks: {avg_tricks_map}')
#
#
# def plot_dict(dict_to_plot, xlabel, ylabel, title, ylim):
#     # Extract keys and values
#     xvals = [k.name for k in dict_to_plot.keys()]
#     # xvals = list(map.keys())
#     yvals = [round(v, 2) for v in dict_to_plot.values()]
#     # yvals = list(map.values())
#
#     # Create a bar chart
#     plt.bar(xvals, yvals)
#
#     # Add labels and a title
#     plt.xlabel(xlabel)
#     plt.ylabel(ylabel)
#     plt.title(title)
#
#     # Set y-axis limits to go up to 5
#     plt.ylim(0, ylim)
#
#     # Add value annotations on top of the bars
#     for i, v in enumerate(yvals):
#         plt.text(i, v, str(v), ha='center', va='bottom')
#
#     # Show the chart
#     plt.show()
#
#
# pretty_sim_count = f'{simulation.quantity:,}'
# plot_dict(avg_points_map, 'Team', 'Average Points Won', f'Simulated {pretty_sim_count} Rounds', 4)
# # plot_dict(win_prob_map, 'Team', 'Win Probability', f'Simulated {pretty_sim_count} Rounds', 1)
# # plot_dict(avg_tricks_map, 'Team', 'Average Tricks Won', f'Simulated {pretty_sim_count} Rounds')
