from django.shortcuts import render, get_object_or_404, redirect
from .models import Tournament
from games.models import Match
from .ranking_service import TournamentRankingService
from teams.statistics.team_statistics_service import TeamStatisticsService
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.exceptions import ValidationError
from .services import TournamentService
from teams.models import Team



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

    tournaments = Tournament.objects.select_related(
        'game_type'
    ).order_by('-created_at')

    return render(
        request,
        'competitions/tournament_list.html',
        {
            'tournaments': tournaments,
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

    rounds = tournament.rounds.all()

    matches = Match.objects.filter(
        round__tournament=tournament
    ).select_related(
        'team1',
        'team2',
        'round',
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

    current_round = rounds.filter(
        status='active'
    ).first()

    if current_round is None:
        current_round = rounds.order_by(
            '-number'
        ).first()

    captain_team = Team.objects.filter(
        captain=request.user
    ).first() if request.user.is_authenticated else None

    is_team_registered = False

    if captain_team:
        is_team_registered = tournament.teams.filter(
            team=captain_team
        ).exists()

    return render(
        request,
        'competitions/tournament_detail.html',
        {
            'tournament': tournament,
            'teams': teams,
            'rounds': rounds,
            'matches': matches,
            'current_round': current_round,
            'total_matches': total_matches,
            'played_matches': played_matches,
            'progress': progress,
            'captain_team': captain_team,
            'is_team_registered': is_team_registered,
        }
    )


@login_required
def register_team_in_tournament(request, tournament_id):

    tournament = get_object_or_404(
        Tournament,
        id=tournament_id
    )

    if request.method != "POST":
        return redirect(
            "tournament_detail",
            tournament_id=tournament.id
        )

    try:

        TournamentService.register_team_by_captain(
            tournament=tournament,
            captain=request.user,
        )

        messages.success(
            request,
            "تیم شما با موفقیت در Tournament ثبت شد."
        )

    except ValidationError as e:

        messages.error(
            request,
            str(e)
        )

    return redirect(
        "tournament_detail",
        tournament_id=tournament.id
    )