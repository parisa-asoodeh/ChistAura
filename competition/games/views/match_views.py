from ..models import Match
from django.shortcuts import render, get_object_or_404
from games.match_detail_service import MatchDetailService
from django.core.exceptions import PermissionDenied
from teams.models import TeamMembership
from django.db.models import Q



def match_list(request):

    matches = Match.objects.all().order_by('-played_at')

    if request.user.is_authenticated and not request.user.is_staff:

        user_team = TeamMembership.objects.filter(
            user=request.user
        ).values_list(
            'team_id',
            flat=True
        ).first()

        if user_team:

            matches = matches.filter(
                Q(team1_id=user_team) |
                Q(team2_id=user_team)
            )

        else:

            matches = matches.none()

    return render(
        request,
        'games/match_list.html',
        {
            'matches': matches
        }
    )



def match_detail(request, match_id):

    match = get_object_or_404(
        Match,
        id=match_id,
    )

    if request.user.is_authenticated and not request.user.is_staff:

        is_member = TeamMembership.objects.filter(
            user=request.user,
            team__in=[
                match.team1_id,
                match.team2_id,
            ],
        ).exists()

        if not is_member:
            raise PermissionDenied

    context = MatchDetailService.build(
        match
    )

    return render(
        request,
        "games/match_detail.html",
        context
    )
