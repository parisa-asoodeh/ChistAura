from unittest.mock import (
    Mock,
    patch,
)

from django.test import SimpleTestCase

from teams.ai.prediction_service import (
    PredictionService,
)


class PredictionServiceTest(SimpleTestCase):

    @patch(
        "teams.ai.prediction_service.WinnerPredictor.predict"
    )
    def test_predict_match(
        self,
        mock_predict,
    ):

        team1 = Mock()
        team2 = Mock()

        mock_predict.return_value = {
            "winner": team1,
        }

        result = PredictionService.predict_match(
            team1,
            team2,
        )

        self.assertEqual(
            result["winner"],
            team1,
        )

        mock_predict.assert_called_once_with(
            team1,
            team2,
        )


    @patch(
        "teams.ai.prediction_service.ChampionPredictor.predict"
    )
    def test_predict_champion(
        self,
        mock_predict,
    ):

        team1 = Mock()
        team2 = Mock()

        tournament = Mock()

        tournament.teams.all.return_value = [

            Mock(team=team1),

            Mock(team=team2),

        ]

        mock_predict.return_value = {
            "champion": team1,
        }

        result = PredictionService.predict_champion(
            tournament,
        )

        self.assertEqual(
            result["champion"],
            team1,
        )

        mock_predict.assert_called_once_with(
            teams=[
                team1,
                team2,
            ],
            tournament=tournament,
        )


    def test_predict_league(self):

        self.assertIsNone(
            PredictionService.predict_league()
        )