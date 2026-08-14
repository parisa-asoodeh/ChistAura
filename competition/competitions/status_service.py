from django.utils import timezone

from .models import Tournament

from .ranking_service import (
    TournamentRankingService,
)


class TournamentStatusService:

    @staticmethod
    def refresh_tournament(tournament):

        rounds = tournament.rounds.all()

        # هنوز به تعداد کل Roundها نرسیده‌ایم.
        if rounds.count() < tournament.total_rounds:
            return tournament

        # حداقل یک Round هنوز تمام نشده است.
        if rounds.exclude(
            status="finished"
        ).exists():
            return tournament

        # حداقل یک Match ناتمام وجود دارد.
        if rounds.filter(
            matches__score_team1__isnull=True,
        ).exists() or rounds.filter(
            matches__score_team2__isnull=True,
        ).exists():
            return tournament

        # همه Roundها و Matchها تمام شده‌اند.
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