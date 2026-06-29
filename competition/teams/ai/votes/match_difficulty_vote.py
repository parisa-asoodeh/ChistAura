from teams.ai.analyzers.match_difficulty_analyzer import (
    MatchDifficultyAnalyzer,
)


class MatchDifficultyVote:

    @staticmethod
    def vote(
        team1_context,
        team2_context,
    ):

        team1 = team1_context["team"]
        team2 = team2_context["team"]

        team1_result = MatchDifficultyAnalyzer.analyze(
            team1_context,
        )

        team2_result = MatchDifficultyAnalyzer.analyze(
            team2_context,
        )

        team1_difficulty = (
            team1_result["difficulty"]
        )

        team2_difficulty = (
            team2_result["difficulty"]
        )

        if team1_difficulty == team2_difficulty:

            vote = None

        elif team1_difficulty == "hard":

            vote = team1

        elif team2_difficulty == "hard":

            vote = team2

        elif team1_difficulty == "medium":

            vote = team1

        else:

            vote = team2

        confidence = abs(
            team1_result["average_difference"] -
            team2_result["average_difference"]
        )

        if vote == team1:

            reason = (
                f"{team1.name} "
                f"در مسابقات سخت‌تری عملکرد خود را حفظ کرده است."
            )

        elif vote == team2:

            reason = (
                f"{team2.name} "
                f"در مسابقات سخت‌تری عملکرد خود را حفظ کرده است."
            )

        else:

            reason = (
                "سطح سختی مسابقات اخیر دو تیم مشابه است."
            )

        return {

            "analyzer": "MatchDifficultyVote",

            "vote": vote,

            "confidence": confidence,

            "reason": reason,
        }