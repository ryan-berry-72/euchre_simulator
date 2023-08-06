from game_basics.Basics import *


spades = Suit(SuitNameEnum.SPADES, SuitColorEnum.BLACK)
clubs = Suit(SuitNameEnum.CLUBS, SuitColorEnum.BLACK)
hearts = Suit(SuitNameEnum.HEARTS, SuitColorEnum.RED)
diamonds = Suit(SuitNameEnum.DIAMONDS, SuitColorEnum.RED)

suits = (spades, clubs, hearts, diamonds)

euchre_deck = (
    Card(spades, CardValueEnum.NINE),
    Card(spades, CardValueEnum.TEN),
    Card(spades, CardValueEnum.JACK),
    Card(spades, CardValueEnum.QUEEN),
    Card(spades, CardValueEnum.KING),
    Card(spades, CardValueEnum.ACE),
    Card(clubs, CardValueEnum.NINE),
    Card(clubs, CardValueEnum.TEN),
    Card(clubs, CardValueEnum.JACK),
    Card(clubs, CardValueEnum.QUEEN),
    Card(clubs, CardValueEnum.KING),
    Card(clubs, CardValueEnum.ACE),
    Card(hearts, CardValueEnum.NINE),
    Card(hearts, CardValueEnum.TEN),
    Card(hearts, CardValueEnum.JACK),
    Card(hearts, CardValueEnum.QUEEN),
    Card(hearts, CardValueEnum.KING),
    Card(hearts, CardValueEnum.ACE),
    Card(diamonds, CardValueEnum.NINE),
    Card(diamonds, CardValueEnum.TEN),
    Card(diamonds, CardValueEnum.JACK),
    Card(diamonds, CardValueEnum.QUEEN),
    Card(diamonds, CardValueEnum.KING),
    Card(diamonds, CardValueEnum.ACE)
)

suit_map = {
    0: spades,
    1: clubs,
    2: hearts,
    3: diamonds
}

trump_suit_hierarchy = {
    spades: {
        Card(spades, CardValueEnum.JACK):       1,
        Card(clubs, CardValueEnum.JACK):        2,
        Card(spades, CardValueEnum.ACE):        3,
        Card(spades, CardValueEnum.KING):       4,
        Card(spades, CardValueEnum.QUEEN):      5,
        Card(spades, CardValueEnum.TEN):        6,
        Card(spades, CardValueEnum.NINE):       7
    },
    clubs: {
        Card(clubs, CardValueEnum.JACK):        1,
        Card(spades, CardValueEnum.JACK):       2,
        Card(clubs, CardValueEnum.ACE):         3,
        Card(clubs, CardValueEnum.KING):        4,
        Card(clubs, CardValueEnum.QUEEN):       5,
        Card(clubs, CardValueEnum.TEN):         6,
        Card(clubs, CardValueEnum.NINE):        7
    },
    hearts: {
        Card(hearts, CardValueEnum.JACK):       1,
        Card(diamonds, CardValueEnum.JACK):     2,
        Card(hearts, CardValueEnum.ACE):        3,
        Card(hearts, CardValueEnum.KING):       4,
        Card(hearts, CardValueEnum.QUEEN):      5,
        Card(hearts, CardValueEnum.TEN):        6,
        Card(hearts, CardValueEnum.NINE):       7
    },
    diamonds: {
        Card(diamonds, CardValueEnum.JACK):     1,
        Card(hearts, CardValueEnum.JACK):       2,
        Card(diamonds, CardValueEnum.ACE):      3,
        Card(diamonds, CardValueEnum.KING):     4,
        Card(diamonds, CardValueEnum.QUEEN):    5,
        Card(diamonds, CardValueEnum.TEN):      6,
        Card(diamonds, CardValueEnum.NINE):     7
    }
}

