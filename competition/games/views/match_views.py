from ..models import Match
from django.shortcuts import render, get_object_or_404
from games.models import MatchPlayerScore
from games.match_detail_service import MatchDetailService



def match_list(request):

    matches = Match.objects.all().order_by('-played_at')

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
        id=match_id
    )

    context = MatchDetailService.build(
        match
    )

    return render(
        request,
        "games/match_detail.html",
        context
    )
