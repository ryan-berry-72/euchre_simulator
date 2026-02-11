"""Unit tests for individual euchre services: dealing, play selection, and call building."""
import random
import unittest

from constants.GameConstants import (
    euchre_deck, euchre_deck_map, spades, hearts, diamonds, suits,
    HAND_MAX_CARD_COUNT,
)
from dtos.BasicDto import Call, CallTypeEnum, Hand, Play, Player, SuitColorEnum
from services.CallService import CallService
from services.DealingService import DealingService
from services.PlayService import PlayService
from utils.CardUtil import get_effective_suit


class TestDealing(unittest.TestCase):
    """Dealing must fill hands to 5, avoid duplicates, and snapshot starting_cards."""

    def _players(self):
        from tests.conftest import make_players
        return make_players()

    def test_fills_each_hand_to_five_cards(self):
        players = self._players()
        DealingService.deal_cards(players, list(euchre_deck[:20]))
        for p in players:
            self.assertEqual(len(p.hand.remaining_cards), HAND_MAX_CARD_COUNT)

    def test_tops_up_partial_hands(self):
        players = self._players()
        players[0].hand.remaining_cards = [euchre_deck_map["ace_of_spades"],
                                           euchre_deck_map["king_of_spades"]]
        DealingService.deal_cards(players, list(euchre_deck[:18]))
        for p in players:
            self.assertEqual(len(p.hand.remaining_cards), HAND_MAX_CARD_COUNT)

    def test_no_duplicate_cards_across_hands(self):
        players = self._players()
        DealingService.deal_cards(players, list(euchre_deck[:20]))
        all_cards = [c for p in players for c in p.hand.remaining_cards]
        self.assertEqual(len(all_cards), len(set(all_cards)))

    def test_starting_cards_is_snapshot(self):
        """Mutating remaining_cards must not affect starting_cards."""
        players = self._players()
        DealingService.deal_cards(players, list(euchre_deck[:20]))
        for p in players:
            before = list(p.hand.starting_cards)
            p.hand.remaining_cards.pop()
            self.assertEqual(p.hand.starting_cards, before)


class TestPlaySelection(unittest.TestCase):
    """Card selection must follow suit when able, respect bowers, and drain the hand."""

    def _player(self, card_names):
        cards = [euchre_deck_map[n] for n in card_names]
        return Player(name="P", team=SuitColorEnum.BLACK, id=1,
                      hand=Hand(starting_cards=list(cards), remaining_cards=list(cards)))

    def test_removes_exactly_one_card(self):
        p = self._player(["ace_of_spades", "king_of_hearts", "nine_of_clubs"])
        play = Play(card=None, player=p, id=1, is_lead=True)
        PlayService.choose_play(play, spades, None)
        self.assertEqual(len(p.hand.remaining_cards), 2)
        self.assertNotIn(play.card, p.hand.remaining_cards)

    def test_must_follow_suit_when_able(self):
        random.seed(0)
        for _ in range(30):
            p = self._player(["ace_of_hearts", "nine_of_hearts", "king_of_spades"])
            play = Play(card=None, player=p, id=1, is_lead=False)
            PlayService.choose_play(play, spades, hearts)
            self.assertEqual(get_effective_suit(play.card, spades), hearts)

    def test_may_play_any_card_when_void(self):
        p = self._player(["ace_of_spades", "nine_of_clubs"])
        play = Play(card=None, player=p, id=1, is_lead=False)
        PlayService.choose_play(play, hearts, diamonds)
        self.assertIn(play.card, [euchre_deck_map["ace_of_spades"],
                                  euchre_deck_map["nine_of_clubs"]])

    def test_left_bower_follows_trump(self):
        """Jack of clubs must follow a spades lead when spades is trump."""
        p = self._player(["jack_of_clubs", "nine_of_hearts"])
        play = Play(card=None, player=p, id=1, is_lead=False)
        PlayService.choose_play(play, spades, spades)
        self.assertEqual(play.card, euchre_deck_map["jack_of_clubs"])

    def test_full_hand_drains_to_empty(self):
        names = ["ace_of_spades", "king_of_hearts", "nine_of_clubs",
                 "ten_of_diamonds", "queen_of_spades"]
        p = self._player(names)
        played = set()
        for i in range(5):
            play = Play(card=None, player=p, id=i+1, is_lead=(i == 0))
            PlayService.choose_play(play, hearts, hearts if i > 0 else None)
            played.add(play.card)
        self.assertEqual(len(p.hand.remaining_cards), 0)
        self.assertEqual(played, {euchre_deck_map[n] for n in names})


