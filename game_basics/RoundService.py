from game_basics.CallService import *
from game_basics.TrickService import *


# plays the round assuming cards are dealt and a call is made
def play_round(round):
    leader_id = get_next_player(round.player_id_map, round.dealer_id).id
    trick = Trick([], None, round.call, None, 1, leader_id)
    while not round.is_complete:
        # play trick
        play_trick(trick, round.player_id_map)

        # update round
        update_round_with_trick(round, trick)

        # prepare next trick
        leader_id = trick.winning_play.player.id
        trick = Trick([], None, round.call, None, trick.id+1, leader_id)


# creates a list of shuffled values based on a given tuple
def shuffle_cards(cards_tuple):
    cards_list = list(cards_tuple)
    random.shuffle(cards_list)
    return cards_list


# assigns shuffled cards to each player's hand and flips top card
def deal_cards(round):
    shuffled_cards = shuffle_cards(euchre_deck)

    # deal cards to remaining_cards list
    next_player = get_next_player(round.player_id_map, round.dealer_id)
    while len(shuffled_cards) > 4:
        next_player.hand.remaining_cards.append(shuffled_cards.pop())
        next_player = get_next_player(round.player_id_map, next_player.id)

    # flip top card
    round.flipped_card = shuffled_cards.pop()

    # update starting_cards for each player
    for key, value in round.player_id_map.items():
        if len(value.hand.remaining_cards) != 5:
            raise Exception('Invalid deal. Player ' + str(value) + ' should have 5 cards')
        value.hand.starting_cards = tuple(value.hand.remaining_cards)


# update round values based on completed trick
def update_round_with_trick(round, trick):
    # record the trick
    round.tricks.append(trick)

    # determine if round is complete
    if len(round.tricks) >= 5:
        round.is_complete = True

    # add 1 trick to the winning team's score
    round.tricks_won_map[trick.winning_play.player.team] += 1
