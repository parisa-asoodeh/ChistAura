from django.test import TestCase

from competitions.models import Subject, Category
from games.question_selection_service import QuestionSelectionService
from games.quiz_models import QuizQuestion


class QuestionSelectionServiceTest(TestCase):

    def test_select_questions_returns_only_matching_questions(self):

        subject = Subject.objects.create(
            name="Chemistry",
            slug="chemistry",
        )

        category = Category.objects.create(
            subject=subject,
            name="Periodic Table",
            slug="periodic-table",
        )

        matching_question = QuizQuestion.objects.create(
            category=category,
            question="Hydrogen symbol?",
            option_a="H",
            option_b="He",
            option_c="Li",
            option_d="O",
            correct_answer="A",
            difficulty="easy",
            is_active=True,
        )

        wrong_difficulty_question = QuizQuestion.objects.create(
            category=category,
            question="Hard question",
            option_a="A",
            option_b="B",
            option_c="C",
            option_d="D",
            correct_answer="A",
            difficulty="hard",
            is_active=True,
        )

        questions = QuestionSelectionService.select_questions(
            category=category,
            difficulty="easy",
            count=10,
        )

        self.assertEqual(
            questions.count(),
            1,
        )

        self.assertIn(
            matching_question,
            questions,
        )

        self.assertNotIn(
            wrong_difficulty_question,
            questions,
        )


    def test_select_questions_returns_requested_count_randomly(self):

        subject = Subject.objects.create(
            name="Math",
            slug="math",
        )

        category = Category.objects.create(
            subject=subject,
            name="Algebra",
            slug="algebra",
        )

        for index in range(5):
            QuizQuestion.objects.create(
                category=category,
                question=f"Question {index}",
                option_a="A",
                option_b="B",
                option_c="C",
                option_d="D",
                correct_answer="A",
                difficulty="easy",
                is_active=True,
            )

        questions = QuestionSelectionService.select_questions(
            category=category,
            difficulty="easy",
            count=3,
        )

        self.assertEqual(
            questions.count(),
            3,
        )

        for question in questions:
            self.assertEqual(
                question.category,
                category,
            )

            self.assertEqual(
                question.difficulty,
                "easy",
            )