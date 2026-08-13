from django.test import TestCase
from django.core.exceptions import ValidationError

from accounts.models import CustomUser

from teams.models import Team

from competitions.models import (
    Tournament,
    TournamentTeam,
    GameType,
)

from competitions.services import TournamentService


class TournamentServiceTest(TestCase):

    def setUp(self):

        # -------------------------------------------------
        # Users
        # -------------------------------------------------

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

        # -------------------------------------------------
        # Teams
        # -------------------------------------------------

        self.team1 = Team.objects.create(
            name="Team 1",
            captain=self.user1,
        )

        self.team2 = Team.objects.create(
            name="Team 2",
            captain=self.user2,
        )

        self.team3 = Team.objects.create(
            name="Team 3",
            captain=self.user3,
        )

        # -------------------------------------------------
        # Game Type
        # -------------------------------------------------

        self.game_type = GameType.objects.create(
            name="Quiz",
            key="quiz",
        )

        # -------------------------------------------------
        # Tournament
        # -------------------------------------------------

        self.tournament = Tournament.objects.create(
            name="Tournament",
            game_type=self.game_type,
        )

        # دو تیم اولیه
        TournamentTeam.objects.create(
            tournament=self.tournament,
            team=self.team1,
        )

        TournamentTeam.objects.create(
            tournament=self.tournament,
            team=self.team2,
        )


    # =====================================================
    # add_team()
    # =====================================================

    def test_add_team_success(self):

        tournament_team = TournamentService.add_team(
            self.tournament,
            self.team3,
        )

        self.assertIsNotNone(
            tournament_team,
        )

        self.assertEqual(
            tournament_team.tournament,
            self.tournament,
        )

        self.assertEqual(
            tournament_team.team,
            self.team3,
        )

        self.assertTrue(
            TournamentTeam.objects.filter(
                tournament=self.tournament,
                team=self.team3,
            ).exists()
        )


    def test_add_team_rejected_when_tournament_is_not_draft(self):

        self.tournament.status = "active"
        self.tournament.save()

        with self.assertRaises(
            ValidationError,
        ):
            TournamentService.add_team(
                self.tournament,
                self.team3,
            )

        self.assertFalse(
            TournamentTeam.objects.filter(
                tournament=self.tournament,
                team=self.team3,
            ).exists()
        )


    # =====================================================
    # remove_team()
    # =====================================================

    def test_remove_team_success(self):

        self.assertTrue(
            TournamentTeam.objects.filter(
                tournament=self.tournament,
                team=self.team1,
            ).exists()
        )

        TournamentService.remove_team(
            self.tournament,
            self.team1,
        )

        self.assertFalse(
            TournamentTeam.objects.filter(
                tournament=self.tournament,
                team=self.team1,
            ).exists()
        )


    def test_remove_team_rejected_when_tournament_is_not_draft(self):

        self.tournament.status = "active"
        self.tournament.save()

        with self.assertRaises(
            ValidationError,
        ):
            TournamentService.remove_team(
                self.tournament,
                self.team1,
            )

        self.assertTrue(
            TournamentTeam.objects.filter(
                tournament=self.tournament,
                team=self.team1,
            ).exists()
        )


    # =====================================================
    # start_tournament()
    # =====================================================

    def test_start_tournament_success(self):

        TournamentService.start_tournament(
            self.tournament,
        )

        self.tournament.refresh_from_db()

        self.assertEqual(
            self.tournament.status,
            "active",
        )

        self.assertIsNotNone(
            self.tournament.started_at,
        )


    def test_start_tournament_rejected_when_tournament_is_not_draft(self):

        self.tournament.status = "active"
        self.tournament.save()

        with self.assertRaises(
            ValidationError,
        ):
            TournamentService.start_tournament(
                self.tournament,
            )


    def test_start_tournament_rejected_when_tournament_has_less_than_two_teams(self):

        TournamentTeam.objects.filter(
            tournament=self.tournament,
            team=self.team2,
        ).delete()

        with self.assertRaises(
            ValidationError,
        ):
            TournamentService.start_tournament(
                self.tournament,
            )

        self.tournament.refresh_from_db()

        self.assertEqual(
            self.tournament.status,
            "draft",
        )

        self.assertIsNone(
            self.tournament.started_at,
        )


    def test_start_tournament_does_not_create_round(self):

        from competitions.models import Round

        TournamentService.start_tournament(
            self.tournament,
        )

        self.assertFalse(
            Round.objects.filter(
                tournament=self.tournament,
            ).exists()
        )


    def test_start_tournament_does_not_create_pairing(self):

        from competitions.models import Pairing

        TournamentService.start_tournament(
            self.tournament,
        )

        self.assertFalse(
            Pairing.objects.filter(
                round__tournament=self.tournament,
            ).exists()
        )


    def test_start_tournament_does_not_create_match(self):

        from games.models import Match

        TournamentService.start_tournament(
            self.tournament,
        )

        self.assertFalse(
            Match.objects.filter(
                round__tournament=self.tournament,
            ).exists()
        )


    def test_start_tournament_does_not_create_game_sessions(self):

        from games.models import GameSession

        TournamentService.start_tournament(
            self.tournament,
        )

        self.assertFalse(
            GameSession.objects.filter(
                match__round__tournament=self.tournament,
            ).exists()
        )


    def test_start_tournament_keeps_teams_unchanged(self):

        TournamentService.start_tournament(
            self.tournament,
        )

        self.assertEqual(
            TournamentTeam.objects.filter(
                tournament=self.tournament,
            ).count(),
            2,
        )