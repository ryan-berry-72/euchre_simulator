from game_basics.Basics import *
from game_basics.GameConstants import *


# determines if the given card falls in the trump suit (accounts for jacks)
def is_trump(card, trump_suit):
    if card.suit == trump_suit \
            or (card.value == CardValueEnum.JACK and card.suit.color == trump_suit.color):
        return True
    return False


# get the general card rank (not considering the play suit)
def get_card_rank_by_trump_suit(card, trump_suit):
    if is_trump(card, trump_suit):
        card_rank = trump_suit_hierarchy[trump_suit][card]
    else:
        card_rank = play_suit_hierarchy[card.suit][card]
    return card_rank


# get the card rank according to the trump and play suits
def get_card_rank_by_trump_and_play_suit(card, trump_suit, play_suit):
    return trump_and_play_suit_hierarchy[trump_suit][play_suit][card]


# gets the effective suit of the card according to trump (accounts for jacks)
def get_effective_suit(card, trump_suit):
    if is_trump(card, trump_suit):
        return trump_suit
    else:
        return card.suit


# key=suit, value=list_of_cards (accounts for jacks in trump suit color)
def create_suit_card_map(cards, trump_suit):
    suit_card_map = {}
    for card in cards:
        effective_suit = get_effective_suit(card, trump_suit)
        if effective_suit not in suit_card_map:
            suit_card_map[effective_suit] = []
        suit_card_map[effective_suit].append(card)
    return suit_card_map


# returns the shorthand name for the given card
def get_card_name(card):
    return str(card.value.name) + ' of ' + str(card.suit.name.name)
