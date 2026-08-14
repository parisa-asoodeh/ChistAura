from django.db.models import Sum

from .models import MatchPlayerScore
from teams.models import TeamMembership
from .game_types.registry import get_game_type
from .player_score_service import PlayerScoreService


class MatchScoringService:

    @staticmethod
    def recalculate_match(match):
        """
        محاسبه مجدد نتیجه Match بر اساس امتیاز بازیکنان.

        این سرویس فقط مسئول Match است و:
        - امتیاز دو تیم را محاسبه می‌کند.
        - کامل بودن Match را بررسی می‌کند.
        - برنده را تعیین می‌کند.
        - وضعیت Round یا Tournament را تغییر نمی‌دهد.
        """

        if not MatchScoringService.is_match_complete(match):
            MatchScoringService._clear_match_result(match)

            PlayerScoreService.update_player_scores(match)

            return match

        scores = MatchPlayerScore.objects.filter(
            match=match,
        )

        team1_score = (
            scores
            .filter(team=match.team1)
            .aggregate(total=Sum("score"))
            .get("total")
            or 0
        )

        team2_score = (
            scores
            .filter(team=match.team2)
            .aggregate(total=Sum("score"))
            .get("total")
            or 0
        )

        game_type = get_game_type(
            match.round.tournament.game_type,
        )

        winner = game_type.determine_winner(
            match,
            team1_score,
            team2_score,
        )

        match.score_team1 = team1_score
        match.score_team2 = team2_score
        match.winner = winner

        match.save(
            update_fields=[
                "score_team1",
                "score_team2",
                "winner",
            ]
        )

        return match


    @staticmethod
    def is_match_complete(match):
        """
        مشخص می‌کند آیا تمام اعضای دو تیم
        برای این Match نتیجه ثبت کرده‌اند یا نه.
        """

        team1_members = TeamMembership.objects.filter(
            team=match.team1,
        ).count()

        team2_members = TeamMembership.objects.filter(
            team=match.team2,
        ).count()

        team1_scores = MatchPlayerScore.objects.filter(
            match=match,
            team=match.team1,
        ).count()

        team2_scores = MatchPlayerScore.objects.filter(
            match=match,
            team=match.team2,
        ).count()

        return (
            team1_scores == team1_members
            and
            team2_scores == team2_members
        )


    @staticmethod
    def can_finalize(match):
        """
        آیا Match آماده نهایی‌شدن است؟
        """

        return MatchScoringService.is_match_complete(
            match,
        )


    @staticmethod
    def finalize_match(match):
        """
        نهایی‌کردن نتیجه Match.

        این متد فقط نتیجه Match را محاسبه می‌کند.
        پایان Round یا Tournament مسئولیت این سرویس نیست.
        """

        if not MatchScoringService.can_finalize(match):
            return MatchScoringService.recalculate_match(
                match,
            )

        return MatchScoringService.recalculate_match(
            match,
        )


    @staticmethod
    def _clear_match_result(match):
        """
        پاک کردن نتیجه Match زمانی که هنوز کامل نشده است.
        """

        match.score_team1 = None
        match.score_team2 = None
        match.winner = None

        match.save(
            update_fields=[
                "score_team1",
                "score_team2",
                "winner",
            ]
        )


    @staticmethod
    def finalize_timeout_match(match):
        scores = MatchPlayerScore.objects.filter(
            match=match,
        )

        team1_score = (
            scores
            .filter(team=match.team1)
            .aggregate(total=Sum("score"))
            .get("total")
            or 0
        )

        team2_score = (
            scores
            .filter(team=match.team2)
            .aggregate(total=Sum("score"))
            .get("total")
            or 0
        )

        game_type = get_game_type(
            match.round.tournament.game_type,
        )

        winner = game_type.determine_winner(
            match,
            team1_score,
            team2_score,
        )

        match.score_team1 = team1_score
        match.score_team2 = team2_score
        match.winner = winner
        match.status = "completed"
        match.forfeit_team = None

        match.save(
            update_fields=[
                "score_team1",
                "score_team2",
                "winner",
                "status",
                "forfeit_team",
            ]
        )

        return match