class TournamentRankingService:

    @staticmethod
    def rank_teams(tournament):

        teams = [
            tt.team
            for tt in tournament.teams.select_related(
                'team'
            )
        ]

        teams.sort(
            key=lambda team: team.get_points_in_tournament(
                tournament
            ),
            reverse=True
        )

        return teams