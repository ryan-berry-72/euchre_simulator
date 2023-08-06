from game_basics.GameService import *
from game_basics.RecordService import *
import time
import copy


def run_simulation(simulation):
    simulation.file_postfix = '-sim-' + str(simulation.id) \
                               + '-games-' + str(simulation.quantity) \
                               + '-batch-' + str(simulation.record_batch_size) \
                               + '-date-' + time.strftime("%Y%m%d-%H%M%S") \
                               + '.csv'

    game_id = 1
    while not simulation.is_complete:
        print('simulating game', game_id)

        game = Game(
            simulation.players,
            create_player_id_map(simulation.players),
            [],
            {SuitColorEnum.BLACK: 0, SuitColorEnum.RED: 0},
            None,
            game_id
        )

        play_game(game)

        update_simulation_with_game(simulation, game)

        game_id += 1


# records game data to the simulation object
def update_simulation_with_game(simulation, game):
    if game.id >= simulation.quantity:
        simulation.is_complete = True

    if simulation.record_games:
        simulation.games.append(copy.deepcopy(game))  # deepcopy to retain player card info

        # record game data
        if len(simulation.games) >= simulation.record_batch_size:
            update_card_win_probabilities(simulation.games)
            # record_games(
            #     simulation.games,
            #     simulation.output_directory + 'games' + simulation.file_postfix
            # )
            # record_player_hands(simulation.games, simulation.full_csv_file)
            simulation.output_game_data = False
            simulation.games = []
