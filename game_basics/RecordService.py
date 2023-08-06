import csv, collections
from os.path import isfile
from game_basics.CardUtil import *

card_rank_wins_map = {}  # key=card_rank, value={key=win_detail, value=quantity}


def record_games(games, csv_file):
    print('recording', len(games), 'games to csv', csv_file)

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

    rows = generate_rows_to_write(games)

    write_rows(csv_file, rows, headers)


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
def generate_rows_to_write(games):
    rows = []
    for game in games:
        for round in game.rounds:
            for trick in round.tricks:
                for play in trick.plays:

                    row = [
                        game.id,
                        round.id,
                        trick.id,
                        round.player_id_map[round.dealer_id].name,
                        round.player_id_map[trick.call.player_id].name,
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


def update_card_win_probabilities(games):

    print('updating win probabilities')

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


def output_card_win_probabilities(csv_file):
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

    write_rows(csv_file, rows, headers)


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
        for round in game.rounds:
            for player in round.players:
                if len(player.hand.starting_cards) != 5:
                    print(round.call)
                    assert(True == False)

                row = [
                    game.id,
                    round.id,
                    player.name,
                    get_card_name(player.hand.starting_cards[0]),
                    get_card_name(player.hand.starting_cards[1]),
                    get_card_name(player.hand.starting_cards[2]),
                    get_card_name(player.hand.starting_cards[3]),
                    get_card_name(player.hand.starting_cards[4]),
                ]
                rows.append(row)

    write_rows(csv_file, rows, headers)
