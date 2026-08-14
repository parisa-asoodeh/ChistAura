from datetime import timedelta

from django.test import TestCase
from django.utils import timezone

from accounts.models import CustomUser
from teams.models import Team, TeamMembership

from competitions.models import (
    Tournament,
    TournamentTeam,
    GameType,
    Subject,
    Round,
    Pairing,
)

from games.models import Match, GameSession


class MatchTimeoutServiceTest(TestCase):

    def setUp(self):

        self.user1 = CustomUser.objects.create_user(
            username="user1",
            password="1234",
        )

        self.user2 = CustomUser.objects.create_user(
            username="user2",
            password="1234",
        )

        self.team1 = Team.objects.create(
            name="Team 1",
            captain=self.user1,
        )

        self.team2 = Team.objects.create(
            name="Team 2",
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

        self.game_type = GameType.objects.create(
            name="Quiz",
            key="quiz",
        )

        self.subject = Subject.objects.create(
            name="Chemistry",
            slug="chemistry",
            is_active=True,
        )

        self.tournament = Tournament.objects.create(
            name="Swiss Tournament",
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

        self.tournament.status = "active"
        self.tournament.save(
            update_fields=["status"],
        )

        self.round = Round.objects.create(
            tournament=self.tournament,
            number=1,
            status="active",
            subject=self.subject,
            ends_at=timezone.now() - timedelta(
                minutes=5,
            ),
        )

        self.pairing = Pairing.objects.create(
            round=self.round,
            team1=self.team1,
            team2=self.team2,
        )

        self.match = Match.objects.create(
            round=self.round,
            pairing=self.pairing,
            team1=self.team1,
            team2=self.team2,
        )

        self.session1 = GameSession.objects.create(
            match=self.match,
            user=self.user1,
            status="started",
            started_at=timezone.now(),
        )

        self.session2 = GameSession.objects.create(
            match=self.match,
            user=self.user2,
            status="pending",
        )

    def test_expired_match_forfeits_to_present_team(self):

        from games.timeout_service import (
            MatchTimeoutService,
        )

        MatchTimeoutService.handle_expired_round(
            self.round,
        )

        self.match.refresh_from_db()

        self.assertEqual(
            self.match.status,
            "forfeit",
        )

        self.assertEqual(
            self.match.forfeit_team,
            self.team1,
        )

        self.assertEqual(
            self.match.winner,
            self.team1,
        )


    def test_expired_match_forfeits_to_team2_when_team1_is_absent(self):

        self.session1.status = "pending"
        self.session1.started_at = None
        self.session1.save(
            update_fields=[
                "status",
                "started_at",
            ],
        )

        self.session2.status = "started"
        self.session2.started_at = timezone.now()
        self.session2.save(
            update_fields=[
                "status",
                "started_at",
            ],
        )

        from games.timeout_service import MatchTimeoutService

        MatchTimeoutService.handle_expired_round(
            self.round,
        )

        self.match.refresh_from_db()

        self.assertEqual(
            self.match.status,
            "forfeit",
        )

        self.assertEqual(
            self.match.forfeit_team,
            self.team2,
        )

        self.assertEqual(
            self.match.winner,
            self.team2,
        )


    def test_expired_match_results_in_double_no_show_when_both_teams_are_absent(
        self,
    ):

        self.session1.status = "pending"
        self.session1.started_at = None
        self.session1.save(
            update_fields=[
                "status",
                "started_at",
            ],
        )

        self.session2.status = "pending"
        self.session2.started_at = None
        self.session2.save(
            update_fields=[
                "status",
                "started_at",
            ],
        )

        from games.timeout_service import MatchTimeoutService

        MatchTimeoutService.handle_expired_round(
            self.round,
        )

        self.match.refresh_from_db()

        self.assertEqual(
            self.match.status,
            "double_forfeit",
        )

        self.assertIsNone(
            self.match.winner,
        )


    def test_expired_match_with_both_teams_present_is_finalized(
        self,
    ):

        from games.models import MatchPlayerScore
        from games.timeout_service import MatchTimeoutService

        MatchPlayerScore.objects.create(
            match=self.match,
            user=self.user1,
            team=self.team1,
            score=30,
            completion_time=100,
        )

        MatchPlayerScore.objects.create(
            match=self.match,
            user=self.user2,
            team=self.team2,
            score=20,
            completion_time=110,
        )

        self.session2.status = "started"
        self.session2.started_at = timezone.now()
        self.session2.save(
            update_fields=[
                "status",
                "started_at",
            ],
        )

        MatchTimeoutService.handle_expired_round(
            self.round,
        )

        self.match.refresh_from_db()

        self.assertEqual(
            self.match.status,
            "completed",
        )

        self.assertEqual(
            self.match.score_team1,
            30,
        )

        self.assertEqual(
            self.match.score_team2,
            20,
        )

        self.assertEqual(
            self.match.winner,
            self.team1,
        )

        self.assertIsNone(
            self.match.forfeit_team,
        )

    def test_expired_match_with_both_teams_present_uses_valid_scores(
        self,
    ):
        extra_user1 = CustomUser.objects.create_user(
            username="user3",
            password="1234",
        )

        extra_user2 = CustomUser.objects.create_user(
            username="user4",
            password="1234",
        )

        extra_user3 = CustomUser.objects.create_user(
            username="user5",
            password="1234",
        )

        extra_user4 = CustomUser.objects.create_user(
            username="user6",
            password="1234",
        )

        TeamMembership.objects.create(
            team=self.team1,
            user=extra_user1,
        )

        TeamMembership.objects.create(
            team=self.team1,
            user=extra_user2,
        )

        TeamMembership.objects.create(
            team=self.team2,
            user=extra_user3,
        )

        TeamMembership.objects.create(
            team=self.team2,
            user=extra_user4,
        )

        from games.models import MatchPlayerScore
        from games.timeout_service import MatchTimeoutService

        MatchPlayerScore.objects.create(
            match=self.match,
            user=self.user1,
            team=self.team1,
            score=30,
            completion_time=100,
        )

        MatchPlayerScore.objects.create(
            match=self.match,
            user=self.user2,
            team=self.team2,
            score=20,
            completion_time=110,
        )

        self.session1.status = "completed"
        self.session1.save(
            update_fields=["status"],
        )

        self.session2.status = "completed"
        self.session2.save(
            update_fields=["status"],
        )

        MatchTimeoutService.handle_expired_round(
            self.round,
        )

        self.match.refresh_from_db()

        self.assertEqual(
            self.match.status,
            "completed",
        )

        self.assertEqual(
            self.match.score_team1,
            30,
        )

        self.assertEqual(
            self.match.score_team2,
            20,
        )

        self.assertEqual(
            self.match.winner,
            self.team1,
        )