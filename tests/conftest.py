"""Shared fixtures and assertion helpers for euchre tests."""
import random

from constants.GameConstants import (
    euchre_deck, euchre_deck_map, HAND_MAX_CARD_COUNT,
)
from dtos.BasicDto import (
    Call, CallTypeEnum, Round, SuitColorEnum,
)
from dtos.SimulationDto import RoundSimulation
from services.CallService import CallService
from services.DealingService import DealingService
from services.PlayService import PlayService
from services.PlayerService import PlayerService
from services.RoundService import RoundService
from services.ShuffleService import ShuffleService
from services.TrickService import TrickService
from services.simulation.RoundSimulationService import RoundSimulationService
from utils.BasicsUtil import create_player_id_map

EUCHRE_DECK_SET = set(euchre_deck)


# ---- factories --------------------------------------------------------------

def make_players(n=4):
    return PlayerService().create_players(n)


def make_round_service():
    return RoundService(
        trick_service=TrickService(play_service=PlayService()),
        dealing_service=DealingService(),
        call_service=CallService(),
        shuffle_service=ShuffleService(),
    )


def make_simulation_service():
    return RoundSimulationService(
        dealing_service=DealingService(),
        shuffle_service=ShuffleService(),
        call_service=CallService(),
        player_service=PlayerService(),
        round_service=make_round_service(),
    )


def deal_full_hands(players):
    """Deal from the deck, excluding cards already in players' hands."""
    held = {c for p in players for c in p.hand.remaining_cards}
    pool = [c for c in euchre_deck if c not in held]
    random.shuffle(pool)
    DealingService.deal_cards(players, pool)


def build_round(players, trump, caller_id, dealer_id):
    deal_full_hands(players)
    return Round(
        players=list(players),
        player_id_map=create_player_id_map(players),
        tricks=[],
        tricks_won_map={SuitColorEnum.BLACK: 0, SuitColorEnum.RED: 0},
        points_won_map={SuitColorEnum.BLACK: 0, SuitColorEnum.RED: 0},
        flipped_card=euchre_deck_map["ace_of_hearts"],
        call=Call(suit=trump, type=CallTypeEnum.REGULAR_P1, player_id=caller_id),
        id=1,
        dealer_id=dealer_id,
    )


def run_simulation(player_card_names, trump, caller_id, dealer_id, quantity,
                   call_type=CallTypeEnum.REGULAR_P1, flipped="ace_of_hearts"):
    svc = make_simulation_service()
    players = make_players()
    for i, names in enumerate(player_card_names):
        players[i].hand.remaining_cards = [euchre_deck_map[n] for n in names]
    return svc.simulate(RoundSimulation(
        players=players,
        call=Call(suit=trump, type=call_type, player_id=caller_id),
        rounds=[],
        flipped_card=euchre_deck_map[flipped],
        quantity=quantity,
        dealer_id=dealer_id,
        keep_rounds=True,
    ))


# ---- round introspection ----------------------------------------------------

def played_cards(rd):
    """All cards played in a round, in play order."""
    return [play.card for trick in rd.tricks for play in trick.plays]


def played_cards_by_player(rd):
    """{ player_id: [card, ...] } from a round's play records."""
    out = {}
    for trick in rd.tricks:
        for play in trick.plays:
            out.setdefault(play.player.id, []).append(play.card)
    return out


# ---- assertion helpers -------------------------------------------------------

def assert_valid_round(test, rd, num_players=4):
    """Assert all structural invariants that must hold for any completed round."""
    cards = played_cards(rd)
    cards_set = set(cards)
    by_player = played_cards_by_player(rd)
    cards_per_player = HAND_MAX_CARD_COUNT
    expected_total = num_players * cards_per_player

    test.assertEqual(len(rd.tricks), 5,
                     f"Round {rd.id}: expected 5 tricks")

    for trick in rd.tricks:
        test.assertEqual(len(trick.plays), num_players,
                         f"Round {rd.id}, trick {trick.id}: wrong play count")

    test.assertEqual(len(cards), expected_total,
                     f"Round {rd.id}: expected {expected_total} plays, got {len(cards)}")

    test.assertEqual(len(cards_set), expected_total,
                     f"Round {rd.id}: duplicate card played")

    test.assertTrue(cards_set.issubset(EUCHRE_DECK_SET),
                    f"Round {rd.id}: non-euchre card played")

    for pid in rd.player_id_map:
        test.assertEqual(len(by_player.get(pid, [])), cards_per_player,
                         f"Round {rd.id}: player {pid} didn't play {cards_per_player} cards")

    test.assertEqual(sum(rd.tricks_won_map.values()), 5,
                     f"Round {rd.id}: tricks won don't sum to 5")

    pts = rd.points_won_map
    nonzero = [v for v in pts.values() if v > 0]
    test.assertEqual(len(nonzero), 1,
                     f"Round {rd.id}: expected one team to score, got {pts}")
