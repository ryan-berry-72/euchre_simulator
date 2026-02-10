"""Unit tests for individual euchre services: dealing and play selection."""
import random
import unittest

from constants.GameConstants import (
    euchre_deck, euchre_deck_map, spades, hearts, diamonds,
    HAND_MAX_CARD_COUNT,
)
from dtos.BasicDto import CallTypeEnum, Hand, Play, Player, SuitColorEnum
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


if __name__ == "__main__":
    unittest.main()
