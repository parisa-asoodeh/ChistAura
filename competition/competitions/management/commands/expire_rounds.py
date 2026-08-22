from django.core.management.base import BaseCommand

from competitions.models import Round
from competitions.tournament_execution_service import (
    TournamentExecutionService,
)
from django.utils import timezone


class Command(BaseCommand):

    help = "پردازش Roundهای منقضی‌شده"

    def handle(self, *args, **options):

        now = timezone.now()

        expired_rounds = (
            Round.objects
            .filter(
                status="active",
                ends_at__isnull=False,
                ends_at__lte=now,
            )
        )

        count = 0

        for round_obj in expired_rounds:

            TournamentExecutionService.expire_round(
                round_obj,
            )

            count += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"{count} Round منقضی‌شده پردازش شد."
            )
        )