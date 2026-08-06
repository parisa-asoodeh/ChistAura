from django.test import TestCase

from competitions.models import Subject, Category
from games.quiz_models import QuizQuestion


class QuizQuestionModelTest(TestCase):

    def test_quiz_question_belongs_to_category_and_subject(self):

        subject = Subject.objects.create(
            name="Chemistry",
            slug="chemistry",
        )

        category = Category.objects.create(
            subject=subject,
            name="Periodic Table",
            slug="periodic-table",
        )

        question = QuizQuestion.objects.create(
            category=category,
            question="Symbol of Hydrogen?",
            option_a="H",
            option_b="He",
            option_c="O",
            option_d="C",
            correct_answer="A",
            difficulty="easy",
        )

        self.assertEqual(
            question.category,
            category
        )

        self.assertEqual(
            question.category.subject,
            subject
        )