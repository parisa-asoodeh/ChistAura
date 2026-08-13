from django.test import TestCase
from django.utils import timezone

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
    Pairing,
    Subject,
)

from competitions.status_service import (
    TournamentStatusService,
)

from games.models import Match
from unittest.mock import patch


class TournamentStatusServiceTest(TestCase):

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
            name="League",
            game_type=self.game_type,
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
        self.tournament.save()

        self.round = Round.objects.create(
            tournament=self.tournament,
            number=1,
            status="scheduled",
            subject=self.subject,
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


    def test_refresh_tournament_when_unfinished_match_exists(
        self,
    ):

        self.tournament.status = "finished"
        self.tournament.champion = self.team1
        self.tournament.finished_at = timezone.now()

        self.tournament.save()

        TournamentStatusService.refresh_tournament(
            self.tournament,
        )

        self.tournament.refresh_from_db()

        self.assertEqual(
            self.tournament.status,
            "active",
        )

        self.assertIsNone(
            self.tournament.champion,
        )

        self.assertIsNone(
            self.tournament.finished_at,
        )


    def test_refresh_tournament_when_all_matches_are_finished(
        self,
    ):

        self.match.score_team1 = 20
        self.match.score_team2 = 10
        self.match.winner = self.team1
        self.match.save()

        TournamentStatusService.refresh_tournament(
            self.tournament,
        )

        self.tournament.refresh_from_db()

        self.assertEqual(
            self.tournament.status,
            "finished",
        )

        self.assertEqual(
            self.tournament.champion,
            self.team1,
        )

        self.assertIsNotNone(
            self.tournament.finished_at,
        )


    def test_refresh_tournament_keeps_active_status_when_match_is_unfinished(
        self,
    ):

        self.tournament.status = "active"
        self.tournament.save()

        TournamentStatusService.refresh_tournament(
            self.tournament,
        )

        self.tournament.refresh_from_db()

        self.assertEqual(
            self.tournament.status,
            "active",
        )

        self.assertIsNone(
            self.tournament.champion,
        )

        self.assertIsNone(
            self.tournament.finished_at,
        )


    @patch(
        "competitions.status_service.TournamentRankingService.rank_teams"
    )
    def test_refresh_tournament_when_no_ranked_teams(
        self,
        mock_rank_teams,
    ):

        self.match.score_team1 = 10
        self.match.score_team2 = 5
        self.match.save()

        mock_rank_teams.return_value = []

        TournamentStatusService.refresh_tournament(
            self.tournament,
        )

        self.tournament.refresh_from_db()

        self.assertEqual(
            self.tournament.status,
            "finished",
        )

        self.assertIsNone(
            self.tournament.champion,
        )

        self.assertIsNotNone(
            self.tournament.finished_at,
        )

        mock_rank_teams.assert_called_once_with(
            self.tournament,
        )