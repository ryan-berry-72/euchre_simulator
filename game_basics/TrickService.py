from game_basics.Basics import *
from game_basics.BasicsUtil import *
from game_basics.PlayService import *
from game_basics.GameConstants import *
from game_basics.CardUtil import *


def play_trick(trick, player_id_map):
    player = player_id_map[trick.leader_id]
    play = Play(None, player, 1, True)

    while not trick.is_complete:
        choose_play(play, trick.call.suit, trick.play_suit)

        # update results of play
        update_play_results(trick, play)

        # determine if round is over
        if len(trick.plays) >= len(player_id_map):
            trick.is_complete = True
        else:
            # prepare next play
            player = get_next_player(player_id_map, play.player.id)
            play = Play(None, player, play.id+1, False)


# updates the result of the play to the trick object
def update_play_results(trick, play):
    trick.plays.append(play)

    # update trick play suit
    if play.is_lead:
        trick.play_suit = get_effective_suit(play.card, trick.call.suit)
        trick.winning_play = play
    else:
        best_play_rank = trump_and_play_suit_hierarchy[trick.call.suit][trick.play_suit][trick.winning_play.card]
        current_play_rank = trump_and_play_suit_hierarchy[trick.call.suit][trick.play_suit][play.card]

        # update winning play
        if current_play_rank < best_play_rank:
            trick.winning_play = play
