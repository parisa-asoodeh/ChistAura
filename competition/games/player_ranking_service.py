from django.contrib.auth import get_user_model
from django.db.models import Sum

from .models import MatchPlayerScore


User = get_user_model()


class PlayerRankingService:

    @staticmethod
    def ranking_key(row):

        return (
            row['total_score'],
            row['average_score'],
        )

    @staticmethod
    def build_leaderboard():

        leaderboard = []

        users = User.objects.all()

        for user in users:

            scores = MatchPlayerScore.objects.filter(
                user=user
            )

            total_score = (
                scores.aggregate(
                    total=Sum('score')
                )['total']
                or 0
            )

            matches_played = scores.count()

            average_score = 0

            if matches_played:

                average_score = (
                    total_score / matches_played
                )

            leaderboard.append({
                'user': user,
                'total_score': total_score,
                'matches_played': matches_played,
                'average_score': round(
                    average_score,
                    2
                ),
            })

        leaderboard.sort(
            key=PlayerRankingService.ranking_key,
            reverse=True
        )

        return leaderboard