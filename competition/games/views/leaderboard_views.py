from teams.models import Team
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from ..player_ranking_service import (
    PlayerRankingService
)

def leaderboard(request):

    teams = Team.objects.all()

    table = []

    for team in teams:
        table.append({
            'team': team,
            'points': team.get_points(),
            'wins': team.get_wins(),
            'draws': team.get_draws(),
            'losses': team.get_losses(),
        })

    table.sort(key=lambda x: x['points'], reverse=True)

    return render(
        request,
        'games/leaderboard.html',
        {
            'table': table
        }
    )



@login_required
def player_leaderboard(request):

    table = (
        PlayerRankingService.build_leaderboard()
    )

    return render(
        request,
        'games/player_leaderboard.html',
        {
            'table': table,
        }
    )