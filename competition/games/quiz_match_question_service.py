from django.core.exceptions import ValidationError
from django.db import transaction

from competitions.models import RoundQuestion

from .quiz_models import QuizMatchQuestion


class QuizMatchQuestionService:

    @staticmethod
    @transaction.atomic
    def create_questions_for_match(*, match):

        if match.round_id is None:
            raise ValidationError(
                "Match باید به یک Round مربوط باشد."
            )

        if QuizMatchQuestion.objects.filter(
            match=match
        ).exists():
            raise ValidationError(
                "برای این Match قبلاً سؤال ایجاد شده است."
            )

        round_questions = RoundQuestion.objects.filter(
            round=match.round
        ).order_by(
            "order"
        )

        if not round_questions.exists():
            raise ValidationError(
                "برای این Round هیچ سؤالی انتخاب نشده است."
            )

        match_questions = [
            QuizMatchQuestion(
                match=match,
                round_question=round_question,
                order=round_question.order,
            )
            for round_question in round_questions
        ]

        return QuizMatchQuestion.objects.bulk_create(
            match_questions
        )