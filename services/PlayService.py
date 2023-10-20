import random

from injector import inject

from utils.CardUtil import create_suit_card_map


class PlayService:
    @inject
    def __init__(self):
        pass

    # randomly determines a card to play and updates the play object
    # follows the general rules of play (i.e. respects play suit)
    @staticmethod
    def choose_play(play, trump_suit, play_suit):
        player_cards = play.player.hand.remaining_cards

        # leading play
        if play.is_lead:
            # update play card
            random_value = random.randint(0, len(player_cards)-1)
            card_to_play = player_cards[random_value]
        # followup play
        else:
            suit_card_map = create_suit_card_map(player_cards, trump_suit)
            # forced to play the play suit
            if play_suit in suit_card_map:
                cards_in_play_suit = suit_card_map[play_suit]
                random_value = random.randint(0, len(cards_in_play_suit)-1)
                card_to_play = cards_in_play_suit[random_value]
            # short-suited and can play whatever
            else:
                random_value = random.randint(0, len(player_cards)-1)
                card_to_play = player_cards[random_value]

        # update play card and removes card from player's hand
        play.card = card_to_play
        player_cards.remove(play.card)
