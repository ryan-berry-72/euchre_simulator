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
        card_index = 0
        for player in players:
            num = HAND_MAX_CARD_COUNT - len(player.hand.remaining_cards)
            dealt = cards[card_index:card_index + num]
            player.hand.remaining_cards = dealt + player.hand.remaining_cards
            player.hand.starting_cards = list(player.hand.remaining_cards)
            card_index += num
        return players
