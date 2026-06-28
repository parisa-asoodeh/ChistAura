from games.models import Match
from teams.models import TeamMembership


class TeamAnalysisService:

    @staticmethod
    def build_team_summary(team):

        return {
            "members": TeamMembership.objects.filter(team=team),
            "wins": team.get_wins(),
            "draws": team.get_draws(),
            "losses": team.get_losses(),
            "played": team.get_played(),
            "points": team.get_points(),
            "form": TeamAnalysisService.get_team_form(team),
        }
    

    @staticmethod
    def get_team_form(team, limit=5):

        matches = (
            Match.objects.filter(team1=team)
            |
            Match.objects.filter(team2=team)
        ).order_by("-played_at")

        form = []

        for match in matches:

            if not match.is_complete:
                continue

            if match.winner == team:
                form.append("برد")

            elif match.winner is None:
                form.append("مساوی")

            else:
                form.append("باخت")

            if len(form) == limit:
                break

        return list(reversed(form))
    

    @staticmethod
    def get_recent_scores(
        team,
        limit=5,
    ):

        matches = (
            Match.objects.filter(
                winner__isnull=False
            )
            .filter(
                team1=team
            ) |
            Match.objects.filter(
                winner__isnull=False
            )
            .filter(
                team2=team
            )
        )

        matches = (
            matches
            .order_by("-played_at")[:limit]
        )

        scores = []

        for match in reversed(matches):

            if match.team1 == team:

                scores.append(
                    match.score_team1
                )

            else:

                scores.append(
                    match.score_team2
                )

        return scores