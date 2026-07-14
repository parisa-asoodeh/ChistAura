from unittest.mock import (
    Mock,
    patch,
)

from django.test import SimpleTestCase

from teams.ai.predictors.winner_predictor import (
    WinnerPredictor,
)


class WinnerPredictorTest(SimpleTestCase):

    def setUp(self):

        self.team1 = Mock()
        self.team1.id = 1
        self.team1.name = "Alpha"

        self.team2 = Mock()
        self.team2.id = 2
        self.team2.name = "Beta"


    def test_calculate_scores(self):

        votes = [

            {
                "analyzer": "AverageVote",
                "vote": self.team1,
                "confidence": 10,
            },

            {
                "analyzer": "MomentumVote",
                "vote": self.team2,
                "confidence": 20,
            },
        ]

        scores = WinnerPredictor.calculate_scores(
            votes,
            self.team1,
            self.team2,
        )

        self.assertEqual(
            scores[self.team1.id],
            15,
        )

        self.assertEqual(
            scores[self.team2.id],
            16,
        )


    def test_choose_team1(self):

        scores = {
            self.team1.id: 40,
            self.team2.id: 20,
        }

        self.assertEqual(
            WinnerPredictor.choose_winner(
                scores,
                self.team1,
                self.team2,
            ),
            self.team1,
        )


    def test_choose_team2(self):

        scores = {
            self.team1.id: 20,
            self.team2.id: 40,
        }

        self.assertEqual(
            WinnerPredictor.choose_winner(
                scores,
                self.team1,
                self.team2,
            ),
            self.team2,
        )


    def test_choose_draw(self):

        scores = {
            self.team1.id: 20,
            self.team2.id: 20,
        }

        self.assertIsNone(
            WinnerPredictor.choose_winner(
                scores,
                self.team1,
                self.team2,
            )
        )


    def test_confidence(self):

        scores = {
            self.team1.id: 60,
            self.team2.id: 40,
        }

        self.assertEqual(
            WinnerPredictor.calculate_confidence(
                scores,
                self.team1,
                self.team1,
                self.team2,
            ),
            60,
        )


    def test_confidence_zero(self):

        scores = {
            self.team1.id: 0,
            self.team2.id: 0,
        }

        self.assertEqual(
            WinnerPredictor.calculate_confidence(
                scores,
                None,
                self.team1,
                self.team2,
            ),
            0,
        )


    def test_build_summary(self):

        self.assertIn(
            "Alpha",
            WinnerPredictor.build_summary(
                self.team1,
                80,
            ),
        )


    @patch(
        "teams.ai.predictors.winner_predictor.PerformanceDataProvider.get_team_context"
    )
    @patch(
        "teams.ai.predictors.winner_predictor.WinnerPredictor.collect_votes"
    )
    def test_predict(
        self,
        mock_collect_votes,
        mock_context,
    ):

        tournament = Mock()

        team1_context = {
            "team": self.team1,
        }

        team2_context = {
            "team": self.team2,
        }

        mock_context.side_effect = [
            team1_context,
            team2_context,
        ]

        votes = [

            {
                "analyzer": "AverageVote",
                "vote": self.team1,
                "confidence": 10,
            },

            {
                "analyzer": "MomentumVote",
                "vote": self.team2,
                "confidence": 20,
            },
        ]

        mock_collect_votes.return_value = votes

        result = WinnerPredictor.predict(
            self.team1,
            self.team2,
            tournament,
        )

        self.assertEqual(
            result["winner"],
            self.team2,
        )

        self.assertEqual(
            result["vote_scores"][self.team1.id],
            15,
        )

        self.assertEqual(
            result["vote_scores"][self.team2.id],
            16,
        )

        self.assertEqual(
            result["team1_context"],
            team1_context,
        )

        self.assertEqual(
            result["team2_context"],
            team2_context,
        )


    @patch(
        "teams.ai.predictors.winner_predictor.AverageVote.vote"
    )
    @patch(
        "teams.ai.predictors.winner_predictor.MomentumVote.vote"
    )
    @patch(
        "teams.ai.predictors.winner_predictor.ConsistencyVote.vote"
    )
    @patch(
        "teams.ai.predictors.winner_predictor.MatchDifficultyVote.vote"
    )
    @patch(
        "teams.ai.predictors.winner_predictor.StarDependencyVote.vote"
    )
    def test_collect_votes(
        self,
        mock_star,
        mock_difficulty,
        mock_consistency,
        mock_momentum,
        mock_average,
    ):

        team1_context = {}
        team2_context = {}

        mock_average.return_value = {
            "analyzer": "AverageVote",
        }

        mock_momentum.return_value = {
            "analyzer": "MomentumVote",
        }

        mock_consistency.return_value = {
            "analyzer": "ConsistencyVote",
        }

        mock_difficulty.return_value = {
            "analyzer": "MatchDifficultyVote",
        }

        mock_star.return_value = {
            "analyzer": "StarDependencyVote",
        }

        votes = WinnerPredictor.collect_votes(
            team1_context,
            team2_context,
        )

        self.assertEqual(
            len(votes),
            5,
        )

        self.assertEqual(
            votes[0]["analyzer"],
            "AverageVote",
        )

        self.assertEqual(
            votes[-1]["analyzer"],
            "StarDependencyVote",
        )