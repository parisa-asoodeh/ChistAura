from django.test import TestCase

from accounts.models import CustomUser
from competitions.models import (
    Tournament,
    TournamentTeam,
    Team,
    GameType,
    Subject,
    Category,
    Round,
    RoundQuestion,
    Pairing,
)
from games.models import Match, GameSession
from games.quiz_models import (
    QuizQuestion,
    QuizMatchQuestion,
    QuizAnswer,
)
from games.quiz_correction_service import QuizCorrectionService


class QuizCorrectionServiceTest(TestCase):

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
            name="General Chemistry",
            subject=self.subject,
        )

        self.round = Round.objects.create(
            tournament=self.tournament,
            number=1,
            status="scheduled",
            subject=self.subject,
            question_difficulty="easy",
            question_count=2,
        )

        self.pairing = Pairing.objects.create(
            round=self.round,
            team1=self.team1,
            team2=self.team2,
        )

        self.match = Match.objects.create(
            round=self.round,
            pairing=self.pairing,
            team1=self.team1,
            team2=self.team2,
        )

        self.session = GameSession.objects.create(
            match=self.match,
            user=self.user1,
        )

        self.question1 = QuizQuestion.objects.create(
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

        self.question2 = QuizQuestion.objects.create(
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

        self.round_question1 = RoundQuestion.objects.create(
            round=self.round,
            question=self.question1,
            order=1,
        )

        self.round_question2 = RoundQuestion.objects.create(
            round=self.round,
            question=self.question2,
            order=2,
        )

        self.match_question1 = QuizMatchQuestion.objects.create(
            match=self.match,
            round_question=self.round_question1,
            order=1,
        )

        self.match_question2 = QuizMatchQuestion.objects.create(
            match=self.match,
            round_question=self.round_question2,
            order=2,
        )

    def test_all_correct_answers_return_full_score(self):
        QuizAnswer.objects.create(
            session=self.session,
            match_question=self.match_question1,
            selected_answer="A",
        )

        QuizAnswer.objects.create(
            session=self.session,
            match_question=self.match_question2,
            selected_answer="B",
        )

        score = QuizCorrectionService.calculate_raw_score(
            self.session
        )

        self.assertEqual(score, 2)

    def test_only_correct_answers_are_counted(self):
        QuizAnswer.objects.create(
            session=self.session,
            match_question=self.match_question1,
            selected_answer="A",
        )

        QuizAnswer.objects.create(
            session=self.session,
            match_question=self.match_question2,
            selected_answer="C",
        )

        score = QuizCorrectionService.calculate_raw_score(
            self.session
        )

        self.assertEqual(score, 1)

    def test_answers_from_another_session_are_not_counted(self):
        other_session = GameSession.objects.create(
            match=self.match,
            user=self.user2,
        )

        QuizAnswer.objects.create(
            session=self.session,
            match_question=self.match_question1,
            selected_answer="A",
        )

        QuizAnswer.objects.create(
            session=other_session,
            match_question=self.match_question2,
            selected_answer="B",
        )

        score = QuizCorrectionService.calculate_raw_score(
            self.session
        )

        self.assertEqual(score, 1)