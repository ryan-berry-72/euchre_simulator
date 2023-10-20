from typing import List

from injector import inject

from dtos.BasicDto import Player, Hand, SuitColorEnum


class PlayerService:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(PlayerService, cls).__new__(cls)
        return cls._instance

    @staticmethod
    def create_players(quantity: int) -> List[Player]:
        players = []
        for player_id in range(1, quantity + 1):
            team = SuitColorEnum.RED if player_id % 2 == 0 else SuitColorEnum.BLACK
            players.append(
                Player(
                    name=f'Player{player_id}',
                    team=team,
                    hand=Hand(
                        starting_cards=[],
                        remaining_cards=[]
                    ),
                    id=player_id,
                )
            )
        return players
