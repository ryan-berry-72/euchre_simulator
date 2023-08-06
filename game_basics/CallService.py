from game_basics.Basics import *
from game_basics.BasicsUtil import *
from game_basics.GameConstants import *
import random


# randomly determines the call and updates to the round
def update_call(round):
    call = Call(None, None)

    # phase 1 calls - pass or pick up
    is_phase1_call = True
    last_player_id = round.dealer_id
    for i in range(len(round.player_id_map)):
        curr_player = get_next_player(round.player_id_map, last_player_id)

        # randomly determine if this player will call (12.5% chance)
        random_value = random.randint(0, len(round.player_id_map)*2-1)
        if i == random_value:
            call.suit = round.flipped_card.suit
            call.player_id = curr_player.id
            call.is_complete = True
            update_dealer_discard(round, call)
            break

    # phase 2 calls - pass or pick suit
    if not call.is_complete:
        is_phase1_call = False
        last_player_id = round.dealer_id
        for i in range(len(round.player_id_map)):
            curr_player = get_next_player(round.player_id_map, last_player_id)

            # randomly determine if this player will call (12.5% chance)
            # if it comes back to dealer, they are forced to call
            random_value = random.randint(0, len(round.player_id_map)*2-1)
            if i == random_value or i >= len(round.player_id_map) - 1:
                call.suit = get_random_suit()
                call.player_id = curr_player.id
                call.is_complete = True
                break

    # determine loner vs regular call
    # loner has a 10% chance
    random_value = random.randint(1, 10)
    if random_value == round.dealer_id:
        if is_phase1_call:
            call.type = CallTypeEnum.LONER_P1
        else:
            call.type = CallTypeEnum.LONER_P2
        update_loner_call(round, call.player_id)
    else:
        if is_phase1_call:
            call.type = CallTypeEnum.REGULAR_P1
        else:
            call.type = CallTypeEnum.REGULAR_P2

    round.call = call


# randomly determines which card to remove from hand
# call parameter may be used later
def update_dealer_discard(round, call):
    dealer_player = round.player_id_map[round.dealer_id]

    # delete random card
    random_value = random.randint(0, len(dealer_player.hand.remaining_cards)-1)
    del dealer_player.hand.remaining_cards[random_value]

    # add flipped card to hand
    dealer_player.hand.remaining_cards.append(round.flipped_card)
    dealer_player.hand.starting_cards = tuple(dealer_player.hand.remaining_cards)


# remove the teammate of the caller from the round
def update_loner_call(round, caller_id):
    # identify teammate
    teammate = get_teammate(round.players, round.player_id_map[caller_id])

    # remove teammate
    round.players.remove(teammate)
    round.player_id_map = create_player_id_map(round.players)


def get_random_suit():
    return suit_map[random.randint(0, len(suit_map)-1)]
