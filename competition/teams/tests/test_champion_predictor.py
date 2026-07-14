from unittest.mock import (
    Mock,
    patch,
)

from django.test import SimpleTestCase

from teams.ai.predictors.champion_predictor import (
    ChampionPredictor,
)


class ChampionPredictorTest(SimpleTestCase):

    def setUp(self):

        self.team1 = Mock()
        self.team1.name = "Alpha"

        self.team2 = Mock()
        self.team2.name = "Beta"

        self.team3 = Mock()
        self.team3.name = "Gamma"


    def test_generate_matchups(self):

        matchups = (
            ChampionPredictor.generate_matchups(
                [
                    self.team1,
                    self.team2,
                    self.team3,
                ]
            )
        )

        self.assertEqual(
            len(matchups),
            3,
        )

        self.assertIn(
            (
                self.team1,
                self.team2,
            ),
            matchups,
        )

        self.assertIn(
            (
                self.team1,
                self.team3,
            ),
            matchups,
        )

        self.assertIn(
            (
                self.team2,
                self.team3,
            ),
            matchups,
        )


    def test_choose_champion(self):

        ranking = [

            {
                "team": self.team2,
                "score": 80,
            },

            {
                "team": self.team1,
                "score": 60,
            },
        ]

        self.assertEqual(
            ChampionPredictor.choose_champion(
                ranking,
            ),
            self.team2,
        )


    def test_choose_champion_empty(self):

        self.assertIsNone(
            ChampionPredictor.choose_champion(
                [],
            )
        )


    def test_build_summary(self):

        summary = (
            ChampionPredictor.build_summary(
                self.team1,
                [
                    {
                        "team": self.team1,
                        "score": 75,
                    }
                ],
            )
        )

        self.assertIn(
            "Alpha",
            summary,
        )

        self.assertIn(
            "75",
            summary,
        )


    def test_build_summary_without_champion(self):

        self.assertIn(
            "نتوانست",
            ChampionPredictor.build_summary(
                None,
                [],
            ),
        )


    @patch(
        "teams.ai.predictors.champion_predictor.WinnerPredictor.predict"
    )
    def test_evaluate_matchups(
        self,
        mock_predict,
    ):

        tournament = Mock()

        mock_predict.return_value = {
            "winner": self.team1,
        }

        result = (
            ChampionPredictor.evaluate_matchups(
                [
                    (
                        self.team1,
                        self.team2,
                    )
                ],
                tournament,
            )
        )

        self.assertEqual(
            len(result),
            1,
        )

        self.assertEqual(
            result[0]["prediction"]["winner"],
            self.team1,
        )

        mock_predict.assert_called_once_with(
            self.team1,
            self.team2,
            tournament,
        )

    @patch(
        "teams.ai.predictors.champion_predictor.ExplanationService.build_prediction_reasons"
    )
    @patch(
        "teams.ai.predictors.champion_predictor.PowerRankingService.build"
    )
    @patch(
        "teams.ai.predictors.champion_predictor.ChampionPredictor.evaluate_matchups"
    )
    @patch(
        "teams.ai.predictors.champion_predictor.ChampionPredictor.generate_matchups"
    )
    def test_predict(
        self,
        mock_generate_matchups,
        mock_evaluate_matchups,
        mock_build_ranking,
        mock_build_reasons,
    ):

        tournament = Mock()

        teams = [
            self.team1,
            self.team2,
        ]

        mock_generate_matchups.return_value = [
            (
                self.team1,
                self.team2,
            )
        ]

        mock_evaluate_matchups.return_value = [

            {
                "team1": self.team1,

                "team2": self.team2,

                "prediction": {

                    "winner": self.team1,

                    "votes": [],
                }
            }

        ]

        mock_build_ranking.return_value = [

            {
                "team": self.team1,

                "score": 80,
            }

        ]

        mock_build_reasons.return_value = [
            "reason 1",
            "reason 2",
        ]

        result = ChampionPredictor.predict(
            teams,
            tournament,
        )

        self.assertEqual(
            result["champion"],
            self.team1,
        )

        self.assertEqual(
            result["ranking"][0]["team"],
            self.team1,
        )

        self.assertEqual(
            result["top_reasons"],
            [
                "reason 1",
                "reason 2",
            ],
        )

        self.assertIn(
            "Alpha",
            result["summary"],
        )

        mock_generate_matchups.assert_called_once_with(
            teams,
        )

        mock_evaluate_matchups.assert_called_once()

        mock_build_ranking.assert_called_once()