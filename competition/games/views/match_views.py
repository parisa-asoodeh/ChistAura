from ..models import Match
from django.shortcuts import render, get_object_or_404



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
    
    return render(
        request,
        'games/match_detail.html',
        {
            'match': match
        }
    )