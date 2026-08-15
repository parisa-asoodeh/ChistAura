from django.core.exceptions import ValidationError
from django.test import TestCase

from accounts.models import CustomUser
from teams.models import Team, TeamMembership

from competitions.models import (
    Tournament,
    TournamentTeam,
    GameType,
    Subject,
    Round,
    RoundQuestion,
)

from games.models import Category, QuizQuestion

from competitions.round_question_service import (
    RoundQuestionService,
)


class RoundQuestionServiceTest(TestCase):

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

        self.other_subject = Subject.objects.create(
            name="Physics",
            slug="physics",
            is_active=True,
        )

        self.category = Category.objects.create(
            name="Chemistry",
            subject=self.subject,
        )

        self.other_category = Category.objects.create(
            name="Physics",
            subject=self.other_subject,
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

        self.round = Round.objects.create(
            tournament=self.tournament,
            number=1,
            status="scheduled",
            subject=self.subject,
            question_difficulty="easy",
            question_count=3,
        )

    def create_question(
        self,
        number,
        category=None,
        difficulty="easy",
        is_active=True,
    ):

        return QuizQuestion.objects.create(
            category=category or self.category,
            question=f"Question {number}",
            option_a="A",
            option_b="B",
            option_c="C",
            option_d="D",
            correct_answer="A",
            difficulty=difficulty,
            is_active=is_active,
        )

    def test_assign_questions_success(self):

        self.create_question(1)
        self.create_question(2)
        self.create_question(3)

        result = RoundQuestionService.assign_questions(
            self.round,
        )

        self.assertEqual(
            len(result),
            3,
        )

        self.assertEqual(
            RoundQuestion.objects.filter(
                round=self.round,
            ).count(),
            3,
        )

    def test_questions_are_ordered_from_one(self):

        self.create_question(1)
        self.create_question(2)
        self.create_question(3)

        RoundQuestionService.assign_questions(
            self.round,
        )

        orders = list(
            RoundQuestion.objects.filter(
                round=self.round,
            )
            .values_list(
                "order",
                flat=True,
            )
        )

        self.assertEqual(
            orders,
            [1, 2, 3],
        )

    def test_only_active_questions_are_selected(self):

        self.create_question(1)
        self.create_question(
            2,
            is_active=False,
        )
        self.create_question(3)
        self.create_question(4)

        result = RoundQuestionService.assign_questions(
            self.round,
        )

        self.assertEqual(
            len(result),
            3,
        )

        inactive_question = QuizQuestion.objects.get(
            question="Question 2",
        )

        self.assertFalse(
            RoundQuestion.objects.filter(
                round=self.round,
                question=inactive_question,
            ).exists()
        )

    def test_only_questions_with_round_subject_are_selected(
        self,
    ):

        self.create_question(1)
        self.create_question(
            2,
            category=self.other_category,
        )
        self.create_question(3)
        self.create_question(4)

        RoundQuestionService.assign_questions(
            self.round,
        )

        questions = RoundQuestion.objects.filter(
            round=self.round,
        )

        self.assertEqual(
            questions.count(),
            3,
        )

        for round_question in questions:

            self.assertEqual(
                round_question.question.category.subject,
                self.subject,
            )

    def test_only_questions_with_round_difficulty_are_selected(
        self,
    ):

        self.create_question(1)
        self.create_question(
            2,
            difficulty="medium",
        )
        self.create_question(3)
        self.create_question(4)

        RoundQuestionService.assign_questions(
            self.round,
        )

        questions = RoundQuestion.objects.filter(
            round=self.round,
        )

        self.assertEqual(
            questions.count(),
            3,
        )

        for round_question in questions:

            self.assertEqual(
                round_question.question.difficulty,
                "easy",
            )

    def test_insufficient_questions_raises_validation_error(
        self,
    ):

        self.create_question(1)
        self.create_question(2)

        with self.assertRaises(
            ValidationError,
        ):

            RoundQuestionService.assign_questions(
                self.round,
            )

        self.assertEqual(
            RoundQuestion.objects.filter(
                round=self.round,
            ).count(),
            0,
        )

    def test_previous_round_questions_are_not_reused(
        self,
    ):

        question1 = self.create_question(1)
        self.create_question(2)
        self.create_question(3)
        self.create_question(4)

        RoundQuestion.objects.create(
            round=self.round,
            question=question1,
            order=1,
        )

        second_round = Round.objects.create(
            tournament=self.tournament,
            number=2,
            status="scheduled",
            subject=self.subject,
            question_difficulty="easy",
            question_count=3,
        )

        RoundQuestionService.assign_questions(
            second_round,
        )

        self.assertFalse(
            RoundQuestion.objects.filter(
                round=second_round,
                question=question1,
            ).exists()
        )

    def test_cannot_assign_questions_to_started_round(
        self,
    ):

        self.round.status = "active"
        self.round.save()

        self.create_question(1)
        self.create_question(2)
        self.create_question(3)

        with self.assertRaises(
            ValidationError,
        ):

            RoundQuestionService.assign_questions(
                self.round,
            )

        self.assertEqual(
            RoundQuestion.objects.filter(
                round=self.round,
            ).count(),
            0,
        )

    def test_inactive_tournament_raises_validation_error(
        self,
    ):

        self.tournament.status = "draft"
        self.tournament.save()

        self.create_question(1)
        self.create_question(2)
        self.create_question(3)

        with self.assertRaises(
            ValidationError,
        ):

            RoundQuestionService.assign_questions(
                self.round,
            )

    def test_assigning_questions_twice_does_not_duplicate(
        self,
    ):

        self.create_question(1)
        self.create_question(2)
        self.create_question(3)

        RoundQuestionService.assign_questions(
            self.round,
        )

        with self.assertRaises(
            ValidationError,
        ):

            RoundQuestionService.assign_questions(
                self.round,
            )

        self.assertEqual(
            RoundQuestion.objects.filter(
                round=self.round,
            ).count(),
            3,
        )


    def test_exact_question_count_is_assigned(self):

        # Arrange
        self.round.question_count = 5
        self.round.save()

        for index in range(5):
            QuizQuestion.objects.create(
                category=self.category,
                question=f"Question {index}",
                option_a="A",
                option_b="B",
                option_c="C",
                option_d="D",
                correct_answer="A",
                difficulty="easy",
                is_active=True,
            )

        # Act
        result = RoundQuestionService.assign_questions(
            self.round,
        )

        # Assert
        self.assertEqual(
            len(result),
            5,
        )

        self.assertEqual(
            RoundQuestion.objects.filter(
                round=self.round,
            ).count(),
            5,
        )