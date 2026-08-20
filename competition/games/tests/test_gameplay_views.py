from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

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

from games.models import (
    Match,
    GameSession,
)


User = get_user_model()


class GamePlayViewTest(TestCase):

    def setUp(self):

        self.user = User.objects.create_user(
            username="user1",
            password="1234",
        )

        self.team = Team.objects.create(
            name="Team 1",
            captain=self.user,
        )

        self.user2 = User.objects.create_user(
            username="user2",
            password="1234",
        )

        self.team2 = Team.objects.create(
            name="Team 2",
            captain=self.user2,
        )

        TeamMembership.objects.create(
            team=self.team2,
            user=self.user2,
        )

        TeamMembership.objects.create(
            team=self.team,
            user=self.user,
        )

        self.game_type = GameType.objects.create(
            name="Quiz",
            key="quiz",
        )

        self.tournament = Tournament.objects.create(
            name="League",
            game_type=self.game_type,
            total_rounds=2,
        )

        TournamentTeam.objects.create(
            tournament=self.tournament,
            team=self.team,
        )

        TournamentTeam.objects.create(
            tournament=self.tournament,
            team=self.team2,
        )

        self.subject = Subject.objects.create(
            name="Chemistry",
            slug="chemistry",
            is_active=True,
        )

        self.round = Round.objects.create(
            tournament=self.tournament,
            number=1,
            status="scheduled",
            subject=self.subject,
            question_difficulty="easy",
            question_count=3,
        )

        self.pairing = Pairing.objects.create(
            round=self.round,
            team1=self.team,
            team2=self.team2,
        )

        self.match = Match.objects.create(
            round=self.round,
            pairing=self.pairing,
            team1=self.team,
            team2=self.team2,
        )

        self.session = GameSession.objects.create(
            match=self.match,
            user=self.user,
            status="pending",
        )

    def test_game_cannot_start_when_round_is_not_active(self):

        self.client.force_login(self.user)

        response = self.client.get(
            reverse(
                "game_play",
                kwargs={
                    "session_id": self.session.id,
                },
            )
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        self.assertContains(
            response,
            "این راند هنوز فعال نشده است.",
        )

        self.session.refresh_from_db()

        self.assertIsNone(
            self.session.started_at,
        )

        self.assertEqual(
            self.session.status,
            "pending",
        )


    def test_game_can_start_when_round_is_active(self):

        self.round.status = "active"
        self.round.save()

        self.client.force_login(self.user)

        response = self.client.get(
            reverse(
                "game_play",
                kwargs={
                    "session_id": self.session.id,
                },
            )
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        self.session.refresh_from_db()

        self.assertIsNotNone(
            self.session.started_at,
        )

        self.assertEqual(
            self.session.status,
            "started",
        )