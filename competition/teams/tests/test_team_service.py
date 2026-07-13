from django.test import TestCase
from django.core.exceptions import ValidationError

from accounts.models import CustomUser

from teams.models import (
    Team,
    TeamMembership,
)

from teams.services import (
    TeamService,
    TeamMemberService,
)

from competitions.models import (
    Tournament,
    TournamentTeam,
    GameType,
)


class TeamServiceTest(TestCase):

    def setUp(self):

        self.captain = CustomUser.objects.create_user(
            username="captain",
            password="1234",
        )

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


    def test_create_team_successfully(
        self,
    ):

        # Act
        team = TeamService.create_team(
            captain=self.captain,
            team_name="Team A",
            members=[
                self.user1,
                self.user2,
            ],
        )

        # Assert
        self.assertEqual(
            team.name,
            "Team A",
        )

        self.assertEqual(
            team.captain,
            self.captain,
        )

        self.assertEqual(
            TeamMembership.objects.filter(
                team=team,
            ).count(),
            3,
        )


    def test_create_team_with_duplicate_name(self):

        # Arrange
        Team.objects.create(
            name="Team A",
            captain=self.captain,
        )

        # Act & Assert
        with self.assertRaises(ValidationError):
            TeamService.create_team(
                captain=self.user1,
                team_name="Team A",
                members=[
                    self.user2,
                    self.user3,
                ],
            )


    def test_create_team_when_captain_already_has_team(
        self,
    ):

        # Arrange
        Team.objects.create(
            name="Team A",
            captain=self.captain,
        )

        # Act & Assert
        with self.assertRaises(ValidationError):
            TeamService.create_team(
                captain=self.captain,
                team_name="Team B",
                members=[
                    self.user1,
                    self.user2,
                ],
            )

    
    def test_create_team_when_member_already_belongs_to_another_team(
        self,
    ):

        # Arrange
        other_team = Team.objects.create(
            name="Other Team",
            captain=self.user3,
        )

        TeamMembership.objects.create(
            team=other_team,
            user=self.user1,
        )

        # Act & Assert
        with self.assertRaises(ValidationError):
            TeamService.create_team(
                captain=self.captain,
                team_name="Team A",
                members=[
                    self.user1,
                    self.user2,
                ],
            )


    def test_create_team_with_less_than_two_members(
        self,
    ):

        # Act & Assert
        with self.assertRaises(ValidationError):
            TeamService.create_team(
                captain=self.captain,
                team_name="Team A",
                members=[
                    self.user1,
                ],
            )

    def test_create_team_removes_duplicate_members_and_captain(
        self,
    ):

        # Act
        team = TeamService.create_team(
            captain=self.captain,
            team_name="Team A",
            members=[
                self.user1,
                self.user1,
                self.user2,
                self.captain,
            ],
        )

        # Assert
        self.assertEqual(
            TeamMembership.objects.filter(
                team=team,
            ).count(),
            3,
        )

        self.assertTrue(
            TeamMembership.objects.filter(
                team=team,
                user=self.captain,
            ).exists()
        )

        self.assertTrue(
            TeamMembership.objects.filter(
                team=team,
                user=self.user1,
            ).exists()
        )

        self.assertTrue(
            TeamMembership.objects.filter(
                team=team,
                user=self.user2,
            ).exists()
        )


class TeamMemberServiceTest(TestCase):
    def setUp(self):

        self.captain = CustomUser.objects.create_user(
            username="captain",
            password="1234",
        )

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

        self.team = Team.objects.create(
            name="Team A",
            captain=self.captain,
        )

        TeamMembership.objects.create(
            team=self.team,
            user=self.captain,
        )

        TeamMembership.objects.create(
            team=self.team,
            user=self.user1,
        )

        self.game_type = GameType.objects.create(
            name="Quiz",
            key="quiz",
        )

        self.tournament = Tournament.objects.create(
            name="League",
            game_type=self.game_type,
        )


    def test_add_member_successfully(
        self,
    ):

        # Act
        TeamMemberService.add_member(
            team=self.team,
            user=self.user2,
        )

        # Assert
        self.assertTrue(
            TeamMembership.objects.filter(
                team=self.team,
                user=self.user2,
            ).exists()
        )

    def test_add_member_when_user_is_already_in_team(
        self,
    ):

        # Act & Assert
        with self.assertRaises(ValidationError):
            TeamMemberService.add_member(
                team=self.team,
                user=self.user1,
            )

    def test_add_member_when_user_is_in_another_team(
        self,
    ):

        # Arrange
        other_team = Team.objects.create(
            name="Other Team",
            captain=self.user3,
        )

        TeamMembership.objects.create(
            team=other_team,
            user=self.user2,
        )

        # Act & Assert
        with self.assertRaises(ValidationError):
            TeamMemberService.add_member(
                team=self.team,
                user=self.user2,
            )

    def test_add_member_when_team_is_in_active_tournament(
        self,
    ):

        # Arrange
        TournamentTeam.objects.create(
            tournament=self.tournament,
            team=self.team,
        )

        self.tournament.status = "active"
        self.tournament.save()

        # Act & Assert
        with self.assertRaises(ValidationError):
            TeamMemberService.add_member(
                team=self.team,
                user=self.user2,
            )

    def test_remove_member_successfully(
        self,
    ):

        # Act
        TeamMemberService.remove_member(
            team=self.team,
            user=self.user1,
        )

        # Assert
        self.assertFalse(
            TeamMembership.objects.filter(
                team=self.team,
                user=self.user1,
            ).exists()
        )

    def test_remove_member_when_user_is_captain(
        self,
    ):

        # Act & Assert
        with self.assertRaises(ValidationError):
            TeamMemberService.remove_member(
                team=self.team,
                user=self.captain,
            )

    def test_remove_member_when_team_is_in_active_tournament(
        self,
    ):

        # Arrange
        TournamentTeam.objects.create(
            tournament=self.tournament,
            team=self.team,
        )

        self.tournament.status = "active"
        self.tournament.save()

        # Act & Assert
        with self.assertRaises(ValidationError):
            TeamMemberService.remove_member(
                team=self.team,
                user=self.user1,
            )

    def test_remove_member_when_user_is_not_member(
        self,
    ):

        # Act & Assert
        with self.assertRaises(ValidationError):
            TeamMemberService.remove_member(
                team=self.team,
                user=self.user2,
            )