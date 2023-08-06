from game_basics.Basics import *


@dataclass
class State:  # 4032 possible states
    most_common_suit: Suit  # [0,3] where 0=spades, 1=clubs, 2=hearts, 3=diamonds
    most_common_suit_count: int  # [2,5]
    bower_count: int  # [0,2]
    off_suit_aces_count: int  # [0,3]
    flipped_card_rank: int  # [1,7]
    call_phase: int  # [0,2] where 0=give card to opponent, 1=give card to ally, 2=call suit


@dataclass
class QPair:
    state: State
    action: "ActionEnum"
    value: float = 0


class ActionEnum(Enum):
    PASS = 0,
    GIVE_OPPONENT = 1,
    GIVE_OPPONENT_LONER = 2,
    GIVE_ALLY = 3,
    GIVE_ALLY_LONER = 4,
    CALL_SUIT = 5,
    CALL_SUIT_LONER = 6
