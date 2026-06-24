class TournamentRankingService:

    @staticmethod
    def ranking_key(
        team,
        tournament
    ):

        return (
            team.get_points_in_tournament(
                tournament
            ),

            team.get_score_difference_in_tournament(
                tournament
            ),

            -team.get_total_time_in_tournament(
                tournament
            ),
        )

    @staticmethod
    def rank_teams(tournament):

        teams = [
            tt.team
            for tt in tournament.teams.select_related(
                'team'
            )
        ]

        teams.sort(
            key=lambda team:
                TournamentRankingService.ranking_key(
                    team,
                    tournament
                ),
            reverse=True
        )

        return teams