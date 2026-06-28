from teams.analysis.team_analysis_service import (
    TeamAnalysisService
)


class MatchDifficultyAnalyzer:

    @staticmethod
    def analyze(team):

        differences = (
            TeamAnalysisService.get_recent_score_differences(
                team
            )
        )

        if not differences:

            return {
                "difficulty": "unknown",
                "average_difference": 0,
                "summary":
                    "داده کافی برای تحلیل سختی مسابقات وجود ندارد."
            }

        average_difference = (
            sum(differences)
            / len(differences)
        )

        if average_difference <= 10:

            difficulty = "hard"

        elif average_difference <= 30:

            difficulty = "medium"

        else:

            difficulty = "easy"

        return {

            "difficulty": difficulty,

            "average_difference": round(
                average_difference,
                1
            ),

            "summary":
                MatchDifficultyAnalyzer.build_summary(
                    team,
                    difficulty,
                ),
        }

    @staticmethod
    def build_summary(
        team,
        difficulty,
    ):

        if difficulty == "hard":

            return (
                f"مسابقات اخیر {team.name} "
                f"بسیار رقابتی بوده‌اند."
            )

        if difficulty == "medium":

            return (
                f"مسابقات اخیر {team.name} "
                f"از نظر سختی در سطح متوسط بوده‌اند."
            )

        return (
            f"مسابقات اخیر {team.name} "
            f"نسبتاً آسان بوده‌اند."
        )