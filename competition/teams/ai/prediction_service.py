from teams.ai.predictors.winner_predictor import (
    WinnerPredictor,
)
from teams.ai.predictors.champion_predictor import (
    ChampionPredictor,
)


class PredictionService:

    @staticmethod
    def predict_match(
        team1,
        team2,
        tournament,
    ):

        return WinnerPredictor.predict(
            team1,
            team2,
            tournament,
        )

    @staticmethod
    def predict_league():

        pass


    @staticmethod
    def predict_champion(
        tournament,
    ):

        teams = [

            tournament_team.team

            for tournament_team in tournament.teams.all()

        ]

        return ChampionPredictor.predict(
            teams=teams,
            tournament=tournament,
        )


    @staticmethod
    def simulate_match():

        pass