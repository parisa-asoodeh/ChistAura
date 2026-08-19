from django.core.management.base import BaseCommand
from django.utils import timezone

from competitions.models import Round
from competitions.tournament_execution_service import (
    TournamentExecutionService,
)
from django.core.exceptions import ValidationError


class Command(BaseCommand):

    help = "Start scheduled rounds whose start time has arrived."

    def handle(self, *args, **options):

        rounds = (
            Round.objects
            .filter(status="scheduled")
            .order_by("starts_at")
        )

        started_count = 0

        for round_obj in rounds:

            if (
                round_obj.starts_at is not None
                and timezone.now() < round_obj.starts_at
            ):
                continue

            try:
                TournamentExecutionService.start_scheduled_round(
                    round_obj,
                )

                started_count += 1

            except ValidationError:
                continue

        self.stdout.write(
            self.style.SUCCESS(
                f"{started_count} scheduled round(s) started."
            )
        )