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

        return " ".join(summaries)