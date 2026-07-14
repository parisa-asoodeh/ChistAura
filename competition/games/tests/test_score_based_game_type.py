from django.test import TestCase
from unittest.mock import Mock

from games.game_types.score_based import (
    ScoreBasedGameType,
)


class ScoreBasedGameTypeTest(TestCase):

    def setUp(self):

        self.match = Mock()

        self.match.team1 = Mock(name="Team1")
        self.match.team2 = Mock(name="Team2")


    def test_is_better_returns_true(self):

        self.assertTrue(
            ScoreBasedGameType.is_better(
                100,
                80,
            )
        )


    def test_is_better_returns_false(self):

        self.assertFalse(
            ScoreBasedGameType.is_better(
                80,
                100,
            )
        )


    def test_calculate_score_returns_raw_score(self):

        self.assertEqual(
            ScoreBasedGameType.calculate_score(
                120,
                35,
            ),
            120,
        )


    def test_determine_winner_team1(self):

        winner = ScoreBasedGameType.determine_winner(
            self.match,
            90,
            70,
        )

        self.assertEqual(
            winner,
            self.match.team1,
        )


    def test_determine_winner_team2(self):

        winner = ScoreBasedGameType.determine_winner(
            self.match,
            60,
            95,
        )

        self.assertEqual(
            winner,
            self.match.team2,
        )


    def test_determine_winner_draw(self):

        winner = ScoreBasedGameType.determine_winner(
            self.match,
            80,
            80,
        )

        self.assertIsNone(
            winner,
        )