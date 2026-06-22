from django.db.models import Sum

from .models import MatchPlayerScore


class MatchScoringService:

    @staticmethod
    def recalculate_match(match):

        team1_score = (
            MatchPlayerScore.objects.filter(
                match=match,
                team=match.team1
            ).aggregate(
                total=Sum('score')
            )['total']
            or 0
        )

        team2_score = (
            MatchPlayerScore.objects.filter(
                match=match,
                team=match.team2
            ).aggregate(
                total=Sum('score')
            )['total']
            or 0
        )

        match.score_team1 = team1_score
        match.score_team2 = team2_score

        if team1_score > team2_score:
            match.winner = match.team1

        elif team2_score > team1_score:
            match.winner = match.team2

        else:
            match.winner = None

        match.save()

        return match