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
    Pairing,
    Subject,
)

from competitions.status_service import (
    TournamentStatusService,
)

from games.models import Match


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
        self.tournament.save(update_fields=["status"])

    def create_round(
        self,
        number,
        status="scheduled",
    ):
        return Round.objects.create(
            tournament=self.tournament,
            number=number,
            status=status,
            subject=self.subject,
        )

    def create_match(
        self,
        round_obj,
        completed=True,
    ):
        pairing = Pairing.objects.create(
            round=round_obj,
            team1=self.team1,
            team2=self.team2,
        )

        if completed:
            return Match.objects.create(
                round=round_obj,
                pairing=pairing,
                team1=self.team1,
                team2=self.team2,
                score_team1=20,
                score_team2=10,
                status="completed",
            )

        return Match.objects.create(
            round=round_obj,
            pairing=pairing,
            team1=self.team1,
            team2=self.team2,
        )

    def test_unfinished_match_does_not_finish_tournament(self):

        round_obj = self.create_round(
            number=1,
            status="active",
        )

        self.create_match(
            round_obj,
            completed=False,
        )

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

    def test_finished_current_round_does_not_finish_tournament_when_more_rounds_remain(
        self,
    ):

        round1 = self.create_round(
            number=1,
            status="finished",
        )

        self.create_match(
            round1,
            completed=True,
        )

        round2 = self.create_round(
            number=2,
            status="scheduled",
        )

        self.create_match(
            round2,
            completed=True,
        )

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

    def test_last_round_finished_finishes_tournament_and_sets_champion(
        self,
    ):

        self.tournament.total_rounds = 1
        self.tournament.save(
            update_fields=["total_rounds"],
        )

        round_obj = self.create_round(
            number=1,
            status="finished",
        )

        self.create_match(
            round_obj,
            completed=True,
        )

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