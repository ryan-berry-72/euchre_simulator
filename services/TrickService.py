from typing import Dict

from injector import inject

from constants.GameConstants import trump_and_play_suit_hierarchy
from dtos.BasicDto import Play, Trick, Player
from utils.BasicsUtil import get_next_player
from utils.CardUtil import get_effective_suit


class TrickService:
    @inject
    def __init__(self, play_service):
        self.play_service = play_service

    def play_trick(self, trick: Trick, player_id_map: Dict[int, Player]) -> None:
        player = player_id_map[trick.leader_id]
        play = Play(
            card=None,
            player=player,
            id=1,
            is_lead=True
        )

        while not trick.is_complete:
            self.play_service.choose_play(play, trick.call.suit, trick.play_suit)

            # update results of play
            self.update_play_results(trick, play)

            # determine if round is over
            if len(trick.plays) >= len(player_id_map):
                trick.is_complete = True
            else:
                # prepare next play
                player = get_next_player(player_id_map, play.player.id)
                play = Play(
                    card=None,
                    player=player,
                    id=play.id + 1,
                    is_lead=False
                )

    # updates the result of the play to the trick object
    @staticmethod
    def update_play_results(trick: Trick, play: Play) -> None:
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
