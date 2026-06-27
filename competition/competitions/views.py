from django.shortcuts import render, get_object_or_404
from .models import Tournament
from games.models import Match
from .ranking_service import TournamentRankingService
from teams.statistics.team_statistics_service import TeamStatisticsService


def tournament_leaderboard(request, tournament_id):

    tournament = get_object_or_404(
        Tournament,
        id=tournament_id
    )

    teams = TournamentRankingService.rank_teams(
        tournament
    )

    table = []

    for team in teams:

        table.append({
            'team': team,
            'points': TeamStatisticsService.get_points_in_tournament(
                team,
                tournament
            ),
            'wins': TeamStatisticsService.get_wins_in_tournament(
                team,
                tournament
            ),
            'draws': TeamStatisticsService.get_draws_in_tournament(
                team,
                tournament
            ),
            'losses': TeamStatisticsService.get_losses_in_tournament(
                team,
                tournament
            ),
            'score_difference':
                TeamStatisticsService.get_score_difference_in_tournament(
                    team,
                    tournament
                ),
            'total_time':
                TeamStatisticsService.get_total_time_in_tournament(
                    team,
                    tournament
                ),
        })

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