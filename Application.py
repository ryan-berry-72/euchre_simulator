from services.simulation.GameSimulationService import *
import os


def main():
    print("Starting Euchre Simulation")

    player1 = Player('Ryan', SuitColorEnum.BLACK, Hand((), []), 1)
    player2 = Player('Craig', SuitColorEnum.RED, Hand((), []), 2)
    player3 = Player('Kyle', SuitColorEnum.BLACK, Hand((), []), 3)
    player4 = Player('Lauren', SuitColorEnum.RED, Hand((), []), 4)
    players = (player1, player2, player3, player4)

    simulation = GameSimulation(
        players=players,
        games=[],
        output_directory='.',
        file_name='',
        id=1,
        quantity=10000,
        record_batch_size=1000,
        is_complete=False,
        record_games=True
    )

    run_simulation(simulation)

    output_card_win_probabilities(os.path.join(simulation.output_directory, f'win-probs-{simulation.file_name}'))


if __name__ == '__main__':
    main()