class TestBuildRoundCall(unittest.TestCase):
    """build_round_call must fill in missing call fields with random values."""

    PLAYER_IDS = [1, 2, 3, 4]
    ITERATIONS = 50

    def test_none_base_call_returns_random_call(self):
        """A None base_call produces a fully random call with REGULAR_P1 type."""
        seen_suits = set()
        seen_players = set()
        for _ in range(self.ITERATIONS):
            result = CallService.build_round_call(None, self.PLAYER_IDS)
            self.assertIn(result.suit, suits)
            self.assertIn(result.player_id, self.PLAYER_IDS)
            self.assertEqual(result.type, CallTypeEnum.REGULAR_P1)
            seen_suits.add(result.suit)
            seen_players.add(result.player_id)
        self.assertGreater(len(seen_suits), 1, "Expected multiple random suits")
        self.assertGreater(len(seen_players), 1, "Expected multiple random player_ids")

    def test_missing_suit_and_player_randomises_both(self):
        base = Call(suit=None, type=CallTypeEnum.REGULAR_P2, player_id=0)
        seen_suits = set()
        seen_players = set()
        for _ in range(self.ITERATIONS):
            result = CallService.build_round_call(base, self.PLAYER_IDS)
            self.assertIn(result.suit, suits)
            self.assertIn(result.player_id, self.PLAYER_IDS)
            self.assertEqual(result.type, CallTypeEnum.REGULAR_P2)
            seen_suits.add(result.suit)
            seen_players.add(result.player_id)
        self.assertGreater(len(seen_suits), 1)
        self.assertGreater(len(seen_players), 1)

    def test_missing_suit_only_randomises_suit(self):
        base = Call(suit=None, type=CallTypeEnum.LONER_P1, player_id=3)
        seen_suits = set()
        for _ in range(self.ITERATIONS):
            result = CallService.build_round_call(base, self.PLAYER_IDS)
            self.assertIn(result.suit, suits)
            self.assertEqual(result.player_id, 3)
            self.assertEqual(result.type, CallTypeEnum.LONER_P1)
            seen_suits.add(result.suit)
        self.assertGreater(len(seen_suits), 1)

    def test_missing_player_only_randomises_player(self):
        base = Call(suit=hearts, type=CallTypeEnum.REGULAR_P1, player_id=0)
        seen_players = set()
        for _ in range(self.ITERATIONS):
            result = CallService.build_round_call(base, self.PLAYER_IDS)
            self.assertEqual(result.suit, hearts)
            self.assertIn(result.player_id, self.PLAYER_IDS)
            self.assertEqual(result.type, CallTypeEnum.REGULAR_P1)
            seen_players.add(result.player_id)
        self.assertGreater(len(seen_players), 1)

    def test_fully_specified_returns_same_object(self):
        base = Call(suit=spades, type=CallTypeEnum.REGULAR_P2, player_id=2)
        result = CallService.build_round_call(base, self.PLAYER_IDS)
        self.assertIs(result, base)

    def test_preserves_type_across_all_call_types(self):
        """Every CallTypeEnum value is preserved when suit/player are filled in."""
        for call_type in CallTypeEnum:
            base = Call(suit=None, type=call_type, player_id=0)
            result = CallService.build_round_call(base, self.PLAYER_IDS)
            self.assertEqual(result.type, call_type)


if __name__ == "__main__":
    unittest.main()
