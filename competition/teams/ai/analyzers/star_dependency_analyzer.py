from games.models import MatchPlayerScore


class StarDependencyAnalyzer:

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

        result = (
            StarDependencyAnalyzer.dependency_percentage(
                scores
            )
        )

        result["summary"] = (
            StarDependencyAnalyzer.build_summary(
                team,
                result,
            )
        )

        return result

    @staticmethod
    def dependency_percentage(scores):

        if not scores:

            return {
                "total": 0,
                "top_score": 0,
                "percentage": 0,
            }

        total = sum(scores)

        if total == 0:

            return {
                "total": 0,
                "top_score": 0,
                "percentage": 0,
            }

        top_score = max(scores)

        percentage = (
            top_score / total
        ) * 100

        return {
            "total": total,
            "top_score": top_score,
            "percentage": percentage,
        }

    @staticmethod
    def build_summary(
        team,
        result,
    ):

        percentage = result["percentage"]

        if percentage < 40:

            return (
                f"امتیازگیری اعضای تیم "
                f"{team.name} "
                f"متعادل بوده و وابستگی "
                f"زیادی به یک بازیکن وجود ندارد."
            )

        if percentage < 60:

            return (
                f"بهترین بازیکن تیم "
                f"{team.name} "
                f"{percentage:.0f}٪ "
                f"از امتیازات تیم را "
                f"کسب کرده است."
            )

        return (
            f"بیش از "
            f"{percentage:.0f}٪ "
            f"از امتیازات تیم "
            f"{team.name} "
            f"توسط یک بازیکن کسب شده و "
            f"تیم وابستگی زیادی به او دارد."
        )