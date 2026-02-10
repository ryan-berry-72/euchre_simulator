import collections
import csv
import logging
from os.path import isfile

from injector import inject

from constants.GameConstants import trump_and_play_suit_hierarchy
from utils.CardUtil import get_card_rank_by_trump_suit, create_card_name

logger = logging.getLogger(__name__)


class RecordService:
    @inject
    def __init__(self):
        # self.card_rank_wins_map = {}  # key=card_rank, value={key=win_detail, value=quantity}
        pass

    @staticmethod
    def record_games(games, csv_file):
        logger.info('recording %s games to csv %s', len(games), csv_file)

        headers = [
            'game_id',
            'round_id',
            'trick_id',
            'dealer_name',
            'caller_name',
            'call_type',
            'trump_suit',
            'player_name',
            'play_id',
            'play_card_value',
            'play_card_suit',
            'play_card_rank',
            'card_rank',
            'trick_winner'
        ]

        rows = RecordService.generate_rows_to_write(games)

        RecordService.write_rows(csv_file, rows, headers)

    @staticmethod
    def write_rows(csv_file, rows, headers):
        # check if we need to add headers
        file_exists = isfile(csv_file)

        # open the file in the write mode
        with open(csv_file, 'a') as f:
            # create the csv writer
            writer = csv.writer(f)

            # write headers
            if not file_exists:
                writer.writerow(headers)

            # write rows to the csv file
            writer.writerows(rows)

    @staticmethod
    def write_rows_dict(csv_file, rows, fieldnames):
        # check if we need to add headers
        file_exists = isfile(csv_file)

        # open the file in the write mode
        with open(csv_file, 'a') as f:
            # create the csv writer
            writer = csv.DictWriter(f, fieldnames=fieldnames)

            # write headers
            if not file_exists:
                writer.writeheader()

            # write rows to the csv file
            writer.writerows(rows)

    # creates a list of rows to be written to csv
    @staticmethod
    def generate_rows_to_write(games):
        rows = []
        for game in games:
            for euchre_round in game.rounds:
                for trick in euchre_round.tricks:
                    for play in trick.plays:

                        row = [
                            game.id,
                            euchre_round.id,
                            trick.id,
                            euchre_round.player_id_map[euchre_round.dealer_id].name,
                            euchre_round.player_id_map[trick.call.player_id].name,
                            trick.call.type.name,
                            trick.call.suit.name.name,
                            play.player.name,
                            play.id,
                            play.card.value.name,
                            play.card.suit.name.name,
                            trump_and_play_suit_hierarchy[trick.call.suit][trick.play_suit][play.card],
                            get_card_rank_by_trump_suit(play.card, trick.call.suit),
                            trick.winning_play.player.name
                        ]
                        rows.append(row)
        return rows

    @staticmethod
    def update_card_win_probabilities(games, card_rank_wins_map=None):

        if card_rank_wins_map is None:
            card_rank_wins_map = {}
        logger.info('updating win probabilities')

        for game in games:
            for round_ in game.rounds:
                for trick in round_.tricks:
                    for play in trick.plays:
                        card_rank = get_card_rank_by_trump_suit(play.card, trick.call.suit)

                        if card_rank not in card_rank_wins_map:
                            win_map = {'wins': 0, 'plays': 0, 'win_prob': 0.0}
                            card_rank_wins_map[card_rank] = win_map

                        win_map = card_rank_wins_map[card_rank]
                        win_map['plays'] += 1

                        if trick.winning_play.card == play.card:
                            win_map['wins'] += 1

                        win_map['win_prob'] = round(win_map['wins'] / win_map['plays'], 2)

    @staticmethod
    def output_card_win_probabilities(csv_file, card_rank_wins_map):
        ordered_card_rank_wins_map = collections.OrderedDict(sorted(card_rank_wins_map.items()))

        headers = [
            'card_rank',
            'wins',
            'plays',
            'win_prob'
        ]

        rows = []
        for key, value in ordered_card_rank_wins_map.items():
            row = [
                key,
                value['wins'],
                value['plays'],
                value['win_prob']
            ]
            rows.append(row)

        RecordService.write_rows(csv_file, rows, headers)

    @staticmethod
    def record_player_hands(games, csv_file):
        headers = [
            'game_id',
            'round_id',
            'player',
            'card1',
            'card2',
            'card3',
            'card4',
            'card5',
        ]

        rows = []
        for game in games:
            for euchre_round in game.rounds:
                for player in euchre_round.players:
                    if len(player.hand.starting_cards) != 5:
                        logger.error('Invalid call: %s', euchre_round.call)
                        raise Exception(f'Player should have five cards {player}')

                    row = [
                        game.id,
                        euchre_round.id,
                        player.name,
                        create_card_name(player.hand.starting_cards[0]),
                        create_card_name(player.hand.starting_cards[1]),
                        create_card_name(player.hand.starting_cards[2]),
                        create_card_name(player.hand.starting_cards[3]),
                        create_card_name(player.hand.starting_cards[4]),
                    ]
                    rows.append(row)

        RecordService.write_rows(csv_file, rows, headers)
