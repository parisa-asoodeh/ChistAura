from games.models import MatchPlayerScore


class AverageAnalyzer:

    @staticmethod
    def analyze(team):
        scores = list(
            MatchPlayerScore.objects.filter(
                team=team
            ).values_list(
                "score",
                flat=True
            )
        )

        result = AverageAnalyzer.average(
            scores
        )

        result["summary"] = (
            AverageAnalyzer.build_summary(
                team,
                result
            )
        )

        return result


        

    @staticmethod
    def average(scores):

        if not scores:

            return {
                "total": 0,
                "players": 0,
                "average": 0,
            }

        total = sum(scores)

        players = len(scores)

        average = total / players

        return {
            "total": total,
            "players": players,
            "average": average,
        }
    

    @staticmethod
    def build_summary(
        team,
        result,
    ):

        average = result["average"]

        return (
            f"میانگین امتیاز اعضای "
            f"{team.name} "
            f"({average:.1f}) "
            f"است."
        )