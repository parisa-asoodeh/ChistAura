from teams.analysis.team_analysis_service import (
    TeamAnalysisService
)


class MomentumAnalyzer:

    @staticmethod
    def analyze(team):

        scores = (
            TeamAnalysisService.get_recent_scores(
                team
            )
        )

        if not scores:

            return {
                "scores": [],
                "change": 0,
                "trend": "stable",
                "summary": (
                    "داده کافی برای تحلیل روند وجود ندارد."
                ),
            }

        first_score = scores[0]

        last_score = scores[-1]

        change = last_score - first_score

        if change > 10:

            trend = "up"

        elif change < -10:

            trend = "down"

        else:

            trend = "stable"

        return {
            "scores": scores,
            "change": change,
            "trend": trend,
            "summary": MomentumAnalyzer.build_summary(
                team,
                trend,
                change,
            ),
        }

    @staticmethod
    def build_summary(
        team,
        trend,
        change,
    ):

        if trend == "up":

            return (
                f"روند عملکرد {team.name} "
                f"در مسابقات اخیر صعودی بوده است."
            )

        if trend == "down":

            return (
                f"روند عملکرد {team.name} "
                f"در مسابقات اخیر نزولی بوده است."
            )

        return (
            f"عملکرد {team.name} "
            f"در مسابقات اخیر تقریباً ثابت بوده است."
        )