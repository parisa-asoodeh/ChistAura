from teams.ai.analyzers.star_dependency_analyzer import (
    StarDependencyAnalyzer,
)


class StarDependencyVote:

    @staticmethod
    def vote(
        team1,
        team2,
    ):

        team1_result = (
            StarDependencyAnalyzer.analyze(
                team1
            )
        )

        team2_result = (
            StarDependencyAnalyzer.analyze(
                team2
            )
        )

        team1_percentage = (
            team1_result["percentage"]
        )

        team2_percentage = (
            team2_result["percentage"]
        )

        if team1_percentage == team2_percentage:

            vote = None

        elif team1_percentage < team2_percentage:

            vote = team1

        else:

            vote = team2

        confidence = abs(
            team1_percentage -
            team2_percentage
        )

        if vote == team1:

            reason = (
                f"{team1.name} "
                f"وابستگی کمتری به یک بازیکن دارد."
            )

        elif vote == team2:

            reason = (
                f"{team2.name} "
                f"وابستگی کمتری به یک بازیکن دارد."
            )

        else:

            reason = (
                "هر دو تیم وابستگی مشابهی به بهترین بازیکن خود دارند."
            )

        return {

            "analyzer": "StarDependencyVote",

            "vote": vote,

            "confidence": confidence,

            "reason": reason,
        }