from .best_player_service import BestPlayerService
from .performance_analysis_service import (
    PerformanceAnalysisService
)


class MatchReportService:

    @staticmethod
    def generate(match):

        best_player = BestPlayerService.get_best_player(match)

        return {
            "winner": match.winner,
            "team1": match.team1,
            "team2": match.team2,
            "score1": match.score_team1,
            "score2": match.score_team2,
            "best_player": best_player,
            "summary": MatchReportService.build_summary(
                match,
                best_player,
            ),
        }

    @staticmethod
    def build_summary(match, best_player):

        if match.winner is None:

            summary = (
                f"دیدار {match.team1.name} و "
                f"{match.team2.name} "
                f"با نتیجه {match.score_team1} - {match.score_team2} "
                f"به تساوی رسید."
            )

        else:

            if match.winner == match.team1:
                winner = match.team1
                loser = match.team2
                winner_score = match.score_team1
                loser_score = match.score_team2
            else:
                winner = match.team2
                loser = match.team1
                winner_score = match.score_team2
                loser_score = match.score_team1

            summary = (
                f"{winner.name} "
                f"با نتیجه "
                f"{winner_score} - {loser_score} "
                f"مقابل {loser.name} "
                f"به پیروزی رسید."
            )

        player_text = ""

        if best_player:

            player_text = (
                f" بهترین بازیکن مسابقه "
                f"{best_player.user.username} "
                f"بود که "
                f"{best_player.score} "
                f"امتیاز "
                f"را در "
                f"{best_player.completion_time} "
                f"ثانیه کسب کرد."
            )

        analysis_text = (
            " "
            + PerformanceAnalysisService.generate(match)
        )

        return (
            summary
            + player_text
            + analysis_text
        )