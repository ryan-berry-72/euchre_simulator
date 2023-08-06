from game_basics.RoundService import *
from game_basics.BasicsUtil import *


def play_game(game):
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
        update_call(round)

        # play the round
        play_round(round)

        # update game with results of round
        update_results(game, round)

        # update values for next round
        dealer_id = get_next_player(game.player_id_map, dealer_id).id
        round_id += 1


# updates game score with results of round, clears player hands, and determines if game is over
def update_results(game, round):
    game.rounds.append(round)

    calling_team = round.player_id_map[round.call.player_id].team
    defending_team = get_opposing_team(calling_team)

    calling_team_wins = round.tricks_won_map[calling_team]
    defending_team_wins = round.tricks_won_map[defending_team]

    # update team scores
    if calling_team_wins > defending_team_wins:
        if calling_team_wins == 5:
            if round.call.type == CallTypeEnum.LONER_P1 or round.call.type == CallTypeEnum.LONER_P2:
                game.team_score_map[calling_team] += 4
            else:
                game.team_score_map[calling_team] += 2
        else:
            game.team_score_map[calling_team] += 1
    else:
        game.team_score_map[defending_team] += 2

    # determine if game is over
    if game.team_score_map[calling_team] >= 10:
        game.winning_team = calling_team
        game.is_complete = True
    elif game.team_score_map[defending_team] >= 10:
        game.winning_team = defending_team
        game.is_complete = True

    # ensure players' hands are cleared
    for player in game.players:
        player.hand.remaining_cards = []
        player.hand.starting_cards = ()
