from django.db.models.signals import (
    post_save,
    post_delete,
)

from django.dispatch import receiver

from .models import MatchPlayerScore
from .scoring import MatchScoringService

from competitions.status_service import (
    TournamentStatusService
)


@receiver(
    post_save,
    sender=MatchPlayerScore
)
def recalculate_after_save(
    sender,
    instance,
    **kwargs
):

    MatchScoringService.recalculate_match(
        instance.match
    )

    TournamentStatusService.refresh_tournament(
        instance.match.tournament
    )


@receiver(
    post_delete,
    sender=MatchPlayerScore
)
def recalculate_after_delete(
    sender,
    instance,
    **kwargs
):

    MatchScoringService.recalculate_match(
        instance.match
    )

    TournamentStatusService.refresh_tournament(
        instance.match.tournament
    )