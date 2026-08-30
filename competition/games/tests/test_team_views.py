from django.test import TestCase
from django.urls import reverse

from accounts.models import CustomUser

from teams.models import Team, TeamMembership

from competitions.models import (
    Tournament,
    TournamentTeam,
    GameType,
)


class ManageTeamMembersViewTest(TestCase):

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

        TeamMembership.objects.create(
            team=self.team,
            user=self.user2,
        )


    def test_captain_can_replace_team_member(
        self,
    ):

        # Arrange
        self.client.login(
            username="captain",
            password="1234",
        )

        # Act
        response = self.client.post(
            reverse(
                "manage_team_members",
                kwargs={
                    "team_id": self.team.id,
                },
            ),
            {
                "action": "replace",
                "old_user_id": self.user1.id,
                "new_user_id": self.user3.id,
            },
        )

        # Assert
        self.assertEqual(
            response.status_code,
            200,
        )

        self.assertFalse(
            TeamMembership.objects.filter(
                team=self.team,
                user=self.user1,
            ).exists()
        )

        self.assertTrue(
            TeamMembership.objects.filter(
                team=self.team,
                user=self.user3,
            ).exists()
        )

        self.assertEqual(
            TeamMembership.objects.filter(
                team=self.team,
            ).count(),
            3,
        )


    def test_non_captain_cannot_manage_team_members(
        self,
    ):

        # Arrange
        self.client.login(
            username="user3",
            password="1234",
        )

        # Act
        response = self.client.post(
            reverse(
                "manage_team_members",
                kwargs={
                    "team_id": self.team.id,
                },
            ),
            {
                "action": "replace",
                "old_user_id": self.user1.id,
                "new_user_id": self.user3.id,
            },
        )

        # Assert
        self.assertEqual(
            response.status_code,
            200,
        )

        self.assertContains(
            response,
            "فقط کاپیتان می‌تواند اعضای تیم را مدیریت کند.",
        )

        self.assertTrue(
            TeamMembership.objects.filter(
                team=self.team,
                user=self.user1,
            ).exists()
        )

        self.assertFalse(
            TeamMembership.objects.filter(
                team=self.team,
                user=self.user3,
            ).exists()
        )


    def test_captain_cannot_replace_themselves(
        self,
    ):

        # Arrange
        self.client.login(
            username="captain",
            password="1234",
        )

        # Act
        response = self.client.post(
            reverse(
                "manage_team_members",
                kwargs={
                    "team_id": self.team.id,
                },
            ),
            {
                "action": "replace",
                "old_user_id": self.captain.id,
                "new_user_id": self.user3.id,
            },
        )

        # Assert
        self.assertEqual(
            response.status_code,
            200,
        )

        self.assertContains(
            response,
            "کاپیتان قابل تعویض نیست.",
        )

        self.assertTrue(
            TeamMembership.objects.filter(
                team=self.team,
                user=self.captain,
            ).exists()
        )

        self.assertFalse(
            TeamMembership.objects.filter(
                team=self.team,
                user=self.user3,
            ).exists()
        )


    def test_replace_member_when_new_user_belongs_to_another_team(
        self,
    ):

        # Arrange
        other_team = Team.objects.create(
            name="Other Team",
            captain=self.user3,
        )

        TeamMembership.objects.create(
            team=other_team,
            user=self.user3,
        )

        self.client.login(
            username="captain",
            password="1234",
        )

        # Act
        response = self.client.post(
            reverse(
                "manage_team_members",
                kwargs={
                    "team_id": self.team.id,
                },
            ),
            {
                "action": "replace",
                "old_user_id": self.user1.id,
                "new_user_id": self.user3.id,
            },
        )

        # Assert
        self.assertEqual(
            response.status_code,
            200,
        )

        self.assertContains(
            response,
            "این کاربر قبلاً عضو تیم دیگری است.",
        )

        self.assertTrue(
            TeamMembership.objects.filter(
                team=self.team,
                user=self.user1,
            ).exists()
        )


    def test_replace_member_when_team_is_in_active_tournament(
        self,
    ):

        # Arrange
        game_type = GameType.objects.create(
            name="Quiz",
            key="quiz",
        )

        tournament = Tournament.objects.create(
            name="League",
            game_type=game_type,
            total_rounds=2,
        )

        TournamentTeam.objects.create(
            tournament=tournament,
            team=self.team,
        )

        tournament.status = "active"
        tournament.save()

        self.client.login(
            username="captain",
            password="1234",
        )

        # Act
        response = self.client.post(
            reverse(
                "manage_team_members",
                kwargs={
                    "team_id": self.team.id,
                },
            ),
            {
                "action": "replace",
                "old_user_id": self.user1.id,
                "new_user_id": self.user3.id,
            },
        )

        # Assert
        self.assertEqual(
            response.status_code,
            200,
        )

        self.assertContains(
            response,
            "در زمان برگزاری لیگ امکان تغییر اعضای تیم وجود ندارد.",
        )

        self.assertTrue(
            TeamMembership.objects.filter(
                team=self.team,
                user=self.user1,
            ).exists()
        )

        self.assertFalse(
            TeamMembership.objects.filter(
                team=self.team,
                user=self.user3,
            ).exists()
        )
