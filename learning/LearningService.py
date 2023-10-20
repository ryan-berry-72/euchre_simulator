import numpy as np
from services.GameService import *

player1 = Player('Ryan', SuitColorEnum.BLACK, Hand((), []), 1)
player2 = Player('Craig', SuitColorEnum.RED, Hand((), []), 2)
player3 = Player('Kyle', SuitColorEnum.BLACK, Hand((), []), 3)
player4 = Player('Lauren', SuitColorEnum.RED, Hand((), []), 4)
players = (player1, player2, player3, player4)

def start_learning(games_count, c, alpha):
    Q = np.zeros(4032, 6)  # state,action
    gamma = 1.0  # controls how random

    for n in range(games_count):
        game_id = n+1

        epsilon = c/(c+n)

        game = Game(
            players,
            create_player_id_map(players),
            [],
            {SuitColorEnum.BLACK: 0, SuitColorEnum.RED: 0},
            None,
            game_id
        )

        round_id = 1
        random_value = random.randint(1, len(game.player_id_map))
        dealer_id = game.player_id_map[random_value].id
        while not game.is_complete:
            # create a round
            round = Round(
                list(game.players),
                game.player_id_map,
                [],
                {SuitColorEnum.BLACK: 0, SuitColorEnum.RED: 0},
                None,
                None,
                round_id,
                dealer_id,
            )

            # deal and call
            deal_cards(round)

            determine_call(round, Q, )

            # play the round
            play_round(round)

            # update game with results of round
            update_results(game, round)

            # update values for next round
            dealer_id = get_next_player(game.player_id_map, dealer_id).id
            round_id += 1

        if epsilon > random.randrange(0.0, 1.0):
            # choose random action - exploration
            action = random.randint(0, 5)
        else:
            # choose best action - exploitation
            action = get_best_action(Q, state)


def get_best_action(Q, state):

