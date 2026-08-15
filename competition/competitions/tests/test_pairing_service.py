from django.test import TestCase
from django.core.exceptions import ValidationError

from accounts.models import CustomUser
from teams.models import Team, TeamMembership

from competitions.models import (
    Tournament,
    TournamentTeam,
    GameType,
    Subject,
    Round,
    Pairing,
    RoundBye,
)

from competitions.pairing_service import SwissPairingService
from competitions.round_service import RoundService


class SwissPairingServiceTest(TestCase):

    def setUp(self):

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

        self.team4 = Team.objects.create(
            name="Team 4",
            captain=self.user4,
        )

        TeamMembership.objects.create(
            team=self.team1,
            user=self.user1,
        )

        TeamMembership.objects.create(
            team=self.team2,
            user=self.user2,
        )

        TeamMembership.objects.create(
            team=self.team3,
            user=self.user3,
        )

        TeamMembership.objects.create(
            team=self.team4,
            user=self.user4,
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
            name="Tournament",
            game_type=self.game_type,
            total_rounds=2,
        )

        for team in [
            self.team1,
            self.team2,
            self.team3,
            self.team4,
        ]:
            TournamentTeam.objects.create(
                tournament=self.tournament,
                team=team,
            )

        self.tournament.status = "active"
        self.tournament.save()

        self.round = Round.objects.create(
            tournament=self.tournament,
            number=1,
            subject=self.subject,
        )

    def test_create_pairings_for_even_number_of_teams(self):

        pairings = SwissPairingService.create_pairings(
            self.round,
        )

        self.assertEqual(
            len(pairings),
            2,
        )

        self.assertEqual(
            Pairing.objects.filter(
                round=self.round,
            ).count(),
            2,
        )

    def test_every_team_is_paired_once(self):

        pairings = SwissPairingService.create_pairings(
            self.round,
        )

        paired_teams = []

        for pairing in pairings:
            paired_teams.append(pairing.team1)
            paired_teams.append(pairing.team2)

        self.assertEqual(
            len(paired_teams),
            4,
        )

        self.assertEqual(
            len(set(paired_teams)),
            4,
        )

    def test_team_cannot_be_paired_with_itself(self):

        pairing = Pairing(
            round=self.round,
            team1=self.team1,
            team2=self.team1,
        )

        with self.assertRaises(
            ValidationError,
        ):
            pairing.save()

    def test_create_pairings_does_not_duplicate_existing_pairings(self):

        SwissPairingService.create_pairings(
            self.round,
        )

        with self.assertRaises(
            ValidationError,
        ):
            SwissPairingService.create_pairings(
                self.round,
            )

    def test_create_pairings_requires_scheduled_round(self):

        self.round.status = "active"
        self.round.save()

        with self.assertRaises(
            ValidationError,
        ):
            SwissPairingService.create_pairings(
                self.round,
            )


    def test_odd_number_of_teams_creates_one_bye(self):

        # Arrange
        user5 = CustomUser.objects.create_user(
            username="user5",
            password="1234",
        )

        team5 = Team.objects.create(
            name="Team 5",
            captain=user5,
        )

        TeamMembership.objects.create(
            team=team5,
            user=user5,
        )

        self.tournament.status = "draft"
        self.tournament.save()

        TournamentTeam.objects.create(
            tournament=self.tournament,
            team=team5,
        )

        self.tournament.status = "active"
        self.tournament.save()

        # Act
        pairings = SwissPairingService.create_pairings(
            self.round,
        )

        # Assert
        self.assertEqual(
            len(pairings),
            2,
        )

        self.assertEqual(
            RoundBye.objects.filter(
                round=self.round,
            ).count(),
            1,
        )


    def test_bye_team_is_not_paired(self):

        # Arrange
        user5 = CustomUser.objects.create_user(
            username="user5",
            password="1234",
        )

        team5 = Team.objects.create(
            name="Team 5",
            captain=user5,
        )

        TeamMembership.objects.create(
            team=team5,
            user=user5,
        )

        self.tournament.status = "draft"
        self.tournament.save()

        TournamentTeam.objects.create(
            tournament=self.tournament,
            team=team5,
        )

        self.tournament.status = "active"
        self.tournament.save()

        # Act
        SwissPairingService.create_pairings(
            self.round,
        )

        bye = RoundBye.objects.get(
            round=self.round,
        )

        # Assert
        self.assertFalse(
            Pairing.objects.filter(
                round=self.round,
                team1=bye.team,
            ).exists()
        )

        self.assertFalse(
            Pairing.objects.filter(
                round=self.round,
                team2=bye.team,
            ).exists()
        )


    def test_bye_has_three_points(self):

        # Arrange
        user5 = CustomUser.objects.create_user(
            username="user5",
            password="1234",
        )

        team5 = Team.objects.create(
            name="Team 5",
            captain=user5,
        )

        TeamMembership.objects.create(
            team=team5,
            user=user5,
        )

        self.tournament.status = "draft"
        self.tournament.save()

        TournamentTeam.objects.create(
            tournament=self.tournament,
            team=team5,
        )

        self.tournament.status = "active"
        self.tournament.save()

        # Act
        SwissPairingService.create_pairings(
            self.round,
        )

        bye = RoundBye.objects.get(
            round=self.round,
        )

        # Assert
        self.assertEqual(
            bye.points,
            3,
        )


    def test_only_one_bye_is_created(self):

        # Arrange
        user5 = CustomUser.objects.create_user(
            username="user5",
            password="1234",
        )

        team5 = Team.objects.create(
            name="Team 5",
            captain=user5,
        )

        TeamMembership.objects.create(
            team=team5,
            user=user5,
        )

        self.tournament.status = "draft"
        self.tournament.save()

        TournamentTeam.objects.create(
            tournament=self.tournament,
            team=team5,
        )

        self.tournament.status = "active"
        self.tournament.save()

        # Act
        SwissPairingService.create_pairings(
            self.round,
        )

        # Assert
        self.assertEqual(
            RoundBye.objects.filter(
                round=self.round,
            ).count(),
            1,
        )


    def test_teams_do_not_play_each_other_again(self):

        # Round اول
        first_round = self.round

        pairings = SwissPairingService.create_pairings(
            first_round,
        )

        self.assertEqual(
            len(pairings),
            2,
        )

        # Round اول را تمام می‌کنیم
        first_round.status = "finished"
        first_round.save()

        # Round دوم
        second_round = RoundService.create_round(
            tournament=self.tournament,
            subject=self.subject,
        )

        # Pairingهای Round دوم
        second_pairings = SwissPairingService.create_pairings(
            second_round,
        )

        # هیچ Pairing جدیدی نباید همان دو تیم Round اول را
        # دوباره مقابل هم قرار دهد.
        first_opponents = {
            frozenset(
                (
                    pairing.team1_id,
                    pairing.team2_id,
                )
            )
            for pairing in pairings
        }

        second_opponents = {
            frozenset(
                (
                    pairing.team1_id,
                    pairing.team2_id,
                )
            )
            for pairing in second_pairings
        }

        self.assertTrue(
            first_opponents.isdisjoint(
                second_opponents
            )
        )