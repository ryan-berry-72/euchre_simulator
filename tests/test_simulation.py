"""Integration tests for euchre round and multi-round simulation."""
import random
import unittest

from constants.GameConstants import (
    euchre_deck_map, spades, clubs, hearts, diamonds,
)
from dtos.BasicDto import Call, CallTypeEnum, SuitColorEnum
from dtos.SimulationDto import RoundSimulation
from tests.conftest import (
    assert_valid_round,
    build_round,
    make_game,
    make_game_service,
    make_players,
    make_round_service,
    make_simulation_service,
    played_cards,
    played_cards_by_player,
    run_simulation,
)


class TestRound(unittest.TestCase):
    """A single round must complete with valid structure and scoring."""

    def _play_round(self, trump, caller_id=1, dealer_id=1):
        players = make_players()
        rd = build_round(players, trump, caller_id, dealer_id)
        make_round_service().play_round(rd)
        return rd, players

    def test_structural_invariants(self):
        for trump in [spades, hearts, clubs, diamonds]:
            rd, _ = self._play_round(trump)
            assert_valid_round(self, rd)

    def test_hands_empty_after_round(self):
        _, players = self._play_round(spades)
        for p in players:
            self.assertEqual(len(p.hand.remaining_cards), 0)

    def test_valid_point_values(self):
        valid = {(0, 2), (2, 0), (1, 0), (0, 1)}
        random.seed(7)
        for _ in range(50):
            rd, _ = self._play_round(spades)
            pts = tuple(rd.points_won_map.values())
            self.assertIn(pts, valid, f"Unexpected scoring: {pts}")

    def test_top_five_trump_always_sweep(self):
        """Right bower + left bower + A/K/Q of trump must win all 5 tricks."""
        players = make_players()
        players[0].hand.remaining_cards = [
            euchre_deck_map["jack_of_spades"], euchre_deck_map["jack_of_clubs"],
            euchre_deck_map["ace_of_spades"], euchre_deck_map["king_of_spades"],
            euchre_deck_map["queen_of_spades"],
        ]
        rd = build_round(players, spades, 1, 1)
        make_round_service().play_round(rd)
        self.assertEqual(rd.tricks_won_map[SuitColorEnum.BLACK], 5)
        self.assertEqual(rd.points_won_map[SuitColorEnum.BLACK], 2)


class TestSimulation(unittest.TestCase):
    """Multi-round simulation must produce independent, valid rounds."""

    def test_round_structural_integrity(self):
        """Every round in a large sim must pass all structural invariants."""
        sim = run_simulation([[], [], [], []], spades, 1, 1, quantity=200)
        for rd in sim.rounds:
            assert_valid_round(self, rd)

    def test_round_isolation_via_card_sets(self):
        """Each round must use 20 unique valid cards — no leakage across rounds."""
        sim = run_simulation([[], [], [], []], hearts, 2, 3, quantity=200)
        for rd in sim.rounds:
            cards = played_cards(rd)
            self.assertEqual(len(cards), 20)
            self.assertEqual(len(set(cards)), 20)

    def test_fixed_cards_always_with_owner(self):
        """Pre-assigned cards must only ever be played by their owner."""
        p1 = ["ace_of_spades", "king_of_spades", "queen_of_spades"]
        p2 = ["ace_of_hearts", "king_of_hearts"]
        p1_set = {euchre_deck_map[n] for n in p1}
        p2_set = {euchre_deck_map[n] for n in p2}

        sim = run_simulation([p1, p2, [], []], spades, 1, 2, quantity=100)
        for rd in sim.rounds:
            by_player = played_cards_by_player(rd)
            self.assertTrue(p1_set.issubset(set(by_player[1])))
            self.assertTrue(p2_set.issubset(set(by_player[2])))
            for pid in [3, 4]:
                self.assertTrue(p1_set.isdisjoint(set(by_player[pid])))
                self.assertTrue(p2_set.isdisjoint(set(by_player[pid])))

    def test_deterministic_winner(self):
        """All-trump hand must win every round with 2 points (sweep)."""
        all_trump = ["jack_of_spades", "jack_of_clubs", "ace_of_spades",
                     "king_of_spades", "queen_of_spades"]
        sim = run_simulation([all_trump, [], [], []], spades, 1, 1, quantity=100)
        for rd in sim.rounds:
            self.assertEqual(rd.tricks_won_map[SuitColorEnum.BLACK], 5)
            self.assertEqual(rd.points_won_map[SuitColorEnum.BLACK], 2)

    def test_scoring_rules_over_many_rounds(self):
        valid = {(0, 2), (2, 0), (1, 0), (0, 1)}
        sim = run_simulation([[], [], [], []], clubs, 2, 3, quantity=500)
        for rd in sim.rounds:
            pts = tuple(rd.points_won_map.values())
            self.assertIn(pts, valid)


