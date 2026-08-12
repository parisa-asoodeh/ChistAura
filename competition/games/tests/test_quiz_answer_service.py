from types import SimpleNamespace
from unittest.mock import patch

from django.test import SimpleTestCase

from games.quiz_answer_service import QuizAnswerService


class QuizAnswerServiceTest(SimpleTestCase):

    @patch("games.quiz_answer_service.QuizAnswer.objects.create")
    def test_save_answers_creates_answer_for_each_question(
        self,
        mock_create,
    ):
        session = SimpleNamespace(id=1)

        question1 = SimpleNamespace(id=10)
        question2 = SimpleNamespace(id=20)

        questions = [
            question1,
            question2,
        ]

        form = SimpleNamespace(
            cleaned_data={
                "question_10": "A",
                "question_20": "C",
            }
        )

        QuizAnswerService.save_answers(
            session=session,
            form=form,
            questions=questions,
        )

        self.assertEqual(
            mock_create.call_count,
            2,
        )

        mock_create.assert_any_call(
            session=session,
            match_question=question1,
            selected_answer="A",
        )

        mock_create.assert_any_call(
            session=session,
            match_question=question2,
            selected_answer="C",
        )

    @patch("games.quiz_answer_service.QuizAnswer.objects.create")
    def test_save_answers_uses_correct_form_key(
        self,
        mock_create,
    ):
        session = SimpleNamespace(id=1)

        question = SimpleNamespace(id=15)

        form = SimpleNamespace(
            cleaned_data={
                "question_15": "B",
            }
        )

        QuizAnswerService.save_answers(
            session=session,
            form=form,
            questions=[question],
        )

        mock_create.assert_called_once_with(
            session=session,
            match_question=question,
            selected_answer="B",
        )