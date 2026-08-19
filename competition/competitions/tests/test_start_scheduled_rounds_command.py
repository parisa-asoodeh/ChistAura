from datetime import timedelta

from django.core.management import call_command
from django.core.exceptions import ValidationError
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
)


class StartScheduledRoundsCommandTest(TestCase):

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
            name="Tournament",
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
            update_fields=["status"]
        )

    def test_round_does_not_start_before_scheduled_time(self):

        round_obj = Round.objects.create(
            tournament=self.tournament,
            number=1,
            status="scheduled",
            subject=self.subject,
            question_difficulty="easy",
            question_count=10,
            starts_at=timezone.now() + timedelta(
                hours=1,
            ),
        )

        call_command(
            "start_scheduled_rounds",
        )

        round_obj.refresh_from_db()

        self.assertEqual(
            round_obj.status,
            "scheduled",
        )

    def test_round_starts_when_scheduled_time_has_arrived(self):

        round_obj = Round.objects.create(
            tournament=self.tournament,
            number=1,
            status="scheduled",
            subject=self.subject,
            question_difficulty="easy",
            question_count=10,
            starts_at=timezone.now() - timedelta(
                minutes=1,
            ),
        )

        call_command(
            "start_scheduled_rounds",
        )

        round_obj.refresh_from_db()

        self.assertEqual(
            round_obj.status,
            "active",
        )

        self.assertIsNotNone(
            round_obj.starts_at,
        )

    def test_round_does_not_start_if_previous_round_is_not_finished(self):

        first_round = Round.objects.create(
            tournament=self.tournament,
            number=1,
            status="active",
            subject=self.subject,
            question_difficulty="easy",
            question_count=10,
            starts_at=timezone.now() - timedelta(
                minutes=10,
            ),
        )

        second_round = Round.objects.create(
            tournament=self.tournament,
            number=2,
            status="scheduled",
            subject=self.subject,
            question_difficulty="easy",
            question_count=10,
            starts_at=timezone.now() - timedelta(
                minutes=1,
            ),
        )

        call_command(
            "start_scheduled_rounds",
        )

        first_round.refresh_from_db()
        second_round.refresh_from_db()

        self.assertEqual(
            first_round.status,
            "active",
        )

        self.assertEqual(
            second_round.status,
            "scheduled",
        )