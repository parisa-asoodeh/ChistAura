from django.db.models import Sum
from games.models import MatchPlayerScore


class TeamStatisticsService:

    @staticmethod
    def get_matches(team):
        return team.home_matches.all() | team.away_matches.all()

    @staticmethod
    def get_wins(team):
        return sum(
            1
            for match in team.won_matches.all()
            if match.is_complete
        )

    @staticmethod
    def get_draws(team):
        return sum(
            1
            for match in TeamStatisticsService.get_matches(team)
            if (
                match.is_complete
                and
                match.winner is None
            )
        )

    @staticmethod
    def get_played(team):
        return sum(
            1
            for match in TeamStatisticsService.get_matches(team)
            if match.is_complete
        )

    @staticmethod
    def get_losses(team):
        return (
            TeamStatisticsService.get_played(team)
            - TeamStatisticsService.get_wins(team)
            - TeamStatisticsService.get_draws(team)
        )

    @staticmethod
    def get_points(team):
        return (
            TeamStatisticsService.get_wins(team) * 3
            + TeamStatisticsService.get_draws(team)
        )
    

    @staticmethod
    def get_matches_in_tournament(team, tournament):
        return (
            team.home_matches.filter(tournament=tournament)
            |
            team.away_matches.filter(tournament=tournament)
        )

    @staticmethod
    def get_wins_in_tournament(team, tournament):
        return sum(
            1
            for match in team.won_matches.filter(
                tournament=tournament
            )
            if match.is_complete
        )

    @staticmethod
    def get_draws_in_tournament(team, tournament):
        return sum(
            1
            for match in TeamStatisticsService.get_matches_in_tournament(
                team,
                tournament
            )
            if match.is_complete and match.winner is None
        )

    @staticmethod
    def get_played_in_tournament(team, tournament):
        return sum(
            1
            for match in TeamStatisticsService.get_matches_in_tournament(
                team,
                tournament
            )
            if match.is_complete
        )

    @staticmethod
    def get_losses_in_tournament(team, tournament):
        return (
            TeamStatisticsService.get_played_in_tournament(team, tournament)
            - TeamStatisticsService.get_wins_in_tournament(team, tournament)
            - TeamStatisticsService.get_draws_in_tournament(team, tournament)
        )

    @staticmethod
    def get_points_in_tournament(team, tournament):
        return (
            TeamStatisticsService.get_wins_in_tournament(team, tournament) * 3
            + TeamStatisticsService.get_draws_in_tournament(team, tournament)
        )

    @staticmethod
    def get_score_difference_in_tournament(team, tournament):
        difference = 0

        matches = TeamStatisticsService.get_matches_in_tournament(
            team,
            tournament
        )

        for match in matches:

            if not match.is_complete:
                continue

            if match.team1 == team:
                difference += (
                    match.score_team1
                    - match.score_team2
                )
            else:
                difference += (
                    match.score_team2
                    - match.score_team1
                )

        return difference

    @staticmethod
    def get_total_time_in_tournament(team, tournament):

        total = (
            MatchPlayerScore.objects.filter(
                match__tournament=tournament,
                team=team,
                completion_time__isnull=False,
            ).aggregate(
                total=Sum("completion_time")
            )["total"]
        )

        return total or 0