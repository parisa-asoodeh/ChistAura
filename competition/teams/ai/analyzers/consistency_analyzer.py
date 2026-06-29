from teams.analysis.team_analysis_service import (
    TeamAnalysisService
)


class ConsistencyAnalyzer:

    @staticmethod
    def analyze(team_context):

        team = team_context["team"]

        scores = (
            TeamAnalysisService.get_recent_scores_from_context(
                team_context
            )
        )

        if not scores:

            return {
                "scores": [],
                "variation": 0,
                "consistency": "unknown",
                "summary": (
                    "داده کافی برای تحلیل ثبات عملکرد وجود ندارد."
                ),
            }

        variation = (
            max(scores) - min(scores)
        )

        if variation <= 10:

            consistency = "high"

        elif variation <= 30:

            consistency = "medium"

        else:

            consistency = "low"

        return {
            "scores": scores,
            "variation": variation,
            "consistency": consistency,
            "summary": ConsistencyAnalyzer.build_summary(
                team,
                consistency,
            ),
        }

    @staticmethod
    def build_summary(
        team,
        consistency,
    ):

        if consistency == "high":

            return (
                f"عملکرد {team.name} "
                f"در مسابقات اخیر بسیار باثبات بوده است."
            )

        if consistency == "medium":

            return (
                f"عملکرد {team.name} "
                f"در مسابقات اخیر ثبات قابل قبولی داشته است."
            )

        return (
            f"عملکرد {team.name} "
            f"در مسابقات اخیر نوسان زیادی داشته است."
        )