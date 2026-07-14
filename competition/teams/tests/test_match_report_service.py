from unittest.mock import (
    Mock,
    patch,
)

from django.test import SimpleTestCase

from teams.ai.match_report_service import (
    MatchReportService,
)


class MatchReportServiceTest(SimpleTestCase):

    def setUp(self):

        self.team1 = Mock()
        self.team1.name = "Alpha"

        self.team2 = Mock()
        self.team2.name = "Beta"

        self.match = Mock()

        self.match.team1 = self.team1
        self.match.team2 = self.team2
        self.match.score_team1 = 100
        self.match.score_team2 = 80
        self.match.winner = self.team1


    @patch(
        "teams.ai.match_report_service.PerformanceAnalysisService.generate"
    )
    def test_build_summary_with_winner(
        self,
        mock_analysis,
    ):

        mock_analysis.return_value = "Analysis"

        best_player = Mock()
        best_player.user.username = "parisa"
        best_player.score = 60
        best_player.completion_time = 120

        summary = MatchReportService.build_summary(
            self.match,
            best_player,
        )

        self.assertIn(
            "Alpha",
            summary,
        )

        self.assertIn(
            "parisa",
            summary,
        )

        self.assertIn(
            "Analysis",
            summary,
        )


    @patch(
        "teams.ai.match_report_service.PerformanceAnalysisService.generate"
    )
    def test_build_summary_draw(
        self,
        mock_analysis,
    ):

        mock_analysis.return_value = "Analysis"

        self.match.winner = None
        self.match.score_team1 = 90
        self.match.score_team2 = 90

        summary = MatchReportService.build_summary(
            self.match,
            None,
        )

        self.assertIn(
            "به تساوی رسید",
            summary,
        )

        self.assertIn(
            "Analysis",
            summary,
        )


    @patch(
        "teams.ai.match_report_service.PerformanceAnalysisService.generate"
    )
    @patch(
        "teams.ai.match_report_service.BestPlayerService.get_best_player"
    )
    def test_generate(
        self,
        mock_best_player,
        mock_analysis,
    ):

        mock_analysis.return_value = "Analysis"

        best_player = Mock()

        best_player.user.username = "parisa"
        best_player.score = 50
        best_player.completion_time = 100

        mock_best_player.return_value = best_player

        result = MatchReportService.generate(
            self.match,
        )

        self.assertEqual(
            result["winner"],
            self.team1,
        )

        self.assertEqual(
            result["best_player"],
            best_player,
        )

        self.assertIn(
            "Analysis",
            result["summary"],
        )

        mock_best_player.assert_called_once_with(
            self.match,
        )