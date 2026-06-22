from django.utils import timezone

from .models import Tournament

from .ranking_service import (
    TournamentRankingService
)


class TournamentStatusService:

    @staticmethod
    def refresh_tournament(tournament):

        unfinished_matches = tournament.matches.filter(
            score_team1__isnull=True
        ).exists()

        # هنوز مسابقه ناتمام داریم
        if unfinished_matches:

            if tournament.status == 'finished':

                tournament.status = 'active'
                tournament.finished_at = None
                tournament.champion = None

                tournament.save(
                    update_fields=[
                        'status',
                        'finished_at',
                        'champion',
                    ]
                )

            return tournament

        teams = TournamentRankingService.rank_teams(
            tournament
        )

        champion = None

        if teams:
            champion = teams[0]

        tournament.status = 'finished'
        tournament.finished_at = timezone.now()
        tournament.champion = champion

        tournament.save(
            update_fields=[
                'status',
                'finished_at',
                'champion',
            ]
        )

        return tournament