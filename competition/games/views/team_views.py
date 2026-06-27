from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from teams.forms import TeamCreateForm
from teams.models import Team, TeamMembership
from teams.services import TeamService
from django.shortcuts import get_object_or_404
from teams.services import TeamMemberService
from django.contrib.auth import get_user_model
from teams.statistics.team_statistics_service import TeamStatisticsService


@login_required
def create_team(request):

    # -----------------------------
    # 1. BUSINESS RULE → move to service
    # -----------------------------
    # (اینجا فقط UX check می‌ذاریم، نه قانون اصلی)
    if request.method == "POST":
        form = TeamCreateForm(request.POST, request_user=request.user)

        if form.is_valid():
            try:
                TeamService.create_team(
                    captain=request.user,
                    team_name=form.cleaned_data['name'],
                    members=form.cleaned_data['members']
                )

                return redirect('home')

            except Exception as e:
                form.add_error(None, str(e))

    else:
        form = TeamCreateForm(request_user=request.user)

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

            'wins': TeamStatisticsService.get_wins(team),
            'draws': TeamStatisticsService.get_draws(team),
            'losses': TeamStatisticsService.get_losses(team),
            'played': TeamStatisticsService.get_played(team),
            'points': TeamStatisticsService.get_points(team),
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


User = get_user_model()

@login_required
def manage_team_members(request, team_id):

    team = get_object_or_404(
        Team,
        id=team_id
    )

    if team.captain != request.user:
        return render(
            request,
            'games/error.html',
            {
                'message': 'فقط کاپیتان می‌تواند اعضای تیم را مدیریت کند.'
            }
        )

    if request.method == "POST":

        action = request.POST.get('action')
        user_id = request.POST.get('user_id')

        user = get_object_or_404(
            User,
            id=user_id
        )

        try:

            if action == "add":

                TeamMemberService.add_member(
                    team=team,
                    user=user
                )

            elif action == "remove":

                TeamMemberService.remove_member(
                    team=team,
                    user=user
                )

        except Exception as e:
            return render(
                request,
                'games/error.html',
                {
                    'message': str(e)
                }
            )

    members = TeamMembership.objects.filter(
        team=team
    )

    available_users = User.objects.exclude(
        id__in=members.values_list(
            'user_id',
            flat=True
        )
    )

    return render(
        request,
        'games/manage_team_members.html',
        {
            'team': team,
            'members': members,
            'available_users': available_users,
        }
    )