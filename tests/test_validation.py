"""Tests for API input validation — every invalid input must return 400 with a clear message."""
import copy
import json
import unittest

from RoundSimulationApi import app


def valid_payload():
    """A minimal valid request payload that produces a 200 response."""
    return {
        "player_names": ["Alice", "Bob", "Carol", "Dave"],
        "player_hands": [
            ["nine_of_spades", "ten_of_spades", "jack_of_spades"],
            ["nine_of_hearts", "ten_of_hearts"],
            ["nine_of_clubs", "ten_of_clubs"],
            ["nine_of_diamonds", "ten_of_diamonds"],
        ],
        "dealer_name": "Alice",
        "flipped_card": "ace_of_spades",
        "caller_name": "Bob",
        "call_suit": "spades",
        "call_type": "REGULAR_P1",
        "quantity": 5,
    }


class TestValidRequest(unittest.TestCase):
    """Sanity check: a well-formed request must succeed."""

    def setUp(self):
        self.client = app.test_client()

    def test_valid_request_returns_200(self):
        resp = self.client.post(
            "/euchre/simulate/round",
            data=json.dumps(valid_payload()),
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertIn("win_prob_map", data)
        self.assertIn("avg_points_map", data)
        self.assertIn("avg_tricks_map", data)

    def test_valid_p2_call_with_different_suit_returns_200(self):
        """P2 calls are not constrained to the flipped card's suit."""
        payload = valid_payload()
        payload["call_type"] = "REGULAR_P2"
        payload["call_suit"] = "hearts"
        resp = self.client.post(
            "/euchre/simulate/round",
            data=json.dumps(payload),
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, 200)


class TestQuantityValidation(unittest.TestCase):

    def setUp(self):
        self.client = app.test_client()

    def test_zero_quantity(self):
        payload = valid_payload()
        payload["quantity"] = 0
        resp = self.client.post(
            "/euchre/simulate/round",
            data=json.dumps(payload),
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, 400)
        self.assertIn("quantity must be a positive integer", resp.get_json()["error"])

    def test_negative_quantity(self):
        payload = valid_payload()
        payload["quantity"] = -1
        resp = self.client.post(
            "/euchre/simulate/round",
            data=json.dumps(payload),
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, 400)
        self.assertIn("quantity must be a positive integer", resp.get_json()["error"])


    def test_quantity_exceeds_max(self):
        payload = valid_payload()
        payload["quantity"] = 1_000_001
        resp = self.client.post(
            "/euchre/simulate/round",
            data=json.dumps(payload),
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, 400)
        self.assertIn("quantity must not exceed", resp.get_json()["error"])


class TestDuplicateCardValidation(unittest.TestCase):

    def setUp(self):
        self.client = app.test_client()

    def test_duplicate_card_across_players(self):
        payload = valid_payload()
        # Put nine_of_spades in both player 1 and player 2's hands
        payload["player_hands"][1] = ["nine_of_spades", "ten_of_hearts"]
        resp = self.client.post(
            "/euchre/simulate/round",
            data=json.dumps(payload),
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, 400)
        self.assertIn("Duplicate card", resp.get_json()["error"])
        self.assertIn("across player hands", resp.get_json()["error"])

    def test_duplicate_card_within_same_player(self):
        payload = valid_payload()
        payload["player_hands"][0] = ["nine_of_spades", "nine_of_spades", "ten_of_spades"]
        resp = self.client.post(
            "/euchre/simulate/round",
            data=json.dumps(payload),
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, 400)
        self.assertIn("Duplicate card", resp.get_json()["error"])


class TestFlippedCardValidation(unittest.TestCase):

    def setUp(self):
        self.client = app.test_client()

    def test_flipped_card_in_player_hand_p2_rejected(self):
        """P2 call: the flipped card was turned down, so it can't be in a hand."""
        payload = valid_payload()
        payload["call_type"] = "REGULAR_P2"
        payload["call_suit"] = "hearts"
        payload["flipped_card"] = "ace_of_hearts"
        payload["player_hands"][0] = ["ace_of_hearts", "ten_of_spades", "jack_of_spades"]
        resp = self.client.post(
            "/euchre/simulate/round",
            data=json.dumps(payload),
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, 400)
        self.assertIn("Flipped card", resp.get_json()["error"])
        self.assertIn("already in a player's hand", resp.get_json()["error"])

    def test_flipped_card_in_dealer_hand_p1_allowed(self):
        """P1 call: dealer picked up the flipped card, so it may be in dealer's hand."""
        payload = valid_payload()
        # dealer is Alice (player 1), flipped card is ace_of_spades, call_type P1
        payload["player_hands"][0] = ["ace_of_spades", "ten_of_spades", "jack_of_spades"]
        resp = self.client.post(
            "/euchre/simulate/round",
            data=json.dumps(payload),
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, 200)

    def test_flipped_card_in_non_dealer_hand_p1_rejected(self):
        """P1 call: only the dealer picks up, so a non-dealer holding it is illegal."""
        payload = valid_payload()
        # dealer is Alice (player 1), but Bob (player 2) has the flipped card
        payload["player_hands"][1] = ["ace_of_spades", "ten_of_hearts"]
        resp = self.client.post(
            "/euchre/simulate/round",
            data=json.dumps(payload),
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, 400)
        self.assertIn("non-dealer", resp.get_json()["error"])


class TestP1SuitConsistency(unittest.TestCase):

    def setUp(self):
        self.client = app.test_client()

    def test_regular_p1_mismatched_suit(self):
        payload = valid_payload()
        # flipped_card is ace_of_spades (spades), but call_suit is hearts
        payload["call_suit"] = "hearts"
        payload["call_type"] = "REGULAR_P1"
        resp = self.client.post(
            "/euchre/simulate/round",
            data=json.dumps(payload),
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, 400)
        self.assertIn("phase 1 calls", resp.get_json()["error"])
        self.assertIn("spades", resp.get_json()["error"])
        self.assertIn("hearts", resp.get_json()["error"])

    def test_loner_p1_mismatched_suit(self):
        payload = valid_payload()
        payload["call_suit"] = "diamonds"
        payload["call_type"] = "LONER_P1"
        resp = self.client.post(
            "/euchre/simulate/round",
            data=json.dumps(payload),
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, 400)
        self.assertIn("phase 1 calls", resp.get_json()["error"])

    def test_p2_mismatched_suit_is_allowed(self):
        """P2 calls may pick any suit, so a mismatch must NOT fail."""
        payload = valid_payload()
        payload["call_suit"] = "hearts"
        payload["call_type"] = "REGULAR_P2"
        resp = self.client.post(
            "/euchre/simulate/round",
            data=json.dumps(payload),
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, 200)


class TestPlayerNameValidation(unittest.TestCase):

    def setUp(self):
        self.client = app.test_client()

    def test_unrecognized_caller_name(self):
        payload = valid_payload()
        payload["caller_name"] = "Nobody"
        resp = self.client.post(
            "/euchre/simulate/round",
            data=json.dumps(payload),
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, 400)
        self.assertIn("does not match any player", resp.get_json()["error"])
        self.assertIn("Nobody", resp.get_json()["error"])

    def test_unrecognized_dealer_name(self):
        payload = valid_payload()
        payload["dealer_name"] = "Nobody"
        resp = self.client.post(
            "/euchre/simulate/round",
            data=json.dumps(payload),
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, 400)
        self.assertIn("does not match any player", resp.get_json()["error"])
        self.assertIn("Nobody", resp.get_json()["error"])

    def test_empty_caller_name_defaults_to_random(self):
        """An empty caller_name should not raise — it defaults to random."""
        payload = valid_payload()
        payload["caller_name"] = ""
        resp = self.client.post(
            "/euchre/simulate/round",
            data=json.dumps(payload),
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, 200)

    def test_empty_dealer_name_defaults_to_random(self):
        """An empty dealer_name should not raise — it defaults to random."""
        payload = valid_payload()
        payload["dealer_name"] = ""
        resp = self.client.post(
            "/euchre/simulate/round",
            data=json.dumps(payload),
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, 200)


class TestInvalidCardAndSuitNames(unittest.TestCase):

    def setUp(self):
        self.client = app.test_client()

    def test_invalid_card_name(self):
        payload = valid_payload()
        payload["player_hands"][0] = ["not_a_card", "ten_of_spades"]
        resp = self.client.post(
            "/euchre/simulate/round",
            data=json.dumps(payload),
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, 400)
        self.assertIn("Invalid card name", resp.get_json()["error"])

    def test_invalid_suit_name(self):
        payload = valid_payload()
        payload["call_suit"] = "bananas"
        resp = self.client.post(
            "/euchre/simulate/round",
            data=json.dumps(payload),
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, 400)
        self.assertIn("Invalid suit name", resp.get_json()["error"])

    def test_invalid_flipped_card_name(self):
        payload = valid_payload()
        payload["flipped_card"] = "joker"
        resp = self.client.post(
            "/euchre/simulate/round",
            data=json.dumps(payload),
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, 400)
        self.assertIn("Invalid card name", resp.get_json()["error"])

    def test_invalid_call_type(self):
        payload = valid_payload()
        payload["call_type"] = "INVALID_TYPE"
        resp = self.client.post(
            "/euchre/simulate/round",
            data=json.dumps(payload),
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, 400)
        self.assertIn("is not a valid enum value", resp.get_json()["error"])


class TestPlayerCountValidation(unittest.TestCase):

    def setUp(self):
        self.client = app.test_client()

    def test_wrong_number_of_player_names(self):
        payload = valid_payload()
        payload["player_names"] = ["Alice", "Bob", "Carol"]  # only 3
        resp = self.client.post(
            "/euchre/simulate/round",
            data=json.dumps(payload),
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, 400)
        self.assertIn("Number of player names must be 4", resp.get_json()["error"])

    def test_wrong_number_of_player_hands(self):
        payload = valid_payload()
        payload["player_hands"] = [[], [], []]  # only 3
        resp = self.client.post(
            "/euchre/simulate/round",
            data=json.dumps(payload),
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, 400)
        self.assertIn("Number of player hands must be 4", resp.get_json()["error"])

    def test_too_many_cards_in_hand(self):
        payload = valid_payload()
        payload["player_hands"][0] = [
            "nine_of_spades", "ten_of_spades", "jack_of_spades",
            "queen_of_spades", "king_of_spades", "ace_of_spades",
        ]
        resp = self.client.post(
            "/euchre/simulate/round",
            data=json.dumps(payload),
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, 400)
        self.assertIn("too many cards", resp.get_json()["error"])


if __name__ == "__main__":
    unittest.main()