class TestLonerSimulation(unittest.TestCase):
    """Loner mode: teammate removed, 3 players per round."""

    def _run_loner(self, caller_id, dealer_id, trump, call_type, quantity,
                   caller_cards=None, flipped="ten_of_hearts"):
        svc = make_simulation_service()
        players = make_players()
        if caller_cards:
            players[caller_id - 1].hand.remaining_cards = [
                euchre_deck_map[n] for n in caller_cards
            ]
        return svc.simulate(RoundSimulation(
            players=players,
            call=Call(suit=trump, type=call_type, player_id=caller_id),
            rounds=[],
            flipped_card=euchre_deck_map[flipped],
            quantity=quantity,
            dealer_id=dealer_id,
            keep_rounds=True,
        ))

    def test_three_players_and_structural_integrity(self):
        sim = self._run_loner(
            caller_id=1, dealer_id=1, trump=spades,
            call_type=CallTypeEnum.LONER_P1, quantity=50,
            caller_cards=["jack_of_spades", "jack_of_clubs", "ace_of_spades",
                          "king_of_spades", "queen_of_spades"],
        )
        for rd in sim.rounds:
            self.assertEqual(len(rd.player_id_map), 3)
            assert_valid_round(self, rd, num_players=3)

    def test_no_duplicate_cards(self):
        sim = self._run_loner(
            caller_id=2, dealer_id=2, trump=hearts,
            call_type=CallTypeEnum.LONER_P2, quantity=100,
            flipped="nine_of_diamonds",
        )
        for rd in sim.rounds:
            cards = played_cards(rd)
            self.assertEqual(len(cards), len(set(cards)))

    def test_works_when_dealer_was_removed(self):
        """Dealer is the removed teammate — game must still function."""
        sim = self._run_loner(
            caller_id=2, dealer_id=4, trump=diamonds,
            call_type=CallTypeEnum.LONER_P2, quantity=30,
            flipped="nine_of_spades",
        )
        for rd in sim.rounds:
            assert_valid_round(self, rd, num_players=3)

    def test_loner_sweep_scores_four_points(self):
        """Caller with top 5 trump in loner mode scores 4 points."""
        sim = self._run_loner(
            caller_id=1, dealer_id=1, trump=hearts,
            call_type=CallTypeEnum.LONER_P1, quantity=50,
            caller_cards=["jack_of_hearts", "jack_of_diamonds", "ace_of_hearts",
                          "king_of_hearts", "queen_of_hearts"],
        )
        for rd in sim.rounds:
            self.assertEqual(rd.tricks_won_map[SuitColorEnum.BLACK], 5)
            self.assertEqual(rd.points_won_map[SuitColorEnum.BLACK], 4)


class TestGame(unittest.TestCase):
    """Integration tests for a full game via GameService."""

    def _play_game(self):
        svc = make_game_service()
        game = make_game(dealer_start_id=1)
        svc.play_game(game)
        return game

    def test_game_completes(self):
        game = self._play_game()
        self.assertTrue(game.is_complete)
        self.assertIsNotNone(game.winning_team)

    def test_winning_team_has_at_least_10_points(self):
        game = self._play_game()
        self.assertGreaterEqual(game.team_score_map[game.winning_team], 10)

    def test_losing_team_has_less_than_10_points(self):
        game = self._play_game()
        for team, score in game.team_score_map.items():
            if team != game.winning_team:
                self.assertLess(score, 10)

    def test_game_has_at_least_5_rounds(self):
        game = self._play_game()
        # minimum 5 rounds to reach 10 pts (max 2 pts/round)
        self.assertGreaterEqual(len(game.rounds), 5)

    def test_dealer_rotates_each_round(self):
        game = self._play_game()
        expected_dealer = 1
        for rd in game.rounds:
            self.assertEqual(rd.dealer_id, expected_dealer)
            expected_dealer = (expected_dealer % 4) + 1


if __name__ == "__main__":
    unittest.main()
