from typing import List

from constants.GameConstants import trump_suit_hierarchy, play_suit_hierarchy, trump_and_play_suit_hierarchy, \
    euchre_deck_map, suit_name_map, euchre_deck, suits
from dtos.BasicDto import CardValueEnum, Card, Suit

_SHORTHAND_VALUE_MAP = {
    "9": "nine", "10": "ten", "J": "jack", "Q": "queen", "K": "king", "A": "ace"
}
_SHORTHAND_SUIT_CHARS = {
    "S": "spades", "C": "clubs", "H": "hearts", "D": "diamonds"
}

_SHORTHAND_CARD_MAP = {
    f"{vk}{sk}": f"{vv}_of_{sv}"
    for vk, vv in _SHORTHAND_VALUE_MAP.items()
    for sk, sv in _SHORTHAND_SUIT_CHARS.items()
}
_SHORTHAND_CARD_MAP.update({k.lower(): v for k, v in _SHORTHAND_CARD_MAP.items()})

_SHORTHAND_SUIT_MAP = {k: v for k, v in _SHORTHAND_SUIT_CHARS.items()}
_SHORTHAND_SUIT_MAP.update({k.lower(): v for k, v in _SHORTHAND_SUIT_CHARS.items()})


def normalize_card_name(name: str) -> str:
    return _SHORTHAND_CARD_MAP.get(name, name)


def normalize_suit_name(name: str) -> str:
    return _SHORTHAND_SUIT_MAP.get(name, name)


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


# precomputed effective suit cache: (card, trump_suit) -> effective suit
_effective_suit_cache = {}
for _card in euchre_deck:
    for _trump in suits:
        _effective_suit_cache[(_card, _trump)] = (
            _trump if is_trump(_card, _trump) else _card.suit
        )


# gets the effective suit of the card according to trump (accounts for jacks)
def get_effective_suit(card, trump_suit):
    return _effective_suit_cache[(card, trump_suit)]


# key=suit, value=list_of_cards (accounts for jacks in trump suit color)
def create_suit_card_map(cards, trump_suit):
    suit_card_map = {}
    for card in cards:
        effective_suit = get_effective_suit(card, trump_suit)
        if effective_suit not in suit_card_map:
            suit_card_map[effective_suit] = []
        suit_card_map[effective_suit].append(card)
    return suit_card_map


def get_card_by_name(card_name: str) -> Card:
    if card_name is None or not card_name:
        return None
    card_name = normalize_card_name(card_name)
    if card_name not in euchre_deck_map:
        raise ValueError(f'Invalid card name: {card_name}')
    return euchre_deck_map[card_name]


def get_cards_by_names(card_names: List[str]) -> List[Card]:
    return [get_card_by_name(card_name) for card_name in card_names]


def get_suit_by_name(suit_name) -> Suit:
    if suit_name is None or not suit_name:
        return None
    suit_name = normalize_suit_name(suit_name)
    if suit_name not in suit_name_map:
        raise ValueError(f'Invalid suit name: {suit_name}')
    return suit_name_map[suit_name]
