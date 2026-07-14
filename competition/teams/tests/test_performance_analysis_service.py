from unittest.mock import (
    Mock,
    patch,
)

from django.test import TestCase

from teams.ai.performance_analysis_service import (
    PerformanceAnalysisService,
)


class PerformanceAnalysisServiceTest(TestCase):

    @patch(
        "teams.ai.performance_analysis_service.PerformanceDataProvider.get_team_context"
    )
    @patch(
        "teams.ai.performance_analysis_service.StarDependencyAnalyzer.analyze"
    )
    @patch(
        "teams.ai.performance_analysis_service.MatchDifficultyAnalyzer.analyze"
    )
    @patch(
        "teams.ai.performance_analysis_service.ConsistencyAnalyzer.analyze"
    )
    @patch(
        "teams.ai.performance_analysis_service.MomentumAnalyzer.analyze"
    )
    @patch(
        "teams.ai.performance_analysis_service.AverageAnalyzer.analyze"
    )
    @patch(
        "teams.ai.performance_analysis_service.BalanceAnalyzer.analyze"
    )
    @patch(
        "teams.ai.performance_analysis_service.ScoreAnalyzer.analyze"
    )
    def test_generate(
        self,
        mock_score,
        mock_balance,
        mock_average,
        mock_momentum,
        mock_consistency,
        mock_difficulty,
        mock_star,
        mock_context,
    ):

        match = Mock()
        match.team1 = Mock()
        match.team2 = Mock()
        match.tournament = Mock()

        mock_context.side_effect = [
            {"team": match.team1},
            {"team": match.team2},
            {"team": match.team1},
            {"team": match.team2},
            {"team": match.team1},
            {"team": match.team2},
            {"team": match.team1},
            {"team": match.team2},
            {"team": match.team1},
            {"team": match.team2},
        ]

        mock_score.return_value = (
            "Score Summary"
        )

        mock_balance.return_value = (
            "Balance Summary"
        )

        mock_average.side_effect = [
            {"summary": "Average T1"},
            {"summary": "Average T2"},
        ]

        mock_momentum.side_effect = [
            {"summary": "Momentum T1"},
            {"summary": "Momentum T2"},
        ]

        mock_consistency.side_effect = [
            {"summary": "Consistency T1"},
            {"summary": "Consistency T2"},
        ]

        mock_difficulty.side_effect = [
            {"summary": "Difficulty T1"},
            {"summary": "Difficulty T2"},
        ]

        mock_star.side_effect = [
            {"summary": "Star T1"},
            {"summary": "Star T2"},
        ]

        result = (
            PerformanceAnalysisService.generate(
                match
            )
        )

        self.assertEqual(
            result,
            (
                "Score Summary "
                "Balance Summary "
                "Average T1 "
                "Average T2 "
                "Momentum T1 "
                "Momentum T2 "
                "Consistency T1 "
                "Consistency T2 "
                "Difficulty T1 "
                "Difficulty T2 "
                "Star T1 "
                "Star T2"
            ),
        )

        self.assertEqual(
            mock_context.call_count,
            2,
        )

        mock_score.assert_called_once_with(
            match,
        )

        mock_balance.assert_called_once_with(
            match,
        )