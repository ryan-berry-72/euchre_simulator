from typing import List, Set

from constants.GameConstants import HAND_MAX_CARD_COUNT
from dtos.BasicDto import Player, Card
from services import ShuffleService


class DealingService:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DealingService, cls).__new__(cls)
        return cls._instance

    @staticmethod
    def deal_cards(players: List[Player], cards: List[Card]) -> List[Player]:
        for player in players:
            num_cards_to_deal = HAND_MAX_CARD_COUNT - len(player.hand.remaining_cards)
            player.hand.remaining_cards = list(cards[:num_cards_to_deal]) + list(player.hand.remaining_cards)
            player.hand.starting_cards = list(player.hand.remaining_cards)
            cards = cards[num_cards_to_deal:]
        return players
