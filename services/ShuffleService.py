import random
from typing import List

from dtos.BasicDto import Card


class ShuffleService:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ShuffleService, cls).__new__(cls)
        return cls._instance

    @staticmethod
    def shuffle_cards(cards: List[Card]) -> None:
        random.shuffle(cards)
