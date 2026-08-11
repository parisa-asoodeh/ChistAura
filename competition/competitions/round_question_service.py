from django.core.exceptions import ValidationError
from django.db import transaction

from games.models import QuizQuestion

from .models import RoundQuestion


class RoundQuestionService:

    @staticmethod
    @transaction.atomic
    def assign_questions(round_obj):

        if round_obj.status != "scheduled":
            raise ValidationError(
                "فقط برای Round زمان‌بندی‌شده می‌توان سؤال انتخاب کرد."
            )

        tournament = round_obj.tournament

        if tournament.status != "active":
            raise ValidationError(
                "Tournament باید فعال باشد."
            )

        if RoundQuestion.objects.filter(
            round=round_obj,
        ).exists():
            raise ValidationError(
                "برای این Round قبلاً سؤال انتخاب شده است."
            )

        used_question_ids = RoundQuestion.objects.filter(
            round__tournament=tournament,
        ).values_list(
            "question_id",
            flat=True,
        )

        questions = QuizQuestion.objects.filter(
            category__subject=round_obj.subject,
            difficulty=round_obj.question_difficulty,
            is_active=True,
        ).exclude(
            id__in=used_question_ids,
        ).order_by(
            "id",
        )

        if questions.count() < round_obj.question_count:
            raise ValidationError(
                "تعداد سؤال‌های مناسب برای این Round کافی نیست."
            )

        selected_questions = list(
            questions[:round_obj.question_count]
        )

        round_questions = [
            RoundQuestion(
                round=round_obj,
                question=question,
                order=index,
            )
            for index, question in enumerate(
                selected_questions,
                start=1,
            )
        ]

        RoundQuestion.objects.bulk_create(
            round_questions,
        )

        return round_questions