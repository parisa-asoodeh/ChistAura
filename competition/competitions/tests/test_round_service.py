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
)

from games.models import Match

from competitions.round_service import RoundService


class RoundServiceTest(TestCase):

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
            total_rounds=3,
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

    # --------------------------------------------------
    # create_round
    # --------------------------------------------------

    def test_create_first_round_success(self):

        round_obj = RoundService.create_round(
            tournament=self.tournament,
            subject=self.subject,
        )

        self.assertEqual(
            round_obj.number,
            1,
        )

        self.assertEqual(
            round_obj.status,
            "scheduled",
        )

        self.assertEqual(
            round_obj.subject,
            self.subject,
        )

        self.assertEqual(
            round_obj.question_difficulty,
            "easy",
        )

        self.assertEqual(
            round_obj.question_count,
            10,
        )

    def test_create_next_round_increments_number(self):

        first_round = RoundService.create_round(
            tournament=self.tournament,
            subject=self.subject,
        )

        second_round = RoundService.create_round(
            tournament=self.tournament,
            subject=self.subject,
        )

        self.assertEqual(
            first_round.number,
            1,
        )

        self.assertEqual(
            second_round.number,
            2,
        )

    def test_create_round_when_tournament_is_not_active(self):

        self.tournament.status = "draft"
        self.tournament.save()

        with self.assertRaises(
            ValidationError,
        ):
            RoundService.create_round(
                tournament=self.tournament,
                subject=self.subject,
            )

        self.assertEqual(
            Round.objects.filter(
                tournament=self.tournament,
            ).count(),
            0,
        )

    def test_create_round_with_inactive_subject(self):

        self.subject.is_active = False
        self.subject.save()

        with self.assertRaises(
            ValidationError,
        ):
            RoundService.create_round(
                tournament=self.tournament,
                subject=self.subject,
            )

    def test_create_round_with_invalid_question_count(self):

        with self.assertRaises(
            ValidationError,
        ):
            RoundService.create_round(
                tournament=self.tournament,
                subject=self.subject,
                question_count=0,
            )

    def test_create_round_with_invalid_difficulty(self):

        with self.assertRaises(
            ValidationError,
        ):
            RoundService.create_round(
                tournament=self.tournament,
                subject=self.subject,
                question_difficulty="invalid",
            )


    def test_create_round_cannot_exceed_total_rounds(self):

        self.tournament.total_rounds = 2
        self.tournament.save()

        RoundService.create_round(
            tournament=self.tournament,
            subject=self.subject,
        )

        RoundService.create_round(
            tournament=self.tournament,
            subject=self.subject,
        )

        with self.assertRaises(
            ValidationError,
        ):
            RoundService.create_round(
                tournament=self.tournament,
                subject=self.subject,
            )

    # --------------------------------------------------
    # start_round
    # --------------------------------------------------

    def test_start_round_success(self):

        round_obj = RoundService.create_round(
            tournament=self.tournament,
            subject=self.subject,
        )

        RoundService.start_round(
            round_obj,
        )

        round_obj.refresh_from_db()

        self.assertEqual(
            round_obj.status,
            "active",
        )

        self.assertIsNotNone(
            round_obj.starts_at,
        )

    def test_start_round_only_from_scheduled_status(self):

        round_obj = RoundService.create_round(
            tournament=self.tournament,
            subject=self.subject,
        )

        round_obj.status = "active"
        round_obj.save()

        with self.assertRaises(
            ValidationError,
        ):
            RoundService.start_round(
                round_obj,
            )

    def test_start_round_when_tournament_is_not_active(self):

        round_obj = RoundService.create_round(
            tournament=self.tournament,
            subject=self.subject,
        )

        self.tournament.status = "draft"
        self.tournament.save()

        with self.assertRaises(
            ValidationError,
        ):
            RoundService.start_round(
                round_obj,
            )

        round_obj.refresh_from_db()

        self.assertEqual(
            round_obj.status,
            "scheduled",
        )

    def test_second_round_cannot_start_before_first_finishes(self):

        first_round = RoundService.create_round(
            tournament=self.tournament,
            subject=self.subject,
        )

        second_round = RoundService.create_round(
            tournament=self.tournament,
            subject=self.subject,
        )

        RoundService.start_round(
            first_round,
        )

        with self.assertRaises(
            ValidationError,
        ):
            RoundService.start_round(
                second_round,
            )

        second_round.refresh_from_db()

        self.assertEqual(
            second_round.status,
            "scheduled",
        )

    def test_second_round_can_start_after_first_finishes(self):

        first_round = RoundService.create_round(
            tournament=self.tournament,
            subject=self.subject,
        )

        second_round = RoundService.create_round(
            tournament=self.tournament,
            subject=self.subject,
        )

        RoundService.start_round(
            first_round,
        )

        Match.objects.create(
            round=first_round,
            team1=self.team1,
            team2=self.team2,
            score_team1=50,
            score_team2=40,
            status="completed",
        )

        RoundService.finish_round(
            first_round,
        )

        RoundService.start_round(
            second_round,
        )

        second_round.refresh_from_db()

        self.assertEqual(
            second_round.status,
            "active",
        )

        self.assertIsNotNone(
            second_round.starts_at,
        )

    # --------------------------------------------------
    # finish_round
    # --------------------------------------------------

    def test_finish_round_success(self):

        round_obj = RoundService.create_round(
            tournament=self.tournament,
            subject=self.subject,
        )

        RoundService.start_round(
            round_obj,
        )

        Match.objects.create(
            round=round_obj,
            team1=self.team1,
            team2=self.team2,
            score_team1=50,
            score_team2=40,
            status="completed",
        )

        RoundService.finish_round(
            round_obj,
        )

        round_obj.refresh_from_db()

        self.assertEqual(
            round_obj.status,
            "finished",
        )

        self.assertIsNotNone(
            round_obj.ends_at,
        )


    def test_finish_round_fails_when_match_is_not_complete(self):

        round_obj = RoundService.create_round(
            tournament=self.tournament,
            subject=self.subject,
        )

        RoundService.start_round(
            round_obj,
        )

        Match.objects.create(
            round=round_obj,
            team1=self.team1,
            team2=self.team2,
        )

        with self.assertRaises(
            ValidationError,
        ):
            RoundService.finish_round(
                round_obj,
            )

        round_obj.refresh_from_db()

        self.assertEqual(
            round_obj.status,
            "active",
        )

        self.assertIsNone(
            round_obj.ends_at,
        )


    def test_finish_round_only_from_active_status(self):

        round_obj = RoundService.create_round(
            tournament=self.tournament,
            subject=self.subject,
        )

        with self.assertRaises(
            ValidationError,
        ):
            RoundService.finish_round(
                round_obj,
            )

        round_obj.refresh_from_db()

        self.assertEqual(
            round_obj.status,
            "scheduled",
        )

        self.assertIsNone(
            round_obj.ends_at,
        )

    def test_finish_round_cannot_finish_finished_round(self):

        round_obj = RoundService.create_round(
            tournament=self.tournament,
            subject=self.subject,
        )

        RoundService.start_round(
            round_obj,
        )

        RoundService.finish_round(
            round_obj,
        )

        with self.assertRaises(
            ValidationError,
        ):
            RoundService.finish_round(
                round_obj,
            )

        round_obj.refresh_from_db()

        self.assertEqual(
            round_obj.status,
            "finished",
        )


    def test_create_duplicate_round_number_is_rejected(self):

        first_round = RoundService.create_round(
            tournament=self.tournament,
            subject=self.subject,
        )

        with self.assertRaises(
            ValidationError,
        ):
            Round.objects.create(
                tournament=self.tournament,
                number=first_round.number,
                subject=self.subject,
            )
