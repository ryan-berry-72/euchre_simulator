from injector import inject

from dtos.BasicDto import Round, SuitColorEnum
from utils.BasicsUtil import get_opposing_team, get_next_player


class GameService:
    @inject
    def __init__(self, round_service):
        self.round_service = round_service

    def play_game(self, game):
        round_id = 1
        dealer_id = game.dealer_start_id
        while not game.is_complete:
            # create a round
            euchre_round = Round(
                players=list(game.players),
                player_id_map=game.player_id_map,
                tricks=[],
                tricks_won_map={SuitColorEnum.BLACK: 0, SuitColorEnum.RED: 0},
                points_won_map={SuitColorEnum.BLACK: 0, SuitColorEnum.RED: 0},
                flipped_card=None,
                call=None,
                id=round_id,
                dealer_id=dealer_id,
            )

            # play the round
            self.round_service.prepare_and_play_round(euchre_round)

            # update game with results of round
            self.update_results(game, euchre_round)

            # update values for next round
            dealer_id = get_next_player(game.player_id_map, dealer_id).id
            round_id += 1

    # updates game score with results of round, clears player hands, and determines if game is over
    @staticmethod
    def update_results(game, euchre_round):
        game.rounds.append(euchre_round)

        calling_team = euchre_round.player_id_map[euchre_round.call.player_id].team
        defending_team = get_opposing_team(calling_team)

        # update team scores
        game.team_score_map[calling_team] += euchre_round.points_won_map[calling_team]
        game.team_score_map[defending_team] += euchre_round.points_won_map[defending_team]

        # determine if game is over
        if game.team_score_map[calling_team] >= 10:
            game.winning_team = calling_team
            game.is_complete = True
        elif game.team_score_map[defending_team] >= 10:
            game.winning_team = defending_team
            game.is_complete = True

        # ensure players' hands are cleared
        for player in game.players:
            player.hand.remaining_cards = []
            player.hand.starting_cards = []
