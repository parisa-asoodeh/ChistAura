from django.utils import timezone

from .models import Tournament

from .ranking_service import (
    TournamentRankingService,
)


class TournamentStatusService:

    @staticmethod
    def refresh_tournament(tournament):

        rounds = tournament.rounds.all()

        if rounds.count() < tournament.total_rounds:
            return tournament

        if rounds.exclude(
            status="finished"
        ).exists():
            return tournament

        if rounds.filter(
            matches__status__in=["pending", "active"],
        ).exists():
            return tournament

        teams = TournamentRankingService.rank_teams(
            tournament,
        )

        champion = teams[0] if teams else None

        tournament.status = "finished"
        tournament.finished_at = timezone.now()
        tournament.champion = champion

        tournament.save(
            update_fields=[
                "status",
                "finished_at",
                "champion",
            ]
        )

        return tournament