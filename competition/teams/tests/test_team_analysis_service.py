from unittest.mock import patch

from django.test import TestCase

from accounts.models import CustomUser

from teams.models import (
    Team,
    TeamMembership,
)

from competitions.models import Tournament

from games.models import Match

from competitions.models import (
    Tournament,
    GameType,
)

from teams.analysis.team_analysis_service import (
    TeamAnalysisService,
)

class TeamAnalysisServiceTest(TestCase):
    def setUp(self):

        self.game_type = GameType.objects.create(
            name="Quiz",
            key="quiz",
        )

        self.tournament = Tournament.objects.create(
            name="League",
            game_type=self.game_type,
        )

        self.user1 = CustomUser.objects.create_user(
            username="user1",
            password="1234",
        )

        self.user2 = CustomUser.objects.create_user(
            username="user2",
            password="1234",
        )

        self.team1 = Team.objects.create(
            name="Alpha",
            captain=self.user1,
        )

        self.team2 = Team.objects.create(
            name="Beta",
            captain=self.user2,
        )

        TeamMembership.objects.create(
            team=self.team1,
            user=self.user1,
        )

        TeamMembership.objects.create(
            team=self.team2,
            user=self.user2,
        )

    @patch(
        "teams.analysis.team_analysis_service.PlayerRankingService.get_total_score"
    )
    def test_build_team_summary(
        self,
        mock_total_score,
    ):

        mock_total_score.return_value = 120

        summary = (
            TeamAnalysisService.build_team_summary(
                self.team1,
            )
        )

        self.assertEqual(
            len(summary["members"]),
            1,
        )

        self.assertEqual(
            summary["members"][0].individual_score,
            120,
        )

        self.assertIn(
            "form",
            summary,
        )

        self.assertIn(
            "wins",
            summary,
        )

    
    def test_get_team_form_without_completed_matches(
        self,
    ):

        Match.objects.create(
            tournament=self.tournament,
            team1=self.team1,
            team2=self.team2,
        )

        form = TeamAnalysisService.get_team_form(
            self.team1,
        )

        self.assertEqual(
            form,
            [],
        )

    def test_get_team_form(
        self,
    ):

        Match.objects.create(
            tournament=self.tournament,
            team1=self.team1,
            team2=self.team2,
            winner=self.team1,
            score_team1=100,
            score_team2=80,
        )

        Match.objects.create(
            tournament=self.tournament,
            team1=self.team1,
            team2=self.team2,
            winner=None,
            score_team1=90,
            score_team2=90,
        )

        Match.objects.create(
            tournament=self.tournament,
            team1=self.team1,
            team2=self.team2,
            winner=self.team2,
            score_team1=70,
            score_team2=95,
        )

        form = TeamAnalysisService.get_team_form(
            self.team1,
        )

        self.assertEqual(
            form,
            [
                "برد",
                "مساوی",
                "باخت",
            ],
        )

    def test_get_team_form_with_limit(
        self,
    ):

        for _ in range(6):

            Match.objects.create(
                tournament=self.tournament,
                team1=self.team1,
                team2=self.team2,
                winner=self.team1,
                score_team1=100,
                score_team2=50,
            )

        form = TeamAnalysisService.get_team_form(
            self.team1,
            limit=3,
        )

        self.assertEqual(
            len(form),
            3,
        )

        self.assertEqual(
            form,
            [
                "برد",
                "برد",
                "برد",
            ],
        )


    def test_get_recent_scores(
        self,
    ):

        Match.objects.create(
            tournament=self.tournament,
            team1=self.team1,
            team2=self.team2,
            winner=self.team1,
            score_team1=100,
            score_team2=80,
        )

        Match.objects.create(
            tournament=self.tournament,
            team1=self.team2,
            team2=self.team1,
            winner=self.team2,
            score_team1=70,
            score_team2=90,
        )

        Match.objects.create(
            tournament=self.tournament,
            team1=self.team1,
            team2=self.team2,
            winner=self.team2,
            score_team1=60,
            score_team2=95,
        )

        scores = TeamAnalysisService.get_recent_scores(
            self.team1,
        )

        self.assertEqual(
            scores,
            [
                100,
                90,
                60,
            ],
        )

    def test_get_recent_scores_with_limit(
        self,
    ):

        for score in [
            10,
            20,
            30,
            40,
            50,
            60,
        ]:

            Match.objects.create(
                tournament=self.tournament,
                team1=self.team1,
                team2=self.team2,
                winner=self.team1,
                score_team1=score,
                score_team2=0,
            )

        scores = TeamAnalysisService.get_recent_scores(
            self.team1,
            limit=3,
        )

        self.assertEqual(
            scores,
            [
                40,
                50,
                60,
            ],
        )


    def test_get_recent_score_differences(
        self,
    ):

        Match.objects.create(
            tournament=self.tournament,
            team1=self.team1,
            team2=self.team2,
            winner=self.team1,
            score_team1=100,
            score_team2=80,
        )

        Match.objects.create(
            tournament=self.tournament,
            team1=self.team2,
            team2=self.team1,
            winner=self.team2,
            score_team1=70,
            score_team2=90,
        )

        Match.objects.create(
            tournament=self.tournament,
            team1=self.team1,
            team2=self.team2,
            winner=self.team2,
            score_team1=60,
            score_team2=95,
        )

        differences = (
            TeamAnalysisService.get_recent_score_differences(
                self.team1,
            )
        )

        self.assertEqual(
            differences,
            [
                20,
                20,
                35,
            ],
        )

    def test_get_recent_score_differences_with_limit(
        self,
    ):

        for diff in [
            10,
            20,
            30,
            40,
            50,
            60,
        ]:

            Match.objects.create(
                tournament=self.tournament,
                team1=self.team1,
                team2=self.team2,
                winner=self.team1,
                score_team1=100,
                score_team2=100 - diff,
            )

        differences = (
            TeamAnalysisService.get_recent_score_differences(
                self.team1,
                limit=3,
            )
        )

        self.assertEqual(
            differences,
            [
                40,
                50,
                60,
            ],
        )

    def test_get_recent_scores_from_context(
        self,
    ):

        context = {
            "scores": [
                10,
                20,
                30,
                40,
                50,
                60,
            ],
        }

        scores = (
            TeamAnalysisService.get_recent_scores_from_context(
                context,
                limit=3,
            )
        )

        self.assertEqual(
            scores,
            [
                40,
                50,
                60,
            ],
        )

    def test_get_recent_scores_from_context_without_limit(
        self,
    ):

        context = {
            "scores": [
                10,
                20,
            ],
        }

        scores = (
            TeamAnalysisService.get_recent_scores_from_context(
                context,
            )
        )

        self.assertEqual(
            scores,
            [
                10,
                20,
            ],
        )

    def test_get_recent_score_differences_from_context(
        self,
    ):

        context = {
            "scores": [
                10,
                30,
                20,
                50,
            ],
        }

        differences = (
            TeamAnalysisService.get_recent_score_differences_from_context(
                context,
            )
        )

        self.assertEqual(
            differences,
            [
                20,
                10,
                30,
            ],
        )

    def test_get_recent_score_differences_from_context_with_one_score(
        self,
    ):

        context = {
            "scores": [
                50,
            ],
        }

        differences = (
            TeamAnalysisService.get_recent_score_differences_from_context(
                context,
            )
        )

        self.assertEqual(
            differences,
            [],
        )