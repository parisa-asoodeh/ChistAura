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

        QuizQuestion.objects.create(
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

        self.assertEqual(
            questions[0],
            matching_question,
        )