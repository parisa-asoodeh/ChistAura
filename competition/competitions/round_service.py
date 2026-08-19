from django.db import transaction
from django.core.exceptions import ValidationError
from django.utils import timezone

from .models import Round


class RoundService:

    @staticmethod
    @transaction.atomic
    def create_round(
        tournament,
        subject,
        question_difficulty="easy",
        question_count=10,
        starts_at=None,
        ends_at=None,
    ):
        if tournament.status != "active":
            raise ValidationError(
                "فقط برای Tournament فعال می‌توان Round ایجاد کرد."
            )

        if not subject.is_active:
            raise ValidationError(
                "موضوع انتخاب‌شده فعال نیست."
            )

        if question_count <= 0:
            raise ValidationError(
                "تعداد سوالات باید بیشتر از صفر باشد."
            )

        if question_difficulty not in dict(
            Round.QUESTION_DIFFICULTY_CHOICES
        ):
            raise ValidationError(
                "درجه سختی سوالات نامعتبر است."
            )

        current_round_count = Round.objects.filter(
            tournament=tournament,
        ).count()

        if current_round_count >= tournament.total_rounds:
            raise ValidationError(
                "تعداد Roundهای Tournament به حد تعیین‌شده رسیده است."
            )

        last_round = (
            Round.objects
            .filter(tournament=tournament)
            .order_by("-number")
            .first()
        )

        number = (
            last_round.number + 1
            if last_round
            else 1
        )

        return Round.objects.create(
            tournament=tournament,
            number=number,
            subject=subject,
            question_difficulty=question_difficulty,
            question_count=question_count,
            starts_at=starts_at,
            ends_at=ends_at,
        )

    @staticmethod
    @transaction.atomic
    def start_round(round_obj):
        round_obj = (
            Round.objects
            .select_for_update()
            .select_related("tournament")
            .get(pk=round_obj.pk)
        )

        if round_obj.status != "scheduled":
            raise ValidationError(
                "فقط Round زمان‌بندی‌شده را می‌توان شروع کرد."
            )

        tournament = round_obj.tournament

        if tournament.status != "active":
            raise ValidationError(
                "Tournament باید فعال باشد."
            )
        if (
            round_obj.starts_at is not None
            and timezone.now() < round_obj.starts_at
        ):
            raise ValidationError(
                "زمان شروع Round هنوز نرسیده است."
            )

        previous_round = (
            Round.objects
            .filter(
                tournament=tournament,
                number__lt=round_obj.number,
            )
            .order_by("-number")
            .first()
        )

        if previous_round and previous_round.status != "finished":
            raise ValidationError(
                "تا پایان Round قبلی امکان شروع این Round وجود ندارد."
            )

        round_obj.status = "active"

        round_obj.save(
            update_fields=[
                "status",
            ]
        )

        return round_obj



    @staticmethod
    @transaction.atomic
    def finish_round(round_obj):
        round_obj = (
            Round.objects
            .select_for_update()
            .select_related("tournament")
            .get(pk=round_obj.pk)
        )

        if round_obj.status != "active":
            raise ValidationError(
                "فقط Round فعال را می‌توان به پایان رساند."
            )

        # ---------------------------------------------------------
        # همه Matchهای این Round باید کامل شده باشند.
        # ---------------------------------------------------------

        unfinished_matches = (
            round_obj.matches
            .filter(
                status__in=["pending", "active"],
            )
            .exists()
        )

        if unfinished_matches:
            raise ValidationError(
                "تا پایان تمام Matchهای این Round، "
                "امکان پایان دادن به Round وجود ندارد."
            )

        # ---------------------------------------------------------
        # پایان Round
        # ---------------------------------------------------------

        round_obj.status = "finished"
        round_obj.ends_at = timezone.now()

        round_obj.save(
            update_fields=[
                "status",
                "ends_at",
            ]
        )

        return round_obj