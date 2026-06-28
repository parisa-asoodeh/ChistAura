from teams.ai.analyzers.consistency_analyzer import (
    ConsistencyAnalyzer,
)


class ConsistencyVote:

    @staticmethod
    def vote(
        team1,
        team2,
    ):

        team1_result = (
            ConsistencyAnalyzer.analyze(
                team1
            )
        )

        team2_result = (
            ConsistencyAnalyzer.analyze(
                team2
            )
        )

        team1_consistency = (
            team1_result["consistency"]
        )

        team2_consistency = (
            team2_result["consistency"]
        )

        if team1_consistency == team2_consistency:

            vote = None

        elif team1_consistency == "high":

            vote = team1

        elif team2_consistency == "high":

            vote = team2

        elif team1_consistency == "medium":

            vote = team1

        else:

            vote = team2

        confidence = abs(
            team1_result["variation"] -
            team2_result["variation"]
        )

        if vote == team1:

            reason = (
                f"ثبات عملکرد "
                f"{team1.name} "
                f"بیشتر است."
            )

        elif vote == team2:

            reason = (
                f"ثبات عملکرد "
                f"{team2.name} "
                f"بیشتر است."
            )

        else:

            reason = (
                "ثبات عملکرد دو تیم مشابه است."
            )

        return {

            "analyzer": "ConsistencyVote",

            "vote": vote,

            "confidence": confidence,

            "reason": reason,
        }
        