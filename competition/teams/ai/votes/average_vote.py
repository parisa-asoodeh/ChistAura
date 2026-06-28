from teams.ai.analyzers.average_analyzer import (
    AverageAnalyzer,
)


class AverageVote:

    @staticmethod
    def vote(team1, team2):

        team1_result = AverageAnalyzer.analyze(
            team1
        )

        team2_result = AverageAnalyzer.analyze(
            team2
        )

        team1_average = team1_result["average"]

        team2_average = team2_result["average"]