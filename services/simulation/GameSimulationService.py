import copy
import time
import logging

from injector import inject

from dtos.BasicDto import Game, SuitColorEnum, GameSimulation
from services.GameService import GameService
from services.RecordService import RecordService
from utils.BasicsUtil import create_player_id_map

logger = logging.getLogger(__name__)


class GameSimulationService:
    @inject
    def __init__(self, game_service: GameService, record_service: RecordService):
        self.game_service = game_service
        self.record_service = record_service

    def run_simulation(self, simulation: GameSimulation) -> None:
        simulation.file_name = '-sim-' + str(simulation.id) \
                               + '-games-' + str(simulation.quantity) \
                               + '-batch-' + str(simulation.record_batch_size) \
                               + '-date-' + time.strftime("%Y%m%d-%H%M%S") \
                               + '.csv'

        game_id = 1
        while not simulation.is_complete:
            logger.debug('simulating game %s', game_id)

            game = Game(
                players=simulation.players,
                player_id_map=create_player_id_map(simulation.players),
                dealer_start_id=simulation.players[0].id,
                rounds=[],
                team_score_map={SuitColorEnum.BLACK: 0, SuitColorEnum.RED: 0},
                winning_team=None,
                id=game_id
            )

            self.game_service.play_game(game)

            self.update_simulation_with_game(simulation, game)

            game_id += 1

    # records game data to the simulation object
    def update_simulation_with_game(self, simulation: GameSimulation, game: Game) -> None:
        if game.id >= simulation.quantity:
            simulation.is_complete = True

        if simulation.record_games:
            simulation.games.append(copy.deepcopy(game))  # deepcopy to retain player card info

            # record game data
            if len(simulation.games) >= simulation.record_batch_size:
                self.record_service.update_card_win_probabilities(simulation.games)
                # record_games(
                #     simulation.games,
                #     simulation.output_directory + 'games' + simulation.file_postfix
                # )

                # record_player_hands(simulation.games, simulation.get_full_file_path())
                simulation.output_game_data = False
                simulation.games = []
