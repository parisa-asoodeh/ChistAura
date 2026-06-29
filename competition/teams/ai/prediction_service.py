from teams.ai.predictors.winner_predictor import (
    WinnerPredictor,
)


class PredictionService:

    @staticmethod
    def predict_match(
        team1,
        team2,
    ):

        return WinnerPredictor.predict(
            team1,
            team2,
        )

    @staticmethod
    def predict_league():

        pass

    @staticmethod
    def predict_champion():

        pass

    @staticmethod
    def simulate_match():

        pass