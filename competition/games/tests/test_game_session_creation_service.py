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
    Subject,
    Round,
)

from games.models import (
    Match,
    GameSession,
)

from games.session_creation_service import (
    GameSessionCreationService,
)

class GameSessionCreationServiceTest(TestCase):
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

        self.subject = Subject.objects.create(
            name="General",
            slug="general",
        )

        self.round = Round.objects.create(
            tournament=self.tournament,
            number=1,
            subject=self.subject,
        )

        self.match = Match.objects.create(
            round=self.round,
            team1=self.team1,
            team2=self.team2,
        )


    def test_create_sessions_success(
        self,
    ):

        # Act
        GameSessionCreationService.create_sessions(
            self.match,
        )

        # Assert
        sessions = GameSession.objects.filter(
            match=self.match,
        )

        self.assertEqual(
            sessions.count(),
            2,
        )

        self.assertTrue(
            sessions.filter(
                user=self.user1,
            ).exists()
        )

        self.assertTrue(
            sessions.filter(
                user=self.user2,
            ).exists()
        )