play_suit_hierarchy = {
    spades: {
        Card(spades, CardValueEnum.ACE):        8,
        Card(spades, CardValueEnum.KING):       9,
        Card(spades, CardValueEnum.QUEEN):      10,
        Card(spades, CardValueEnum.JACK):       11,
        Card(spades, CardValueEnum.TEN):        12,
        Card(spades, CardValueEnum.NINE):       13,
    },
    clubs: {
        Card(clubs, CardValueEnum.ACE):         8,
        Card(clubs, CardValueEnum.KING):        9,
        Card(clubs, CardValueEnum.QUEEN):       10,
        Card(clubs, CardValueEnum.JACK):        11,
        Card(clubs, CardValueEnum.TEN):         12,
        Card(clubs, CardValueEnum.NINE):        13,
    },
    hearts: {
        Card(hearts, CardValueEnum.ACE):        8,
        Card(hearts, CardValueEnum.KING):       9,
        Card(hearts, CardValueEnum.QUEEN):      10,
        Card(hearts, CardValueEnum.JACK):       11,
        Card(hearts, CardValueEnum.TEN):        12,
        Card(hearts, CardValueEnum.NINE):       13,
    },
    diamonds: {
        Card(diamonds, CardValueEnum.ACE):      8,
        Card(diamonds, CardValueEnum.KING):     9,
        Card(diamonds, CardValueEnum.QUEEN):    10,
        Card(diamonds, CardValueEnum.JACK):     11,
        Card(diamonds, CardValueEnum.TEN):      12,
        Card(diamonds, CardValueEnum.NINE):     13,
    }
}

dead_suit_hierarchy = {
    spades: {
        Card(spades, CardValueEnum.ACE):        14,
        Card(spades, CardValueEnum.KING):       15,
        Card(spades, CardValueEnum.QUEEN):      16,
        Card(spades, CardValueEnum.JACK):       17,
        Card(spades, CardValueEnum.TEN):        18,
        Card(spades, CardValueEnum.NINE):       19,
    },
    clubs: {
        Card(clubs, CardValueEnum.ACE):         14,
        Card(clubs, CardValueEnum.KING):        15,
        Card(clubs, CardValueEnum.QUEEN):       16,
        Card(clubs, CardValueEnum.JACK):        17,
        Card(clubs, CardValueEnum.TEN):         18,
        Card(clubs, CardValueEnum.NINE):        19,
    },
    hearts: {
        Card(hearts, CardValueEnum.ACE):        14,
        Card(hearts, CardValueEnum.KING):       15,
        Card(hearts, CardValueEnum.QUEEN):      16,
        Card(hearts, CardValueEnum.JACK):       17,
        Card(hearts, CardValueEnum.TEN):        18,
        Card(hearts, CardValueEnum.NINE):       19,
    },
    diamonds: {
        Card(diamonds, CardValueEnum.ACE):      14,
        Card(diamonds, CardValueEnum.KING):     15,
        Card(diamonds, CardValueEnum.QUEEN):    16,
        Card(diamonds, CardValueEnum.JACK):     17,
        Card(diamonds, CardValueEnum.TEN):      18,
        Card(diamonds, CardValueEnum.NINE):     19,
    }
}

trump_and_play_suit_hierarchy = {
    spades: {
        spades:     {},
        clubs:      {},
        hearts:     {},
        diamonds:   {}
    },
    clubs: {
        spades:     {},
        clubs:      {},
        hearts:     {},
        diamonds:   {}
    },
    hearts: {
        spades:     {},
        clubs:      {},
        hearts:     {},
        diamonds:   {}
    },
    diamonds: {
        spades:     {},
        clubs:      {},
        hearts:     {},
        diamonds:   {}
    }
}


# populates the hierarchy for every possible combination of trump and play suit
def populate_trump_and_play_suit_hierarchy():
    for key, value in trump_and_play_suit_hierarchy.items():
        trump_suit = key
        for key2, value2 in value.items():
            play_suit = key2

            # if trump_suit == play_suit, use only play_suit_hierarchy
            if trump_suit == play_suit:
                for suit in suits:
                    if suit != trump_suit:
                        value2.update(play_suit_hierarchy[suit])
            # use combination of play_suit_hierarchy and dead_suit_hierarchy
            else:
                for suit in suits:
                    if suit == play_suit:
                        value2.update(play_suit_hierarchy[suit])
                    elif suit != trump_suit:
                        value2.update(dead_suit_hierarchy[suit])

            # always add trump suit hierarchy
            value2.update(trump_suit_hierarchy[trump_suit])


populate_trump_and_play_suit_hierarchy()
