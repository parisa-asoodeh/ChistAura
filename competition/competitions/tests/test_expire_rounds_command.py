from datetime import timedelta

from django.core.management import call_command
from django.test import TestCase
from django.utils import timezone

from accounts.models import CustomUser
from teams.models import Team, TeamMembership

from competitions.models import (
    Tournament,
    TournamentTeam,
    GameType,
    Subject,
    Category,
    Round,
    Pairing,
)

from games.models import Match, GameSession, QuizQuestion


class ExpireRoundsCommandTest(TestCase):

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

        self.category = Category.objects.create(
            name="General Chemistry",
            subject=self.subject,
            is_active=True,
        )

        for index in range(20):
            QuizQuestion.objects.create(
                category=self.category,
                question=f"Question {index + 1}",
                option_a="A",
                option_b="B",
                option_c="C",
                option_d="D",
                correct_answer="A",
                difficulty="easy",
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
            update_fields=["status"],
        )

    def create_expired_round(self, number=1):

        round_obj = Round.objects.create(
            tournament=self.tournament,
            number=number,
            status="active",
            subject=self.subject,
            question_difficulty="easy",
            question_count=10,
            ends_at=timezone.now() - timedelta(
                minutes=5,
            ),
        )

        pairing = Pairing.objects.create(
            round=round_obj,
            team1=self.team1,
            team2=self.team2,
        )

        match = Match.objects.create(
            round=round_obj,
            pairing=pairing,
            team1=self.team1,
            team2=self.team2,
        )

        GameSession.objects.create(
            match=match,
            user=self.user1,
            status="started",
            started_at=timezone.now(),
        )

        GameSession.objects.create(
            match=match,
            user=self.user2,
            status="pending",
        )

        return round_obj, match

    def test_expired_round_is_processed(self):

        round_obj, match = self.create_expired_round()

        call_command(
            "expire_rounds",
        )

        round_obj.refresh_from_db()
        match.refresh_from_db()

        self.assertEqual(
            round_obj.status,
            "finished",
        )

        self.assertEqual(
            match.status,
            "forfeit",
        )

        self.assertEqual(
            match.forfeit_team,
            self.team1,
        )

    def test_round_is_not_processed_before_end_time(self):

        round_obj = Round.objects.create(
            tournament=self.tournament,
            number=1,
            status="active",
            subject=self.subject,
            question_difficulty="easy",
            question_count=10,
            ends_at=timezone.now() + timedelta(
                hours=1,
            ),
        )

        call_command(
            "expire_rounds",
        )

        round_obj.refresh_from_db()

        self.assertEqual(
            round_obj.status,
            "active",
        )

    def test_finished_round_is_not_processed(self):

        round_obj = Round.objects.create(
            tournament=self.tournament,
            number=1,
            status="finished",
            subject=self.subject,
            question_difficulty="easy",
            question_count=10,
            ends_at=timezone.now() - timedelta(
                minutes=5,
            ),
        )

        call_command(
            "expire_rounds",
        )

        round_obj.refresh_from_db()

        self.assertEqual(
            round_obj.status,
            "finished",
        )

    def test_round_without_end_time_is_not_processed(self):

        round_obj = Round.objects.create(
            tournament=self.tournament,
            number=1,
            status="active",
            subject=self.subject,
            question_difficulty="easy",
            question_count=10,
            ends_at=None,
        )

        call_command(
            "expire_rounds",
        )

        round_obj.refresh_from_db()

        self.assertEqual(
            round_obj.status,
            "active",
        )

    def test_multiple_expired_rounds_are_processed(self):

        user3 = CustomUser.objects.create_user(
            username="user3",
            password="1234",
        )

        user4 = CustomUser.objects.create_user(
            username="user4",
            password="1234",
        )

        team3 = Team.objects.create(
            name="Team 3",
            captain=user3,
        )

        team4 = Team.objects.create(
            name="Team 4",
            captain=user4,
        )

        TeamMembership.objects.create(
            team=team3,
            user=user3,
        )

        TeamMembership.objects.create(
            team=team4,
            user=user4,
        )

        tournament = Tournament.objects.create(
            name="Multiple Expired Rounds Tournament",
            game_type=self.game_type,
            total_rounds=2,
        )

        TournamentTeam.objects.create(
            tournament=tournament,
            team=self.team1,
        )

        TournamentTeam.objects.create(
            tournament=tournament,
            team=self.team2,
        )

        TournamentTeam.objects.create(
            tournament=tournament,
            team=team3,
        )

        TournamentTeam.objects.create(
            tournament=tournament,
            team=team4,
        )

        tournament.status = "active"
        tournament.save(
            update_fields=["status"],
        )

        round1 = Round.objects.create(
            tournament=tournament,
            number=1,
            status="active",
            subject=self.subject,
            question_difficulty="easy",
            question_count=10,
            ends_at=timezone.now() - timedelta(
                minutes=10,
            ),
        )

        pairing1 = Pairing.objects.create(
            round=round1,
            team1=self.team1,
            team2=self.team2,
        )

        match1 = Match.objects.create(
            round=round1,
            pairing=pairing1,
            team1=self.team1,
            team2=self.team2,
        )

        GameSession.objects.create(
            match=match1,
            user=self.user1,
            status="started",
            started_at=timezone.now(),
        )

        GameSession.objects.create(
            match=match1,
            user=self.user2,
            status="pending",
        )

        round2 = Round.objects.create(
            tournament=tournament,
            number=2,
            status="scheduled",
            subject=self.subject,
            question_difficulty="easy",
            question_count=10,
            starts_at=timezone.now() - timedelta(
                minutes=10,
            ),
            ends_at=timezone.now() - timedelta(
                minutes=5,
            ),
        )

        call_command(
            "expire_rounds",
        )

        round1.refresh_from_db()
        round2.refresh_from_db()

        self.assertEqual(
            round1.status,
            "finished",
        )

        self.assertEqual(
            round2.status,
            "scheduled",
        )

        self.assertEqual(
            round2.pairings.count(),
            2,
        )

        self.assertEqual(
            round2.matches.count(),
            2,
        )