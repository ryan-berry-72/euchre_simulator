import os
from dataclasses import dataclass, field
from typing import Tuple, List, Dict

from dtos.BasicDto import Player, Game, Round, Call, Card


@dataclass
class GameSimulation:
    players: Tuple[Player]
    games: List[Game]
    output_directory: str
    file_name: str
    id: int = 0
    quantity: int = 0  # number of games to be simulated
    record_batch_size: int = 100  # only used if record_games=True
    is_complete: bool = False
    record_games: bool = False  # indicates whether games will be stored and recorded

    def get_full_file_path(self):
        return os.path.join(self.output_directory, self.file_name)


@dataclass
class RoundSimulation:
    players: List[Player]
    call: Call
    rounds: List[Round]
    flipped_card: Card
    dealer_id: int = 0  # 0 represents a random dealer (1-4 are valid player ids)
    id: int = 0
    quantity: int = 1  # number of games to be simulated
    is_complete: bool = False
    keep_rounds: bool = False
    total_points: dict = None
    total_wins: dict = None
    total_tricks_by_player: dict = None
    passing_player_ids: List[int] = field(default_factory=list)


@dataclass
class RoundSimulationRequest:
    player_names: List[str]  # clockwise-ordered list of player names around a table
    player_hands: List[List[str]]  # clockwise-ordered list of players' hands around a table
    dealer_name: str
    flipped_card: str
    caller_name: str
    call_suit: str
    call_type: str  # maps to CallTypeEnum
    quantity: int = 0  # number of games to be simulated
    passing_player_names: List[str] = field(default_factory=list)


@dataclass
class RoundSimulationResponse:
    win_prob_map: Dict[str, float]  # key=player_name, value=win_prob
    avg_points_map: Dict[str, float]  # key=player_name, value=avg_points
    avg_tricks_map: Dict[str, float]  # key=player_name, value=avg_tricks
