from games.models import MatchPlayerScore


class AverageAnalyzer:

    @staticmethod
    def analyze(match):

        team1_scores = list(
            MatchPlayerScore.objects.filter(
                match=match,
                team=match.team1
            ).values_list(
                "score",
                flat=True
            )
        )

        team2_scores = list(
            MatchPlayerScore.objects.filter(
                match=match,
                team=match.team2
            ).values_list(
                "score",
                flat=True
            )
        )

        team1_average = (
            AverageAnalyzer.average(
                team1_scores
            )
        )

        team2_average = (
            AverageAnalyzer.average(
                team2_scores
            )
        )

        return {
            "team1": team1_average,
            "team2": team2_average,
            "summary": AverageAnalyzer.build_summary(
                match,
                team1_average,
                team2_average,
            ),
        }

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
        match,
        team1_average,
        team2_average,
    ):

        avg1 = team1_average["average"]

        avg2 = team2_average["average"]

        if avg1 > avg2:

            return (
                f"میانگین امتیاز اعضای "
                f"{match.team1.name} "
                f"({avg1:.1f}) "
                f"بالاتر از "
                f"{match.team2.name} "
                f"({avg2:.1f}) "
                f"بود."
            )

        if avg2 > avg1:

            return (
                f"میانگین امتیاز اعضای "
                f"{match.team2.name} "
                f"({avg2:.1f}) "
                f"بالاتر از "
                f"{match.team1.name} "
                f"({avg1:.1f}) "
                f"بود."
            )

        return (
            "میانگین امتیاز اعضای "
            "دو تیم برابر بود."
        )