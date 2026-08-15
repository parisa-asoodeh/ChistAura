from django.test import TestCase
from django.core.exceptions import ValidationError

from accounts.models import CustomUser
from teams.models import Team

from competitions.models import (
    Tournament,
    TournamentTeam,
    GameType,
    Subject,
    Round,
    Pairing,
    RoundQuestion,
    Category,
)

from games.models import Match
from competitions.match_creation_service import MatchCreationService

from games.session_creation_service import (
    GameSessionCreationService,
)
from games.models import GameSession
from games.quiz_models import QuizQuestion, QuizMatchQuestion
from unittest.mock import patch




class MatchCreationServiceTest(TestCase):

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

        self.game_type = GameType.objects.create(
            name="Quiz",
            key="quiz",
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
        self.tournament.save()

        self.subject = Subject.objects.create(
            name="Chemistry",
            slug="chemistry",
            is_active=True,
        )

        self.category = Category.objects.create(
            name="Chemistry",
            subject=self.subject,
        )

        self.round = Round.objects.create(
            tournament=self.tournament,
            number=1,
            status="scheduled",
            subject=self.subject,
            question_difficulty="easy",
            question_count=3,
        )

        question1 = QuizQuestion.objects.create(
            category=self.category,
            question="Question 1",
            option_a="A",
            option_b="B",
            option_c="C",
            option_d="D",
            correct_answer="A",
            difficulty="easy",
            is_active=True,
        )

        question2 = QuizQuestion.objects.create(
            category=self.category,
            question="Question 2",
            option_a="A",
            option_b="B",
            option_c="C",
            option_d="D",
            correct_answer="B",
            difficulty="easy",
            is_active=True,
        )

        question3 = QuizQuestion.objects.create(
            category=self.category,
            question="Question 3",
            option_a="A",
            option_b="B",
            option_c="C",
            option_d="D",
            correct_answer="C",
            difficulty="easy",
            is_active=True,
        )

        RoundQuestion.objects.create(
            round=self.round,
            question=question1,
            order=1,
        )

        RoundQuestion.objects.create(
            round=self.round,
            question=question2,
            order=2,
        )

        RoundQuestion.objects.create(
            round=self.round,
            question=question3,
            order=3,
        )

        self.pairing = Pairing.objects.create(
            round=self.round,
            team1=self.team1,
            team2=self.team2,
        )


    def test_create_match_from_pairing(self):
        """
        Match باید مستقیماً از Pairing ساخته شود
        و Round و تیم‌ها را از همان Pairing دریافت کند.
        """

        match = MatchCreationService.create_match_from_pairing(
            self.pairing
        )

        self.assertIsNotNone(match)

        self.assertEqual(
            match.pairing,
            self.pairing,
        )

        self.assertEqual(
            match.round,
            self.round,
        )

        self.assertEqual(
            match.team1,
            self.team1,
        )

        self.assertEqual(
            match.team2,
            self.team2,
        )


    def test_match_created_with_exact_pairing_data(self):
        """
        هیچ داده‌ای نباید هنگام ساخت Match
        با Pairing ناسازگار باشد.
        """

        match = MatchCreationService.create_match_from_pairing(
            self.pairing
        )

        self.assertEqual(
            match.round_id,
            self.pairing.round_id,
        )

        self.assertEqual(
            match.team1_id,
            self.pairing.team1_id,
        )

        self.assertEqual(
            match.team2_id,
            self.pairing.team2_id,
        )

        self.assertEqual(
            match.pairing_id,
            self.pairing.id,
        )


    def test_duplicate_match_for_pairing_is_rejected(self):
        """
        برای هر Pairing فقط یک Match مجاز است.
        """

        MatchCreationService.create_match_from_pairing(
            self.pairing
        )

        with self.assertRaises(
            ValidationError
        ):
            MatchCreationService.create_match_from_pairing(
                self.pairing
            )


    def test_match_cannot_be_created_for_finished_round(self):
        """
        Pairing مربوط به Round نامعتبر نباید
        بتواند Match تولید کند.
        """

        other_round = Round.objects.create(
            tournament=self.tournament,
            number=2,
            status="finished",
            subject=self.subject,
            question_difficulty="easy",
            question_count=3,
        )

        invalid_pairing = Pairing.objects.create(
            round=other_round,
            team1=self.team1,
            team2=self.team2,
        )

        with self.assertRaises(
            ValidationError
        ):
            MatchCreationService.create_match_from_pairing(
                invalid_pairing
            )


    def test_game_sessions_are_created_for_all_match_team_members(self):
        """
        برای هر بازیکن دو تیم Match باید دقیقاً یک GameSession ساخته شود.
        """

        from teams.models import TeamMembership

        TeamMembership.objects.create(
            team=self.team1,
            user=self.user1,
        )

        TeamMembership.objects.create(
            team=self.team2,
            user=self.user2,
        )

        match = MatchCreationService.create_match_from_pairing(
            self.pairing
        )

        GameSessionCreationService.create_sessions(
            match
        )

        sessions = GameSession.objects.filter(
            match=match
        )

        self.assertEqual(
            sessions.count(),
            2,
        )

        self.assertTrue(
            sessions.filter(
                user=self.user1
            ).exists()
        )

        self.assertTrue(
            sessions.filter(
                user=self.user2
            ).exists()
        )


    def test_game_session_is_created_only_for_match_team_members(self):
        """
        بازیکنی که عضو هیچ‌کدام از دو تیم Match نیست
        نباید برای Match او GameSession ساخته شود.
        """

        from teams.models import TeamMembership

        outsider = CustomUser.objects.create_user(
            username="outsider",
            password="1234",
        )

        TeamMembership.objects.create(
            team=self.team1,
            user=self.user1,
        )

        TeamMembership.objects.create(
            team=self.team2,
            user=self.user2,
        )

        match = MatchCreationService.create_match_from_pairing(
            self.pairing
        )

        GameSessionCreationService.create_sessions(
            match
        )

        self.assertFalse(
            GameSession.objects.filter(
                match=match,
                user=outsider,
            ).exists()
        )


    def test_each_match_player_gets_only_one_game_session(self):
        """
        هر بازیکن باید برای یک Match فقط یک GameSession داشته باشد.
        """

        from teams.models import TeamMembership

        TeamMembership.objects.create(
            team=self.team1,
            user=self.user1,
        )

        TeamMembership.objects.create(
            team=self.team2,
            user=self.user2,
        )

        match = MatchCreationService.create_match_from_pairing(
            self.pairing
        )

        GameSessionCreationService.create_sessions(
            match
        )

        GameSessionCreationService.create_sessions(
            match
        )

        self.assertEqual(
            GameSession.objects.filter(
                match=match,
                user=self.user1,
            ).count(),
            1,
        )

        self.assertEqual(
            GameSession.objects.filter(
                match=match,
                user=self.user2,
            ).count(),
            1,
        )


    def test_create_match_from_pairing_creates_quiz_match_questions(self):
        match = MatchCreationService.create_match_from_pairing(
            self.pairing,
        )

        self.assertEqual(
            QuizMatchQuestion.objects.filter(
                match=match,
            ).count(),
            self.round.question_count,
        )

        round_question_ids = set(
            RoundQuestion.objects.filter(
                round=self.round,
            ).values_list(
                "id",
                flat=True,
            )
        )

        match_question_round_question_ids = set(
            QuizMatchQuestion.objects.filter(
                match=match,
            ).values_list(
                "round_question_id",
                flat=True,
            )
        )

        self.assertEqual(
            match_question_round_question_ids,
            round_question_ids,
        )


    def test_match_creation_creates_quiz_match_questions(self):

        match = MatchCreationService.create_match_from_pairing(
            self.pairing,
        )

        match_questions = QuizMatchQuestion.objects.filter(
            match=match,
        )

        self.assertEqual(
            match_questions.count(),
            self.round.question_count,
        )

        self.assertEqual(
            list(
                match_questions.values_list(
                    "round_question_id",
                    flat=True,
                )
            ),
            list(
                RoundQuestion.objects.filter(
                    round=self.round,
                ).values_list(
                    "id",
                    flat=True,
                )
            ),
        )

    def test_match_creation_rolls_back_if_session_creation_fails(self):
        with patch.object(
            GameSessionCreationService,
            "create_sessions",
            side_effect=ValidationError(
                "Session creation failed."
            ),
        ):
            with self.assertRaises(ValidationError):
                MatchCreationService.create_match_from_pairing(
                    self.pairing,
                )

        self.assertFalse(
            Match.objects.filter(
                pairing=self.pairing,
            ).exists()
        )