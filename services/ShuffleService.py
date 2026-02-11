import random
from typing import List

from dtos.BasicDto import Card


class ShuffleService:
    @staticmethod
    def shuffle_cards(cards: List[Card]) -> None:
        random.shuffle(cards)
