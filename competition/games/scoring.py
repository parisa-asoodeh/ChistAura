from django.db.models import Sum
from .models import MatchPlayerScore
from teams.models import TeamMembership
from .game_types.registry import get_game_type


class MatchScoringService:

    @staticmethod
    def recalculate_match(match):

        scores = MatchPlayerScore.objects.filter(
            match=match
        )


        team1_scores_exist = scores.filter(
            team=match.team1
        ).exists()


        team2_scores_exist = scores.filter(
            team=match.team2
        ).exists()


        # اگر هر دو تیم هنوز امتیاز نگرفته‌اند
        # یا فقط یکی از تیم‌ها امتیاز دارد،
        # مسابقه کامل نشده است
        if not team1_scores_exist or not team2_scores_exist:

            match.score_team1 = None
            match.score_team2 = None
            match.winner = None

            match.save(
                update_fields=[
                    'score_team1',
                    'score_team2',
                    'winner',
                ]
            )

            return match



        team1_score = (
            scores.filter(
                team=match.team1
            )
            .aggregate(
                total=Sum('score')
            )['total']
            or 0
        )


        team2_score = (
            scores.filter(
                team=match.team2
            )
            .aggregate(
                total=Sum('score')
            )['total']
            or 0
        )


        if not MatchScoringService.is_match_complete(
            match
        ):

            match.score_team1 = None
            match.score_team2 = None
            match.winner = None

            match.save(
                update_fields=[
                    'score_team1',
                    'score_team2',
                    'winner',
                ]
            )

            return match


        match.score_team1 = team1_score
        match.score_team2 = team2_score


        game_type = get_game_type(
            match.tournament.game_type
        )

        match.winner = (
            game_type.determine_winner(
                match,
                team1_score,
                team2_score
            )
        )

        match.save(
            update_fields=[
                'score_team1',
                'score_team2',
                'winner',
            ]
        )

        return match



    @staticmethod
    def is_match_complete(match):

        team1_members = TeamMembership.objects.filter(
            team=match.team1
        ).count()

        team2_members = TeamMembership.objects.filter(
            team=match.team2
        ).count()

        team1_scores = MatchPlayerScore.objects.filter(
            match=match,
            team=match.team1
        ).count()

        team2_scores = MatchPlayerScore.objects.filter(
            match=match,
            team=match.team2
        ).count()

        return (
            team1_scores == team1_members
            and
            team2_scores == team2_members
        )