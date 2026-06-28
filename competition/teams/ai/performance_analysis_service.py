from .analyzers.score_analyzer import (
    ScoreAnalyzer,
)

from .analyzers.balance_analyzer import (
    BalanceAnalyzer,
)
from .analyzers.star_dependency_analyzer import (
    StarDependencyAnalyzer
)
from .analyzers.average_analyzer import (
    AverageAnalyzer
)
from .analyzers.momentum_analyzer import (
    MomentumAnalyzer
)
from .analyzers.consistency_analyzer import (
    ConsistencyAnalyzer
)
from .analyzers.match_difficulty_analyzer import (
    MatchDifficultyAnalyzer
)



class PerformanceAnalysisService:

    @staticmethod
    def generate(match):

        match_analyzers = [

            ScoreAnalyzer.analyze(match),

            BalanceAnalyzer.analyze(match),
        ]

        summaries = []

        for analyzer in match_analyzers:

            if isinstance(analyzer, dict):

                summaries.append(
                    analyzer["summary"]
                )

            else:

                summaries.append(
                    analyzer
                )


        team_analyzers = [

            AverageAnalyzer,

            MomentumAnalyzer,

            ConsistencyAnalyzer,

            MatchDifficultyAnalyzer,
            
            StarDependencyAnalyzer,
        ]

        for analyzer in team_analyzers:

            team1_result = analyzer.analyze(
                match.team1
            )

            team2_result = analyzer.analyze(
                match.team2
            )

            summaries.append(
                team1_result["summary"]
            )

            summaries.append(
                team2_result["summary"]
            )

        return " ".join(summaries)