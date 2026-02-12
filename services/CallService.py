import random

from injector import inject

from constants.GameConstants import suit_map, suits
from dtos.BasicDto import Call, Round, CallTypeEnum
from utils.BasicsUtil import get_next_player, get_teammate, create_player_id_map


class CallService:
    # randomly determines the call and updates to the round
    def update_call(self, euchre_round: Round) -> None:
        call = Call(
            suit=None,
            type=None
        )

        # phase 1 calls - pass or pick up
        is_phase1_call = True
        last_player_id = euchre_round.dealer_id
        for i in range(len(euchre_round.player_id_map)):
            curr_player = get_next_player(euchre_round.player_id_map, last_player_id)

            # randomly determine if this player will call (12.5% chance)
            random_value = random.randint(0, len(euchre_round.player_id_map) * 2 - 1)
            if i == random_value:
                call.suit = euchre_round.flipped_card.suit
                call.player_id = curr_player.id
                call.is_complete = True
                self.update_dealer_discard(euchre_round)
                break

        # phase 2 calls - pass or pick suit
        if not call.is_complete:
            is_phase1_call = False
            last_player_id = euchre_round.dealer_id
            for i in range(len(euchre_round.player_id_map)):
                curr_player = get_next_player(euchre_round.player_id_map, last_player_id)

                # randomly determine if this player will call (12.5% chance)
                # if it comes back to dealer, they are forced to call
                random_value = random.randint(0, len(euchre_round.player_id_map) * 2 - 1)
                if i == random_value or i >= len(euchre_round.player_id_map) - 1:
                    call.suit = self.get_random_suit()
                    call.player_id = curr_player.id
                    call.is_complete = True
                    break

        # determine loner vs regular call
        # loner has a 10% chance
        random_value = random.randint(1, 10)
        if random_value == euchre_round.dealer_id:
            if is_phase1_call:
                call.type = CallTypeEnum.LONER_P1
            else:
                call.type = CallTypeEnum.LONER_P2
            self.update_loner_call(euchre_round, call.player_id)
        else:
            if is_phase1_call:
                call.type = CallTypeEnum.REGULAR_P1
            else:
                call.type = CallTypeEnum.REGULAR_P2

        euchre_round.call = call

    # randomly determines which card to remove from hand
    # call parameter may be used later
    @staticmethod
    def update_dealer_discard(euchre_round):
        dealer_player = euchre_round.player_id_map[euchre_round.dealer_id]

        # delete random card
        random_value = random.randint(0, len(dealer_player.hand.remaining_cards)-1)
        del dealer_player.hand.remaining_cards[random_value]

        # add flipped card to hand
        dealer_player.hand.remaining_cards.append(euchre_round.flipped_card)
        dealer_player.hand.starting_cards = tuple(dealer_player.hand.remaining_cards)

    # remove the teammate of the caller from the round
    @staticmethod
    def update_loner_call(euchre_round, caller_id):
        # identify teammate
        teammate = get_teammate(euchre_round.players, euchre_round.player_id_map[caller_id])

        # remove teammate
        euchre_round.players.remove(teammate)
        euchre_round.player_id_map = create_player_id_map(euchre_round.players)

    @staticmethod
    def build_round_call(base_call, player_ids):
        if base_call is None:
            return Call(
                suit=random.choice(suits),
                type=CallTypeEnum.REGULAR_P1,
                player_id=random.choice(player_ids),
            )
        suit = base_call.suit if base_call.suit is not None else random.choice(suits)
        player_id = base_call.player_id if base_call.player_id != 0 else random.choice(player_ids)
        if suit == base_call.suit and player_id == base_call.player_id:
            return base_call
        return Call(suit=suit, type=base_call.type, player_id=player_id)

    @staticmethod
    def get_random_suit():
        return suit_map[random.randint(0, len(suit_map)-1)]
