from django.test import TestCase
from django.core.exceptions import ValidationError

from accounts.models import CustomUser
from teams.models import Team
from competitions.models import (
    Tournament,
    TournamentTeam,
    Round,
    Pairing,
    GameType,
    Subject,
    Category,
    RoundQuestion,
)
from games.models import Match
from games.quiz_models import (
    QuizQuestion,
    QuizMatchQuestion,
)
from games.quiz_match_question_service import (
    QuizMatchQuestionService,
)


class QuizMatchQuestionServiceTest(TestCase):

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
            status="draft",
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
            slug="chemistry",
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

    def create_question(self, number):
        return QuizQuestion.objects.create(
            category=self.category,
            question=f"Question {number}",
            option_a="A",
            option_b="B",
            option_c="C",
            option_d="D",
            correct_answer="A",
            difficulty="easy",
            is_active=True,
        )

    def create_round_question(self, question, order):
        return RoundQuestion.objects.create(
            round=self.round,
            question=question,
            order=order,
        )

    def test_creates_match_questions_from_round_questions(self):
        question1 = self.create_question(1)
        question2 = self.create_question(2)
        question3 = self.create_question(3)

        round_question1 = self.create_round_question(
            question1,
            1,
        )
        round_question2 = self.create_round_question(
            question2,
            2,
        )
        round_question3 = self.create_round_question(
            question3,
            3,
        )

        QuizMatchQuestionService.create_questions_for_match(
            match=self.match,
        )

        match_questions = QuizMatchQuestion.objects.filter(
            match=self.match,
        ).order_by("order")

        self.assertEqual(
            match_questions.count(),
            3,
        )

        self.assertEqual(
            list(
                match_questions.values_list(
                    "round_question_id",
                    flat=True,
                )
            ),
            [
                round_question1.id,
                round_question2.id,
                round_question3.id,
            ],
        )

    def test_match_question_order_matches_round_question_order(self):
        question1 = self.create_question(1)
        question2 = self.create_question(2)

        round_question1 = self.create_round_question(
            question1,
            1,
        )
        round_question2 = self.create_round_question(
            question2,
            2,
        )

        QuizMatchQuestionService.create_questions_for_match(
            match=self.match,
        )

        match_question1 = QuizMatchQuestion.objects.get(
            match=self.match,
            round_question=round_question1,
        )

        match_question2 = QuizMatchQuestion.objects.get(
            match=self.match,
            round_question=round_question2,
        )

        self.assertEqual(
            match_question1.order,
            round_question1.order,
        )

        self.assertEqual(
            match_question2.order,
            round_question2.order,
        )

    def test_does_not_use_round_questions_from_another_round(self):
        question1 = self.create_question(1)
        question2 = self.create_question(2)

        valid_round_question = self.create_round_question(
            question1,
            1,
        )

        other_round = Round.objects.create(
            tournament=self.tournament,
            number=2,
            status="scheduled",
            subject=self.subject,
            question_difficulty="easy",
            question_count=1,
        )

        invalid_round_question = RoundQuestion.objects.create(
            round=other_round,
            question=question2,
            order=1,
        )

        QuizMatchQuestionService.create_questions_for_match(
            match=self.match,
        )

        match_questions = QuizMatchQuestion.objects.filter(
            match=self.match,
        )

        self.assertEqual(
            match_questions.count(),
            1,
        )

        self.assertEqual(
            match_questions.first().round_question,
            valid_round_question,
        )

        self.assertNotEqual(
            match_questions.first().round_question,
            invalid_round_question,
        )

    def test_same_round_questions_can_be_used_by_multiple_matches(self):
        question1 = self.create_question(1)
        question2 = self.create_question(2)

        round_question1 = self.create_round_question(
            question1,
            1,
        )
        round_question2 = self.create_round_question(
            question2,
            2,
        )

        QuizMatchQuestionService.create_questions_for_match(
            match=self.match,
        )

        second_pairing = Pairing.objects.create(
            round=self.round,
            team1=self.team2,
            team2=self.team1,
        )

        second_match = Match.objects.create(
            round=self.round,
            pairing=second_pairing,
            team1=self.team2,
            team2=self.team1,
        )

        QuizMatchQuestionService.create_questions_for_match(
            match=second_match,
        )

        first_questions = set(
            QuizMatchQuestion.objects.filter(
                match=self.match,
            ).values_list(
                "round_question_id",
                flat=True,
            )
        )

        second_questions = set(
            QuizMatchQuestion.objects.filter(
                match=second_match,
            ).values_list(
                "round_question_id",
                flat=True,
            )
        )

        self.assertEqual(
            first_questions,
            {
                round_question1.id,
                round_question2.id,
            },
        )

        self.assertEqual(
            second_questions,
            {
                round_question1.id,
                round_question2.id,
            },
        )

    def test_match_questions_cannot_be_created_for_round_question_from_different_round(
        self,
    ):
        question1 = self.create_question(1)

        other_round = Round.objects.create(
            tournament=self.tournament,
            number=2,
            status="scheduled",
            subject=self.subject,
            question_difficulty="easy",
            question_count=1,
        )

        other_round_question = RoundQuestion.objects.create(
            round=other_round,
            question=question1,
            order=1,
        )

        with self.assertRaises(ValidationError):
            QuizMatchQuestion.objects.create(
                match=self.match,
                round_question=other_round_question,
                order=1,
            )