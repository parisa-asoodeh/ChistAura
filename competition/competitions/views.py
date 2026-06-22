from django.shortcuts import render, get_object_or_404

from .models import Tournament
from games.models import Match


def tournament_leaderboard(request, tournament_id):

    tournament = get_object_or_404(
        Tournament,
        id=tournament_id
    )

    teams = [
        tt.team
        for tt in tournament.teams.select_related(
            'team'
        )
    ]

    table = []

    for team in teams:

        table.append({
            'team': team,
            'points': team.get_points_in_tournament(
                tournament
            ),
            'wins': team.get_wins_in_tournament(
                tournament
            ),
            'draws': team.get_draws_in_tournament(
                tournament
            ),
            'losses': team.get_losses_in_tournament(
                tournament
            ),
        })

    table.sort(
        key=lambda row: row['points'],
        reverse=True
    )

    return render(
        request,
        'competitions/tournament_leaderboard.html',
        {
            'tournament': tournament,
            'table': table,
        }
    )


def tournament_list(request):

    tournaments = Tournament.objects.all()

    return render(
        request,
        'competitions/tournament_list.html',
        {
            'tournaments': tournaments
        }
    )


def tournament_detail(request, tournament_id):

    tournament = get_object_or_404(
        Tournament,
        id=tournament_id
    )

    teams = tournament.teams.select_related(
        'team'
    )

    matches = Match.objects.filter(
        tournament=tournament
    )

    total_matches = matches.count()

    played_matches = sum(
        1
        for match in matches
        if match.is_complete
    )

    progress = 0

    if total_matches:
        progress = int(
            played_matches * 100 / total_matches
        )

    return render(
        request,
        'competitions/tournament_detail.html',
        {
            'tournament': tournament,
            'teams': teams,
            'matches': matches,

            'total_matches': total_matches,
            'played_matches': played_matches,
            'progress': progress,
        }
    )