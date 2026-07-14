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
from .providers.performance_data_provider import (
    PerformanceDataProvider,
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

        team1_context = PerformanceDataProvider.get_team_context(
            match.tournament,
            match.team1,
        )
        
        team2_context = PerformanceDataProvider.get_team_context(
            match.tournament,
            match.team2,
        )

        for analyzer in team_analyzers:

            team1_result = analyzer.analyze(team1_context)
            team2_result = analyzer.analyze(team2_context)


            summaries.append(
                team1_result["summary"]
            )

            summaries.append(
                team2_result["summary"]
            )

        return " ".join(summaries)