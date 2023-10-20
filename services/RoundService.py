import random

from injector import inject

from constants.GameConstants import euchre_deck
from dtos.BasicDto import Trick, CallTypeEnum
from utils.BasicsUtil import get_next_player, get_opposing_team


class RoundService:
    @inject
    def __init__(self, trick_service, dealing_service, call_service, shuffle_service):
        self.trick_service = trick_service
        self.dealing_service = dealing_service
        self.call_service = call_service
        self.shuffle_service = shuffle_service

    def prepare_and_play_round(self, euchre_round):
        self.shuffle_service.shuffle_cards(euchre_deck)
        self.dealing_service.deal_cards(euchre_round)
        self.call_service.update_call(euchre_round)
        self.play_round(euchre_round)

    # plays the round assuming cards are dealt and a call is made
    def play_round(self, euchre_round):
        leader_id = get_next_player(euchre_round.player_id_map, euchre_round.dealer_id).id
        trick = Trick(
            plays=[],
            winning_play=None,
            call=euchre_round.call,
            play_suit=None,
            id=1,
            leader_id=leader_id
        )
        while not euchre_round.is_complete:
            # play trick
            self.trick_service.play_trick(trick, euchre_round.player_id_map)

            # update round
            self.update_round_with_trick(euchre_round, trick)

            # prepare next trick
            leader_id = trick.winning_play.player.id
            trick = Trick([], None, euchre_round.call, None, trick.id + 1, leader_id)

        self.update_team_points_won(euchre_round)

    # assigns shuffled cards to each player's hand and flips top card
    def deal_cards(self, euchre_round):
        shuffled_cards = self.shuffle_service.shuffle_cards(euchre_deck)

        # deal cards to remaining_cards list
        next_player = get_next_player(euchre_round.player_id_map, euchre_round.dealer_id)
        while len(shuffled_cards) > 4:
            next_player.hand.remaining_cards.append(shuffled_cards.pop())
            next_player = get_next_player(euchre_round.player_id_map, next_player.id)

        # flip top card
        euchre_round.flipped_card = shuffled_cards.pop()

        # update starting_cards for each player
        for key, value in euchre_round.player_id_map.items():
            if len(value.hand.remaining_cards) != 5:
                raise Exception('Invalid deal. Player ' + str(value) + ' should have 5 cards')
            value.hand.starting_cards = tuple(value.hand.remaining_cards)

    # update round values based on completed trick
    @staticmethod
    def update_round_with_trick(euchre_round, trick):
        # record the trick
        euchre_round.tricks.append(trick)

        # determine if round is complete
        if len(euchre_round.tricks) >= 5:
            euchre_round.is_complete = True

        # add 1 trick to the winning team's score
        euchre_round.tricks_won_map[trick.winning_play.player.team] += 1

    # updates points won for each team based on tricks won and call made
    @staticmethod
    def update_team_points_won(euchre_round):
        calling_team = euchre_round.player_id_map[euchre_round.call.player_id].team
        defending_team = get_opposing_team(calling_team)

        calling_team_wins = euchre_round.tricks_won_map[calling_team]
        defending_team_wins = euchre_round.tricks_won_map[defending_team]

        # update team scores
        if calling_team_wins > defending_team_wins:
            if calling_team_wins == 5:
                if euchre_round.call.type == CallTypeEnum.LONER_P1 or euchre_round.call.type == CallTypeEnum.LONER_P2:
                    euchre_round.points_won_map[calling_team] = 4
                else:
                    euchre_round.points_won_map[calling_team] = 2
            else:
                euchre_round.points_won_map[calling_team] = 1
        else:
            euchre_round.points_won_map[defending_team] = 2
