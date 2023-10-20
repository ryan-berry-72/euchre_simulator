from dataclasses import dataclass
from enum import Enum, auto
from typing import List, Tuple


@dataclass(eq=True, frozen=True)
class Suit:
    name: "SuitNameEnum"
    color: "SuitColorEnum"


@dataclass(eq=True, frozen=True)
class Card:
    suit: Suit
    value: "CardValueEnum"

    def __str__(self):
        return create_card_name(self.value, self.suit.name)


@dataclass
class Hand:
    starting_cards: List[Card]
    remaining_cards: List[Card]


@dataclass
class Player:
    name: str
    team: "SuitColorEnum"
    hand: Hand
    id: int = 0  # also indicates position (i.e. id 2 is to the left of 1 and id 3 is to the left of 2)


@dataclass
class Play:
    card: Card
    player: Player
    id: int = 0
    is_lead: bool = False  # True if this is the first play in a trick, False otherwise


@dataclass
class Call:
    suit: Suit
    type: "CallTypeEnum"
    player_id: int = 0
    is_complete: bool = False

    def __str__(self):
        return f'Player{self.player_id} called {self.suit.name.name.lower()}'


@dataclass
class Trick:
    plays: List[Play]
    winning_play: Play
    call: Call
    play_suit: Suit
    id: int = 0
    leader_id: int = 0  # id of player that will play the first card
    is_complete: bool = False


@dataclass
class Round:
    players: List[Player]
    player_id_map: dict  # key=player_id, value=player
    tricks: List[Trick]
    tricks_won_map: dict  # key=team, value=quantity_tricks_won
    points_won_map: dict  # key=team, value=points_won
    flipped_card: Card
    call: Call
    id: int = 0
    dealer_id: int = 0  # player_id
    is_complete: bool = False


@dataclass
class Game:
    players: Tuple[Player]
    player_id_map: dict  # key=player_id_map, value=player
    dealer_start_id: int
    rounds: List[Round]
    team_score_map: dict  # key=team, value=score
    winning_team: "SuitColorEnum"
    id: int = 0
    is_complete: bool = False


class CardValueEnum(Enum):
    NINE = auto()
    TEN = auto()
    JACK = auto()
    QUEEN = auto()
    KING = auto()
    ACE = auto()


class SuitNameEnum(Enum):
    SPADES = auto()
    CLUBS = auto()
    HEARTS = auto()
    DIAMONDS = auto()


class SuitColorEnum(Enum):
    BLACK = auto()
    RED = auto()


class CallTypeEnum(Enum):
    REGULAR_P1 = "regular_phase_1"
    REGULAR_P2 = "regular_phase_2"
    LONER_P1 = "loner_phase_1"
    LONER_P2 = "loner_phase_2"

    @staticmethod
    def create(input_string: str):
        try:
            return CallTypeEnum[input_string]
        except KeyError:
            raise Exception(f"'{input_string}' is not a valid enum value.")


def create_card_name(value: CardValueEnum, name: SuitNameEnum) -> str:
    return f'{value.name.lower()}_of_{name.name.lower()}'
