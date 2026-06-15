from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from teams.forms import TeamCreateForm
from teams.models import Team, TeamMembership
from teams.services import TeamService
from django.shortcuts import get_object_or_404
from .models import Match
from collections import defaultdict

@login_required
def create_team(request):

    # اگر کاربر قبلاً عضو تیم باشد
    if TeamMembership.objects.filter(user=request.user).exists():
        return render(
            request,
            'games/error.html',
            {
                'message': 'شما قبلاً عضو یک تیم شده‌اید.'
            }
        )

    if request.method == 'POST':

        form = TeamCreateForm(request.POST)

        if form.is_valid():

            TeamService.create_team(
                captain=request.user,
                team_name=form.cleaned_data['name'],
                members=form.cleaned_data['members']
            )

            return redirect('home')

    else:
        form = TeamCreateForm()

    return render(
        request,
        'games/create_team.html',
        {
            'form': form
        }
    )



def team_list(request):
    teams = sorted(
        Team.objects.all(),
        key=lambda t: t.get_points(),
        reverse=True
    )

    return render(
        request,
        'games/team_list.html',
        {
            'teams': teams
        }
    )


def team_detail(request, team_id):

    team = get_object_or_404(Team, id=team_id)
    members = TeamMembership.objects.filter(team=team)

    return render(
        request,
        'games/team_detail.html',
        {
            'team': team,
            'members': members,

            'wins': team.get_wins(),
            'draws': team.get_draws(),
            'losses': team.get_losses(),
            'played': team.get_played(),
            'points': team.get_points(),
        }
    )


@login_required
def my_team(request):

    membership = TeamMembership.objects.filter(
        user=request.user
    ).first()

    if not membership:
        return render(
            request,
            'games/error.html',
            {
                'message': 'شما هنوز عضو هیچ تیمی نیستید.'
            }
        )

    return redirect(
        'team_detail',
        team_id=membership.team.id
    )


def match_list(request):

    matches = Match.objects.all().order_by('-played_at')

    return render(
        request,
        'games/match_list.html',
        {
            'matches': matches
        }
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