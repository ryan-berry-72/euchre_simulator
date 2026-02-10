import random

from injector import inject

from utils.CardUtil import get_effective_suit


class PlayService:
    @inject
    def __init__(self):
        pass

    # randomly determines a card to play and updates the play object
    # follows the general rules of play (i.e. respects play suit)
    @staticmethod
    def choose_play(play, trump_suit, play_suit):
        player_cards = play.player.hand.remaining_cards

        if play.is_lead:
            idx = random.randrange(len(player_cards))
        else:
            matching = [i for i, c in enumerate(player_cards)
                        if get_effective_suit(c, trump_suit) == play_suit]
            idx = random.choice(matching) if matching else random.randrange(len(player_cards))

        play.card = player_cards.pop(idx)
