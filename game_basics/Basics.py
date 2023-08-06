from dataclasses import dataclass
from enum import Enum
from typing import List, Tuple


@dataclass(eq=True, frozen=True)
class Suit:
    name: "SuitNameEnum"
    color: "SuitColorEnum"


@dataclass(eq=True, frozen=True)
class Card:
    suit: Suit
    value: "CardValueEnum"


@dataclass
class Hand:
    starting_cards: Tuple[Card]
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
    flipped_card: Card
    call: Call
    id: int = 0
    dealer_id: int = 0  # player_id
    is_complete: bool = False


@dataclass
class Game:
    players: Tuple[Player]
    player_id_map: dict  # key=player_id_map, value=player
    rounds: List[Round]
    team_score_map: dict  # key=team, value=score
    winning_team: "SuitColorEnum"
    id: int = 0
    is_complete: bool = False


@dataclass
class Simulation:
    players: Tuple[Player]
    games: List[Game]
    output_directory: str
    file_postfix: str
    id: int = 0
    quantity: int = 0  # number of games to be simulated
    record_batch_size: int = 100  # only used if record_games=True
    is_complete: bool = False
    record_games: bool = False  # indicates whether games will be stored and recorded


class CardValueEnum(Enum):
    ACE = 1,
    TWO = 2,
    THREE = 3,
    FOUR = 4,
    FIVE = 5,
    SIX = 6,
    SEVEN = 7,
    EIGHT = 8,
    NINE = 9,
    TEN = 10,
    JACK = 11,
    QUEEN = 12,
    KING = 13


class SuitNameEnum(Enum):
    SPADES = "Spades",
    CLUBS = "Clubs",
    HEARTS = "Hearts",
    DIAMONDS = "Diamonds"


class SuitColorEnum(Enum):
    BLACK = "Black",
    RED = "Red"


class CallTypeEnum(Enum):
    REGULAR_P1 = "Regular Phase 1",
    REGULAR_P2 = "Regular Phase 2",
    LONER_P1 = "Loner Phase 1",
    LONER_P2 = "Loner Phase 2"
