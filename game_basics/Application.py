from game_basics.Basics import *
from game_basics.GameService import *
from game_basics.SimulationService import *
from game_basics.AnalysisService import *


def main():
    print("Starting Euchre Simulation")

    player1 = Player('Ryan', SuitColorEnum.BLACK, Hand((), []), 1)
    player2 = Player('Craig', SuitColorEnum.RED, Hand((), []), 2)
    player3 = Player('Kyle', SuitColorEnum.BLACK, Hand((), []), 3)
    player4 = Player('Lauren', SuitColorEnum.RED, Hand((), []), 4)
    players = (player1, player2, player3, player4)

    simulation = Simulation(
        players,
        [],
        '/Users/ryanberry/Documents/euchre_arch2_output/',
        '',
        1,
        1000000,
        1000,
        False,
        True
    )

    run_simulation(simulation)

    output_card_win_probabilities(simulation.output_directory + 'win-probs' + simulation.file_postfix)


if __name__ == '__main__':
    main()
