from games.models import (
    Match,
    MatchPlayerScore,
)


class PerformanceDataProvider:

    @staticmethod
    def get_team_context(
        tournament,
        team,
    ):

        matches = list(

            Match.objects.filter(
                round__tournament=tournament,
            ).filter(
                team1=team,
            )

            |

            Match.objects.filter(
                round__tournament=tournament,
                team2=team,
            )

        )


        scores = list(

            MatchPlayerScore.objects.filter(
                match__in=matches,
                team=team,
            ).values_list(
                "score",
                flat=True,
            )

        )


        history = PerformanceDataProvider.get_history(
            team,
            tournament,
        )

        mode = (
            "history"
            if len(matches) == 0
            else "current"
        )

        return {

            "team": team,

            "matches": list(matches),

            "scores": (
                scores
                if scores
                else history
            ),

            "history": history,

            "mode": mode,
        }
    

    @staticmethod
    def get_history(
        team,
        tournament,
    ):

        return list(

            MatchPlayerScore.objects.filter(
                team=team,
            ).exclude(
                match__round__tournament=tournament,
            ).values_list(
                "score",
                flat=True,
            )

        )