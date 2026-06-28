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



class PerformanceAnalysisService:

    @staticmethod
    def generate(match):

        analyzers = [

            ScoreAnalyzer.analyze(match),

            BalanceAnalyzer.analyze(match),

            StarDependencyAnalyzer.analyze(match),

            AverageAnalyzer.analyze(match),
        ]

        summaries = []

        for analyzer in analyzers:

            if isinstance(analyzer, dict):

                summaries.append(
                    analyzer["summary"]
                )

            else:

                summaries.append(
                    analyzer
                )

        # MomentumAnalyzer با بقیه فرق دارد چون Match Analyzer است
        team1_momentum = (
            MomentumAnalyzer.analyze(
                match.team1
            )
        )

        team2_momentum = (
            MomentumAnalyzer.analyze(
                match.team2
            )
        )

        summaries.append(
            team1_momentum["summary"]
        )

        summaries.append(
            team2_momentum["summary"]
        )

        # ConsistencyAnalyzer هم یک Match Analyzer است
        team1_consistency = (
            ConsistencyAnalyzer.analyze(
                match.team1
            )
        )

        team2_consistency = (
            ConsistencyAnalyzer.analyze(
                match.team2
            )
        )

        summaries.append(
            team1_consistency["summary"]
        )

        summaries.append(
            team2_consistency["summary"]
        )

        return " ".join(summaries)