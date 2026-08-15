from django.test import TestCase

from accounts.models import CustomUser

from teams.models import (
    Team,
    TeamMembership,
)

from competitions.models import (
    Tournament,
    TournamentTeam,
    GameType,
    Round,
    Subject,
)

from games.models import (
    Match,
    MatchPlayerScore,
)

from teams.ai.providers.performance_data_provider import (
    PerformanceDataProvider,
)


class PerformanceDataProviderTest(TestCase):

    def setUp(self):

        # -------------------------
        # Users
        # -------------------------

        self.user1 = CustomUser.objects.create_user(
            username="user1",
            password="1234",
        )

        self.user2 = CustomUser.objects.create_user(
            username="user2",
            password="1234",
        )

        self.user3 = CustomUser.objects.create_user(
            username="user3",
            password="1234",
        )

        self.user4 = CustomUser.objects.create_user(
            username="user4",
            password="1234",
        )

        # -------------------------
        # Teams
        # -------------------------

        self.team1 = Team.objects.create(
            name="Team 1",
            captain=self.user1,
        )

        self.team2 = Team.objects.create(
            name="Team 2",
            captain=self.user3,
        )

        # -------------------------
        # Memberships
        # -------------------------

        TeamMembership.objects.create(
            team=self.team1,
            user=self.user1,
        )

        TeamMembership.objects.create(
            team=self.team1,
            user=self.user2,
        )

        TeamMembership.objects.create(
            team=self.team2,
            user=self.user3,
        )

        TeamMembership.objects.create(
            team=self.team2,
            user=self.user4,
        )

        # -------------------------
        # Game Type
        # -------------------------

        self.game_type = GameType.objects.create(
            name="Quiz",
            key="quiz",
        )

        # -------------------------
        # Subject
        # -------------------------

        self.subject = Subject.objects.create(
            name="Math",
            slug="math",
        )

        # =====================================================
        # Current Tournament
        # =====================================================

        self.tournament = Tournament.objects.create(
            name="League 1",
            game_type=self.game_type,
            total_rounds=2,
        )

        TournamentTeam.objects.create(
            tournament=self.tournament,
            team=self.team1,
        )

        TournamentTeam.objects.create(
            tournament=self.tournament,
            team=self.team2,
        )

        # Current Round

        self.round = Round.objects.create(
            tournament=self.tournament,
            number=1,
            subject=self.subject,
        )

        # Current Match

        self.match = Match.objects.create(
            round=self.round,
            team1=self.team1,
            team2=self.team2,
        )

        # =====================================================
        # Previous Tournament
        # =====================================================

        self.tournament2 = Tournament.objects.create(
            name="League 2",
            game_type=self.game_type,
            total_rounds=2,
        )

        TournamentTeam.objects.create(
            tournament=self.tournament2,
            team=self.team1,
        )

        TournamentTeam.objects.create(
            tournament=self.tournament2,
            team=self.team2,
        )

        # Previous Round

        self.round2 = Round.objects.create(
            tournament=self.tournament2,
            number=1,
            subject=self.subject,
        )

        # Previous Match

        self.match2 = Match.objects.create(
            round=self.round2,
            team1=self.team1,
            team2=self.team2,
        )

    # =====================================================
    # get_history
    # =====================================================

    def test_get_history(self):

        MatchPlayerScore.objects.create(
            match=self.match2,
            user=self.user1,
            team=self.team1,
            score=40,
        )

        history = PerformanceDataProvider.get_history(
            self.team1,
            self.tournament,
        )

        self.assertEqual(
            history,
            [40],
        )

    # =====================================================
    # Current Mode
    # =====================================================

    def test_get_team_context_in_current_mode(
        self,
    ):

        MatchPlayerScore.objects.create(
            match=self.match,
            user=self.user1,
            team=self.team1,
            score=10,
        )

        context = PerformanceDataProvider.get_team_context(
            self.tournament,
            self.team1,
        )

        self.assertEqual(
            context["mode"],
            "current",
        )

        self.assertEqual(
            context["scores"],
            [10],
        )

        self.assertEqual(
            context["history"],
            [],
        )

        self.assertEqual(
            len(context["matches"]),
            1,
        )

        self.assertEqual(
            context["team"],
            self.team1,
        )

    # =====================================================
    # History Mode
    # =====================================================

    def test_get_team_context_in_history_mode(
        self,
    ):

        history_team = Team.objects.create(
            name="History Team",
            captain=self.user1,
        )

        TeamMembership.objects.create(
            team=history_team,
            user=self.user1,
        )

        TournamentTeam.objects.create(
            tournament=self.tournament2,
            team=history_team,
        )

        history_match = Match.objects.create(
            round=self.round2,
            team1=history_team,
            team2=self.team2,
        )

        MatchPlayerScore.objects.create(
            match=history_match,
            user=self.user1,
            team=history_team,
            score=40,
        )

        context = PerformanceDataProvider.get_team_context(
            self.tournament,
            history_team,
        )

        self.assertEqual(
            context["mode"],
            "history",
        )

        self.assertEqual(
            context["scores"],
            [40],
        )

        self.assertEqual(
            context["history"],
            [40],
        )

        self.assertEqual(
            context["matches"],
            [],
        )

        self.assertEqual(
            context["team"],
            history_team,
        )

    # =====================================================
    # No Matches / No History
    # =====================================================

    def test_get_team_context_without_matches_or_history(
        self,
    ):

        new_team = Team.objects.create(
            name="New Team",
            captain=self.user1,
        )

        TeamMembership.objects.create(
            team=new_team,
            user=self.user1,
        )

        context = PerformanceDataProvider.get_team_context(
            self.tournament,
            new_team,
        )

        self.assertEqual(
            context["mode"],
            "history",
        )

        self.assertEqual(
            context["matches"],
            [],
        )

        self.assertEqual(
            context["history"],
            [],
        )

        self.assertEqual(
            context["scores"],
            [],
        )

        self.assertEqual(
            context["team"],
            new_team,
        )